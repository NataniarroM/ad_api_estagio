import React, { useState } from 'react';
import './Cadastro.css';
import Cabecalho from './components/Cabecalho';

export default function Cadastro() {
  const [nome, setNome] = useState('');
  const [email, setEmail] = useState('');
  const [senha, setSenha] = useState('');
  const [confirmarSenha, setConfirmarSenha] = useState('');
  const [tipoConta, setTipoConta] = useState('estudante');
  const [carregando, setCarregando] = useState(false);
  const [mensagem, setMensagem] = useState({ tipo: '', texto: '' });

  const aoEnviarCadastro = async (e) => {
    e.preventDefault();

    if (senha !== confirmarSenha) {
      setMensagem({ tipo: 'erro', texto: 'As senhas não coincidem.' });
      return;
    }

    setCarregando(true);
    setMensagem({ tipo: '', texto: '' });

    try {
    const resposta = await fetch('http://127.0.0.1:8000/auth/cadastro', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          nome,
          email,
          senha,
          tipo: tipoConta,
        }),
      });

      if (resposta.ok) {
        setMensagem({ tipo: 'sucesso', texto: 'Conta criada com sucesso!' });
        setNome('');
        setEmail('');
        setSenha('');
        setConfirmarSenha('');
      } else {
        const dadosErro = await resposta.json();
        setMensagem({
          tipo: 'erro',
          texto: dadosErro.detail || 'Erro ao realizar o cadastro.',
        });
      }
    } catch (erro) {
      console.error('Erro de conexão:', erro);
      setMensagem({
        tipo: 'erro',
        texto: 'Não foi possível conectar ao servidor.',
      });
    } finally {
      setCarregando(false);
    }
  };

  return (
    <div className="pagina-cadastro">
      <Cabecalho />
      {/* Conteúdo Principal / Cartão de Cadastro */}
      <main className="conteudo-cadastro">
        <div className="cartao-cadastro">
          <h2 className="titulo-pagina">Crie a sua conta</h2>
          <p className="subtitulo-pagina">Comece a procurar as melhores oportunidades</p>

          {/* Botões para Escolher o Tipo de Conta */}
          <div className="seletor-tipo-conta">
            <button
              type="button"
              className={`botao-tipo ${tipoConta === 'estudante' ? 'ativo' : ''}`}
              onClick={() => setTipoConta('estudante')}
            >
              Estudante
            </button>
            <button
              type="button"
              className={`botao-tipo ${tipoConta === 'empresa' ? 'ativo' : ''}`}
              onClick={() => setTipoConta('empresa')}
            >
              Empresa
            </button>
          </div>

          {mensagem.texto && (
            <div className={`mensagem-alerta ${mensagem.tipo}`}>
              {mensagem.texto}
            </div>
          )}

          {/* Formulário */}
          <form onSubmit={aoEnviarCadastro} className="formulario-cadastro">
            <div className="grupo-campo">
              <label className="rotulo-campo">Nome Completo</label>
              <div className="caixa-campo">
                <input
                  type="text"
                  className="campo-texto"
                  placeholder="Digite o seu nome"
                  value={nome}
                  onChange={(e) => setNome(e.target.value)}
                  required
                />
              </div>
            </div>

            <div className="grupo-campo">
              <label className="rotulo-campo">E-mail</label>
              <div className="caixa-campo">
                <input
                  type="email"
                  className="campo-texto"
                  placeholder="exemplo@email.com"
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
                  placeholder="Mínimo de 6 caracteres"
                  value={senha}
                  onChange={(e) => setSenha(e.target.value)}
                  required
                />
              </div>
            </div>

            <div className="grupo-campo">
              <label className="rotulo-campo">Confirmar Senha</label>
              <div className="caixa-campo">
                <input
                  type="password"
                  className="campo-texto"
                  placeholder="Repita a sua senha"
                  value={confirmarSenha}
                  onChange={(e) => setConfirmarSenha(e.target.value)}
                  required
                />
              </div>
            </div>

            <button type="submit" className="botao-cadastrar" disabled={carregando}>
              {carregando ? 'A criar conta...' : 'Cadastrar'}
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