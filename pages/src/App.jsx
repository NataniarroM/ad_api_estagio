import React, { useState } from 'react';
import './App.css';

const VAGAS_DADOS = [
  {
    id: '1',
    titulo: 'Estágio em Desenvolvimento Frontend',
    empresa: 'Acme Tech',
    candidatos: '12 candidatos',
    tags: ['Remoto', 'Tecnologia', 'Estágio'],
    descricao:
      'A Acme Tech é uma empresa de tecnologia focada em soluções digitais inovadoras. Buscamos um estagiário...',
    salario: 'R$ 1.200 - R$ 1.600',
    postado: 'Postada há 2 dias',
    corIcone: '#A855F7',
  },
  {
    id: '2',
    titulo: 'Estágio em Produto',
    empresa: 'Digitalk',
    candidatos: '24 candidatos',
    tags: ['Híbrido', 'Produto', 'Estágio'],
    descricao:
      'A Digitalk está em busca de um estagiário para atuar no time de Produto, contribuindo com pesquisas...',
    salario: 'R$ 1.000 - R$ 1.400',
    postado: 'Postada há 1 dia',
    corIcone: '#EF4444',
  },
  {
    id: '3',
    titulo: 'Estágio em Marketing',
    empresa: 'Next Media',
    candidatos: '18 candidatos',
    tags: ['Presencial', 'Marketing', 'Estágio'],
    descricao:
      'Venha fazer parte do nosso time de marketing e ajudar a construir grandes campanhas.',
    salario: 'R$ 800 - R$ 1.200',
    postado: 'Postada há 3 dias',
    corIcone: '#10B981',
  },
  {
    id: '4',
    titulo: 'Estágio em Design de Produto',
    empresa: 'Pixel Labs',
    candidatos: '30 candidatos',
    tags: ['Remoto', 'Design', 'Estágio'],
    descricao:
      'Buscamos um estagiário apaixonado por design, para atuar na criação de interfaces e experiências...',
    salario: 'R$ 1.200 - R$ 1.800',
    postado: 'Postada há 4 dias',
    corIcone: '#6366F1',
  },
];

export default function App() {
  const [cargo, setCargo] = useState('');
  const [local, setLocal] = useState('');

  return (
    <div className="container">
      
      {/* Cabeçalho / Navbar */}
      <header className="navbar">
        <div className="brand-container">
          <div className="brand-logo">
            <span className="brand-logo-text">E</span>
          </div>
          <span className="brand-name">
            Estag<span className="brand-name-highlight">Up</span>
          </span>
        </div>

        <div className="nav-links">
          <a href="#inicio" className="nav-link">Início</a>
          <a href="#vagas" className="nav-link">Vagas</a>
          <a href="#empresas" className="nav-link">Empresas</a>
          <a href="#conteudos" className="nav-link">Conteúdos</a>
        </div>

        <div className="nav-actions">
          <button className="primary-button">Cadastrar-se</button>
          <button className="secondary-button">Entrar</button>
        </div>
      </header>

      {/* Hero Section */}
      <section className="hero-section">
        <h1 className="hero-title">
          Encontre seu<br />próximo estágio
        </h1>
        <p className="hero-subtitle">
          Conectando estudantes a grandes oportunidades.[cite: 1]
        </p>

        {/* Caixa de Pesquisa */}
        <div className="search-container">
          <div className="input-wrapper">
            <span className="input-icon">🔍</span>
            <input
              type="text"
              className="text-input"
              placeholder="Cargo, empresa ou palavra-chave"
              value={cargo}
              onChange={(e) => setCargo(e.target.value)}
            />
          </div>
          <div className="separator" />
          <div className="input-wrapper">
            <span className="input-icon">📍</span>
            <input
              type="text"
              className="text-input"
              placeholder="Cidade ou estado"
              value={local}
              onChange={(e) => setLocal(e.target.value)}
            />
          </div>
          <button className="search-button">Buscar</button>
        </div>
      </section>

      {/* Secção de Vagas */}
      <main className="content-section">
        <div className="section-header">
          <h2 className="section-title">
            Vagas encontradas{' '}
            <span className="counter-badge">124 vagas</span>
          </h2>
        </div>

        <div className="jobs-grid">
          {VAGAS_DADOS.map((item) => (
            <div key={item.id} className="job-card">
              <div className="job-card-header">
                <div className="job-info-container">
                  <div
                    className="company-avatar"
                    style={{ backgroundColor: item.corIcone }}
                  >
                    <span className="company-avatar-text">{item.empresa[0]}</span>
                  </div>
                  <div>
                    <h3 className="job-title">{item.titulo}</h3>
                    <p className="job-company">
                      {item.empresa} • {item.candidatos}
                    </p>
                  </div>
                </div>
                <button className="bookmark-button">
                  <span className="bookmark-icon">🔖</span>
                </button>
              </div>

              <div className="tag-list">
                {item.tags.map((tag, index) => (
                  <span key={index} className="tag-item">
                    {tag}
                  </span>
                ))}
              </div>

              <p className="job-description">{item.descricao}</p>

              <div className="job-card-footer">
                <span className="job-salary">{item.salario}</span>
                <span className="job-date">{item.postado}</span>
              </div>
            </div>
          ))}
        </div>
      </main>
    </div>
  );
}