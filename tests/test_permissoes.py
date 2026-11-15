# ---------------------------------------------------------------------------
# test_permissoes.py
#
# Testes das REGRAS DE PERMISSÃO das vagas:
#   - estudante não cria, edita nem apaga vaga;
#   - empresa só edita/apaga as PRÓPRIAS vagas;
#   - admin pode editar e apagar QUALQUER vaga;
#   - o cadastro não deixa ninguém se cadastrar como admin.
#
# Como funciona: usamos um banco SQLite em MEMÓRIA (some quando o teste acaba),
# então estes testes não precisam do Postgres nem do Firebase.
# A única coisa trocada por "mentira" é o login: em vez de conferir um token no
# Firebase, o teste diz quem é o usuário pelo cabeçalho "X-Teste-Uid".
# O resto (buscar o usuário no banco, checar o tipo, checar o dono) é o código real.
# ---------------------------------------------------------------------------

import pytest
from fastapi import Header
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app
from app.models import Empresa, Usuario, Vaga
from app.seguranca import get_usuario_atual

DADOS_VAGA = {
    "titulo": "Estágio em Python",
    "descricao": "Vaga de teste",
    "modalidade": "remota",
    "carga_horaria": 20,
    "cidade": "Bauru",
    "data_publicacao": "2026-11-01",
    "data_limite": "2026-12-01",
}


def falso_usuario_atual(x_teste_uid: str = Header(...)):
    """Finge o login: o 'uid' do usuário vem direto do cabeçalho X-Teste-Uid."""
    return {"uid": x_teste_uid, "email": None}


@pytest.fixture()
def cliente():
    """Cria um banco novo na memória, com usuários e vagas de exemplo, para cada teste."""
    # StaticPool faz todas as conexões usarem o MESMO banco em memória.
    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    Base.metadata.create_all(engine)
    Sessao = sessionmaker(bind=engine)

    # --- dados de exemplo ---
    db = Sessao()
    def novo_usuario(uid, tipo):
        u = Usuario(firebase_uid=uid, nome=uid, email=f"{uid}@email.com",
                    senha_hash="x", tipo_usuario=tipo)
        db.add(u)
        db.flush()  # gera o id_usuario
        return u

    estudante = novo_usuario("estudante", "usuario")
    empresa_a = novo_usuario("empresa_a", "recrutador")
    empresa_b = novo_usuario("empresa_b", "recrutador")
    novo_usuario("admin", "administrador")

    ea = Empresa(id_usuario=empresa_a.id_usuario, razao_social="A LTDA",
                 nome_fantasia="A", cnpj="11.111.111/0001-11", cidade="Bauru")
    eb = Empresa(id_usuario=empresa_b.id_usuario, razao_social="B LTDA",
                 nome_fantasia="B", cnpj="22.222.222/0001-22", cidade="Bauru")
    db.add_all([ea, eb])
    db.flush()

    # A vaga com id 1 pertence à empresa A.
    from datetime import date
    db.add(Vaga(id_empresa=ea.id_empresa, titulo="Vaga da A", descricao="d",
                modalidade="remota", carga_horaria=20, cidade="Bauru",
                data_publicacao=date(2026, 11, 1), data_limite=date(2026, 12, 1)))
    db.commit()
    db.close()

    # --- troca o banco real pelo de memória, e o login real pelo de mentira ---
    def db_de_teste():
        sessao = Sessao()
        try:
            yield sessao
        finally:
            sessao.close()

    app.dependency_overrides[get_db] = db_de_teste
    app.dependency_overrides[get_usuario_atual] = falso_usuario_atual
    yield TestClient(app)
    app.dependency_overrides.clear()  # desfaz as trocas ao final do teste


def como(uid):
    """Monta o cabeçalho que diz 'quem está logado' neste teste."""
    return {"X-Teste-Uid": uid}


# ============================ CRIAR VAGA ============================

def test_estudante_nao_cria_vaga(cliente):
    resposta = cliente.post("/api/vagas/", json=DADOS_VAGA, headers=como("estudante"))
    assert resposta.status_code == 403


def test_empresa_cria_vaga(cliente):
    resposta = cliente.post("/api/vagas/", json=DADOS_VAGA, headers=como("empresa_b"))
    assert resposta.status_code == 201


def test_empresa_pode_ter_mais_de_uma_vaga(cliente):
    # A empresa A já tem 1 vaga; criamos a segunda.
    resposta = cliente.post("/api/vagas/", json=DADOS_VAGA, headers=como("empresa_a"))
    assert resposta.status_code == 201


# ============================ APAGAR VAGA ============================

def test_estudante_nao_apaga_vaga(cliente):
    resposta = cliente.delete("/api/vagas/1", headers=como("estudante"))
    assert resposta.status_code == 403


def test_empresa_nao_apaga_vaga_de_outra(cliente):
    resposta = cliente.delete("/api/vagas/1", headers=como("empresa_b"))
    assert resposta.status_code == 403


def test_empresa_apaga_a_propria_vaga(cliente):
    resposta = cliente.delete("/api/vagas/1", headers=como("empresa_a"))
    assert resposta.status_code == 204


def test_admin_apaga_qualquer_vaga(cliente):
    resposta = cliente.delete("/api/vagas/1", headers=como("admin"))
    assert resposta.status_code == 204


def test_apagar_vaga_que_nao_existe(cliente):
    resposta = cliente.delete("/api/vagas/999", headers=como("admin"))
    assert resposta.status_code == 404


# ============================ EDITAR VAGA ============================

def test_empresa_nao_edita_vaga_de_outra(cliente):
    resposta = cliente.put("/api/vagas/1", json={"titulo": "Hackeada"}, headers=como("empresa_b"))
    assert resposta.status_code == 403


def test_admin_edita_qualquer_vaga(cliente):
    resposta = cliente.put("/api/vagas/1", json={"titulo": "Novo título"}, headers=como("admin"))
    assert resposta.status_code == 200
    assert resposta.json()["titulo"] == "Novo título"


# ============================ CADASTRO ============================

def test_cadastro_nao_aceita_tipo_admin(cliente):
    dados = {"nome": "Mal Intencionado", "email": "mal@email.com",
             "senha": "123456", "tipo_usuario": "administrador"}
    resposta = cliente.post("/auth/cadastro", json=dados)
    # 422 = o tipo "admin" é recusado antes de qualquer coisa ser criada.
    assert resposta.status_code == 422