from typing import Optional
import requests
from fastapi import APIRouter, Depends, HTTPException, status
from firebase_admin import auth
from pydantic import BaseModel, Field, field_validator
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.models import Usuario
from app.seguranca import get_usuario_atual

router = APIRouter(prefix="/auth", tags=["Autenticação"])

URL_LOGIN_FIREBASE = (
    "https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword"
)
PADRAO_EMAIL = r"^[^@\s]+@[^@\s]+\.[^@\s]+$"


class CadastroEntrada(BaseModel):
    nome: str = Field(min_length=2, max_length=150)
    email: str = Field(pattern=PADRAO_EMAIL)
    senha: str = Field(min_length=6, max_length=100)
    tipo_usuario: str = Field(default="estudante", pattern="^(estudante|empresa|admin)$")
    id_curso: Optional[int] = None
    telefone: Optional[str] = Field(default=None, max_length=20)
    semestre: Optional[int] = Field(default=None, gt=0)

    @field_validator("id_curso", "semestre", mode="before")
    @classmethod
    def converter_zero_para_none(cls, valor):
        return None if valor == 0 else valor


class LoginEntrada(BaseModel):
    email: str = Field(pattern=PADRAO_EMAIL)
    senha: str = Field(min_length=1)


@router.post("/cadastro", status_code=status.HTTP_201_CREATED)
def cadastrar(dados: CadastroEntrada, db: Session = Depends(get_db)):
    """Cria um usuário no Firebase e sincroniza o perfil na tabela usuario do PostgreSQL."""
    try:
        usuario_fb = auth.create_user(
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
            detail="Erro ao criar o usuário no Firebase",
        )

    novo_usuario_db = Usuario(
        firebase_uid=usuario_fb.uid,
        id_curso=dados.id_curso,
        nome=dados.nome,
        email=dados.email,
        senha_hash="GERENCIADO_PELO_FIREBASE",
        tipo_usuario=dados.tipo_usuario,
        telefone=dados.telefone,
        semestre=dados.semestre,
        aluno=(dados.tipo_usuario == "estudante"),
    )

    db.add(novo_usuario_db)
    try:
        db.commit()
        db.refresh(novo_usuario_db)
    except IntegrityError:
        db.rollback()
        auth.delete_user(usuario_fb.uid)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Erro ao salvar usuário no banco (e-mail duplicado ou id_curso inexistente).",
        )

    return {
        "id_usuario": novo_usuario_db.id_usuario,
        "uid": usuario_fb.uid,
        "email": novo_usuario_db.email,
        "nome": novo_usuario_db.nome,
        "tipo_usuario": novo_usuario_db.tipo_usuario,
    }


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