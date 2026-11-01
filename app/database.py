from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from app.config import settings

# Mecanismo de gerenciamento de acesso ao banco
engine = create_engine(settings.DATABASE_URL)

# Fábrica de sessões, gera acessos separados e automáticos
Session = sessionmaker(bind=engine)

# Base de modelo API
Base = declarative_base

# Não entendi também, pela documentão e pela IA parece abrir e fechar o acesso ao banco
def get_db():
    db = Session()
    try:
        yield db
    finally:
        db.close()
