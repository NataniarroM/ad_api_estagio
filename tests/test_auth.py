# ---------------------------------------------------------------------------
# test_auth.py
#
# Testes automáticos da autenticação. Para rodar:
#     docker compose exec api pytest
#
# IDEIA IMPORTANTE: estes testes NÃO usam o Firebase de verdade.
# Usamos "mocks" (peças de mentira) que fingem ser o Firebase. Assim:
#   - os testes rodam em milissegundos, sem internet e ssem credenciais;
#   - conseguimos simular situações difíceis (senha errada, e-mail repetido...);
#   - não criamos usuários de verdade no Firebase a cada teste.
#
# Cada teste segue 3 passos:
#   1) preparar  -> monta a situação (ex: o Firebase "responde" tal coisa)
#   2) executar  -> chama o endpoint da API
#   3) conferir  -> usa "assert" para ver se o resultado é o esperado
# ---------------------------------------------------------------------------

# MagicMock: cria um objeto de mentira que aceita qualquer uso.
# patch: troca uma função real por uma de mentira, só durante o teste.
from unittest.mock import MagicMock, patch

# pytest: a ferramenta que descobre e roda os testes.
import pytest

# TestClient: simula um navegador/front-end chamando a API, sem precisar ligá-la.
from fastapi.testclient import TestClient

# "auth" do Firebase: usado aqui só para pegar o tipo de erro EmailAlreadyExistsError.
from firebase_admin import auth

from app.config import settings
from app.main import app

# Cria o cliente de teste.
# Sem usar "with", a função de inicialização (lifespan) NÃO roda,
# então o Firebase real não é conectado durante os testes.
client = TestClient(app)

# Dados de exemplo reaproveitados em vários testes.
CADASTRO_OK = {"nome": "Maria", "email": "maria@email.com", "senha": "123456"}
LOGIN_OK = {"email": "maria@email.com", "senha": "123456"}


# "fixture" = preparação que o pytest faz sozinho antes de cada teste.
# autouse=True significa que vale para TODOS os testes deste arquivo.
@pytest.fixture(autouse=True)
def firebase_de_mentira(monkeypatch):
    # Nos testes, fingimos que o Firebase já está conectado (firebase_iniciado -> True).
    # "monkeypatch" desfaz a troca sozinho quando o teste termina.
    monkeypatch.setattr("app.routers.auth_router.firebase_iniciado", lambda: True)


def resposta_firebase(status_code, motivo=None):
    """Cria uma resposta falsa do Firebase, com o código e o motivo de erro desejados."""
    corpo = {"error": {"message": motivo}} if motivo else {}
    return MagicMock(status_code=status_code, json=lambda: corpo)


# ============================ TESTES DE CADASTRO ============================

# @patch troca auth.create_user (que falaria com o Firebase) por uma função de mentira.
# O objeto de mentira chega ao teste no parâmetro "mock_create_user".
@patch("app.routers.auth_router.auth.create_user")
def test_cadastro_com_sucesso(mock_create_user):
    # 1) preparar: o "Firebase" devolve um usuário criado.
    mock_create_user.return_value = MagicMock(
        uid="abc123", email="maria@email.com", display_name="Maria"
    )

    # 2) executar: chama o endpoint como se fosse o front-end.
    resposta = client.post("/auth/cadastro", json=CADASTRO_OK)

    # 3) conferir: 201 = criado; o uid veio; e a senha NÃO foi devolvida.
    assert resposta.status_code == 201
    assert resposta.json()["uid"] == "abc123"
    assert "senha" not in resposta.json()


@patch("app.routers.auth_router.auth.create_user")
def test_cadastro_email_repetido(mock_create_user):
    # Simula o Firebase reclamando que o e-mail já existe.
    mock_create_user.side_effect = auth.EmailAlreadyExistsError("já existe", None, None)

    resposta = client.post("/auth/cadastro", json=CADASTRO_OK)

    # 409 = conflito.
    assert resposta.status_code == 409


def test_cadastro_senha_curta():
    # Copia os dados corretos, mas troca a senha por uma de só 3 caracteres.
    dados = {**CADASTRO_OK, "senha": "123"}

    resposta = client.post("/auth/cadastro", json=dados)

    # 422 = dados fora das regras. O Firebase nem chega a ser chamado.
    assert resposta.status_code == 422


