import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import './Cadastro.css';
import Cabecalho from './components/Cabecalho';

export default function Cadastro() {
  const navigate = useNavigate();
  const [form, setForm] = useState({
    nome: '',
    email: '',
    senha: '',
    telefone: '',
    semestre: '',
    id_curso: '',
  });
  const [tipoConta, setTipoConta] = useState('usuario');
  const [cursos, setCursos] = useState([]);
  const [carregando, setCarregando] = useState(false);
  const [mensagem, setMensagem] = useState({ tipo: '', texto: '' });

  useEffect(() => {
    fetch('http://localhost:8000/api/cursos')
      .then((res) => (res.ok ? res.json() : []))
      .then((data) => setCursos(Array.isArray(data) ? data : []))
      .catch(() => setCursos([]));
  }, []);

  const handleChange = (e) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  const selecionarTipoConta = (tipo) => {
    setTipoConta(tipo);
    if (tipo !== 'usuario') {
      setForm((prev) => ({ ...prev, semestre: '', id_curso: '' }));
    }
  };

  const aoEnviarCadastro = async (e) => {
    e.preventDefault();

    if (form.senha.length < 6) {
      return setMensagem({ tipo: 'erro', texto: 'A senha deve ter no mínimo 6 caracteres.' });
    }

    setCarregando(true);
    setMensagem({ tipo: '', texto: '' });

    const ehAluno = tipoConta === 'usuario';

    try {
      const resposta = await fetch('http://localhost:8000/auth/cadastro', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          nome: form.nome.trim(),
          email: form.email.trim(),
          senha: form.senha,
          tipo_usuario: tipoConta,
          telefone: form.telefone ? String(form.telefone).trim() : null,
          semestre: ehAluno && form.semestre ? Number(form.semestre) : null,
          id_curso: ehAluno && form.id_curso ? Number(form.id_curso) : null,
        }),
      });

      const dados = await resposta.json().catch(() => ({}));

      if (resposta.ok) {
        setMensagem({ tipo: 'sucesso', texto: 'Conta criada com sucesso! Redirecionando...' });
        setForm({ nome: '', email: '', senha: '', telefone: '', semestre: '', id_curso: '' });
        setTimeout(() => navigate('/login'), 1500);
      } else {
        const detalhe = Array.isArray(dados.detail)
          ? dados.detail.map((d) => d.msg).join(', ')
          : dados.detail;
        setMensagem({ tipo: 'erro', texto: detalhe || 'Erro ao realizar o cadastro.' });
      }
    } catch (erro) {
      setMensagem({ tipo: 'erro', texto: 'Não foi possível conectar ao servidor.' });
    } finally {
      setCarregando(false);
    }
  };

  const camposGerais = [
    { label: 'Nome Completo', name: 'nome', type: 'text', placeholder: 'Digite o seu nome', obrigatorio: true },
    { label: 'E-mail', name: 'email', type: 'email', placeholder: 'exemplo@email.com', obrigatorio: true },
    { label: 'Senha', name: 'senha', type: 'password', placeholder: 'Mínimo de 6 caracteres', obrigatorio: true },
    { label: 'Telefone (Apenas números)', name: 'telefone', type: 'tel', placeholder: 'Ex: 11988888888', obrigatorio: false },
  ];

  return (
    <div className="pagina-cadastro">
      <Cabecalho />
      <main className="conteudo-cadastro">
        <div className="cartao-cadastro">
          <h2 className="titulo-pagina">Crie a sua conta</h2>
          <p className="subtitulo-pagina">Comece a procurar as melhores oportunidades</p>

          <div className="seletor-tipo-conta">
            {['usuario', 'recrutador'].map((tipo) => (
              <button
                key={tipo}
                type="button"
                className={`botao-tipo ${tipoConta === tipo ? 'ativo' : ''}`}
                onClick={() => selecionarTipoConta(tipo)}
              >
                {tipo.charAt(0).toUpperCase() + tipo.slice(1)}
              </button>
            ))}
          </div>

          <p className="subtitulo-pagina">
            Contas de administrador são criadas pelo responsável pelo sistema.
            Se você já tem uma, use a opção Entrar.
          </p>

          {mensagem.texto && (
            <div className={`mensagem-alerta ${mensagem.tipo}`}>{mensagem.texto}</div>
          )}

          <form onSubmit={aoEnviarCadastro} className="formulario-cadastro">
            {camposGerais.map((campo) => (
              <div className="grupo-campo" key={campo.name}>
                <label className="rotulo-campo">{campo.label}</label>
                <div className="caixa-campo">
                  <input
                    type={campo.type}
                    name={campo.name}
                    className="campo-texto"
                    placeholder={campo.placeholder}
                    value={form[campo.name]}
                    onChange={handleChange}
                    required={campo.obrigatorio}
                  />
                </div>
              </div>
            ))}

            {tipoConta === 'usuario' && (
              <>
                <div className="grupo-campo">
                  <label className="rotulo-campo">Semestre (Apenas números)</label>
                  <div className="caixa-campo">
                    <input
                      type="number"
                      name="semestre"
                      className="campo-texto"
                      placeholder="Ex: 3"
                      value={form.semestre}
                      onChange={handleChange}
                      min={1}
                    />
                  </div>
                </div>

                <div className="grupo-campo">
                  <label className="rotulo-campo">Curso (Opcional)</label>
                  <div className="caixa-campo">
                    <select
                      name="id_curso"
                      className="campo-texto"
                      value={form.id_curso}
                      onChange={handleChange}
                    >
                      <option value="">-- Selecione o seu curso --</option>
                      {cursos.map((curso) => (
                        <option key={curso.id_curso || curso.id} value={curso.id_curso || curso.id}>
                          {curso.nome}
                        </option>
                      ))}
                    </select>
                  </div>
                </div>
              </>
            )}

            <button type="submit" className="botao-cadastrar" disabled={carregando}>
              {carregando ? 'Criando conta...' : 'Cadastrar'}
            </button>
          </form>

          <div className="rodape-card">
            <span>Já tem uma conta? </span>
            <Link to="/login" className="link-entrar">Entrar</Link>
          </div>
        </div>
      </main>
    </div>
  );
}
