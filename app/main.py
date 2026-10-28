from fastapi import FastAPI
from app.config import settings

app = FastAPI(title=settings.PROJECT_NAME)

@app.get("/")
def home():
    return {
        "status": "ok",
        "mensagem": f"{settings.PROJECT_NAME} está funcionando!"
    }