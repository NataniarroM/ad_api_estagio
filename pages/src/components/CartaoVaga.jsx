import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import './CartaoVaga.css';
import fav from '../assets/favoritos.png';

export default function CartaoVaga({ vaga }) {
  const [favorito, setFavorito] = useState(false);

  // Identificador único da vaga (suporta id_vaga ou id)
  const idVagaAtual = vaga.id_vaga || vaga.id;

  // Verifica se a vaga já está salva nos favoritos ao carregar o card
  useEffect(() => {
    const salvas = JSON.parse(localStorage.getItem('vagasFavoritas')) || [];
    const jaFavoritada = salvas.some(v => (v.id_vaga || v.id) === idVagaAtual);
    setFavorito(jaFavoritada);
  }, [idVagaAtual]);

  // Função para favoritar ou desfavoritar
  const handleFavoritar = (e) => {
    e.preventDefault(); // Impede que o Link abra a página de detalhes
    e.stopPropagation(); // Impede a propagação do clique para os elementos pais

    const salvas = JSON.parse(localStorage.getItem('vagasFavoritas')) || [];
    const index = salvas.findIndex(v => (v.id_vaga || v.id) === idVagaAtual);

    let novasSalvas;
    if (index >= 0) {
      // Se já está salva, remove dos favoritos
      novasSalvas = salvas.filter(v => (v.id_vaga || v.id) !== idVagaAtual);
      setFavorito(false);
    } else {
      // Se não está salva, adiciona a vaga inteira (com o id_vaga) aos favoritos
      novasSalvas = [...salvas, vaga];
      setFavorito(true);
    }

    // Atualiza o localStorage do navegador
    localStorage.setItem('vagasFavoritas', JSON.stringify(novasSalvas));
  };

  return (
    <Link to={`/vaga/${idVagaAtual}`} className="card-vaga-link" style={{ textDecoration: 'none' }}>
      <div className="cartao-vaga">
        <div className="topo-cartao">
          <div className="info-empresa">
            <div
              className="avatar-empresa"
              style={{ backgroundColor: vaga.corIcone || '#A855F7' }}
            >
              <span className="texto-avatar">
                {vaga.empresa ? vaga.empresa[0] : 'E'}
              </span>
            </div>
            <div>
              <h3 className="titulo-vaga">{vaga.titulo}</h3>
              <p className="subtitulo-empresa">
                {vaga.empresa} {vaga.candidatos ? `• ${vaga.candidatos}` : ''}
              </p>
            </div>
          </div>
          
          {/* Botão de Favoritar com estilo dinâmico opcional */}
          <button 
            className={`botao-favorito ${favorito ? 'favorito-ativo' : ''}`} 
            onClick={handleFavoritar}
            title={favorito ? "Remover dos favoritos" : "Salvar nos favoritos"}
          >
            <img src={fav} alt="Favoritar" />
          </button>
        </div>

        <div className="lista-tags">
          {Array.isArray(vaga.tags) && vaga.tags.map((tag, index) => (
            <span key={index} className="item-tag">{tag}</span>
          ))}
        </div>

        <p className="descricao-vaga">{vaga.descricao}</p>

        <div className="rodape-cartao">
          <span className="salario-vaga">{vaga.salario}</span>
          <span className="data-vaga">{vaga.postado}</span>
        </div>
      </div>
    </Link>
  );
}