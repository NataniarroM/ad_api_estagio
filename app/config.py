import os
from dotenv import load_dotenv

load_dotenv()

# Centralizando a configuração da API, seu nome, porta, banco de dados e credenciais do firebase.
class Settings:
    PROJECT_NAME: str = os.getenv("PROJECT_NAME", "API vagas de estagio")
    PORT: int = int(os.getenv("PORT", 8000))
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@db:5432/vagas_db")
    FIREBASE_CREDENTIALS_PATH: str = os.getenv("FIREBASE_CREDENTIALS_PATH", "arquivo_firebase.json")
    FIREBASE_API_KEY: str = os.getenv("FIREBASE_API_KEY", "")

settings = Settings()