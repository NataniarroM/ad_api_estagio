import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import Cabecalho from './components/Cabecalho';
import './CadastroVaga.css';

const API = 'http://localhost:8000';

export default function CadastroVaga() {
  const navigate = useNavigate();
  const token = localStorage.getItem('access_token');
  const [autorizado, setAutorizado] = useState(false);
  const [mensagem, setMensagem] = useState({ tipo: '', texto: '' });
  const [carregando, setCarregando] = useState(false);
  const [precisaEmpresa, setPrecisaEmpresa] = useState(false);
  const [salvandoEmpresa, setSalvandoEmpresa] = useState(false);

  const cadastrarEmpresa = async (e) => {
    e.preventDefault();
    const empresa = Object.fromEntries(new FormData(e.currentTarget));
    empresa.nome_fantasia = empresa.nome_fantasia.trim();
    setSalvandoEmpresa(true);
    try {
      const resposta = await fetch(`${API}/empresas/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` },
        body: JSON.stringify(empresa),
      });
      const dados = await resposta.json().catch(() => ({}));
      if (!resposta.ok) {
        const detalhe = Array.isArray(dados.detail)
          ? dados.detail.map((item) => item.msg).join(', ') : dados.detail;
        throw new Error(detalhe || 'Erro ao cadastrar empresa.');
      }
      setPrecisaEmpresa(false);
      setMensagem({ tipo: 'sucesso', texto: 'Empresa cadastrada! Agora clique em Publicar Vaga para concluir.' });
    } catch (erro) {
      setMensagem({ tipo: 'erro', texto: erro.message });
    } finally {
      setSalvandoEmpresa(false);
    }
  };

  useEffect(() => {
    if (!token) {
      navigate('/login', { replace: true });
      return;
    }
    let ativo = true;
    fetch(`${API}/auth/perfil`, { headers: { Authorization: `Bearer ${token}` } })
      .then(async (resposta) => {
        if (!ativo) return;
        if (resposta.status === 401) {
          navigate('/login', { replace: true });
          return;
        }
        if (!resposta.ok) throw new Error('Erro ao verificar seu perfil. Recarregue a página.');
        const perfil = await resposta.json();
        if (!ativo) return;
        if (['recrutador', 'administrador', 'adm'].includes(perfil.tipo_usuario)) {
          setAutorizado(true);
        } else {
          navigate('/', { replace: true });
        }
      })
      .catch((erro) => {
        if (ativo) setMensagem({ tipo: 'erro', texto: erro.message });
      });
    return () => { ativo = false; };
  }, [token, navigate]);

  const publicar = async (e) => {
    e.preventDefault();
    const vaga = Object.fromEntries(new FormData(e.currentTarget));
    vaga.bolsa = vaga.bolsa === '' ? null : Number(vaga.bolsa);
    vaga.carga_horaria = Number(vaga.carga_horaria);
    if (vaga.data_limite < vaga.data_publicacao) {
      setMensagem({ tipo: 'erro', texto: 'A data limite deve ser igual ou posterior à publicação.' });
      return;
    }
    setCarregando(true);
    setMensagem({ tipo: '', texto: '' });
    try {
      const resposta = await fetch(`${API}/api/vagas/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` },
        body: JSON.stringify(vaga),
      });
      const dados = await resposta.json().catch(() => ({}));
      if (!resposta.ok) {
        if (resposta.status === 403 && dados.detail === 'Cadastre os dados da sua empresa antes de publicar vagas.') {
          setPrecisaEmpresa(true);
        }
        const detalhe = Array.isArray(dados.detail)
          ? dados.detail.map((item) => item.msg).join(', ') : dados.detail;
        throw new Error(detalhe || 'Erro ao publicar a vaga.');
      }
      setMensagem({ tipo: 'sucesso', texto: 'Vaga publicada com sucesso!' });
    } catch (erro) {
      setMensagem({ tipo: 'erro', texto: erro.message });
    } finally {
      setCarregando(false);
    }
  };

  return (
    <>
      <Cabecalho />
      <main className="vaga-container">
        <section className="vaga-card">
          <div className="vaga-header"><h2>Publicar Nova Vaga</h2></div>
          {mensagem.texto && <p role="alert" className={`alerta-${mensagem.tipo}`}>{mensagem.texto}</p>}
          {autorizado && (
            <div className="empresa-opcoes">
              <h3>Dados da empresa</h3>
              <p>Se sua conta ainda não tem uma empresa vinculada, cadastre os dados antes de publicar a vaga.</p>
              <button
                type="button"
                className="btn-cancelar"
                aria-expanded={precisaEmpresa}
                aria-controls="cadastro-empresa"
                onClick={() => setPrecisaEmpresa(!precisaEmpresa)}
              >
                {precisaEmpresa ? 'Ocultar dados da empresa' : 'Adicionar dados da empresa'}
              </button>
            </div>
          )}
          {autorizado && precisaEmpresa && (
            <section id="cadastro-empresa" aria-label="Cadastro da empresa">
              <h3>Cadastrar empresa</h3>
              <p>Vincule sua empresa à conta para publicar. Os dados da vaga serão mantidos abaixo.</p>
              <form className="vaga-form" onSubmit={cadastrarEmpresa}>
                <div className="form-grupo">
                  <label htmlFor="empresa-nome">Nome da empresa</label>
                  <input id="empresa-nome" name="nome_fantasia" maxLength={150} pattern=".*\S.*" required />
                </div>
                <button className="btn-publicar" disabled={salvandoEmpresa}>
                  {salvandoEmpresa ? 'Salvando...' : 'Salvar empresa'}
                </button>
              </form>
            </section>
          )}
          {!autorizado ? (!mensagem.texto && <p>Verificando acesso...</p>) : (
            <form className="vaga-form" onSubmit={publicar}>
              <div className="form-grupo">
                <label htmlFor="titulo">Título da vaga</label>
                <input id="titulo" name="titulo" maxLength={150} required />
              </div>
              <div className="form-grupo">
                <label htmlFor="local">Cidade</label>
                <input id="local" name="cidade" maxLength={100} required />
              </div>
              <div className="form-grupo">
                <label htmlFor="modalidade">Modalidade</label>
                <select id="modalidade" name="modalidade" defaultValue="presencial">
                  <option value="presencial">Presencial</option>
                  <option value="hibrida">Híbrido</option>
                  <option value="remota">Remoto</option>
                </select>
              </div>
              <div className="form-linha">
                <div className="form-grupo">
                  <label htmlFor="salario">Bolsa (R$)</label>
                  <input id="salario" name="bolsa" type="number" min="0" step="0.01" />
                </div>
                <div className="form-grupo">
                  <label htmlFor="carga_horaria">Carga horária</label>
                  <input id="carga_horaria" name="carga_horaria" type="number" min="1" defaultValue="30" required />
                </div>
              </div>
              <div className="form-grupo">
                <label htmlFor="descricao">Descrição</label>
                <textarea id="descricao" name="descricao" required />
              </div>
              <div className="form-grupo">
                <label htmlFor="requisitos">Requisitos</label>
                <textarea id="requisitos" name="requisitos" />
              </div>
              <div className="form-linha">
                <div className="form-grupo">
                  <label htmlFor="data_publicacao">Data de publicação</label>
                  <input id="data_publicacao" name="data_publicacao" type="date" defaultValue={new Date().toLocaleDateString('en-CA')} required />
                </div>
                <div className="form-grupo">
                  <label htmlFor="data_limite">Data limite</label>
                  <input id="data_limite" name="data_limite" type="date" required />
                </div>
              </div>
              <div className="vaga-acoes">
                <button type="button" className="btn-cancelar" onClick={() => navigate('/')}>Voltar para vagas</button>
                <button type="submit" className="btn-publicar" disabled={carregando}>{carregando ? 'Publicando...' : 'Publicar Vaga'}</button>
              </div>
            </form>
          )}
        </section>
      </main>
    </>
  );
}
