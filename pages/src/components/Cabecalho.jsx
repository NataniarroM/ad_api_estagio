import React from 'react';
import { Link } from 'react-router-dom';
import './Cabecalho.css';

export default function Cabecalho() {
  return (
    <header className="cabecalho">
      {/* Envolvemos a área-logo inteira com o Link para a rota "/" */}
      <Link to="/" className="area-logo-link">
        <div className="area-logo">
          <div className="icone-logo">
            <span className="texto-icone">E</span>
          </div>
          <span className="nome-marca">
            Estag<span className="destaque-marca">Up</span>
          </span>
        </div>
      </Link>


      <div className="acoes-menu">
        <Link to="/cadastro" className="botao-primario">
          Cadastrar-se
        </Link>
        <Link to="/login" className="botao-secundario">
          Entrar
        </Link>
      </div>
    </header>
  );
}