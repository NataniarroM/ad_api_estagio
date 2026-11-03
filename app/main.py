import os
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.config import settings
from app.firebase_config import iniciar_firebase
from app.routers import auth_router


# Roda uma vez quando a API liga: conecta no Firebase
@asynccontextmanager
async def lifespan(app: FastAPI):
    if os.path.exists(settings.FIREBASE_CREDENTIALS_PATH):
        iniciar_firebase()
    else:
        print("AVISO: arquivo de credenciais do Firebase não encontrado. "
              "Cadastro e login não vão funcionar.")
    yield


app = FastAPI(title=settings.PROJECT_NAME, lifespan=lifespan)

# Rotas de autenticação (/auth/cadastro, /auth/login, /auth/me)
app.include_router(auth_router.router)


# Inicialização da API
@app.get("/")
def home():
    return {
        "status": "ok",
        "mensagem": f"{settings.PROJECT_NAME} está funcionando!"
    }