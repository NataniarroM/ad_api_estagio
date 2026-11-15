
import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import Cabecalho from './components/Cabecalho';
import fundoCadastro from './assets/fundo-login-estagup.png';
import './Cadastro.css';

// Ícones utilizados nos campos
function Icone({ nome, tamanho = 20 }) {
  const desenhos = {
    usuario: (
      <>
        <circle cx="12" cy="7" r="4" />
        <path d="M4 21v-2a8 8 0 0 1 16 0v2" />
      </>
    ),
    recrutador: (
      <>
        <rect x="3" y="7" width="18" height="14" rx="2" />
        <path d="M8 7V5a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2" />
        <path d="M3 13h18" />
      </>
    ),
    administrador: (
      <>
        <path d="M12 2 20 5v6c0 5-3.5 8-8 11-4.5-3-8-6-8-11V5z" />
        <path d="m9 12 2 2 4-4" />
      </>
    ),
    email: (
      <>
        <rect x="3" y="5" width="18" height="14" rx="2" />
        <path d="m3 7 9 7 9-7" />
      </>
    ),
    senha: (
      <>
        <rect x="5" y="10" width="14" height="11" rx="2" />
        <path d="M8 10V7a4 4 0 0 1 8 0v3" />
      </>
    ),
    telefone: (
      <path d="M22 16.9v3a2 2 0 0 1-2.2 2A19 19 0 0 1 2.1 4.2 2 2 0 0 1 4.1 2h3a2 2 0 0 1 2 1.7l.5 3a2 2 0 0 1-.6 1.8L7.1 10a16 16 0 0 0 6.9 6.9l1.5-1.9a2 2 0 0 1 1.8-.6l3 .5a2 2 0 0 1 1.7 2Z" />
    ),
    semestre: (
      <>
        <rect x="3" y="5" width="18" height="16" rx="2" />
        <path d="M7 3v4M17 3v4M3 10h18" />
        <path d="M8 14h2M14 14h2M8 18h2" />
      </>
    ),
    curso: (
      <>
        <path d="M2 9 12 4l10 5-10 5z" />
        <path d="M6 11v6c3 3 9 3 12 0v-6" />
        <path d="M22 9v7" />
      </>
    ),
    olho: (
      <>
        <path d="M2 12s3.5-6 10-6 10 6 10 6-3.5 6-10 6-10-6-10-6Z" />
        <circle cx="12" cy="12" r="3" />
      </>
    ),
    ocultar: (
      <>
        <path d="M2 12s3.5-6 10-6 10 6 10 6-3.5 6-10 6-10-6-10-6Z" />
        <circle cx="12" cy="12" r="3" />
        <path d="M3 3 21 21" />
      </>
    )
  };

  return (
    <svg
      width={tamanho}
      height={tamanho}
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="1.8"
      strokeLinecap="round"
      strokeLinejoin="round"
      aria-hidden="true"
    >
      {desenhos[nome]}
    </svg>
  );
}

// Logo acadêmica do EstagUp
function LogoAcademica() {
  return (
    <div className="logo-cadastro">
      <svg viewBox="0 0 64 64" aria-hidden="true">
        <path
          d="M4 19 L32 7 L60 19 L32 32 Z"
          fill="#291B17"
        />
        <path
          d="M16 27 V36 Q32 49 48 36 V27 L32 34 Z"
          fill="#291B17"
        />
        <path
          d="M9 22 V40"
          stroke="#A9533D"
          strokeWidth="3"
          strokeLinecap="round"
        />
        <circle cx="9" cy="42" r="3" fill="#A9533D" />
        <path
          d="M9 52 Q32 60 55 35"
          fill="none"
          stroke="#A9533D"
          strokeWidth="5"
          strokeLinecap="round"
        />
        <path
          d="M44 35 L57 33 L55 46"
          fill="none"
          stroke="#A9533D"
          strokeWidth="5"
          strokeLinecap="round"
          strokeLinejoin="round"
        />
      </svg>
    </div>
  );
}

