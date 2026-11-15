import uuid
import pytest
from sqlalchemy.exc import IntegrityError
from app.models import Curso, Usuario, Empresa, Vaga, Candidatura


# 1. Teste de todos os modelos
@pytest.mark.parametrize("model_instance", [
    Curso(
        nome="Análise e Desenvolvimento de Sistemas",
        nivel="tecnologo"
    ),
    Usuario(
        firebase_uid="uid_pytest_123",
        nome="Candidato Teste",
        email="emailteste@exemplo.com",
        senha_hash="hash_simulado",
        tipo_usuario="usuario"
    ),
    Empresa(
        id_usuario=1,
        razao_social="Empresa Teste LTDA",
        nome_fantasia="Empresa Teste",
        cnpj="12.345.678/0001-90",
        cidade="Bauru"
    ),
    Vaga(
        id_empresa=1,
        titulo="Estágio em Desenvolvimento Python",
        descricao="Vaga para atuação com FastAPI e PostgreSQL",
        modalidade="remota",
        carga_horaria=30,
        cidade="Bauru",
        data_publicacao="2026-11-03",
        data_limite="2026-12-31"
    ),
    Candidatura(
        id_usuario=1,
        id_vaga=1,
        status_candidatura="enviada"
    )
])
def test_all_models_structure_generic(model_instance):
    """Garante que todas as instâncias dos modelos possuem o atributo __tablename__ mapeado."""
    assert model_instance is not None
    assert hasattr(model_instance, "__tablename__")
    assert isinstance(getattr(model_instance, "__tablename__"), str)


# 2. Testes de Restrição de Unicidade (O db_sessao vem do conftest.py)
def test_usuario_unique_email_constraint(db_sessao):
    """Valida se o PostgreSQL rejeita cadastrar dois usuários com o mesmo e-mail."""
    sufixo = uuid.uuid4().hex[:8]
    email_dup = f"dup_{sufixo}@teste.com"

    u1 = Usuario(
        firebase_uid=f"uid_1_{sufixo}",
        nome="User A",
        email=email_dup,
        senha_hash="hash",
        tipo_usuario="usuario"
    )
    u2 = Usuario(
        firebase_uid=f"uid_2_{sufixo}",
        nome="User B",
        email=email_dup,
        senha_hash="hash",
        tipo_usuario="usuario"
    )

    db_sessao.add(u1)
    db_sessao.commit()

    db_sessao.add(u2)
    with pytest.raises(IntegrityError):
        db_sessao.commit()
    db_sessao.rollback()

    db_sessao.delete(u1)
    db_sessao.commit()


def test_usuario_unique_firebase_uid_constraint(db_sessao):
    """Valida se o PostgreSQL rejeita dois usuários com o mesmo firebase_uid."""
    sufixo = uuid.uuid4().hex[:8]
    uid_dup = f"uid_rep_{sufixo}"

    u1 = Usuario(
        firebase_uid=uid_dup,
        nome="User X",
        email=f"user_x_{sufixo}@teste.com",
        senha_hash="hash",
        tipo_usuario="usuario"
    )
    u2 = Usuario(
        firebase_uid=uid_dup,
        nome="User Y",
        email=f"user_y_{sufixo}@teste.com",
        senha_hash="hash",
        tipo_usuario="usuario"
    )

    db_sessao.add(u1)
    db_sessao.commit()

    db_sessao.add(u2)
    with pytest.raises(IntegrityError):
        db_sessao.commit()
    db_sessao.rollback()

    db_sessao.delete(u1)
    db_sessao.commit()