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

        <div className="barra-pesquisa">
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
          <button className="botao-buscar">Buscar</button>
        </div>
      </section>
      <div className='bar'>
      <button className="botao-favorito" onClick={irParaFavoritos} title="Ver Favoritos">
        <img src={fav} alt="Favoritos" />
      </button>
      <button className="botao-perfil" onClick={irParaPerfil} title="Ver Perfil">
        <img src={perfil} alt="Perfil" />
      </button>
      </div>
      {/* Lista de Vagas */}
      <main className="secao-conteudo">
        <div className="cabecalho-secao">
          <h2 className="titulo-secao">
            Vagas encontradas <span className="badge-contador">{vagas.length} vagas</span>
          </h2>
        </div>

        {carregando ? (
          <p style={{ textAlign: 'center', color: '#666', padding: '20px' }}>
            A carregar vagas do banco de dados...
          </p>
        ) : (
          <div className="grade-vagas">
            {/* 3. A key única foi adicionada aqui para corrigir o aviso do console */}
            {vagas.map((item) => (
              <CartaoVaga key={item.id_vaga || item.id} vaga={item} />
            ))}
          </div>
        )}
      </main>
    </div>
  );
}