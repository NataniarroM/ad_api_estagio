import uuid
import pytest
from app.main import app
from app.database import Sessao
from app.models import Usuario, Empresa, Vaga, Candidatura
from app.seguranca import get_usuario_db


@pytest.fixture
def usuarios_teste():
    """Cria um usuário Recrutador e um usuário Candidato temporários no banco e remove ao final."""
    db = Sessao()
    uid_rec = f"uid_rec_{uuid.uuid4().hex[:8]}"
    uid_usr = f"uid_usr_{uuid.uuid4().hex[:8]}"

    user_recrutador = Usuario(
        firebase_uid=uid_rec,
        nome="Recrutador Teste Pytest",
        email=f"{uid_rec}@teste.com",
        senha_hash="GERENCIADO_PELO_FIREBASE",
        tipo_usuario="recrutador",
    )
    user_candidato = Usuario(
        firebase_uid=uid_usr,
        nome="Estudante Teste Pytest",
        email=f"{uid_usr}@teste.com",
        senha_hash="GERENCIADO_PELO_FIREBASE",
        tipo_usuario="usuario",
    )
    db.add_all([user_recrutador, user_candidato])
    db.commit()
    db.refresh(user_recrutador)
    db.refresh(user_candidato)

    yield {"recrutador": user_recrutador, "usuario": user_candidato}

    # Limpeza pós-teste respeitando a ordem das chaves estrangeiras
    app.dependency_overrides.clear()
    db.query(Candidatura).filter(Candidatura.id_usuario == user_candidato.id_usuario).delete()
    emp = db.query(Empresa).filter(Empresa.id_usuario == user_recrutador.id_usuario).first()
    if emp:
        db.query(Vaga).filter(Vaga.id_empresa == emp.id_empresa).delete()
        db.delete(emp)
    db.delete(user_candidato)
    db.delete(user_recrutador)
    db.commit()
    db.close()


# --- 1. TESTES DE SEGURANÇA (SEM AUTENTICAÇÃO) ---

def test_criar_vaga_sem_token_falha(cliente):
    """Garante que requisições sem token Bearer sejam bloqueadas."""
    app.dependency_overrides.clear()
    payload = {
        "titulo": "Estágio Não Autorizado",
        "descricao": "Teste sem login",
        "modalidade": "remota",
        "carga_horaria": 20,
        "cidade": "Bauru",
        "data_publicacao": "2026-11-14",
        "data_limite": "2026-12-30",
    }
    response = cliente.post("/api/vagas/", json=payload)
    assert response.status_code in (401, 403)


# --- 2. TESTES DE CONTROLE DE ACESSO (PERFIL INVÁLIDO) ---

def test_estudante_nao_pode_cadastrar_empresa(cliente, usuarios_teste):
    """Garante que um usuário do tipo 'usuario' receba 403 ao tentar criar empresa."""
    app.dependency_overrides[get_usuario_db] = lambda: usuarios_teste["usuario"]

    payload = {
        "razao_social": "Empresa Fake LTDA",
        "nome_fantasia": "Fake",
        "cnpj": f"99.{uuid.uuid4().int % 900 + 100}.000/0001-00",
        "cidade": "Bauru",
    }
    response = cliente.post("/empresas/", json=payload)
    assert response.status_code == 403


# --- 3. TESTES DO FLUXO COMPLETO (EMPRESA -> VAGA -> CANDIDATURA) ---

def test_fluxo_completo_empresa_vaga_candidatura(cliente, usuarios_teste):
    """Testa criação de empresa, publicação/edição de vaga, candidatura e bloqueio de duplicidade."""
    # A) Autentica como Recrutador e cria o perfil empresarial
    app.dependency_overrides[get_usuario_db] = lambda: usuarios_teste["recrutador"]
    cnpj_unico = f"11.{uuid.uuid4().int % 900 + 100}.333/0001-44"
    resp_emp = cliente.post(
        "/empresas/",
        json={
            "razao_social": "Pytest Tech LTDA",
            "nome_fantasia": "Pytest Tech",
            "cnpj": cnpj_unico,
            "cidade": "Bauru",
            "site": "https://pytest.dev",
        },
    )
    assert resp_emp.status_code == 201
    assert resp_emp.json()["nome_fantasia"] == "Pytest Tech"

    # B) Publica uma nova vaga vinculada automaticamente à empresa logada
    resp_vaga = cliente.post(
        "/api/vagas/",
        json={
            "titulo": "Estágio QA & Python",
            "descricao": "Automação de testes com pytest e FastAPI.",
            "requisitos": "Python básico",
            "modalidade": "hibrida",
            "bolsa": 1400.00,
            "carga_horaria": 30,
            "cidade": "Bauru",
            "data_publicacao": "2026-11-14",
            "data_limite": "2026-12-20",
        },
    )
    assert resp_vaga.status_code == 201
    dados_vaga = resp_vaga.json()
    id_vaga = dados_vaga["id_vaga"]
    assert dados_vaga["status_vaga"] == "publicada"

    # C) Atualiza a bolsa da vaga (PUT)
    resp_put = cliente.put(f"/api/vagas/{id_vaga}", json={"bolsa": 1650.00})
    assert resp_put.status_code == 200
    assert float(resp_put.json()["bolsa"]) == 1650.00

    # D) Alterna autenticação para Candidato ('usuario') e realiza candidatura
    app.dependency_overrides[get_usuario_db] = lambda: usuarios_teste["usuario"]
    resp_cand = cliente.post(
        "/candidatura/",
        json={"id_vaga": id_vaga, "curriculo_url": "https://meu-cv.com/cv.pdf"},
    )
    assert resp_cand.status_code == 201

    # E) Tenta candidatar-se novamente à mesma vaga (deve falhar com 400)
    resp_cand_dup = cliente.post("/candidatura/", json={"id_vaga": id_vaga})
    assert resp_cand_dup.status_code == 400

    # F) Lista minhas candidatura
    resp_minhas = cliente.get("/candidatura/minhas")
    assert resp_minhas.status_code == 200
    assert any(c["id_vaga"] == id_vaga for c in resp_minhas.json())


def test_buscar_vaga_inexistente_retorna_404(cliente):
    """Valida retorno 404 Not Found ao consultar ID de vaga inexistente."""
    response = cliente.get("/api/vagas/999999")
    assert response.status_code == 404