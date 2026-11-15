import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import Cabecalho from './components/Cabecalho';
import './Perfil.css';

export default function Perfil() {
  const navigate = useNavigate();

  const [perfil, setPerfil] = useState({
    nome: '',
    subtitulo: '',
    email: '',
    telefone: '',
    local: '',
    semestre: '',
    tipo_usuario: '',
  });

  const [carregando, setCarregando] = useState(true);
  const [mensagem, setMensagem] = useState({ tipo: '', texto: '' });

  useEffect(() => {
    const carregarPerfil = async () => {
      const token = localStorage.getItem('access_token');

      if (!token) {
        navigate('/login');
        return;
      }

      try {
        const resposta = await fetch('http://localhost:8000/auth/perfil', {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        });

        if (resposta.status === 401) {
          localStorage.removeItem('access_token');
          localStorage.removeItem('tipo_usuario');
          navigate('/login');
          return;
        }

        if (!resposta.ok) {
          throw new Error('Não foi possível carregar os dados do perfil.');
        }

        const dados = await resposta.json();

        const descricaoCargo =
          dados.tipo_usuario === 'recrutador'
            ? 'Recrutador'
            : dados.tipo_usuario === 'administrador'
            ? 'Administrador'
            : dados.semestre
            ? `Estudante • ${dados.semestre}º Semestre`
            : 'Estudante';

        setPerfil({
          nome: dados.nome || 'Usuário',
          subtitulo: descricaoCargo,
          email: dados.email || '',
          telefone: dados.telefone || 'Não informado',
          local: dados.local || 'Não informado',
          semestre: dados.semestre || '',
          tipo_usuario: dados.tipo_usuario || 'usuario',
        });
      } catch (erro) {
        console.error('Erro ao buscar perfil:', erro);
        setMensagem({ tipo: 'erro', texto: erro.message });
      } finally {
        setCarregando(false);
      }
    };

    carregarPerfil();
  }, [navigate]);

  const gerarIniciais = (nomeCompleto) => {
    if (!nomeCompleto) return 'U';
    const partes = nomeCompleto.trim().split(' ').filter(Boolean);
    if (partes.length === 1) return partes[0].slice(0, 2).toUpperCase();
    return (partes[0][0] + partes[partes.length - 1][0]).toUpperCase();
  };

  if (carregando) {
    return (
      <div className="pagina-perfil">
        <Cabecalho />
        <main className="conteudo-perfil">
          <p className="texto-carregando">A carregar perfil...</p>
        </main>
      </div>
    );
  }

  return (
    <div className="pagina-perfil">
      <Cabecalho />

      <main className="conteudo-perfil">
        <div className="cartao-perfil-topo">
          <div className="avatar-grande">
            <span className="texto-avatar-grande">{gerarIniciais(perfil.nome)}</span>
          </div>
          <div className="info-usuario-topo">
            <h1 className="nome-usuario">{perfil.nome}</h1>
            <p className="subtitulo-usuario">{perfil.subtitulo}</p>
          </div>
        </div>

        {mensagem.texto && (
          <div className={`mensagem-alerta ${mensagem.tipo}`}>
            {mensagem.texto}
          </div>
        )}

        <div className="corpo-perfil">
          <aside className="menu-lateral-perfil">
            <a href="#perfil" className="item-menu-perfil ativo"> Informações Pessoais</a>
            <a href="#curriculo" className="item-menu-perfil"> Currículo</a>
          </aside>

          <section className="detalhes-perfil">
            <div className="bloco-detalhes">
              <h2 className="titulo-bloco">Informações Pessoais</h2>

              <div className="grid-informacoes">
                <div className="item-info">
                  <span className="rotulo-info">Nome Completo</span>
                  <span className="valor-info">{perfil.nome}</span>
                </div>
                <div className="item-info">
                  <span className="rotulo-info">E-mail</span>
                  <span className="valor-info">{perfil.email}</span>
                </div>
                <div className="item-info">
                  <span className="rotulo-info">Telefone</span>
                  <span className="valor-info">{perfil.telefone}</span>
                </div>
                <div className="item-info">
                  <span className="rotulo-info">Localização</span>
                  <span className="valor-info">{perfil.local}</span>
                </div>
              </div>
            </div>
          </section>
        </div>
      </main>
    </div>
  );
}