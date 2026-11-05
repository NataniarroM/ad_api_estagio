import React from 'react';
import './CartaoVaga.css';

export default function CartaoVaga({ vaga }) {
  return (
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
        <button className="botao-favorito">
          <span className="icone-favorito">🔖</span>
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
  );
}