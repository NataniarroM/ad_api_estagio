# ---------------------------------------------------------------------------
# test_seed.py
#
# Testes dos dados iniciais (app/seed.py). Banco SQLite em memória e Firebase
# de mentira: não precisam de Postgres, internet nem credenciais.
# ---------------------------------------------------------------------------

from unittest.mock import MagicMock, patch

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base
from app.models import Curso, Usuario
from app.seed import CURSOS_INICIAIS, garantir_admin, garantir_cursos


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


def test_cria_todos_os_cursos_no_banco_vazio(db):
    criados = garantir_cursos(db)

    assert criados == len(CURSOS_INICIAIS)
    assert db.query(Curso).count() == len(CURSOS_INICIAIS)


def test_rodar_duas_vezes_nao_duplica(db):
    garantir_cursos(db)
    criados_na_segunda = garantir_cursos(db)

    assert criados_na_segunda == 0
    assert db.query(Curso).count() == len(CURSOS_INICIAIS)


def test_nao_mexe_em_curso_que_ja_existe(db):
    # Um curso da lista já existe (mesmo nome) e está inativo: o seed deve respeitar.
    nome = CURSOS_INICIAIS[0]["nome"]
    db.add(Curso(nome=nome, nivel="bacharelado", ativo=False))
    db.commit()

    garantir_cursos(db)

    assert db.query(Curso).filter(Curso.nome == nome).count() == 1
    assert db.query(Curso).filter(Curso.nome == nome).first().ativo is False


@patch("app.criar_admin.auth.get_user_by_email")
def test_admin_reaproveita_conta_do_firebase(mock_get, db):
    mock_get.return_value = MagicMock(uid="uid-admin")

    usuario = garantir_admin(db, "admin@email.com", "Admin", "senha123")

    assert usuario.tipo_usuario == "administrador"
    assert db.query(Usuario).count() == 1


@patch("app.criar_admin.auth.get_user_by_email")
def test_admin_duas_vezes_nao_duplica(mock_get, db):
    mock_get.return_value = MagicMock(uid="uid-admin")

    garantir_admin(db, "admin@email.com", "Admin", "senha123")
    garantir_admin(db, "admin@email.com", "Admin", "senha123")

    assert db.query(Usuario).count() == 1