
import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import Cabecalho from './components/Cabecalho';
import './login.css';
import fundoLogin from './assets/fundo-login-estagup.png';

export default function Login() {
  const navigate = useNavigate();

  const [email, setEmail] = useState('');
  const [senha, setSenha] = useState('');
  const [mostrarSenha, setMostrarSenha] = useState(false);
  const [carregando, setCarregando] = useState(false);
  const [mensagem, setMensagem] = useState({
    tipo: '',
    texto: ''
  });

  const aoEnviarLogin = async (e) => {
    e.preventDefault();
    setCarregando(true);
    setMensagem({ tipo: '', texto: '' });

    try {
      const resposta = await fetch(
        'http://localhost:8080/auth/login',
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ email, senha }),
        }
      );

      const dados = await resposta.json();

      if (!resposta.ok) {
        throw new Error(
          dados.detail || 'E-mail ou senha incorretos.'
        );
      }

      const token = dados.access_token;
      localStorage.setItem('access_token', token);

      const respostaPerfil = await fetch(
        'http://localhost:8080/api/perfil',
        {
          method: 'GET',
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );

      if (!respostaPerfil.ok) {
        throw new Error(
          'Erro ao carregar os dados do perfil.'
        );
      }

      const dadosPerfil = await respostaPerfil.json();
      const tipoUsuario = dadosPerfil.tipo;

      localStorage.setItem('tipo_usuario', tipoUsuario);

      setMensagem({
        tipo: 'sucesso',
        texto: 'Login efetuado com sucesso!'
      });

      setTimeout(() => {
        if (
          tipoUsuario === 'recrutador' ||
          tipoUsuario === 'empresa'
        ) {
          navigate('/cadastrovaga');
        } else {
          navigate('/');
        }
      }, 1000);

    } catch (erro) {
      console.error('Erro no login:', erro);

      setMensagem({
        tipo: 'erro',
        texto:
          erro.message ||
          'Não foi possível conectar ao servidor.',
      });
    } finally {
      setCarregando(false);
    }
  };

  return (
    <div className="pagina-login">
      <Cabecalho />

      <main
        className="conteudo-login"
        style={{
          backgroundImage: `url(${fundoLogin})`,
          backgroundSize: 'cover',
          backgroundPosition: 'center',
          backgroundRepeat: 'no-repeat',
          backgroundColor: '#fff7f2'
        }}
      >
        <div className="cartao-login">

          {/* LOGO ACADÊMICA */}
          <div className="logo-login">
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

              <circle
                cx="9"
                cy="42"
                r="3"
                fill="#A9533D"
              />

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

          {/* TÍTULO */}
          <h2 className="titulo-pagina">
            Bem-vindo de <span>volta!</span>
          </h2>

          <p className="subtitulo-pagina">
            Entre na sua conta para continuar.
          </p>

          {/* MENSAGENS */}
          {mensagem.texto && (
            <div
              className={`mensagem-alerta ${mensagem.tipo}`}
            >
              {mensagem.texto}
            </div>
          )}

          {/* FORMULÁRIO */}
          <form
            onSubmit={aoEnviarLogin}
            className="formulario-login"
          >

            {/* E-MAIL */}
            <div className="grupo-campo">
              <label
                className="rotulo-campo"
                htmlFor="email-login"
              >
                E-mail
              </label>

              <div className="caixa-campo">
                <svg
                  viewBox="0 0 24 24"
                  width="20"
                  height="20"
                  fill="none"
                  stroke="currentColor"
                  strokeWidth="1.8"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  aria-hidden="true"
                >
                  <rect
                    x="3"
                    y="5"
                    width="18"
                    height="14"
                    rx="2"
                  />
                  <path d="m3 7 9 7 9-7" />
                </svg>

                <input
                  id="email-login"
                  type="email"
                  className="campo-texto"
                  placeholder="seu@email.com"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  required
                />
              </div>
            </div>

            {/* SENHA */}
            <div className="grupo-campo">
              <label
                className="rotulo-campo"
                htmlFor="senha-login"
              >
                Senha
              </label>

              <div className="caixa-campo">
                <svg
                  viewBox="0 0 24 24"
                  width="20"
                  height="20"
                  fill="none"
                  stroke="currentColor"
                  strokeWidth="1.8"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  aria-hidden="true"
                >
                  <rect
                    x="5"
                    y="10"
                    width="14"
                    height="11"
                    rx="2"
                  />
                  <path d="M8 10V7a4 4 0 0 1 8 0v3" />
                  <path d="M12 14v3" />
                </svg>

                <input
                  id="senha-login"
                  type={mostrarSenha ? 'text' : 'password'}
                  className="campo-texto"
                  placeholder="Sua senha"
                  value={senha}
                  onChange={(e) => setSenha(e.target.value)}
                  required
                />

                {/* MOSTRAR / OCULTAR SENHA */}
                <button
                  type="button"
                  className="botao-ver-senha"
                  onClick={() => setMostrarSenha(!mostrarSenha)}
                  aria-label={
                    mostrarSenha
                      ? 'Ocultar senha'
                      : 'Mostrar senha'
                  }
                >
                  <svg
                    viewBox="0 0 24 24"
                    width="20"
                    height="20"
                    fill="none"
                    stroke="currentColor"
                    strokeWidth="1.8"
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    aria-hidden="true"
                  >
                    <path d="M2 12s3.5-6 10-6 10 6 10 6-3.5 6-10 6-10-6-10-6Z" />
                    <circle cx="12" cy="12" r="3" />

                    {mostrarSenha && (
                      <path d="M3 3l18 18" />
                    )}
                  </svg>
                </button>
              </div>
            </div>

            {/* ESQUECEU A SENHA */}
            <div className="opcoes-login">
              <a
                href="#recuperar"
                className="link-esqueci"
              >
                Esqueceu a senha?
              </a>
            </div>

            {/* BOTÃO ENTRAR */}
            <button
              type="submit"
              className="botao-entrar"
              disabled={carregando}
            >
              {carregando ? 'Entrando...' : 'Entrar'}
            </button>
          </form>

          {/* CADASTRO */}
          <div className="rodape-card">
            <span>Ainda não tem uma conta? </span>

            <Link
              to="/cadastro"
              className="link-cadastrar"
            >
              Cadastre-se
            </Link>
          </div>

        </div>
      </main>
    </div>
  );
}
