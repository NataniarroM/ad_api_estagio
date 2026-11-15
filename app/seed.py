# ---------------------------------------------------------------------------
# seed.py
#
# "Seed" = dados iniciais. Roda sozinho toda vez que a API liga e garante que
# o banco tem o MÍNIMO para o projeto funcionar:
#   - os cursos iniciais (uma linha por curso, na lista CURSOS_INICIAIS);
#   - o usuário administrador (e-mail/nome/senha vêm do arquivo .env).
#
# É IDEMPOTENTE: pode rodar mil vezes que não duplica nada nem dá conflito.
# Só cria o que ainda não existe. Por isso funciona igual depois de
# "docker compose down -v" (banco zerado) ou numa máquina nova.
#
# Também dá para rodar na mão:
#     docker compose exec api python -m app.seed
# ---------------------------------------------------------------------------

import os
import time

# Importar app.config carrega o arquivo .env (load_dotenv roda lá dentro).
from app.config import settings  # noqa: F401
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.criar_admin import garantir_usuario_no_firebase, promover_no_banco
from app.database import Sessao
from app.firebase_config import firebase_iniciado, iniciar_firebase
from app.models import Curso

# ---------------------------------------------------------------------------
# DADOS INICIAIS: para criar mais um curso, é só acrescentar uma linha aqui.
# "nivel" precisa ser: tecnologo, bacharelado ou licenciatura.
# ---------------------------------------------------------------------------
CURSOS_INICIAIS = [
    {"nome": "Ciência da Computação", "nivel": "bacharelado"},
    {"nome": "Engenharia de Software", "nivel": "bacharelado"},
    {"nome": "Sistemas de Informação", "nivel": "bacharelado"},
    {"nome": "Análise e Desenvolvimento de Sistemas", "nivel": "tecnologo"},
    {"nome": "Administração", "nivel": "bacharelado"},
    {"nome": "Engenharia de Computação", "nivel": "bacharelado"},
    {"nome": "Redes de Computadores", "nivel": "tecnologo"},
    {"nome": "Ciências Contábeis", "nivel": "bacharelado"},
    {"nome": "Design Gráfico", "nivel": "tecnologo"},
    {"nome": "Matemática", "nivel": "licenciatura"},
]


def garantir_cursos(db: Session) -> int:
    """Cria os cursos da lista que ainda não existem. Devolve quantos foram criados."""
    criados = 0
    for dados in CURSOS_INICIAIS:
        # Procura pelo NOME: se já existe um curso com esse nome, pula.
        ja_existe = db.query(Curso).filter(Curso.nome == dados["nome"]).first()
        if not ja_existe:
            db.add(Curso(nome=dados["nome"], nivel=dados["nivel"], ativo=True))
            criados += 1
    db.commit()
    return criados


def garantir_admin(db: Session, email: str, nome: str, senha: str):
    """Garante que o administrador existe no Firebase E no banco.

    - Se o e-mail já existe no Firebase, reaproveita (a senha não muda).
    - Se não existe, cria com a senha informada.
    - No banco, cria a linha ou só promove a administrador.
    """
    usuario_fb = garantir_usuario_no_firebase(email, nome, lambda: senha)
    return promover_no_banco(db, usuario_fb.uid, email, nome)


def esperar_banco(tentativas: int = 15) -> bool:
    """O Postgres pode demorar alguns segundos para ligar. Tenta várias vezes."""
    for _ in range(tentativas):
        try:
            db = Sessao()
            db.execute(text("SELECT 1"))   # pergunta boba só para ver se o banco responde
            db.close()
            return True
        except Exception:
            time.sleep(2)
    return False


def executar_seed():
    """Roda tudo. Nunca derruba a API: se algo falhar, só avisa no terminal."""
    try:
        if not esperar_banco():
            print("SEED: o banco não respondeu. Dados iniciais não foram criados.")
            return

        db = Sessao()
        try:
            criados = garantir_cursos(db)
            print(f"SEED: cursos conferidos ({criados} novo(s)).")

            # --- administrador: só se o .env tiver e-mail e senha ---
            email = os.getenv("ADMIN_EMAIL", "")
            nome = os.getenv("ADMIN_NOME", "Administrador")
            senha = os.getenv("ADMIN_SENHA", "")
            if not (email and senha):
                print("SEED: ADMIN_EMAIL/ADMIN_SENHA não definidos no .env; admin não criado.")
            else:
                if not firebase_iniciado():
                    iniciar_firebase()       # no comando manual o Firebase ainda não foi ligado
                usuario = garantir_admin(db, email, nome, senha)
                print(f"SEED: administrador pronto ({usuario.email}).")
        finally:
            db.close()
    except Exception as erro:
        print(f"SEED: falhou ({erro}). A API continua ligada.")


if __name__ == "__main__":
    executar_seed()