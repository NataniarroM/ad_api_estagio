import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import Cabecalho from './components/Cabecalho';
import './CadastraCurso.css';

export default function CadastraCurso() {
  const navigate = useNavigate();
  const token = localStorage.getItem('access_token');

  const [autorizado, setAutorizado] = useState(false);
  const [verificando, setVerificando] = useState(true);
  const [idCurso, setIdCurso] = useState('');
  const [nome, setNome] = useState('');
  const [carregando, setCarregando] = useState(false);
  const [mensagem, setMensagem] = useState({ tipo: '', texto: '' });

  useEffect(() => {
    if (!token) {
      navigate('/login', { replace: true });
      return;
    }

    fetch('http://localhost:8000/auth/perfil', {
      headers: { Authorization: `Bearer ${token}` },
    })
      .then((res) => (res.ok ? res.json() : null))
      .then((dadosPerfil) => {
        const tipo = dadosPerfil?.tipo_usuario;
        if (tipo) localStorage.setItem('tipo_usuario', tipo);

        if (tipo === 'administrador' || tipo === 'adm') {
          setAutorizado(true);
        } else {
          navigate('/', { replace: true });
        }
      })
      .catch(() => navigate('/', { replace: true }))
      .finally(() => setVerificando(false));
  }, [token, navigate]);

  if (verificando || !autorizado) return null;

  const aoSalvar = async (e) => {
    e.preventDefault();
    setCarregando(true);
    setMensagem({ tipo: '', texto: '' });

    try {
      const resposta = await fetch('http://localhost:8000/api/cursos/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({
          id_curso: Number(idCurso),
          nome: nome.trim(),
        }),
      });

      const dados = await resposta.json().catch(() => ({}));

      if (resposta.ok) {
        setMensagem({ tipo: 'sucesso', texto: 'Curso cadastrado com sucesso!' });
        setIdCurso('');
        setNome('');
      } else {
        const detalhe = Array.isArray(dados.detail)
          ? dados.detail.map((d) => d.msg).join(', ')
          : dados.detail;
        setMensagem({ tipo: 'erro', texto: detalhe || 'Erro ao cadastrar curso.' });
      }
    } catch {
      setMensagem({ tipo: 'erro', texto: 'Erro de conexão com o servidor.' });
    } finally {
      setCarregando(false);
    }
  };

  return (
    <div className="pagina-cadastra-curso">
      <Cabecalho />
      <main className="conteudo-cadastra-curso">
        <div className="cartao-cadastra-curso">
          <h2>Cadastrar Curso</h2>

          {mensagem.texto && (
            <div className={`mensagem-alerta ${mensagem.tipo}`}>{mensagem.texto}</div>
          )}

          <form onSubmit={aoSalvar} className="formulario-curso">
            <label>
              ID do Curso
              <input
                type="number"
                placeholder="Ex: 1"
                value={idCurso}
                onChange={(e) => setIdCurso(e.target.value)}
                min={1}
                required
              />
            </label>

            <label>
              Nome do Curso
              <input
                type="text"
                placeholder="Ex: Engenharia de Software"
                value={nome}
                onChange={(e) => setNome(e.target.value)}
                required
              />
            </label>

            <button type="submit" disabled={carregando}>
              {carregando ? 'Salvando...' : 'Cadastrar'}
            </button>
          </form>
        </div>
      </main>
    </div>
  );
}