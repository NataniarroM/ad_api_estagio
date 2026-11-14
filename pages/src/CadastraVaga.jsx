import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import './CadastroVaga.css';

export default function CadastroVaga() {
  const navigate = useNavigate();

  const [titulo, setTitulo] = useState('');
  const [descricao, setDescricao] = useState('');
  const [local, setLocal] = useState('');
  const [modalidade, setModalidade] = useState('Presencial');
  const [salario, setSalario] = useState('');
  const [erro, setErro] = useState('');
  const [sucesso, setSucesso] = useState('');
  const [carregando, setCarregando] = useState(false);

  // Proteção de rota no Front-end: verifica se é recrutador ao abrir a página
  useEffect(() => {
    const token = localStorage.getItem('access_token');
    const tipoUsuario = localStorage.getItem('tipo_usuario'); // Salvo no momento do login

    if (!token) {
      navigate('/login');
      return;
    }

    if (tipoUsuario !== 'recrutador' && tipoUsuario !== 'empresa') {
      navigate('/'); // Redireciona estudantes/outros perfis para a home
    }
  }, [navigate]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setErro('');
    setSucesso('');
    setCarregando(true);

    const token = localStorage.getItem('access_token');

    try {
      const resposta = await fetch('http://127.0.0.1:8000/api/vagas/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          titulo,
          descricao,
          local: `${local} (${modalidade})`,
          salario: salario ? parseFloat(salario) : null
        })
      });

      const dados = await resposta.json();

      if (!resposta.ok) {
        if (resposta.status === 403) {
          throw new Error('Acesso negado: Apenas recrutadores podem publicar vagas.');
        }
        throw new Error(dados.detail || 'Erro ao publicar a vaga. Verifique os campos.');
      }

      setSucesso('Vaga publicada com sucesso!');
      setTitulo('');
      setDescricao('');
      setLocal('');
      setSalario('');

      setTimeout(() => {
        navigate('/');
      }, 2000);

    } catch (err) {
      setErro(err.message);
    } finally {
      setCarregando(false);
    }
  };

  return (
    <div className="vaga-container">
      <div className="vaga-card">
        <div className="vaga-header">
          <h2>Publicar Nova Vaga</h2>
          <p>Preencha os detalhes da oportunidade de estágio para atrair candidatos</p>
        </div>

        {erro && <div className="alerta-erro">{erro}</div>}
        {sucesso && <div className="alerta-sucesso">{sucesso}</div>}

        <form onSubmit={handleSubmit} className="vaga-form">
          <div className="form-grupo">
            <label htmlFor="titulo">Título da Vaga *</label>
            <input
              id="titulo"
              type="text"
              placeholder="Ex: Estágio em Desenvolvimento Front-end"
              value={titulo}
              onChange={(e) => setTitulo(e.target.value)}
              required
            />
          </div>

          <div className="form-linha">
            <div className="form-grupo">
              <label htmlFor="local">Cidade / Estado *</label>
              <input
                id="local"
                type="text"
                placeholder="Ex: São Paulo, SP"
                value={local}
                onChange={(e) => setLocal(e.target.value)}
                required
              />
            </div>

            <div className="form-grupo">
              <label htmlFor="modalidade">Modalidade</label>
              <select
                id="modalidade"
                value={modalidade}
                onChange={(e) => setModalidade(e.target.value)}
              >
                <option value="Presencial">Presencial</option>
                <option value="Híbrido">Híbrido</option>
                <option value="Remoto">Remoto</option>
              </select>
            </div>
          </div>

          <div className="form-grupo">
            <label htmlFor="salario">Bolsa-auxílio (R$) — Opcional</label>
            <input
              id="salario"
              type="number"
              step="0.01"
              min="0"
              placeholder="Ex: 1500.00"
              value={salario}
              onChange={(e) => setSalario(e.target.value)}
            />
          </div>

          <div className="form-grupo">
            <label htmlFor="descricao">Descrição e Requisitos *</label>
            <textarea
              id="descricao"
              rows="5"
              placeholder="Descreva as atividades, requisitos técnicos e benefícios..."
              value={descricao}
              onChange={(e) => setDescricao(e.target.value)}
              required
            />
          </div>

          <div className="vaga-acoes">
            <button
              type="button"
              className="btn-cancelar"
              onClick={() => navigate('/')}
            >
              Cancelar
            </button>
            <button
              type="submit"
              className="btn-publicar"
              disabled={carregando}
            >
              {carregando ? 'Publicando...' : 'Publicar Vaga'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}