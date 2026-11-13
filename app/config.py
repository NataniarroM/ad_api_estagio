import os
from dotenv import load_dotenv

load_dotenv()

# Centralizando a configuração da API, seu nome, porta, banco de dados e credenciais do firebase.
class Settings:
    PROJECT_NAME: str = os.getenv("PROJECT_NAME", "API vagas de estagio")
    PORT: int = int(os.getenv("PORT", 8000))
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@db:5432/vagas_db")

    # Caminho do arquivo JSON com a "chave de administrador" do Firebase.
    # Esse arquivo NÃO vai para o GitHub (está no .gitignore). Cada pessoa baixa o seu
    # no console do Firebase: Configurações do projeto > Contas de serviço.
    # O nome padrão é o mesmo que o .gitignore já bloqueia, para ninguém subir por engano.
    FIREBASE_CREDENTIALS_PATH: str = os.getenv("FIREBASE_CREDENTIALS_PATH", "firebase_credentials.json")

    # Chave de API da Web do Firebase. É usada só no login (ver app/routers/auth_router.py).
    # Fica no arquivo .env, nunca escrita direto no código.
    # O valor padrão "" (vazio) faz a API avisar com clareza quando a chave não foi configurada.
    FIREBASE_API_KEY: str = os.getenv("FIREBASE_API_KEY", "")

settings = Settings()