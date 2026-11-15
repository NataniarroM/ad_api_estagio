import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom'; // 1. Importar o useNavigate
import Cabecalho from './components/Cabecalho';
import CartaoVaga from './components/CartaoVaga';
import './App.css';
import lupa from './assets/lupa.png';
import pin from './assets/pin.png';
import fav from './assets/favoritos.png';
import perfil from './assets/perfil_icon.png';

export default function App() {
  const navigate = useNavigate(); // 2. Inicializar o navigate dentro do componente
  const [termoBusca, setTermoBusca] = useState('');
  const [localBusca, setLocalBusca] = useState('');
  const [vagas, setVagas] = useState([]);
  const [carregando, setCarregando] = useState(true);
  const [tipoUsuario, setTipoUsuario] = useState(
    () => localStorage.getItem('tipo_usuario') || ''
  );

  const [filtrosAplicados, setFiltrosAplicados] = useState({
    termo: '',
    local: ''
  });

  const API_URL = 'http://localhost:8000';

  useEffect(() => {
    fetch(`${API_URL}/api/vagas/`)
      .then((resposta) => resposta.json())
      .then((dados) => {
        setVagas(Array.isArray(dados) ? dados : []);
        setCarregando(false);
      })
      .catch((erro) => {
        console.error('Erro ao carregar as vagas:', erro);
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

  const ehAdmin = tipoUsuario === 'administrador' || tipoUsuario === 'adm';
  const ehRecrutador = tipoUsuario === 'recrutador';
  const podeCadastrarVaga = ehRecrutador || ehAdmin;
  const podeCadastrarCurso = ehAdmin;

  const normalizar = (valor) =>
    String(valor ?? '')
      .normalize('NFD')
      .replace(/[\u0300-\u036f]/g, '')
      .toLowerCase()
      .trim();

  const aplicarBusca = (e) => {
    e.preventDefault();

    setFiltrosAplicados({
      termo: termoBusca,
      local: localBusca
    });
  };

  const vagasFiltradas = vagas.filter((vaga) => {
    const texto = [
      vaga.titulo,
      vaga.empresa,
      vaga.descricao,
      ...(Array.isArray(vaga.tags) ? vaga.tags : [])
    ].map(normalizar).join(' ');

    const local = normalizar(
      vaga.local ?? vaga.cidade ?? vaga.estado ?? ''
    );

    return (
      texto.includes(normalizar(filtrosAplicados.termo)) &&
      local.includes(normalizar(filtrosAplicados.local))
    );
  });

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

      {/* Banner / Pesquisa */}
      <section className="secao-topo">
        <h1 className="titulo-principal">
          Encontre seu<br />próximo estágio
        </h1>
        <p className="subtitulo-principal">
          Conectando estudantes a grandes oportunidades.
        </p>

        <form className="barra-pesquisa" onSubmit={aplicarBusca}>
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
          <button type="submit" className="botao-buscar">Buscar</button>
        </form>
      </section>
      <div className='bar'>
      <button className="botao-favorito" onClick={irParaFavoritos} title="Ver Favoritos">
        <img src={fav} alt="Favoritos" />
      </button>
      <button className="botao-perfil" onClick={irParaPerfil} title="Ver Perfil">
        <img src={perfil} alt="Perfil" />
      </button>
      {podeCadastrarVaga && (
        <button type="button" className="botao-gestao" onClick={() => navigate('/cadastrovaga')}>
          + Cadastrar Vaga
        </button>
      )}
      {podeCadastrarCurso && (
        <button type="button" className="botao-gestao" onClick={() => navigate('/cadastracurso')}>
          + Cadastrar Curso
        </button>
      )}
      </div>
      {/* Lista de Vagas */}
      <main className="secao-conteudo">
        <div className="cabecalho-secao">
          <h2 className="titulo-secao">
            Vagas encontradas <span className="badge-contador">{vagasFiltradas.length} vagas</span>
          </h2>
        </div>

        {carregando ? (
          <p style={{ textAlign: 'center', color: '#666', padding: '20px' }}>
            A carregar vagas do banco de dados...
          </p>
        ) : vagasFiltradas.length === 0 ? (
          <p className="texto-sem-resultados">Nenhuma vaga encontrada.</p>
        ) : (
          <div className="grade-vagas">
            {/* 3. A key única foi adicionada aqui para corrigir o aviso do console */}
            {vagasFiltradas.map((item) => (
              <CartaoVaga key={item.id_vaga || item.id} vaga={item} />
            ))}
          </div>
        )}
      </main>
    </div>
  );
}
