import pytest
from sqlalchemy import text
from app.database import engine, get_db


def test_database_engine_connection():
    # Verifica se a engine construída pelo SQLAlchemy estabelece conexão como o Banco
    with engine.connect() as connection:
        result = connection.execute(text("SELECT 1"))
        assert result.scalar() == 1


def test_get_db_generator():
    # Verifica se as sessões são iniciadas e encerradas pelo gerador
    db_gen = get_db()
    db = next(db_gen)

    assert db is not None
    # Consulta simples à sessão atual
    result = db.execute(text("SELECT 1"))
    assert result.scalar() == 1

    # Simula o término do ciclo de vida da requisição
    try:
        next(db_gen)
    except StopIteration:
        pass  # O gerador finaliza com sucesso