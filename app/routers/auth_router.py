from typing import Optional
import requests

# APIRouter: agrupa endpoints relacionados (como uma "mini-API" dentro da API).
# Depends: usado para rodar a verificação de token antes do endpoint.
# HTTPException: usada para devolver erros HTTP com mensagem.
# status: códigos HTTP com nomes legíveis (HTTP_201_CREATED = 201 etc.).
from fastapi import APIRouter, Depends, HTTPException, status

# "auth" do Firebase Admin: sabe criar usuários e conferir tokens.
from firebase_admin import auth
from pydantic import BaseModel, Field, field_validator
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

# Configurações do projeto (lidas do .env).
from app.config import settings
from app.database import get_db
from app.models import Usuario
from app.seguranca import get_usuario_atual

# Cria o grupo de rotas.
#   prefix="/auth"  -> todos os endpoints abaixo começam com /auth
#   tags=[...]      -> agrupa os endpoints sob esse nome na documentação (/docs)
router = APIRouter(prefix="/auth", tags=["Autenticação"])

URL_LOGIN_FIREBASE = (
    "https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword"
)
PADRAO_EMAIL = r"^[^@\s]+@[^@\s]+\.[^@\s]+$"

# Códigos de erro que o Firebase devolve quando o problema é e-mail ou senha errados.
# Qualquer outro erro do Firebase (ex: chave da API errada) NÃO é culpa do usuário.
ERROS_DE_LOGIN = (
    "INVALID_PASSWORD",           # senha errada
    "EMAIL_NOT_FOUND",            # e-mail não cadastrado
    "INVALID_LOGIN_CREDENTIALS",  # e-mail ou senha errados (mensagem nova do Firebase)
    "USER_DISABLED",              # conta desativada
)


# ---------- MODELOS: descrevem e validam os dados que chegam na API ----------
# Se o front-end mandar dados fora destas regras, o FastAPI responde 422
# automaticamente, sem executar o código do endpoint.

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
    """Dados que o front-end precisa enviar para fazer login."""
    email: str = Field(pattern=PADRAO_EMAIL)
    senha: str = Field(min_length=1)  # no login só exigimos que não esteja vazia


# ---------- ENDPOINT 1: CADASTRO ----------

# @router.post -> o endpoint responde a requisições do tipo POST, no caminho /auth/cadastro.
# status_code=201 -> código de sucesso para "algo foi criado".
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
        # Já existe alguém com esse e-mail. 409 significa "conflito".
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Este e-mail já está cadastrado",
        )
    except ValueError:
        # O Firebase não aceitou os dados enviados. 400 significa "requisição inválida".
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Dados de cadastro inválidos",
        )
    except Exception:
        # Qualquer outro erro inesperado. 500 significa "erro no servidor".
        # Não mostramos o erro real ao usuário para não vazar informação interna.
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


# ---------- ENDPOINT 2: LOGIN ----------

@router.post("/login")
def login(dados: LoginEntrada):
    """Faz login no Firebase e devolve o token que o front-end vai usar."""

    # Sem a chave da API não dá para fazer login. Avisamos com clareza.
    if not settings.FIREBASE_API_KEY:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="FIREBASE_API_KEY não configurada no servidor",
        )

    try:
        # A nossa API faz uma chamada HTTP (POST) para o Firebase,
        # enviando o e-mail e a senha, para ele conferir.
        resposta = requests.post(
            URL_LOGIN_FIREBASE,
            # A chave da API vai na URL, como o Firebase exige.
            params={"key": settings.FIREBASE_API_KEY},
            # Corpo da chamada, em formato JSON.
            json={
                "email": dados.email,
                "password": dados.senha,
                # Pede para o Firebase devolver o token de login.
                "returnSecureToken": True,
            },
            # Se o Firebase não responder em 10 segundos, desiste (evita travar a API).
            timeout=10,
        )
    except requests.RequestException:
        # Não conseguiu nem falar com o Firebase (sem internet, por exemplo).
        # 502 significa "problema no serviço externo".
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Não foi possível se comunicar com o Firebase",
        )

    # O Firebase responde 200 quando o login deu certo.
    # Qualquer outro código significa que algo deu errado.
    if resposta.status_code != 200:
        # Tenta descobrir o motivo que o Firebase mandou (ex: INVALID_PASSWORD).
        try:
            motivo = resposta.json()["error"]["message"]
            # Às vezes vem texto depois de ":"; ficamos só com o código.
            motivo = str(motivo).split(":")[0].strip()
        except (ValueError, KeyError, TypeError):
            # A resposta veio em formato inesperado: motivo desconhecido.
            motivo = ""

        # Se o problema é e-mail ou senha errados, é erro do usuário: 401.
        # A mensagem é a MESMA para e-mail inexistente e senha errada, de propósito:
        # assim ninguém consegue descobrir quais e-mails estão cadastrados.
        if motivo in ERROS_DE_LOGIN:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="E-mail ou senha incorretos",
            )

        # Qualquer outro motivo é problema de configuração (ex: chave da API errada).
        # Separar os dois casos ajuda a achar o defeito sem culpar o usuário.
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro de configuração do Firebase (confira a FIREBASE_API_KEY)",
        )

    # Deu certo: pegamos o token ("idToken") da resposta do Firebase e devolvemos.
    # O front-end deve guardar esse token e enviá-lo nas próximas requisições.
    return {"access_token": resposta.json()["idToken"], "token_type": "bearer"}


# ---------- ENDPOINT 3: PERFIL (protegido) ----------

@router.get("/me")
def meu_perfil(usuario: dict = Depends(get_usuario_atual)):
    """Endpoint protegido: só responde se o token for válido."""
    return usuario