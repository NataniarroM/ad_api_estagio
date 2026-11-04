from unittest.mock import MagicMock, patch
from fastapi.testclient import TestClient
from firebase_admin import auth

from app.config import settings
from app.main import app

# Sem "with", então o Firebase real NÃO é iniciado nos testes
client = TestClient(app)

CADASTRO_OK = {"nome": "Maria", "email": "maria@email.com", "senha": "123456"}
LOGIN_OK = {"email": "maria@email.com", "senha": "123456"}


# ---------- Cadastro ----------

@patch("app.routers.auth_router.auth.create_user")
def test_cadastro_com_sucesso(mock_create_user):
    mock_create_user.return_value = MagicMock(
        uid="abc123", email="maria@email.com", display_name="Maria"
    )

    resposta = client.post("/auth/cadastro", json=CADASTRO_OK)

    assert resposta.status_code == 201
    assert resposta.json()["uid"] == "abc123"
    assert "senha" not in resposta.json()


@patch("app.routers.auth_router.auth.create_user")
def test_cadastro_email_repetido(mock_create_user):
    mock_create_user.side_effect = auth.EmailAlreadyExistsError("já existe", None, None)

    resposta = client.post("/auth/cadastro", json=CADASTRO_OK)

    assert resposta.status_code == 409


def test_cadastro_senha_curta():
    dados = {**CADASTRO_OK, "senha": "123"}

    resposta = client.post("/auth/cadastro", json=dados)

    assert resposta.status_code == 422


def test_cadastro_email_invalido():
    dados = {**CADASTRO_OK, "email": "isso-nao-e-email"}

    resposta = client.post("/auth/cadastro", json=dados)

    assert resposta.status_code == 422


# ---------- Login ----------

@patch("app.routers.auth_router.requests.post")
def test_login_com_sucesso(mock_post, monkeypatch):
    monkeypatch.setattr(settings, "FIREBASE_API_KEY", "chave-falsa")
    mock_post.return_value = MagicMock(
        status_code=200, json=lambda: {"idToken": "token-de-teste"}
    )

    resposta = client.post("/auth/login", json=LOGIN_OK)

    assert resposta.status_code == 200
    assert resposta.json()["access_token"] == "token-de-teste"


@patch("app.routers.auth_router.requests.post")
def test_login_senha_errada(mock_post, monkeypatch):
    monkeypatch.setattr(settings, "FIREBASE_API_KEY", "chave-falsa")
    mock_post.return_value = MagicMock(status_code=400)

    resposta = client.post("/auth/login", json=LOGIN_OK)

    assert resposta.status_code == 401


# ---------- Endpoint protegido ----------

def test_me_sem_token():
    resposta = client.get("/auth/me")

    assert resposta.status_code in (401, 403)


@patch("app.seguranca.auth.verify_id_token")
def test_me_token_invalido(mock_verify):
    mock_verify.side_effect = Exception("token ruim")

    resposta = client.get("/auth/me", headers={"Authorization": "Bearer abc"})

    assert resposta.status_code == 401


@patch("app.seguranca.auth.verify_id_token")
def test_me_token_valido(mock_verify):
    mock_verify.return_value = {"uid": "abc123", "email": "maria@email.com"}

    resposta = client.get("/auth/me", headers={"Authorization": "Bearer abc"})

    assert resposta.status_code == 200
    assert resposta.json()["uid"] == "abc123"
