import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.database import Sessao

# Cria o cliente HTTP para simular a API
@pytest.fixture(scope="module")
def cliente():
    with TestClient(app) as teste_cliente:
        yield teste_cliente

# Inicia o banco, roda o teste e limpa tudo depois
@pytest.fixture()
def db_sessao():
    sessao = Sessao()
    try:
        yield sessao
    finally:
        sessao.rollback()
        sessao.close()