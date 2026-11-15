from types import SimpleNamespace

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.seguranca import get_usuario_db


@pytest.mark.parametrize("tipo", ["usuario", "recrutador", "administrador"])
def test_perfil_retorna_dados_do_banco_sem_campos_privados(tipo):
    usuario = SimpleNamespace(
        id_usuario=7, nome="Maria", email="maria@example.com",
        telefone="11999999999", semestre=3, id_curso=2,
        tipo_usuario=tipo, senha_hash="privado", firebase_uid="uid-privado",
    )
    anteriores = app.dependency_overrides.copy()
    app.dependency_overrides[get_usuario_db] = lambda: usuario
    try:
        resposta = TestClient(app).get("/auth/perfil")
    finally:
        app.dependency_overrides.clear()
        app.dependency_overrides.update(anteriores)

    assert resposta.status_code == 200
    assert resposta.json() == {
        "id_usuario": 7, "nome": "Maria", "email": "maria@example.com",
        "telefone": "11999999999", "semestre": 3, "id_curso": 2,
        "tipo_usuario": tipo,
    }
