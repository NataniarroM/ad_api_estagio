# ---------------------------------------------------------------------------
# test_criar_admin.py
#
# Testes do comando que cria o administrador (app/criar_admin.py).
# Usam banco SQLite em memória e um Firebase de mentira: não precisam de Postgres,
# de internet nem de credenciais, e não criam usuários de verdade.
# ---------------------------------------------------------------------------

from unittest.mock import MagicMock, patch

import pytest
from firebase_admin import auth
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.criar_admin import garantir_usuario_no_firebase, promover_no_banco
from app.database import Base
from app.models import Usuario


@pytest.fixture()
def db():
    """Banco novo na memória para cada teste."""
    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    Base.metadata.create_all(engine)
    sessao = sessionmaker(bind=engine)()
    yield sessao
    sessao.close()


def test_cria_admin_quando_nao_existe_no_banco(db):
    usuario = promover_no_banco(db, "uid1", "admin@email.com", "Admin")

    assert usuario.tipo_usuario == "administrador"
    assert db.query(Usuario).count() == 1


def test_promove_usuario_que_ja_existe(db):
    # Já existe um usuário comum com esse firebase_uid.
    db.add(Usuario(firebase_uid="uid1", nome="Ana", email="ana@email.com",
                   senha_hash="x", tipo_usuario="usuario"))
    db.commit()

    usuario = promover_no_banco(db, "uid1", "ana@email.com", "Ana")

    assert usuario.tipo_usuario == "administrador"   # foi promovido...
    assert db.query(Usuario).count() == 1            # ...sem criar uma segunda linha


def test_rodar_duas_vezes_nao_duplica(db):
    promover_no_banco(db, "uid1", "admin@email.com", "Admin")
    promover_no_banco(db, "uid1", "admin@email.com", "Admin")

    assert db.query(Usuario).count() == 1


@patch("app.criar_admin.auth.create_user")
@patch("app.criar_admin.auth.get_user_by_email")
def test_firebase_reaproveita_usuario_existente(mock_get, mock_create):
    mock_get.return_value = MagicMock(uid="uid-existente")
    pedir_senha = MagicMock()

    usuario_fb = garantir_usuario_no_firebase("admin@email.com", "Admin", pedir_senha)

    assert usuario_fb.uid == "uid-existente"
    mock_create.assert_not_called()      # não criou outro usuário
    pedir_senha.assert_not_called()      # nem pediu senha


@patch("app.criar_admin.auth.create_user")
@patch("app.criar_admin.auth.get_user_by_email")
def test_firebase_cria_usuario_quando_nao_existe(mock_get, mock_create):
    mock_get.side_effect = auth.UserNotFoundError("não existe")
    mock_create.return_value = MagicMock(uid="uid-novo")

    usuario_fb = garantir_usuario_no_firebase("admin@email.com", "Admin", lambda: "senha123")

    assert usuario_fb.uid == "uid-novo"
    mock_create.assert_called_once_with(
        email="admin@email.com", password="senha123", display_name="Admin"
    )