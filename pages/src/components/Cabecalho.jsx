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
          <div className="icone-logo">
            <span className="texto-icone">E</span>
          </div>
          <span className="nome-marca">
            Estag<span className="destaque-marca">Up</span>
          </span>
        </div>
      </Link>

      <div className="acoes-menu">
        {!logado ? (
          <>
            <Link to="/cadastro" className="botao-primario">
              Cadastrar-se
            </Link>
            <Link to="/login" className="botao-secundario">
              Entrar
            </Link>
          </>
        ) : (
          <>
            {podeCadastrarVaga && (
              <Link to="/cadastrovaga" className="botao-primario">
                Cadastrar Vaga
              </Link>
            )}

            {podeCadastrarCurso && (
              <Link to="/cadastracurso" className="botao-primario">
                Cadastrar Curso
              </Link>
            )}

            <Link to="/perfil" className="botao-secundario">
              Meu Perfil
            </Link>

            <button type="button" onClick={aoSair} className="botao-secundario">
              Sair
            </button>
          </>
        )}
      </div>
    </header>
  );
}