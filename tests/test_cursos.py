# Testes do CRUD de cursos (app/routers/cursos_router.py).
# Como funciona:
#   - cada teste usa um banco SQLite NOVO, na memória (some quando o teste acaba),
#     então não precisa do Postgres nem do Firebase;
#   - quem está "logado" é escolhido pelo teste (administrador ou usuário comum),
#     trocando o porteiro get_usuario_db por uma versão de mentira.
# Cada teste segue 3 passos: preparar -> executar -> conferir (assert).
# Usei o Claude pra fazer alguns defs, a maioria foi só CTRLC CTRLV

from types import SimpleNamespace

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app
from app.models import Curso
from app.seguranca import get_usuario_db

CURSO_OK = {"nome": "Ciência da Computação", "nivel": "bacharelado"}


@pytest.fixture()
def api():
    """Prepara um banco novo na memória para cada teste e entrega o cliente de teste."""
    # StaticPool faz todas as conexões usarem o MESMO banco em memória.
    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    Base.metadata.create_all(engine)   # cria as tabelas a partir do models.py
    Sessao = sessionmaker(bind=engine)

    def db_de_teste():
        sessao = Sessao()
        try:
            yield sessao
        finally:
            sessao.close()

    # Troca o banco real (Postgres) pelo de memória, só durante o teste.
    app.dependency_overrides[get_db] = db_de_teste
    yield TestClient(app)
    app.dependency_overrides.clear()   # desfaz todas as trocas ao final do teste


def logar_como(tipo):
    """Finge que quem está logado é um usuário do tipo informado ("administrador" ou "usuario")."""
    app.dependency_overrides[get_usuario_db] = lambda: SimpleNamespace(
        id_usuario=1, tipo_usuario=tipo
    )


def criar_curso_como_admin(api, **dados):
    """Atalho: cria um curso como administrador e devolve a resposta."""
    logar_como("administrador")
    return api.post("/api/cursos", json={**CURSO_OK, **dados})


# SIXX SEVENNN LISTAR / BUSCAR (público) 

def test_listar_cursos_sem_login_vazio(api):
    resposta = api.get("/api/cursos")

    assert resposta.status_code == 200      # qualquer um pode listar, sem token
    assert resposta.json() == []            # banco novo = lista vazia


def test_listar_mostra_so_ativos_por_padrao(api):
    criar_curso_como_admin(api, nome="Curso Ativo")
    criar_curso_como_admin(api, nome="Curso Inativo", ativo=False)

    so_ativos = api.get("/api/cursos").json()
    todos = api.get("/api/cursos?apenas_ativos=false").json()

    assert [c["nome"] for c in so_ativos] == ["Curso Ativo"]
    assert len(todos) == 2


def test_buscar_curso_por_id(api):
    criado = criar_curso_como_admin(api).json()

    resposta = api.get(f"/api/cursos/{criado['id_curso']}")

    assert resposta.status_code == 200
    assert resposta.json()["nome"] == "Ciência da Computação"


def test_buscar_curso_inexistente(api):
    resposta = api.get("/api/cursos/999")

    assert resposta.status_code == 404


# CRIAR

def test_admin_cria_curso(api):
    resposta = criar_curso_como_admin(api)

    assert resposta.status_code == 201
    corpo = resposta.json()
    assert corpo["id_curso"] is not None    # o banco gerou o id
    assert corpo["ativo"] is True           # sem informar, nasce ativo


def test_usuario_comum_nao_cria_curso(api):
    logar_como("usuario")

    resposta = api.post("/api/cursos", json=CURSO_OK)

    assert resposta.status_code == 403      # 403 = logado, mas sem permissão


def test_criar_curso_sem_login(api):
    # Sem logar_como(): nenhum token foi enviado.
    resposta = api.post("/api/cursos", json=CURSO_OK)

    # Dependendo da versão do FastAPI a recusa vem como 401 ou 403. Aceitamos os dois.
    assert resposta.status_code in (401, 403)


@pytest.mark.parametrize("dados_invalidos", [
    {"nome": "Curso", "nivel": "mestrado"},     # nível que o banco não aceita
    {"nome": "A", "nivel": "bacharelado"},      # nome curto demais (mínimo 2 letras)
    {"nivel": "bacharelado"},                   # faltou o nome
])
def test_criar_curso_com_dados_invalidos(api, dados_invalidos):
    logar_como("administrador")

    resposta = api.post("/api/cursos", json=dados_invalidos)

    assert resposta.status_code == 422          # 422 = dados fora das regras


# ATUALIZAR

def test_admin_atualiza_curso(api):
    id_curso = criar_curso_como_admin(api).json()["id_curso"]

    resposta = api.put(f"/api/cursos/{id_curso}", json={"ativo": False})

    assert resposta.status_code == 200
    assert resposta.json()["ativo"] is False
    assert resposta.json()["nome"] == "Ciência da Computação"   # o que não foi enviado não muda


def test_atualizar_curso_inexistente(api):
    logar_como("administrador")

    resposta = api.put("/api/cursos/999", json={"nome": "Novo nome"})

    assert resposta.status_code == 404


def test_usuario_comum_nao_atualiza_curso(api):
    id_curso = criar_curso_como_admin(api).json()["id_curso"]
    logar_como("usuario")

    resposta = api.put(f"/api/cursos/{id_curso}", json={"nome": "Hackeado"})

    assert resposta.status_code == 403


# APAGAR

def test_admin_apaga_curso(api):
    id_curso = criar_curso_como_admin(api).json()["id_curso"]

    resposta = api.delete(f"/api/cursos/{id_curso}")

    assert resposta.status_code == 204
    assert api.get(f"/api/cursos/{id_curso}").status_code == 404   # sumiu de verdade


def test_apagar_curso_inexistente(api):
    logar_como("administrador")

    resposta = api.delete("/api/cursos/999")

    assert resposta.status_code == 404


def test_usuario_comum_nao_apaga_curso(api):
    id_curso = criar_curso_como_admin(api).json()["id_curso"]
    logar_como("usuario")

    resposta = api.delete(f"/api/cursos/{id_curso}")

    assert resposta.status_code == 403


# BANCO REAL (Postgres)
# Este teste usa o banco de verdade (o do Docker), pela fixture "db_sessao" do conftest.py.
# Ele garante que o modelo Curso bate com a tabela do schema.sql (coluna nome_curso).

def test_modelo_curso_bate_com_a_tabela_do_postgres(db_sessao):
    curso = Curso(nome="Curso de Teste", nivel="tecnologo")
    db_sessao.add(curso)
    db_sessao.flush()    # manda o INSERT ao banco, sem gravar de vez (o conftest faz rollback no fim)

    assert curso.id_curso is not None