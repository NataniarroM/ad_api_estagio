import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import Cabecalho from './components/Cabecalho';
import './Login.css';

export default function Login() {//cria os campos 
  const [email, setEmail] = useState('');
  const [senha, setSenha] = useState('');
  const [carregando, setCarregando] = useState(false);
  const [mensagem, setMensagem] = useState({ tipo: '', texto: '' });

  const aoEnviarLogin = async (e) => {//prepara o formulario para carregar, carregamento = true
    e.preventDefault();
    setCarregando(true);
    setMensagem({ tipo: '', texto: '' });

    try {
      // Exemplo de requisição para o endpoint de login do FastAPI
      const resposta = await fetch('http://127.0.0.1:8000/api/login', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',//formato json
        },
        body: JSON.stringify({ email, senha }),//variaveis que estão salvas em json
      });

      if (resposta.ok) {
        setMensagem({ tipo: 'sucesso', texto: 'Login efetuado com sucesso!' });
        //login ok
      } else {
        const dadosErro = await resposta.json();
        setMensagem({
          tipo: 'erro',
          texto: dadosErro.detail || 'E-mail ou senha incorretos.',//volta de erro
        });
      }
    } catch (erro) {
      console.error('Erro de conexão:', erro);
      setMensagem({
        tipo: 'erro',
        texto: 'Não foi possível conectar ao servidor.',
      });
    } finally {
      setCarregando(false);//se errado = carregamento false
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
                  onChange={(e) => setEmail(e.target.value)}//inserir email
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
                  onChange={(e) => setSenha(e.target.value)}//inserir senha
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