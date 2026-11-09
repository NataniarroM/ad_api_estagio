import React from 'react';
import { Link } from 'react-router-dom';
import './CartaoVaga.css';
import fav from '../assets/favoritos.png';

export default function CartaoVaga({ vaga }) {
  return (
    <Link to={`/vaga/${vaga.id}`} className="card-vaga-link" style={{ textDecoration: 'none' }}>
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
          <button className="botao-favorito" onClick={(e) => e.preventDefault()}>
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