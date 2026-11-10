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

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rotas de autenticação (/auth/cadastro, /auth/login, /auth/me)
app.include_router(auth_router.router)


# Inicialização da API
@app.get("/")
def home():
    return {
        "status": "ok",
        "mensagem": f"{settings.PROJECT_NAME} está funcionando!"
    }