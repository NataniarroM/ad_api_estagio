import requests
from fastapi import APIRouter, Depends, HTTPException, status
from firebase_admin import auth
from pydantic import BaseModel, Field

from app.config import settings
from app.seguranca import get_usuario_atual

router = APIRouter(prefix="/auth", tags=["Autenticação"])

# Endereço do Firebase usado para fazer login com e-mail e senha
URL_LOGIN_FIREBASE = (
    "https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword"
)

# Formato simples de e-mail: texto@texto.texto
PADRAO_EMAIL = r"^[^@\s]+@[^@\s]+\.[^@\s]+$"


class CadastroEntrada(BaseModel):
    nome: str = Field(min_length=2, max_length=100)
    email: str = Field(pattern=PADRAO_EMAIL)
    senha: str = Field(min_length=6, max_length=100)


class LoginEntrada(BaseModel):
    email: str = Field(pattern=PADRAO_EMAIL)
    senha: str = Field(min_length=1)


@router.post("/cadastro", status_code=status.HTTP_201_CREATED)
def cadastrar(dados: CadastroEntrada):
    """Cria um usuário no Firebase. A senha fica guardada de forma segura por lá."""
    try:
        usuario = auth.create_user(
            email=dados.email,
            password=dados.senha,
            display_name=dados.nome,
        )
    except auth.EmailAlreadyExistsError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Este e-mail já está cadastrado",
        )
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Dados de cadastro inválidos",
        )
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao criar o usuário",
        )

    return {"uid": usuario.uid, "email": usuario.email, "nome": usuario.display_name}


@router.post("/login")
def login(dados: LoginEntrada):
    """Faz login no Firebase e devolve o token que o front-end vai usar."""
    if not settings.FIREBASE_API_KEY:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="FIREBASE_API_KEY não configurada no servidor",
        )

    try:
        resposta = requests.post(
            URL_LOGIN_FIREBASE,
            params={"key": settings.FIREBASE_API_KEY},
            json={
                "email": dados.email,
                "password": dados.senha,
                "returnSecureToken": True,
            },
            timeout=10,
        )
    except requests.RequestException:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Não foi possível se comunicar com o Firebase",
        )

    if resposta.status_code != 200:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="E-mail ou senha incorretos",
        )

    return {"access_token": resposta.json()["idToken"], "token_type": "bearer"}


@router.get("/me")
def meu_perfil(usuario: dict = Depends(get_usuario_atual)):
    """Endpoint protegido: só responde se o token for válido."""
    return usuario
