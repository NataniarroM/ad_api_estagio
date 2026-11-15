
import React from 'react';
import { Link } from 'react-router-dom';
import './Cabecalho.css';

export default function Cabecalho() {
  return (
    <header className="cabecalho">

      {/* Logo do EstagUp */}
      <Link to="/" className="area-logo-link">
        <div className="area-logo">

          {/* Simbolo academico */}
          <svg
            className="simbolo-academico"
            viewBox="0 0 64 64"
            width="44"
            height="44"
            aria-hidden="true"
          >
            {/* Capelo */}
            <path
              d="M4 19 L32 7 L60 19 L32 32 Z"
              fill="#291B17"
            />
            <path
              d="M16 27 V36 Q32 49 48 36 V27 L32 34 Z"
              fill="#291B17"
            />

            {/* Borla */}
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

            {/* Seta de crescimento */}
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

          {/* Nome da marca */}
          <span className="nome-marca">
            Estag<span className="destaque-marca">Up</span>
          </span>

        </div>
      </Link>

      {/* Botoes do cabecalho */}
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
