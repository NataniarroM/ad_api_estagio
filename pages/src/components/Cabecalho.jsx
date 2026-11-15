import React, { useState, useEffect } from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import './Cabecalho.css';

export default function Cabecalho() {
  const navigate = useNavigate();
  const location = useLocation();

  const [logado, setLogado] = useState(Boolean(localStorage.getItem('access_token')));
  const [tipoUsuario, setTipoUsuario] = useState(localStorage.getItem('tipo_usuario') || '');

  useEffect(() => {
    const token = localStorage.getItem('access_token');
    setLogado(Boolean(token));

    if (!token) {
      setTipoUsuario('');
      return;
    }

    const salvo = localStorage.getItem('tipo_usuario');
    if (salvo) setTipoUsuario(salvo);

    fetch('http://localhost:8000/auth/perfil', {
      headers: { Authorization: `Bearer ${token}` },
    })
      .then((res) => (res.ok ? res.json() : null))
      .then((dadosPerfil) => {
        if (dadosPerfil?.tipo_usuario) {
          setTipoUsuario(dadosPerfil.tipo_usuario);
          localStorage.setItem('tipo_usuario', dadosPerfil.tipo_usuario);
        }
      })
      .catch(() => {});
  }, [location.pathname]);

  const aoSair = () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('tipo_usuario');
    setLogado(false);
    setTipoUsuario('');
    navigate('/login');
  };

  const ehAdmin = tipoUsuario === 'administrador' || tipoUsuario === 'adm';
  const podeCadastrarVaga = tipoUsuario === 'recrutador' || ehAdmin;
  const podeCadastrarCurso = ehAdmin;

  return (
    <header className="cabecalho">
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
