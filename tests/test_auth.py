# ---------------------------------------------------------------------------
# test_auth.py
#
# Testes automáticos da AUTENTICAÇÃO (cadastro, login e perfil).
# Para rodar:
#     docker compose exec api pytest tests/test_auth.py -q
#
# IDEIA: estes testes NÃO usam o Firebase nem o Postgres de verdade.
#   - O Firebase é trocado por "mocks" (peças de mentira que respondem o que
#     o teste mandar). Assim rodam sem internet e sem criar usuário de verdade.
#   - O banco é um SQLite em MEMÓRIA (some quando o teste termina).
#
# Cada teste segue 3 passos:
#   1) preparar  -> monta a situação (ex: o Firebase "responde" tal coisa)
#   2) executar  -> chama o endpoint da API
#   3) conferir  -> usa "assert" para ver se o resultado é o esperado
# ---------------------------------------------------------------------------

from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient
from firebase_admin import auth
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.config import settings
from app.database import Base, get_db
from app.main import app
from app.models import Usuario

# Dados de exemplo reaproveitados em vários testes.
CADASTRO_OK = {"nome": "Maria", "email": "maria@email.com", "senha": "123456"}
LOGIN_OK = {"email": "maria@email.com", "senha": "123456"}


@pytest.fixture()
def banco():
    """Cria um banco SQLite em memória, novo a cada teste, e o entrega à API.

    O cadastro agora grava na tabela `usuario`, então precisamos de um banco.
    StaticPool faz todas as conexões usarem o MESMO banco em memória.
    """
    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    Base.metadata.create_all(engine)
    Sessao = sessionmaker(bind=engine)

    # Troca o get_db real (Postgres) por um que usa o banco de teste.
    def get_db_teste():
        db = Sessao()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = get_db_teste
    yield Sessao  # o teste recebe a "fábrica de sessões" para consultar o banco
    app.dependency_overrides.clear()  # desfaz a troca ao terminar


@pytest.fixture()
def client(banco):
    """Cliente de teste: simula o front-end chamando a API.
    Sem `with`, o startup (que conectaria ao Firebase de verdade) não roda."""
    return TestClient(app)


def resposta_firebase(status_code, motivo=None):
    """Cria uma resposta falsa do Firebase, com o código e o motivo de erro desejados."""
    corpo = {"error": {"message": motivo}} if motivo else {}
    return MagicMock(status_code=status_code, json=lambda: corpo)


# ============================ TESTES DE CADASTRO ============================

# @patch troca auth.create_user (que falaria com o Firebase) por uma função de mentira.
@patch("app.routers.auth_router.auth.create_user")
def test_cadastro_com_sucesso(mock_create_user, client, banco):
    # 1) preparar: o "Firebase" devolve um usuário criado.
    mock_create_user.return_value = MagicMock(
        uid="abc123", email="maria@email.com", display_name="Maria"
    )

    # 2) executar
    resposta = client.post("/auth/cadastro", json=CADASTRO_OK)

    # 3) conferir: 201 = criado; a senha NÃO volta; e o usuário foi gravado no banco.
    assert resposta.status_code == 201
    assert "123456" not in resposta.text
    db = banco()
    usuario = db.query(Usuario).filter_by(firebase_uid="abc123").first()
    assert usuario is not None
    assert usuario.email == "maria@email.com"
    assert usuario.tipo_usuario == "usuario"  # padrão quando não se escolhe o tipo
    db.close()


@patch("app.routers.auth_router.auth.create_user")
def test_cadastro_recrutador(mock_create_user, client, banco):
    mock_create_user.return_value = MagicMock(
        uid="rec1", email="rec@email.com", display_name="Rec"
    )

    dados = {**CADASTRO_OK, "email": "rec@email.com", "tipo_usuario": "recrutador"}
    resposta = client.post("/auth/cadastro", json=dados)

    assert resposta.status_code == 201
    db = banco()
    assert db.query(Usuario).filter_by(firebase_uid="rec1").first().tipo_usuario == "recrutador"
    db.close()


@patch("app.routers.auth_router.auth.create_user")
def test_cadastro_nao_aceita_administrador(mock_create_user, client):
    # Segurança: ninguém pode virar admin pelo cadastro público.
    dados = {**CADASTRO_OK, "tipo_usuario": "administrador"}

    resposta = client.post("/auth/cadastro", json=dados)

    assert resposta.status_code == 422        # recusado pela validação
    mock_create_user.assert_not_called()      # o Firebase nem foi chamado


@patch("app.routers.auth_router.auth.create_user")
def test_cadastro_email_repetido(mock_create_user, client):
    # Simula o Firebase reclamando que o e-mail já existe.
    mock_create_user.side_effect = auth.EmailAlreadyExistsError("já existe", None, None)

    resposta = client.post("/auth/cadastro", json=CADASTRO_OK)

    assert resposta.status_code == 409  # 409 = conflito


