import pytest
from fastapi.testclient import TestClient

from app.main import app

def test_tela_home(cliente):
    # Valida se o cliente está respondendo através das respostas de confirmação
    response = cliente.get("/")
    
    assert response.status_code == 200
    assert response.json()["status"] == "ok"

