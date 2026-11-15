
import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import Cabecalho from './components/Cabecalho';
import CartaoVaga from './components/CartaoVaga';
import './App.css';

import lupa from './assets/lupa.png';
import pin from './assets/pin.png';
import fav from './assets/favoritos.png';
import perfil from './assets/perfil_icon.png';

export default function App() {
  const navigate = useNavigate();
  const [termoBusca, setTermoBusca] = useState('');
  const [localBusca, setLocalBusca] = useState('');
  const [filtroTermo, setFiltroTermo] = useState('');
  const [filtroLocal, setFiltroLocal] = useState('');
  const [vagas, setVagas] = useState([]);
  const [carregando, setCarregando] = useState(true);
  const [tipoUsuario, setTipoUsuario] = useState(
    () => localStorage.getItem('tipo_usuario') || ''
  );

  const API_URL = 'http://localhost:8000';

  useEffect(() => {
    fetch(`${API_URL}/api/vagas/`)
      .then((resposta) => {
        if (!resposta.ok) {
          throw new Error(`Erro ${resposta.status} ao buscar vagas`);
        }
        return resposta.json();
      })
      .then((dados) => {
        setVagas(Array.isArray(dados) ? dados : []);
        setCarregando(false);
      })
      .catch((erro) => {
        console.error('Erro ao carregar as vagas:', erro);
        setVagas([]);
        setCarregando(false);
      });
  }, []);

  // Busca o tipo_usuario em /auth/perfil igual ao Login.jsx
  useEffect(() => {
    const token = localStorage.getItem('access_token');
    if (!token) {
      setTipoUsuario('');
      return;
    }

    fetch(`${API_URL}/auth/perfil`, {
      headers: { Authorization: `Bearer ${token}` },
    })
      .then((res) => (res.ok ? res.json() : null))
      .then((dadosPerfil) => {
        if (dadosPerfil?.tipo_usuario) {
          setTipoUsuario(dadosPerfil.tipo_usuario);
          localStorage.setItem('tipo_usuario', dadosPerfil.tipo_usuario);
        }
      })
      .catch((erro) => console.error('Erro ao verificar perfil:', erro));
  }, []);

  const aplicarBusca = (e) => {
    e.preventDefault();
    setFiltroTermo(termoBusca.trim().toLowerCase());
    setFiltroLocal(localBusca.trim().toLowerCase());
  };

  const vagasFiltradas = vagas.filter((vaga) => {
    const nomeEmpresa =
      typeof vaga.empresa === 'object' && vaga.empresa !== null
        ? vaga.empresa.nome || ''
        : vaga.empresa || '';

    const textoVaga = `${vaga.titulo || ''} ${nomeEmpresa} ${vaga.descricao || ''}`.toLowerCase();
    const localVaga = `${vaga.local || ''} ${vaga.cidade || ''} ${vaga.estado || ''}`.toLowerCase();

    const bateTermo = !filtroTermo || textoVaga.includes(filtroTermo);
    const bateLocal = !filtroLocal || localVaga.includes(filtroLocal);

    return bateTermo && bateLocal;
  });

  const ehAdmin = tipoUsuario === 'administrador' || tipoUsuario === 'adm';
  const ehRecrutador = tipoUsuario === 'recrutador';
  const podeCadastrarVaga = ehRecrutador || ehAdmin;
  const podeCadastrarCurso = ehAdmin;

  const irParaFavoritos = (e) => {
    e.preventDefault();
    navigate('/favoritos');
  };

  const irParaPerfil = (e) => {
    e.preventDefault();
    navigate('/perfil');
  };

  return (
    <div className="pagina-principal">
      <Cabecalho />

      <section className="secao-topo">
        <h1 className="titulo-principal">
<<<<<<< Updated upstream
          Encontre seu<br />próximo estágio
        </h1>
=======
          Encontre seu
          <span className="titulo-destaque">
            próximo estágio
          </span>
        </h1>

>>>>>>> Stashed changes
        <p className="subtitulo-principal">
          Conectando estudantes a grandes oportunidades.
        </p>

        <form
          className="barra-pesquisa"
          onSubmit={aplicarBusca}
        >
          <div className="grupo-input">
            <img src={lupa} alt="Buscar" />

            <input
              type="text"
              className="campo-texto"
              placeholder="Cargo, empresa ou palavra-chave"
              value={termoBusca}
              onChange={(e) => setTermoBusca(e.target.value)}
            />
          </div>

          <div className="separador" />

          <div className="grupo-input">
            <img src={pin} alt="Local" />

            <input
              type="text"
              className="campo-texto"
              placeholder="Cidade ou estado"
              value={localBusca}
              onChange={(e) => setLocalBusca(e.target.value)}
            />
          </div>

          <button type="submit" className="botao-buscar">
            Buscar
          </button>
        </form>
      </section>

      <div className="bar">
        <button className="botao-favorito" onClick={irParaFavoritos} title="Ver Favoritos">
          <img src={fav} alt="Favoritos" />
        </button>

        <button className="botao-perfil" onClick={irParaPerfil} title="Ver Perfil">
          <img src={perfil} alt="Perfil" />
        </button>

        {podeCadastrarVaga && (
          <button
            type="button"
            className="botao-gestao"
            onClick={() => navigate('/cadastrovaga')}
          >
            + Cadastrar Vaga
          </button>
        )}

        {podeCadastrarCurso && (
          <button
            type="button"
            className="botao-gestao"
            onClick={() => navigate('/cadastracurso')}
          >
            + Cadastrar Curso
          </button>
        )}
      </div>
      {/* Lista de Vagas */}
      <main className="secao-conteudo">
        <div className="cabecalho-secao">
          <h2 className="titulo-secao">
            Vagas encontradas{' '}
            <span className="badge-contador">
              {vagasFiltradas.length} vagas
            </span>
          </h2>
        </div>

        {carregando ? (
          <p className="texto-carregando">
            A carregar vagas do banco de dados...
          </p>
        ) : (
          <div className="grade-vagas">
<<<<<<< Updated upstream
            {vagas.map((item) => (
=======
            {vagasFiltradas.map((item) => (
>>>>>>> Stashed changes
              <CartaoVaga key={item.id_vaga || item.id} vaga={item} />
            ))}
          </div>
        )}
      </main>
    </div>
  );
}
