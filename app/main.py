# os: usado para conferir se o arquivo de credenciais existe.
import os

# asynccontextmanager: permite criar a função "lifespan" abaixo,
# que roda código quando a API LIGA (e quando DESLIGA).
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.config import settings

# Função que conecta a API ao Firebase (ver app/firebase_config.py).
from app.firebase_config import iniciar_firebase

# Os endpoints de autenticação (/auth/cadastro, /auth/login, /auth/me).
from app.routers import auth_router


# O FastAPI executa esta função uma vez quando a API liga.
# Tudo o que vem ANTES do "yield" roda na inicialização.
# Tudo o que vem DEPOIS do "yield" rodaria no desligamento (não precisamos de nada).
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Só tenta conectar ao Firebase se o arquivo de credenciais existir.
    if os.path.exists(settings.FIREBASE_CREDENTIALS_PATH):
        iniciar_firebase()
    else:
        # Sem o arquivo, a API liga mesmo assim (o resto do projeto, como o banco,
        # continua funcionando), mas avisa no terminal.
        # Os endpoints de cadastro e login responderão com erro explicando o problema.
        print("AVISO: arquivo de credenciais do Firebase não encontrado. "
              "Cadastro e login não vão funcionar.")
    yield


# Cria a aplicação. "lifespan=lifespan" liga a função de inicialização acima.
app = FastAPI(title=settings.PROJECT_NAME, lifespan=lifespan)

# Registra os endpoints de autenticação na aplicação.
# Sem esta linha, as rotas /auth/... não existiriam.
app.include_router(auth_router.router)


# Inicialização da API
@app.get("/")
def home():
    return {
        "status": "ok",
        "mensagem": f"{settings.PROJECT_NAME} está funcionando!"
    }