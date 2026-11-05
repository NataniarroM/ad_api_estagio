import React, { useState, useEffect } from 'react';
import Cabecalho from './components/Cabecalho';
import './Perfil.css';


export default function Perfil() {
  const [perfil, setPerfil] = useState({
    nome: 'Mariana Silva',
    subtitulo: 'Estudante de Engenharia de Software',
    email: 'mariana.silva@email.com',
    telefone: '(11) 99999-0000',
    local: 'São Paulo, SP',
  });

  const [editando, setEditando] = useState(false);
  const [mensagem, setMensagem] = useState({ tipo: '', texto: '' });

  // Exemplo de busca de dados ao backend FastAPI (simulado ou real)
  useEffect(() => {
    // Podes substituir pelo teu endpoint GET do perfil
    // fetch('http://127.0.0.1:8000/api/perfil')
  }, []);

  const aoSalvar = (e) => {
    e.preventDefault();
    setEditando(false);
    setMensagem({ tipo: 'sucesso', texto: 'Perfil atualizado com sucesso!' });
  };

  return (
    <div className="pagina-perfil">
      <Cabecalho />

      <main className="conteudo-perfil">
        <div className="cartao-perfil-topo">
          <div className="avatar-grande">
            <span className="texto-avatar-grande">MS</span>
          </div>
          <div className="info-usuario-topo">
            <h1 className="nome-usuario">{perfil.nome}</h1>
            <p className="subtitulo-usuario">{perfil.subtitulo}</p>
          </div>
          <button 
            className="botao-editar-perfil" 
            onClick={() => setEditando(!editando)}
          >
            {editando ? 'Cancelar' : '✏️ Editar Perfil'}
          </button>
        </div>

        {mensagem.texto && (
          <div className={`mensagem-alerta ${mensagem.tipo}`}>
            {mensagem.texto}
          </div>
        )}

        <div className="corpo-perfil">
          {/* Navegação lateral interna ou separadores */}
          <aside className="menu-lateral-perfil">
            <a href="#perfil" className="item-menu-perfil ativo">👤 Informações Pessoais</a>
            <a href="#curriculo" className="item-menu-perfil">📄 Currículo</a>
            <a href="#candidaturas" className="item-menu-perfil">📋 Candidaturas</a>
            <a href="#favoritos" className="item-menu-perfil">⭐ Vagas Salvas</a>
            <a href="#notificacoes" className="item-menu-perfil">🔔 Notificações</a>
          </aside>

          {/* Secção de Informações / Formulário */}
          <section className="detalhes-perfil">
            <div className="bloco-detalhes">
              <h2 className="titulo-bloco">Informações Pessoais</h2>

              {editando ? (
                formEditavel(perfil, setPerfil, aoSalvar)
              ) : (
                <div className="grid-informacoes">
                  <div className="item-info">
                    <span className="rotulo-info">Nome Completo</span>
                    <span className="valor-info">{perfil.nome}</span>
                  </div>
                  <div className="item-info">
                    <span className="rotulo-info">E-mail</span>
                    <span className="valor-info">{perfil.email}</span>
                  </div>
                  <div className="item-info">
                    <span className="rotulo-info">Telefone</span>
                    <span className="valor-info">{perfil.telefone}</span>
                  </div>
                  <div className="item-info">
                    <span className="rotulo-info">Localização</span>
                    <span className="valor-info">{perfil.local}</span>
                  </div>
                </div>
              )}
            </div>
          </section>
        </div>
      </main>
    </div>
  );
}

// Sub-componente para o formulário de edição
function formEditavel(perfil, setPerfil, aoSalvar) {
  return (
    <form onSubmit={aoSalvar} className="formulario-edicao">
      <div className="grupo-campo">
        <label className="rotulo-campo">Nome Completo</label>
        <input 
          type="text" 
          className="campo-texto" 
          value={perfil.nome} 
          onChange={(e) => setPerfil({...perfil, nome: e.target.value})}
        />
      </div>
      <div className="grupo-campo">
        <label className="rotulo-campo">E-mail</label>
        <input 
          type="email" 
          className="campo-texto" 
          value={perfil.email} 
          onChange={(e) => setPerfil({...perfil, email: e.target.value})}
        />
      </div>
      <div className="grupo-campo">
        <label className="rotulo-campo">Telefone</label>
        <input 
          type="text" 
          className="campo-texto" 
          value={perfil.telefone} 
          onChange={(e) => setPerfil({...perfil, telefone: e.target.value})}
        />
      </div>
      <div className="grupo-campo">
        <label className="rotulo-campo">Localização</label>
        <input 
          type="text" 
          className="campo-texto" 
          value={perfil.local} 
          onChange={(e) => setPerfil({...perfil, local: e.target.value})}
        />
      </div>
      <button type="submit" className="botao-salvar-perfil">Guardar Alterações</button>
    </form>
  );
}