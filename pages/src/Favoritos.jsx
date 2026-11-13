import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import CartaoVaga from '../src/components/CartaoVaga';
import './Favoritos.css'; 

export default function Favoritos() {
  const navigate = useNavigate();
  const [vagasFavoritas, setVagasFavoritas] = useState([]);

  useEffect(() => {
    const salvas = JSON.parse(localStorage.getItem('vagasFavoritas')) || [];
    setVagasFavoritas(salvas);
  }, []);

  const removerFavorito = (id_vaga) => {
    const atualizadas = vagasFavoritas.filter(v => v.id_vaga !== id_vaga);
    setVagasFavoritas(atualizadas);
    localStorage.setItem('vagasFavoritas', JSON.stringify(atualizadas));
  };

  return (
    <div className="pagina-favoritos">
      <button className="botao-voltar-favoritos" onClick={() => navigate('/')}>
        &larr; Voltar às vagas
      </button>

      <h1>Minhas Vagas Favoritas </h1>

      {vagasFavoritas.length === 0 ? (
        <p className="mensagem-vazia">
          Você ainda não favoritou nenhuma vaga.
        </p>
      ) : (
        <div className="lista-favoritos">
          {vagasFavoritas.map((vaga) => (
            <div key={vaga.id_vaga} className="item-favorito-wrapper">
              <CartaoVaga vaga={vaga} />
              <button 
                className="botao-remover-favorito"
                onClick={() => removerFavorito(vaga.id_vaga)}
              >
                Remover dos favoritos
              </button>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}