import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import Cabecalho from './components/Cabecalho';
import './detalhes.css';

export default function Detalhes() {
  const { id } = useParams(); // Pega o ID da vaga que veio pela URL
  const navigate = useNavigate();
  
  const [vaga, setVaga] = useState(null);
  const [carregando, setCarregando] = useState(true);
  const [erro, setErro] = useState(null);
  const [inscrito, setInscrito] = useState(false);
  const [carregandoInscricao, setCarregandoInscricao] = useState(false);

  // Busca os dados da vaga específica no FastAPI ao carregar a página
  useEffect(() => {
    fetch(`http://127.0.0.1:8000/api/vagas/${id}`)
      .then((resposta) => {
        if (!resposta.ok) {
          throw new Error('Não foi possível carregar os detalhes da vaga.');
        }
        return resposta.json();
      })
      .then((dados) => {
        setVaga(dados);
        setCarregando(false);
      })
      .catch((err) => {
        console.error('Erro ao buscar vaga:', err);
        setErro('Erro ao carregar os detalhes da vaga.');
        setCarregando(false);
      });
  }, [id]);

  // Envia a candidatura para a API FastAPI
  const handleInscricao = async () => {
    setCarregandoInscricao(true);
    try {
      const resposta = await fetch(`http://127.0.0.1:8000/api/vagas/${id}/candidatar`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (resposta.ok) {
        setInscrito(true);
      } else {
        alert('Erro ao realizar candidatura. Tente novamente.');
      }
    } catch (err) {
      console.error('Erro de conexão:', err);
      alert('Erro de conexão com o servidor.');
    } finally {
      setCarregandoInscricao(false);
    }
  };

  if (carregando) {
    return (
      <div className="pagina-detalhes">
        <Cabecalho />
        <p style={{ textAlign: 'center', marginTop: '50px', color: '#666' }}>
          A carregar detalhes da vaga...
        </p>
      </div>
    );
  }

  if (erro || !vaga) {
    return (
      <div className="pagina-detalhes">
        <Cabecalho />
        <div className="container-vaga" style={{ textAlign: 'center', marginTop: '50px' }}>
          <p style={{ color: '#ef4444', marginBottom: '20px' }}>{erro || 'Vaga não encontrada.'}</p>
          <button className="botao-voltar" onClick={() => navigate('/')}>
            &larr; Voltar às vagas
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="pagina-detalhes">
      <Cabecalho />

      <div className="container-vaga">
        <button className="botao-voltar" onClick={() => navigate(-1)}>
          &larr; Voltar às vagas
        </button>

        <div className="cabecalho-vaga">
          <div>
            <h1>{vaga.titulo}</h1>
            <h2>{vaga.empresa} &bull; <span className="local-vaga">{vaga.local || 'Localização não informada'}</span></h2>
          </div>
          <div className="badges-vaga">
            <span className="badge tipo">{vaga.tipo || 'Estágio'}</span>
            <span className="badge bolsa">{vaga.salario || vaga.bolsa || 'A combinar'}</span>
          </div>
        </div>

        <hr className="divisor" />

        <div className="corpo-vaga">
          <section className="secao-info">
            <h3>Sobre a oportunidade</h3>
            <p>{vaga.descricao}</p>
          </section>

          {vaga.requisitos && (
            <section className="secao-info">
              <h3>Requisitos e Qualificações</h3>
              <ul>
                {Array.isArray(vaga.requisitos) ? (
                  vaga.requisitos.map((req, index) => (
                    <li key={index}>{req}</li>
                  ))
                ) : (
                  <li>{vaga.requisitos}</li>
                )}
              </ul>
            </section>
          )}

          {vaga.beneficios && (
            <section className="secao-info">
              <h3>Benefícios</h3>
              <ul>
                {Array.isArray(vaga.beneficios) ? (
                  vaga.beneficios.map((ben, index) => (
                    <li key={index}>{ben}</li>
                  ))
                ) : (
                  <li>{vaga.beneficios}</li>
                )}
              </ul>
            </section>
          )}
        </div>

        <div className="rodape-candidatura">
          {inscrito ? (
            <div className="mensagem-sucesso-inscricao">
              ✅ Candidatura realizada com sucesso! A empresa entrará em contacto em breve.
            </div>
          ) : (
            <button 
              className="botao-inscrever" 
              onClick={handleInscricao}
              disabled={carregandoInscricao}
            >
              {carregandoInscricao ? 'A inscrever...' : 'Candidatar-me a esta vaga'}
            </button>
          )}
        </div>
      </div>
    </div>
  );
}