def test_cadastro_email_invalido():
    dados = {**CADASTRO_OK, "email": "isso-nao-e-email"}

    resposta = client.post("/auth/cadastro", json=dados)

    assert resposta.status_code == 422


def test_cadastro_sem_firebase_configurado(monkeypatch):
    # Neste teste, desfazemos a mentira da fixture: agora o Firebase está "desconectado".
    monkeypatch.setattr("app.routers.auth_router.firebase_iniciado", lambda: False)

    resposta = client.post("/auth/cadastro", json=CADASTRO_OK)

    # 503 = serviço indisponível (falta configurar o Firebase).
    assert resposta.status_code == 503


# ============================= TESTES DE LOGIN ==============================

# Aqui o que trocamos por mentira é requests.post, a chamada HTTP ao Firebase.
@patch("app.routers.auth_router.requests.post")
def test_login_com_sucesso(mock_post, monkeypatch):
    # Define uma chave de API falsa só para este teste.
    monkeypatch.setattr(settings, "FIREBASE_API_KEY", "chave-falsa")
    # O "Firebase" responde 200 (ok) com um token.
    mock_post.return_value = MagicMock(
        status_code=200, json=lambda: {"idToken": "token-de-teste"}
    )

    resposta = client.post("/auth/login", json=LOGIN_OK)

    assert resposta.status_code == 200
    assert resposta.json()["access_token"] == "token-de-teste"


@patch("app.routers.auth_router.requests.post")
def test_login_senha_errada(mock_post, monkeypatch):
    monkeypatch.setattr(settings, "FIREBASE_API_KEY", "chave-falsa")
    # O "Firebase" diz que e-mail ou senha estão errados.
    mock_post.return_value = resposta_firebase(400, "INVALID_LOGIN_CREDENTIALS")

    resposta = client.post("/auth/login", json=LOGIN_OK)

    # 401 = não autenticado.
    assert resposta.status_code == 401


@patch("app.routers.auth_router.requests.post")
def test_login_chave_da_api_errada(mock_post, monkeypatch):
    monkeypatch.setattr(settings, "FIREBASE_API_KEY", "chave-errada")
    # O "Firebase" reclama da chave: problema de configuração, não do usuário.
    mock_post.return_value = resposta_firebase(400, "API key not valid.")

    resposta = client.post("/auth/login", json=LOGIN_OK)

    # 500 = erro do servidor (e não 401, porque o usuário não errou nada).
    assert resposta.status_code == 500


def test_login_sem_chave_da_api(monkeypatch):
    # Simula o .env sem a FIREBASE_API_KEY preenchida.
    monkeypatch.setattr(settings, "FIREBASE_API_KEY", "")

    resposta = client.post("/auth/login", json=LOGIN_OK)

    assert resposta.status_code == 500


# ==================== TESTES DO ENDPOINT PROTEGIDO (/auth/me) ====================

def test_me_sem_token():
    # Chama sem enviar nenhum token.
    resposta = client.get("/auth/me")

    # Dependendo da versão do FastAPI, a recusa vem como 401 ou 403. Aceitamos os dois.
    assert resposta.status_code in (401, 403)


# Aqui trocamos por mentira a função que confere o token no Firebase.
@patch("app.seguranca.auth.verify_id_token")
def test_me_token_invalido(mock_verify):
    # Simula o Firebase recusando o token.
    mock_verify.side_effect = Exception("token ruim")

    # Envia um token qualquer no cabeçalho Authorization.
    resposta = client.get("/auth/me", headers={"Authorization": "Bearer abc"})

    assert resposta.status_code == 401


@patch("app.seguranca.auth.verify_id_token")
def test_me_token_valido(mock_verify):
    # Simula o Firebase aceitando o token e devolvendo os dados do usuário.
    mock_verify.return_value = {"uid": "abc123", "email": "maria@email.com"}

    resposta = client.get("/auth/me", headers={"Authorization": "Bearer abc"})

    assert resposta.status_code == 200
    assert resposta.json()["uid"] == "abc123"