export default function Cadastro() {
  const navigate = useNavigate();
  const [form, setForm] = useState({
    nome: '',
    email: '',
    senha: '',
    confirmarSenha: '',
    telefone: '',
    semestre: '',
    id_curso: ''
  });

  const [tipoConta, setTipoConta] = useState('usuario');
  const [cursos, setCursos] = useState([]);
  const [carregando, setCarregando] = useState(false);
  const [mostrarSenha, setMostrarSenha] = useState(false);
  const [mostrarConfirmacao, setMostrarConfirmacao] = useState(false);
  const [mensagem, setMensagem] = useState({
    tipo: '',
    texto: ''
  });

  // Busca os cursos na API
  useEffect(() => {
    fetch('http://127.0.0.1:8000/api/cursos')
      .then((res) => res.ok ? res.json() : [])
      .then((data) => setCursos(Array.isArray(data) ? data : []))
      .catch((err) => console.error('Erro ao buscar cursos:', err));
  }, []);

  const handleChange = (e) => {
    setForm({
      ...form,
      [e.target.name]: e.target.value
    });
  };

  const selecionarTipoConta = (tipo) => {
    setTipoConta(tipo);
    if (tipo !== 'usuario') {
      setForm((anterior) => ({ ...anterior, semestre: '', id_curso: '' }));
    }
  };

  // Envio do cadastro
  const aoEnviarCadastro = async (e) => {
    e.preventDefault();

    if (form.senha !== form.confirmarSenha) {
      setMensagem({
        tipo: 'erro',
        texto: 'As senhas não coincidem.'
      });
      return;
    }

    if (form.senha.length < 6) {
      setMensagem({ tipo: 'erro', texto: 'A senha deve ter no mínimo 6 caracteres.' });
      return;
    }

    setCarregando(true);
    setMensagem({ tipo: '', texto: '' });

    try {
      const resposta = await fetch(
        'http://127.0.0.1:8000/auth/cadastro',
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            nome: form.nome.trim(),
            email: form.email.trim(),
            senha: form.senha,
            tipo_usuario: tipoConta,
            telefone: form.telefone.trim() || null,
            semestre: tipoConta === 'usuario' && form.semestre
              ? Number(form.semestre)
              : null,
            id_curso: tipoConta === 'usuario' && form.id_curso
              ? Number(form.id_curso)
              : null
          })
        }
      );

      if (resposta.ok) {
        setMensagem({
          tipo: 'sucesso',
          texto: 'Conta criada com sucesso! Redirecionando...'
        });

        setForm({
          nome: '',
          email: '',
          senha: '',
          confirmarSenha: '',
          telefone: '',
          semestre: '',
          id_curso: ''
        });
        setTimeout(() => navigate('/login'), 1500);
      } else {
        const dadosErro = await resposta.json().catch(() => ({}));
        const detalhe = Array.isArray(dadosErro.detail)
          ? dadosErro.detail.map((item) => item.msg).join(', ')
          : dadosErro.detail;

        setMensagem({
          tipo: 'erro',
          texto: detalhe || 'Erro ao realizar o cadastro.'
        });
      }
    } catch (erro) {
      console.error('Erro ao cadastrar:', erro);

      setMensagem({
        tipo: 'erro',
        texto: 'Não foi possível conectar ao servidor.'
      });
    } finally {
      setCarregando(false);
    }
  };

  const campos = [
    {
      label: 'Nome Completo',
      name: 'nome',
      type: 'text',
      placeholder: 'Digite o seu nome',
      icone: 'usuario',
      autoComplete: 'name'
    },
    {
      label: 'E-mail',
      name: 'email',
      type: 'email',
      placeholder: 'exemplo@email.com',
      icone: 'email',
      autoComplete: 'email'
    },
    {
      label: 'Senha',
      name: 'senha',
      type: 'password',
      placeholder: 'Mínimo de 6 caracteres',
      icone: 'senha',
      autoComplete: 'new-password'
    },
    {
      label: 'Confirmar Senha',
      name: 'confirmarSenha',
      type: 'password',
      placeholder: 'Repita a sua senha',
      icone: 'senha',
      autoComplete: 'new-password'
    },
    {
      label: 'Telefone (Apenas números)',
      name: 'telefone',
      type: 'tel',
      placeholder: 'Ex: 11988888888',
      icone: 'telefone',
      autoComplete: 'tel',
      inputMode: 'numeric'
    },
    {
      label: 'Semestre (Apenas números)',
      name: 'semestre',
      type: 'number',
      placeholder: 'Ex: 3',
      icone: 'semestre',
      min: 1
    }
  ];

  const tipos = [
    { valor: 'usuario', nome: 'Usuário', icone: 'usuario' },
    { valor: 'recrutador', nome: 'Recrutador', icone: 'recrutador' },
    { valor: 'administrador', nome: 'Administrador', icone: 'administrador' }
  ];

  return (
    <div className="pagina-cadastro">
      <Cabecalho />

      <main
        className="conteudo-cadastro"
        style={{
          backgroundImage: `url(${fundoCadastro})`,
          backgroundSize: 'cover',
          backgroundPosition: 'center',
          backgroundRepeat: 'no-repeat',
          backgroundColor: '#fff7f2'
        }}
      >
        <div className="cartao-cadastro">

          <LogoAcademica />

          <h2 className="titulo-pagina">
            Crie a sua <span>conta</span>
          </h2>

          <p className="subtitulo-pagina">
            Comece a procurar as melhores oportunidades
          </p>

          {/* Tipo de conta */}
          <div className="seletor-tipo-conta">
            {tipos.map((tipo) => (
              <button
                key={tipo.valor}
                type="button"
                className={`botao-tipo ${
                  tipoConta === tipo.valor ? 'ativo' : ''
                }`}
                onClick={() => selecionarTipoConta(tipo.valor)}
              >
                <Icone nome={tipo.icone} tamanho={17} />
                <span>{tipo.nome}</span>
              </button>
            ))}
          </div>

          {/* Mensagens */}
          {mensagem.texto && (
            <div className={`mensagem-alerta ${mensagem.tipo}`}>
              {mensagem.texto}
            </div>
          )}

          <form
            onSubmit={aoEnviarCadastro}
            className="formulario-cadastro"
          >

            {/* Campos do formulário */}
            {campos.filter((campo) => tipoConta === 'usuario' || campo.name !== 'semestre').map((campo) => {
              const ehSenha = campo.name === 'senha';
              const ehConfirmacao = campo.name === 'confirmarSenha';
              const temOlho = ehSenha || ehConfirmacao;

              const visivel = ehSenha
                ? mostrarSenha
                : mostrarConfirmacao;

              return (
                <div className="grupo-campo" key={campo.name}>
                  <label
                    className="rotulo-campo"
                    htmlFor={`cadastro-${campo.name}`}
                  >
                    {campo.label}
                  </label>

                  <div className="caixa-campo">
                    <Icone nome={campo.icone} />

                    <input
                      id={`cadastro-${campo.name}`}
                      type={
                        temOlho && visivel
                          ? 'text'
                          : campo.type
                      }
                      name={campo.name}
                      className="campo-texto"
                      placeholder={campo.placeholder}
                      value={form[campo.name]}
                      onChange={handleChange}
                      autoComplete={campo.autoComplete}
                      inputMode={campo.inputMode}
                      min={campo.min}
                      required={!['telefone', 'semestre'].includes(campo.name)}
                    />

                    {temOlho && (
                      <button
                        type="button"
                        className="botao-ver-senha"
                        onClick={() => {
                          if (ehSenha) {
                            setMostrarSenha(!mostrarSenha);
                          } else {
                            setMostrarConfirmacao(!mostrarConfirmacao);
                          }
                        }}
                        aria-label={
                          visivel
                            ? 'Ocultar senha'
                            : 'Mostrar senha'
                        }
                      >
                        <Icone
                          nome={visivel ? 'ocultar' : 'olho'}
                        />
                      </button>
                    )}
                  </div>
                </div>
              );
            })}

            {/* Curso */}
            {tipoConta === 'usuario' && (<div className="grupo-campo">
              <label
                className="rotulo-campo"
                htmlFor="cadastro-curso"
              >
                Curso (Opcional)
              </label>

              <div className="caixa-campo">
                <Icone nome="curso" />

                <select
                  id="cadastro-curso"
                  name="id_curso"
                  className="campo-texto"
                  value={form.id_curso}
                  onChange={handleChange}
                >
                  <option value="">
                    -- Selecione o seu curso --
                  </option>

                  {cursos.map((curso) => (
                    <option
                      key={curso.id_curso}
                      value={curso.id_curso}
                    >
                      ID: {curso.id_curso} - {curso.nome}
                    </option>
                  ))}
                </select>
              </div>
            </div>)}

            {/* Cadastrar */}
            <button
              type="submit"
              className="botao-cadastrar"
              disabled={carregando}
            >
              {carregando ? 'Criando conta...' : 'Cadastrar'}
            </button>

          </form>

          <div className="rodape-card">
            <span>Já tem uma conta? </span>
            <Link to="/login" className="link-entrar">
              Entrar
            </Link>
          </div>

        </div>
      </main>
    </div>
  );
}
