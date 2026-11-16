
import React, { useState, useEffect, useRef } from 'react';
import { Link, useNavigate, useSearchParams } from 'react-router-dom';
import Candidaturas from './components/Candidaturas';
import Cabecalho from './components/Cabecalho';
import fundoPerfil from './assets/fundo-login-estagup.png';
import './Perfil.css';

// Ícones do perfil
function Icone({ nome, tamanho = 22 }) {
  const desenhos = {
    usuario: (
      <>
        <circle cx="12" cy="7" r="4" />
        <path d="M4 21v-2a8 8 0 0 1 16 0v2" />
      </>
    ),

    curriculo: (
      <>
        <path d="M7 2h7l5 5v15H5V2z" />
        <path d="M14 2v5h5" />
        <path d="M8 12h8M8 16h8" />
      </>
    ),

    candidaturas: (
      <>
        <rect x="5" y="4" width="14" height="18" rx="2" />
        <path d="M9 4V2h6v2M9 10h6M9 14h6" />
      </>
    ),

    favoritos: (
      <path d="m12 2 3.1 6.4 7.1 1-5.1 5 .9 7-6-3.3-6 3.3.9-7-5.1-5 7.1-1z" />
    ),

    notificacoes: (
      <>
        <path d="M18 8a6 6 0 0 0-12 0c0 7-3 7-3 9h18c0-2-3-2-3-9" />
        <path d="M10 21h4" />
      </>
    ),

    email: (
      <>
        <rect x="3" y="5" width="18" height="14" rx="2" />
        <path d="m3 7 9 7 9-7" />
      </>
    ),

    telefone: (
      <path d="M22 16.9v3a2 2 0 0 1-2.2 2A19 19 0 0 1 2.1 4.2 2 2 0 0 1 4.1 2h3a2 2 0 0 1 2 1.7l.5 3a2 2 0 0 1-.6 1.8L7.1 10a16 16 0 0 0 6.9 6.9l1.5-1.9a2 2 0 0 1 1.8-.6l3 .5a2 2 0 0 1 1.7 2Z" />
    ),

    local: (
      <>
        <path d="M20 10c0 5-8 12-8 12S4 15 4 10a8 8 0 1 1 16 0Z" />
        <circle cx="12" cy="10" r="3" />
      </>
    ),

    editar: (
      <>
        <path d="M12 20h9" />
        <path d="M16 4a2 2 0 0 1 3 3L8 18l-4 1 1-4Z" />
      </>
    ),

    upload: (
      <>
        <path d="M12 16V3" />
        <path d="m7 8 5-5 5 5" />
        <path d="M4 16v4a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2v-4" />
      </>
    ),

    baixar: (
      <>
        <path d="M12 3v13" />
        <path d="m7 11 5 5 5-5" />
        <path d="M4 17v4h16v-4" />
      </>
    ),

    lixeira: (
      <>
        <path d="M3 6h18M8 6V4h8v2" />
        <path d="M6 6l1 15h10l1-15" />
        <path d="M10 10v7M14 10v7" />
      </>
    ),

    olho: (
      <>
        <path d="M2 12s3.5-6 10-6 10 6 10 6-3.5 6-10 6-10-6-10-6Z" />
        <circle cx="12" cy="12" r="3" />
      </>
    )
  };

  return (
    <svg
      width={tamanho}
      height={tamanho}
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="1.8"
      strokeLinecap="round"
      strokeLinejoin="round"
      aria-hidden="true"
    >
      {desenhos[nome]}
    </svg>
  );
}