def test_cadastro_senha_curta(client):
    dados = {**CADASTRO_OK, "senha": "123"}   # só 3 caracteres
    resposta = client.post("/auth/cadastro", json=dados)
    assert resposta.status_code == 422        # dados fora das regras


def test_cadastro_email_invalido(client):
    dados = {**CADASTRO_OK, "email": "isso-nao-e-email"}
    resposta = client.post("/auth/cadastro", json=dados)
    assert resposta.status_code == 422


# ============================= TESTES DE LOGIN ==============================

# Aqui o que trocamos por mentira é requests.post, a chamada HTTP ao Firebase.
@patch("app.routers.auth_router.requests.post")
def test_login_com_sucesso(mock_post, client, monkeypatch):
    monkeypatch.setattr(settings, "FIREBASE_API_KEY", "chave-falsa")
    mock_post.return_value = MagicMock(
        status_code=200, json=lambda: {"idToken": "token-de-teste"}
    )

    resposta = client.post("/auth/login", json=LOGIN_OK)

    assert resposta.status_code == 200
    assert resposta.json()["access_token"] == "token-de-teste"


@patch("app.routers.auth_router.requests.post")
def test_login_senha_errada(mock_post, client, monkeypatch):
    monkeypatch.setattr(settings, "FIREBASE_API_KEY", "chave-falsa")
    mock_post.return_value = resposta_firebase(400, "INVALID_LOGIN_CREDENTIALS")

    resposta = client.post("/auth/login", json=LOGIN_OK)

    assert resposta.status_code == 401  # 401 = não autenticado


@patch("app.routers.auth_router.requests.post")
def test_login_chave_da_api_errada(mock_post, client, monkeypatch):
    monkeypatch.setattr(settings, "FIREBASE_API_KEY", "chave-errada")
    mock_post.return_value = resposta_firebase(400, "API key not valid.")

    resposta = client.post("/auth/login", json=LOGIN_OK)

    # 500 e não 401: o erro é de configuração do servidor, o usuário não errou nada.
    assert resposta.status_code == 500


def test_login_sem_chave_da_api(client, monkeypatch):
    monkeypatch.setattr(settings, "FIREBASE_API_KEY", "")
    resposta = client.post("/auth/login", json=LOGIN_OK)
    assert resposta.status_code == 500
    
@patch("app.routers.auth_router.requests.post")
def test_login_devolve_tipo_usuario(mock_post, client, banco, monkeypatch):
    monkeypatch.setattr(settings, "FIREBASE_API_KEY", "chave-falsa")
    # O usuário precisa existir no banco, com o mesmo uid que o Firebase devolve.
    db = banco()
    db.add(Usuario(firebase_uid="uid-adm", nome="Admin", email="maria@email.com",
                   senha_hash="x", tipo_usuario="administrador"))
    db.commit()
    db.close()
    mock_post.return_value = MagicMock(
        status_code=200, json=lambda: {"idToken": "tok", "localId": "uid-adm"}
    )

    resposta = client.post("/auth/login", json=LOGIN_OK)

    assert resposta.status_code == 200
    assert resposta.json()["tipo_usuario"] == "administrador"


# ================= TESTES DO ENDPOINT PROTEGIDO (/auth/perfil) =================

def test_perfil_sem_token(client):
    # Sem cabeçalho Authorization. Dependendo da versão do FastAPI vem 401 ou 403.
    resposta = client.get("/auth/perfil")
    assert resposta.status_code in (401, 403)


# Trocamos por mentira a função que confere o token no Firebase.
@patch("app.seguranca.auth.verify_id_token")
def test_perfil_token_invalido(mock_verify, client):
    mock_verify.side_effect = Exception("token ruim")   # Firebase recusa o token

    resposta = client.get("/auth/perfil", headers={"Authorization": "Bearer abc"})

    assert resposta.status_code == 401


@patch("app.seguranca.auth.verify_id_token")
def test_perfil_token_valido(mock_verify, client, banco):
    # O usuário precisa existir no banco, com o mesmo firebase_uid do token.
    db = banco()
    db.add(Usuario(firebase_uid="abc123", nome="Maria", email="maria@email.com",
                   senha_hash="x", tipo_usuario="usuario"))
    db.commit()
    db.close()
    mock_verify.return_value = {"uid": "abc123", "email": "maria@email.com"}

    resposta = client.get("/auth/perfil", headers={"Authorization": "Bearer abc"})

    assert resposta.status_code == 200
    assert "maria@email.com" in resposta.text


@patch("app.seguranca.auth.verify_id_token")
def test_perfil_usuario_fora_do_banco(mock_verify, client):
    # Token válido no Firebase, mas sem linha na tabela usuario -> 404.
    mock_verify.return_value = {"uid": "desconhecido", "email": "x@email.com"}

    resposta = client.get("/auth/perfil", headers={"Authorization": "Bearer abc"})

    assert resposta.status_code == 404
    
    test_login_sem_chave_da_api