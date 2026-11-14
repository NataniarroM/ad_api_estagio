import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import Cabecalho from './components/Cabecalho';
import './Login.css';

export default function Login() {
  const navigate = useNavigate();
  const [email, setEmail] = useState('');
  const [senha, setSenha] = useState('');
  const [carregando, setCarregando] = useState(false);
  const [mensagem, setMensagem] = useState({ tipo: '', texto: '' });

  const aoEnviarLogin = async (e) => {
    e.preventDefault();
    setCarregando(true);
    setMensagem({ tipo: '', texto: '' });

    try {
      // 1. Apontando para o Java na porta 8080
      const resposta = await fetch('http://localhost:8080/auth/login', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ email, senha }),
      });

      const dados = await resposta.json();

      if (!resposta.ok) {
        throw new Error(dados.detail || 'E-mail ou senha incorretos.');
      }

      // Guarda o token
      const token = dados.access_token;
      localStorage.setItem('access_token', token);

      // 2. Apontando para o Java na porta 8080 para pegar o perfil
      const respostaPerfil = await fetch('http://localhost:8080/api/perfil', {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });

      if (!respostaPerfil.ok) {
        throw new Error('Erro ao carregar os dados do perfil.');
      }

      const dadosPerfil = await respostaPerfil.json();
      const tipoUsuario = dadosPerfil.tipo; 

      localStorage.setItem('tipo_usuario', tipoUsuario);
      setMensagem({ tipo: 'sucesso', texto: 'Login efetuado com sucesso!' });

      // 3. Redireciona
      setTimeout(() => {
        if (tipoUsuario === 'recrutador' || tipoUsuario === 'empresa') {
          navigate('/cadastrovaga');
        } else {
          navigate('/');
        }
      }, 1000);

    } catch (erro) {
      console.error('Erro no login:', erro);
      setMensagem({
        tipo: 'erro',
        texto: erro.message || 'Não foi possível conectar ao servidor.',
      });
    } finally {
      setCarregando(false);
    }
  };

  return (
    <div className="pagina-login">
      <Cabecalho />
      <main className="conteudo-login">
        <div className="cartao-login">
          <h2 className="titulo-pagina">Bem-vindo de volta!</h2>
          <p className="subtitulo-pagina">Entre na sua conta para continuar</p>

          {mensagem.texto && (
            <div className={`mensagem-alerta ${mensagem.tipo}`}>
              {mensagem.texto}
            </div>
          )}

          <form onSubmit={aoEnviarLogin} className="formulario-login">
            <div className="grupo-campo">
              <label className="rotulo-campo">E-mail</label>
              <div className="caixa-campo">
                <input
                  type="email"
                  className="campo-texto"
                  placeholder="seu@email.com"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  required
                />
              </div>
            </div>

            <div className="grupo-campo">
              <label className="rotulo-campo">Senha</label>
              <div className="caixa-campo">
                <input
                  type="password"
                  className="campo-texto"
                  placeholder="Sua senha"
                  value={senha}
                  onChange={(e) => setSenha(e.target.value)}
                  required
                />
              </div>
            </div>

            <div className="opcoes-login">
              <a href="#recuperar" className="link-esqueci">Esqueceu a senha?</a>
            </div>

            <button type="submit" className="botao-entrar" disabled={carregando}>
              {carregando ? 'A entrar...' : 'Entrar'}
            </button>
          </form>

          <div className="rodape-card">
            <span>Ainda não tem uma conta? </span>
            <Link to="/cadastro" className="link-cadastrar">Cadastre-se</Link>
          </div>
        </div>
      </main>
    </div>
  );
}