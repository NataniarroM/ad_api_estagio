
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
  const [vagas, setVagas] = useState([]);
  const [carregando, setCarregando] = useState(true);

  const [filtrosAplicados, setFiltrosAplicados] = useState({
    termo: '',
    local: ''
  });

  useEffect(() => {
    fetch('http://127.0.0.1:8000/api/vagas')
      .then((resposta) => resposta.json())
      .then((dados) => {
        setVagas(dados);
        setCarregando(false);
      })
      .catch((erro) => {
        console.error('Erro ao carregar as vagas:', erro);
        setCarregando(false);
      });
  }, []);

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

      <section className="secao-topo">
        <h1 className="titulo-principal">
          Encontre seu<br />próximo estágio
        </h1>

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
        <button
          className="botao-favorito"
          onClick={irParaFavoritos}
          title="Ver Favoritos"
        >
          <img src={fav} alt="Favoritos" />
        </button>

        <button
          className="botao-perfil"
          onClick={irParaPerfil}
          title="Ver Perfil"
        >
          <img src={perfil} alt="Perfil" />
        </button>
      </div>

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
          <p
            style={{
              textAlign: 'center',
              color: '#666',
              padding: '20px'
            }}
          >
            A carregar vagas...
          </p>
        ) : (
          <div className="grade-vagas">
            {vagasFiltradas.map((item) => (
              <CartaoVaga
                key={item.id_vaga || item.id}
                vaga={item}
              />
            ))}
          </div>
        )}
      </main>
    </div>
  );
}