export default function Perfil() {

  const navigate = useNavigate();
  const [carregando, setCarregando] = useState(true);
  const [perfil, setPerfil] = useState({
    nome: '', subtitulo: '', email: '', telefone: '', local: ''
  });

  const [rascunho, setRascunho] = useState(perfil);
  const [editando, setEditando] = useState(false);
  const [parametros] = useSearchParams();
  const [menuAtivo, setMenuAtivo] = useState(
    () => parametros.get('aba') === 'candidaturas' ? 'candidaturas' : 'pessoais'
  );

  const [mensagem, setMensagem] = useState({
    tipo: '',
    texto: ''
  });

  // Currículo
  const [arquivoCv, setArquivoCv] = useState(null);
  const [urlCv, setUrlCv] = useState('');
  const [mostrarCv, setMostrarCv] = useState(false);

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

  const inputCv = useRef(null);

  // Gera uma URL temporária para o arquivo selecionado
  useEffect(() => {
    if (!arquivoCv) {
      setUrlCv('');
      return;
    }

    const url = URL.createObjectURL(arquivoCv);

    setUrlCv(url);

    return () => {
      URL.revokeObjectURL(url);
    };
  }, [arquivoCv]);

  // Edição do perfil
  const iniciarEdicao = () => {
    setRascunho({ ...perfil });
    setEditando(true);
    setMenuAtivo('pessoais');
    setMensagem({ tipo: '', texto: '' });
  };

  const cancelarEdicao = () => {
    setRascunho({ ...perfil });
    setEditando(false);
  };

  const alterarCampo = (e) => {
    const { name, value } = e.target;

    setRascunho((anterior) => ({
      ...anterior,
      [name]: value
    }));
  };

  const aoSalvar = (e) => {
    e.preventDefault();

    setPerfil({ ...rascunho });
    setEditando(false);

    setMensagem({
      tipo: 'sucesso',
      texto: 'Perfil atualizado com sucesso!'
    });
  };

  // Seleção do currículo
  const selecionarCv = (e) => {
    const arquivo = e.target.files?.[0];

    e.target.value = '';

    if (!arquivo) return;

    const formatoValido = /\.(pdf|doc|docx)$/i.test(
      arquivo.name
    );

    if (!formatoValido) {
      setMensagem({
        tipo: 'erro',
        texto: 'Selecione um arquivo PDF, DOC ou DOCX.'
      });
      return;
    }

    if (arquivo.size > 10 * 1024 * 1024) {
      setMensagem({
        tipo: 'erro',
        texto: 'O currículo deve ter no máximo 10 MB.'
      });
      return;
    }

    setArquivoCv(arquivo);
    setMostrarCv(false);

    setMensagem({
      tipo: 'sucesso',
      texto: 'Currículo selecionado com sucesso!'
    });
  };

  // Remover currículo
  const removerCv = () => {
    setArquivoCv(null);
    setMostrarCv(false);
    setMensagem({ tipo: '', texto: '' });
  };

  // Formatação do tamanho do arquivo
  const formatarTamanho = (bytes) => {
    if (bytes < 1024 * 1024) {
      return `${(bytes / 1024).toFixed(1)} KB`;
    }

    return `${(bytes / 1024 / 1024).toFixed(2)} MB`;
  };

  const ehPdf = arquivoCv
    ? /\.pdf$/i.test(arquivoCv.name)
    : false;

  // Iniciais do avatar
  const iniciais = perfil.nome
    .trim()
    .split(/\s+/)
    .slice(0, 2)
    .map((parte) => parte.charAt(0).toUpperCase())
    .join('');

  const menu = [
    {
      id: 'pessoais',
      nome: 'Informações Pessoais',
      icone: 'usuario'
    },
    {
      id: 'curriculo',
      nome: 'Currículo',
      icone: 'curriculo'
    },
    {
      id: 'candidaturas',
      nome: 'Candidaturas',
      icone: 'candidaturas'
    },
    {
      id: 'favoritos',
      nome: 'Vagas Salvas',
      icone: 'favoritos'
    },
    {
      id: 'notificacoes',
      nome: 'Notificações',
      icone: 'notificacoes'
    }
  ];

  const informacoes = [
    {
      rotulo: 'Nome Completo',
      valor: perfil.nome,
      icone: 'usuario'
    },
    {
      rotulo: 'E-mail',
      valor: perfil.email,
      icone: 'email'
    },
    {
      rotulo: 'Telefone',
      valor: perfil.telefone,
      icone: 'telefone'
    },
    {
      rotulo: 'Localização',
      valor: perfil.local,
      icone: 'local'
    }
  ];

  const camposEdicao = [
    {
      nome: 'nome',
      rotulo: 'Nome Completo',
      tipo: 'text'
    },
    {
      nome: 'email',
      rotulo: 'E-mail',
      tipo: 'email'
    },
    {
      nome: 'telefone',
      rotulo: 'Telefone',
      tipo: 'tel'
    },
    {
      nome: 'local',
      rotulo: 'Localização',
      tipo: 'text'
    }
  ];

  const tituloMenu = menu.find(
    (item) => item.id === menuAtivo
  );

  if (carregando) {
    return (
      <div className="pagina-perfil">
        <Cabecalho />
        <main className="conteudo-perfil"><p role="status">Carregando perfil...</p></main>
      </div>
    );
  }

  return (
    <div
      className="pagina-perfil"
      style={{
        backgroundImage: `url(${fundoPerfil})`
      }}
    >
      <Cabecalho />

      <main className="conteudo-perfil">

        {/* CABEÇALHO DO PERFIL */}
        <section className="cartao-perfil-topo">

          <div className="avatar-grande">
            <span className="texto-avatar-grande">
              {iniciais}
            </span>
          </div>

          <div className="info-usuario-topo">
            <h1 className="nome-usuario">
              {perfil.nome}
            </h1>

            <p className="subtitulo-usuario">
              {perfil.subtitulo}
            </p>
          </div>

          <button
            type="button"
            className="botao-editar-perfil"
            onClick={
              editando ? cancelarEdicao : iniciarEdicao
            }
          >
            {!editando && (
              <Icone nome="editar" tamanho={18} />
            )}

            {editando ? 'Cancelar' : 'Editar Perfil'}
          </button>

        </section>

        {/* ALERTAS */}
        {mensagem.texto && (
          <div
            className={`mensagem-alerta ${mensagem.tipo}`}
            role="status"
          >
            {mensagem.texto}
          </div>
        )}

        <div className="corpo-perfil">

          {/* MENU LATERAL */}
          <aside className="menu-lateral-perfil">

            {menu.map((item) => {

              if (item.id === 'favoritos') {
                return (
                  <Link
                    key={item.id}
                    to="/favoritos"
                    className="item-menu-perfil"
                  >
                    <Icone nome={item.icone} />
                    <span>{item.nome}</span>
                  </Link>
                );
              }

              return (
                <button
                  key={item.id}
                  type="button"
                  className={`item-menu-perfil ${
                    menuAtivo === item.id ? 'ativo' : ''
                  }`}
                  onClick={() => {
                    setMenuAtivo(item.id);
                    setEditando(false);
                    setMensagem({ tipo: '', texto: '' });
                  }}
                >
                  <Icone nome={item.icone} />
                  <span>{item.nome}</span>
                </button>
              );
            })}

          </aside>

          {/* PAINEL DIREITO */}
          <section className="detalhes-perfil">

            <div className="bloco-detalhes">

              {/* INFORMAÇÕES PESSOAIS */}
              {menuAtivo === 'pessoais' && (
                <>
                  <div className="cabecalho-bloco-perfil">

                    <span className="icone-titulo-perfil">
                      <Icone nome="usuario" tamanho={25} />
                    </span>

                    <h2 className="titulo-bloco">
                      Informações Pessoais
                    </h2>

                  </div>

                  {editando ? (

                    <form
                      onSubmit={aoSalvar}
                      className="formulario-edicao"
                    >

                      {camposEdicao.map((campo) => (
                        <div
                          className="grupo-campo"
                          key={campo.nome}
                        >
                          <label
                            className="rotulo-campo"
                            htmlFor={`perfil-${campo.nome}`}
                          >
                            {campo.rotulo}
                          </label>

                          <input
                            id={`perfil-${campo.nome}`}
                            type={campo.tipo}
                            name={campo.nome}
                            className="campo-texto"
                            value={rascunho[campo.nome]}
                            onChange={alterarCampo}
                            required
                          />
                        </div>
                      ))}

                      <button
                        type="submit"
                        className="botao-salvar-perfil"
                      >
                        Guardar Alterações
                      </button>

                    </form>

                  ) : (

                    <div className="grid-informacoes">

                      {informacoes.map((info) => (
                        <div
                          className="item-info"
                          key={info.rotulo}
                        >

                          <span className="icone-info">
                            <Icone nome={info.icone} />
                          </span>

                          <div className="texto-info">

                            <span className="rotulo-info">
                              {info.rotulo}
                            </span>

                            <span className="valor-info">
                              {info.valor}
                            </span>

                          </div>
                        </div>
                      ))}

                    </div>
                  )}
                </>
              )}

              {/* SEÇÃO CURRÍCULO */}
              {menuAtivo === 'curriculo' && (

                <div className="secao-curriculo">

                  <div className="cabecalho-bloco-perfil">

                    <span className="icone-titulo-perfil">
                      <Icone nome="curriculo" tamanho={25} />
                    </span>

                    <h2 className="titulo-bloco">
                      Meu Currículo
                    </h2>

                  </div>

                  <p className="descricao-curriculo">
                    Adicione seu currículo para manter seus
                    documentos organizados.
                  </p>

                  {/* INPUT DE ARQUIVO */}
                  <input
                    ref={inputCv}
                    type="file"
                    accept=".pdf,.doc,.docx"
                    className="input-arquivo-curriculo"
                    onChange={selecionarCv}
                    aria-label="Selecionar arquivo de currículo"
                  />

                  {!arquivoCv ? (

                    /* SEM CURRÍCULO */
                    <div className="area-upload-curriculo">

                      <span className="icone-upload-curriculo">
                        <Icone nome="upload" tamanho={30} />
                      </span>

                      <h3>Adicione seu currículo</h3>

                      <p>
                        Escolha um arquivo do seu computador
                        para adicionar ao perfil.
                      </p>

                      <button
                        type="button"
                        className="botao-upload-curriculo"
                        onClick={() => inputCv.current?.click()}
                      >
                        <Icone nome="upload" tamanho={18} />
                        Selecionar currículo
                      </button>

                      <span className="formatos-curriculo">
                        PDF, DOC ou DOCX • Máximo de 10 MB
                      </span>

                    </div>

                  ) : (

                    /* CURRÍCULO SELECIONADO */
                    <div className="curriculo-selecionado">

                      <div className="arquivo-curriculo">

                        <span className="icone-arquivo-curriculo">
                          <Icone nome="curriculo" tamanho={28} />
                        </span>

                        <div className="informacoes-arquivo">
                          <strong>{arquivoCv.name}</strong>
                          <span>
                            {formatarTamanho(arquivoCv.size)}
                          </span>
                        </div>

                      </div>

                      {/* AÇÕES */}
                      <div className="acoes-curriculo">

                        {ehPdf && urlCv && (
                          <button
                            type="button"
                            className="acao-curriculo"
                            onClick={() => setMostrarCv(!mostrarCv)}
                          >
                            <Icone nome="olho" tamanho={17} />

                            {mostrarCv
                              ? 'Ocultar PDF'
                              : 'Visualizar PDF'}
                          </button>
                        )}

                        {urlCv && (
                          <a
                            href={urlCv}
                            download={arquivoCv.name}
                            className="acao-curriculo"
                          >
                            <Icone nome="baixar" tamanho={17} />
                            Baixar
                          </a>
                        )}

                        <button
                          type="button"
                          className="acao-curriculo"
                          onClick={() => inputCv.current?.click()}
                        >
                          <Icone nome="upload" tamanho={17} />
                          Substituir
                        </button>

                        <button
                          type="button"
                          className="acao-curriculo remover"
                          onClick={removerCv}
                        >
                          <Icone nome="lixeira" tamanho={17} />
                          Remover
                        </button>

                      </div>

                      {/* VISUALIZADOR PDF */}
                      {ehPdf && mostrarCv && urlCv && (

                        <div className="previa-curriculo">

                          <h3>
                            Pré-visualização do currículo
                          </h3>

                          <iframe
                            src={urlCv}
                            title="Pré-visualização do currículo em PDF"
                            className="visualizador-curriculo"
                          />

                        </div>
                      )}

                      {!ehPdf && (
                        <p className="aviso-curriculo">
                          Arquivos Word podem ser baixados,
                          mas não são exibidos no visualizador.
                        </p>
                      )}

                    </div>
                  )}

                  <p className="aviso-armazenamento">
                    O arquivo é mantido apenas enquanto esta
                    página estiver aberta. Ele ainda não é
                    enviado ao servidor.
                  </p>

                </div>
              )}

              {/* OUTRAS SEÇÕES */}
              {menuAtivo === 'candidaturas' && <Candidaturas />}
              {menuAtivo !== 'pessoais' &&
                menuAtivo !== 'candidaturas' &&
                menuAtivo !== 'curriculo' && (

                  <div className="conteudo-em-breve">

                    <span className="icone-titulo-perfil">
                      <Icone
                        nome={tituloMenu?.icone}
                        tamanho={26}
                      />
                    </span>

                    <h2 className="titulo-bloco">
                      {tituloMenu?.nome}
                    </h2>

                    <p>
                      Esta área ainda está em desenvolvimento.
                    </p>

                  </div>
                )}

            </div>

          </section>

        </div>
      </main>
    </div>
  );
}
