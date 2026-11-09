import React, { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import './detalhes.css';

export default function Detalhes() {
  const { id } = useParams(); // Pega o ID da vaga que veio pela URL
  const navigate = useNavigate();
  const [inscrito, setInscrito] = useState(false);
  const [carregando, setCarregando] = useState(false);

  // Exemplo de dados de uma vaga (num projeto real, isto viria de uma API ou props)
  const vaga = {
    id: id,
    titulo: 'Desenvolvedor Frontend React Junior',
    empresa: 'Tech Solutions Brasil',
    local: 'São Paulo, SP (Híbrido)',
    tipo: 'Estágio',
    bolsa: 'R$ 1.800,00',
    cargaHoraria: '30h semanais',
    descricao: 'Procuramos um estudante motivado para integrar a nossa equipa de desenvolvimento, ajudando a criar interfaces modernas e responsivas utilizando React, CSS e JavaScript.',
    requisitos: [
      'Estar a cursar Ciência da Computação, Engenharia, Análise de Sistemas ou áreas afins.',
      'Conhecimentos básicos em HTML, CSS e JavaScript.',
      'Familiaridade com React é um diferencial.',
      'Vontade de aprender e trabalhar em equipa.'
    ],
    beneficios: [
      'Vale Transporte / Auxílio Home Office',
      'Vale Refeição',
      'Seguro de Vida',
      'Possibilidade de efetivação'
    ]
  };

  const handleInscricao = async () => {
    setCarregando(true);
    // Aqui podes colocar o fetch para a tua API FastAPI (ex: /vagas/{id}/candidatar)
    setTimeout(() => {
      setInscrito(true);
      setCarregando(false);
    }, 1000); // Simulando o tempo de resposta do servidor
  };

  return (
    <div className="pagina-detalhes">
      <div className="container-vaga">
        <button className="botao-voltar" onClick={() => navigate(-1)}>
          &larr; Voltar às vagas
        </button>

        <div className="cabecalho-vaga">
          <div>
            <h1>{vaga.titulo}</h1>
            <h2>{vaga.empresa} &bull; <span className="local-vaga">{vaga.local}</span></h2>
          </div>
          <div className="badges-vaga">
            <span className="badge tipo">{vaga.tipo}</span>
            <span className="badge bolsa">{vaga.bolsa}</span>
          </div>
        </div>

        <hr className="divisor" />

        <div className="corpo-vaga">
          <section className="secao-info">
            <h3>Sobre a oportunidade</h3>
            <p>{vaga.descricao}</p>
          </section>

          <section className="secao-info">
            <h3>Requisitos e Qualificações</h3>
            <ul>
              {vaga.requisitos.map((req, index) => (
                <li key={index}>{req}</li>
              ))}
            </ul>
          </section>

          <section className="secao-info">
            <h3>Benefícios</h3>
            <ul>
              {vaga.beneficios.map((ben, index) => (
                <li key={index}>{ben}</li>
              ))}
            </ul>
          </section>
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
              disabled={carregando}
            >
              {carregando ? 'A inscrever...' : 'Candidatar-me a esta vaga'}
            </button>
          )}
        </div>
      </div>
    </div>
  );
}