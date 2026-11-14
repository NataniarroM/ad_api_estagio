import React, { useState, useEffect } from 'react';
import './Cadastro.css';
import Cabecalho from './components/Cabecalho';

export default function Cadastro() {
  const [form, setForm] = useState({
    nome: '', email: '', senha: '', confirmarSenha: '', telefone: '', semestre: '', id_curso: ''
  });
  const [tipoConta, setTipoConta] = useState('usuario');
  const [cursos, setCursos] = useState([]);
  const [carregando, setCarregando] = useState(false);
  const [mensagem, setMensagem] = useState({ tipo: '', texto: '' });

  // Busca os cursos na API para preencher a barra de rolagem
  useEffect(() => {
    fetch('http://127.0.0.1:8000/api/cursos')
      .then(res => res.ok ? res.json() : [])
      .then(data => setCursos(data))
      .catch(err => console.error('Erro ao buscar cursos:', err));
  }, []);

  const handleChange = (e) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  const aoEnviarCadastro = async (e) => {
    e.preventDefault();
    if (form.senha !== form.confirmarSenha) {
      return setMensagem({ tipo: 'erro', texto: 'As senhas não coincidem.' });
    }

    setCarregando(true);
    setMensagem({ tipo: '', texto: '' });

    try {
      const resposta = await fetch('http://127.0.0.1:8000/auth/cadastro', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          nome: form.nome,
          email: form.email,
          senha: form.senha,
          tipo: tipoConta,
          // Convertendo telefone e semestre para números inteiros (int) conforme o seu back-end exige
          telefone: form.telefone ? Number(form.telefone) : null,
          semestre: form.semestre ? Number(form.semestre) : null,
          id_curso: form.id_curso ? Number(form.id_curso) : null,
        }),
      });

      if (resposta.ok) {
        setMensagem({ tipo: 'sucesso', texto: 'Conta criada com sucesso!' });
        setForm({ nome: '', email: '', senha: '', confirmarSenha: '', telefone: '', semestre: '', id_curso: '' });
      } else {
        const dadosErro = await resposta.json();
        setMensagem({ tipo: 'erro', texto: dadosErro.detail || 'Erro ao realizar o cadastro.' });
      }
    } catch (erro) {
      setMensagem({ tipo: 'erro', texto: 'Não foi possível conectar ao servidor.' });
    } finally {
      setCarregando(false);
    }
  };

  return (
    <div className="pagina-cadastro">
      <Cabecalho />
      <main className="conteudo-cadastro">
        <div className="cartao-cadastro">
          <h2 className="titulo-pagina">Crie a sua conta</h2>
          <p className="subtitulo-pagina">Comece a procurar as melhores oportunidades</p>

          <div className="seletor-tipo-conta">
            {['usuario', 'recrutador', 'administrador'].map((tipo) => (
              <button
                key={tipo}
                type="button"
                className={`botao-tipo ${tipoConta === tipo ? 'ativo' : ''}`}
                onClick={() => setTipoConta(tipo)}
              >
                {tipo.charAt(0).toUpperCase() + tipo.slice(1)}
              </button>
            ))}
          </div>

          {mensagem.texto && (
            <div className={`mensagem-alerta ${mensagem.tipo}`}>{mensagem.texto}</div>
          )}

          <form onSubmit={aoEnviarCadastro} className="formulario-cadastro">
            {[
              { label: 'Nome Completo', name: 'nome', type: 'text', placeholder: 'Digite o seu nome' },
              { label: 'E-mail', name: 'email', type: 'email', placeholder: 'exemplo@email.com' },
              { label: 'Senha', name: 'senha', type: 'password', placeholder: 'Mínimo de 6 caracteres' },
              { label: 'Confirmar Senha', name: 'confirmarSenha', type: 'password', placeholder: 'Repita a sua senha' },
              { label: 'Telefone (Apenas números)', name: 'telefone', type: 'number', placeholder: 'Ex: 11988888888' },
              { label: 'Semestre (Apenas números)', name: 'semestre', type: 'number', placeholder: 'Ex: 3' },
            ].map((campo) => (
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
                    required
                  />
                </div>
              </div>
            ))}

            <div className="grupo-campo">
              <label className="rotulo-campo">Curso</label>
              <div className="caixa-campo">
                <select
                  name="id_curso"
                  className="campo-texto"
                  value={form.id_curso}
                  onChange={handleChange}
                  required
                >
                  <option value="">-- Selecione o seu curso --</option>
                  {cursos.map((curso) => (
                    <option key={curso.id} value={curso.id}>
                      ID: {curso.id} - {curso.nome}
                    </option>
                  ))}
                </select>
              </div>
            </div>

            <button type="submit" className="botao-cadastrar" disabled={carregando}>
              {carregando ? 'Criando conta...' : 'Cadastrar'}
            </button>
          </form>

          <div className="rodape-card">
            <span>Já tem uma conta? </span>
            <a href="/login" className="link-entrar">Entrar</a>
          </div>
        </div>
      </main>
    </div>
  );
}