import React, { useEffect, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';

const API = 'http://localhost:8000';
const situacoes = {
  enviada: 'Enviada', em_analise: 'Em análise', aprovada: 'Aprovada',
  rejeitada: 'Não selecionada', entrevista: 'Entrevista',
};

export default function Candidaturas() {
  const navigate = useNavigate();
  const [candidaturas, setCandidaturas] = useState([]);
  const [carregando, setCarregando] = useState(true);
  const [erro, setErro] = useState('');
  const [tentativa, setTentativa] = useState(0);

  useEffect(() => {
    let ativo = true;
    const carregar = async () => {
      setCarregando(true);
      setErro('');
      try {
        const token = localStorage.getItem('access_token');
        if (!token) { navigate('/login'); return; }
        const resposta = await fetch(`${API}/candidatura/minhas`, {
          headers: { Authorization: `Bearer ${token}` },
        });
        if (!ativo) return;
        if (resposta.status === 401) { navigate('/login'); return; }
        if (!resposta.ok) throw new Error('Não foi possível carregar suas candidaturas.');
        const dados = await resposta.json();
        if (!Array.isArray(dados)) throw new Error('Resposta inválida ao carregar candidaturas.');
        const itens = await Promise.all(dados.map(async (candidatura) => {
          try {
            const res = await fetch(`${API}/api/vagas/${candidatura.id_vaga}`);
            return { ...candidatura, vaga: res.ok ? await res.json() : null };
          } catch {
            return { ...candidatura, vaga: null };
          }
        }));
        if (ativo) setCandidaturas(itens);
      } catch (falha) {
        if (ativo) setErro(falha.message);
      } finally {
        if (ativo) setCarregando(false);
      }
    };
    carregar();
    return () => { ativo = false; };
  }, [navigate, tentativa]);

  return (
    <div className="secao-candidaturas">
      <h2 className="titulo-bloco">Candidaturas</h2>
      {carregando ? <p role="status">Carregando candidaturas...</p> : erro ? (
        <div role="alert">
          <p>{erro}</p>
          <button type="button" className="acao-curriculo" onClick={() => setTentativa(tentativa + 1)}>Tentar novamente</button>
        </div>
      ) : candidaturas.length === 0 ? (
        <div>
          <p>Você ainda não se candidatou a nenhuma vaga.</p>
          <Link className="acao-curriculo" to="/">Encontrar vagas</Link>
        </div>
      ) : (
        <ul className="lista-candidaturas">
          {candidaturas.map((item) => (
            <li key={item.id_candidatura} className="cartao-candidatura">
              <div>
                <h3>{item.vaga?.titulo || `Vaga #${item.id_vaga}`}</h3>
                {item.vaga?.cidade && <p>{item.vaga.cidade}</p>}
                <span className="situacao-candidatura">{situacoes[item.status_candidatura] || item.status_candidatura || 'Enviada'}</span>
              </div>
              {item.vaga ? <Link className="acao-curriculo" to={`/vaga/${item.id_vaga}`}>Ver vaga</Link> : <p>Detalhes da vaga indisponíveis.</p>}
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
