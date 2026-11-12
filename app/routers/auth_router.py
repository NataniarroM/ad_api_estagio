# ---------------------------------------------------------------------------
# auth_router.py
#
# Aqui ficam os 3 endpoints de autenticação da API:
#
#   POST /auth/cadastro  -> cria um usuário novo no Firebase
#   POST /auth/login     -> confere e-mail e senha e devolve um TOKEN
#   GET  /auth/me        -> endpoint protegido; mostra quem está logado
#
# Fluxo completo, do ponto de vista do front-end:
#   1. O usuário se cadastra em /auth/cadastro.
#   2. O usuário faz login em /auth/login e recebe um "access_token".
#   3. Nas próximas requisições, o front-end envia esse token no cabeçalho:
#          Authorization: Bearer <token>
#   4. Os endpoints protegidos conferem o token (ver app/seguranca.py).
# ---------------------------------------------------------------------------

# "requests" é a biblioteca para a nossa API fazer chamadas HTTP a outros sites.
# Aqui ela é usada para falar com o Firebase no login.
import requests

# APIRouter: agrupa endpoints relacionados (como uma "mini-API" dentro da API).
# Depends: usado para rodar a verificação de token antes do endpoint.
# HTTPException: usada para devolver erros HTTP com mensagem.
# status: códigos HTTP com nomes legíveis (HTTP_201_CREATED = 201 etc.).
from fastapi import APIRouter, Depends, HTTPException, status

# "auth" do Firebase Admin: sabe criar usuários e conferir tokens.
from firebase_admin import auth

# BaseModel: base para criar "modelos" que descrevem e validam os dados recebidos.
# Field: permite definir regras para cada campo (tamanho mínimo, formato...).
from pydantic import BaseModel, Field

# Configurações do projeto (lidas do .env).
from app.config import settings

# Função que diz se a conexão com o Firebase está ativa.
from app.firebase_config import firebase_iniciado

# O "porteiro" que confere o token (usado no endpoint /auth/me).
from app.seguranca import get_usuario_atual

# Cria o grupo de rotas.
#   prefix="/auth"  -> todos os endpoints abaixo começam com /auth
#   tags=[...]      -> agrupa os endpoints sob esse nome na documentação (/docs)
router = APIRouter(prefix="/auth", tags=["Autenticação"])

# Endereço da API do Firebase que confere e-mail e senha e devolve o token.
# Usamos o endereço REST porque a biblioteca firebase_admin NÃO consegue
# conferir senha: ela só serve para tarefas de administrador (criar usuário, etc.).
URL_LOGIN_FIREBASE = (
    "https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword"
)

# Regra (expressão regular) para conferir se um e-mail tem formato válido.
# Em português: "texto" + "@" + "texto" + "." + "texto", sem espaços.
#   ^           começo do texto
#   [^@\s]+     um ou mais caracteres que não sejam "@" nem espaço
#   @           a arroba
#   [^@\s]+     um ou mais caracteres que não sejam "@" nem espaço
#   \.          um ponto
#   [^@\s]+     um ou mais caracteres que não sejam "@" nem espaço
#   $           fim do texto
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
    """Dados que o front-end precisa enviar para cadastrar um usuário."""
    nome: str = Field(min_length=2, max_length=100)   # entre 2 e 100 letras
    email: str = Field(pattern=PADRAO_EMAIL)          # precisa ter formato de e-mail
    senha: str = Field(min_length=6, max_length=100)  # mínimo 6 (exigência do Firebase)


class LoginEntrada(BaseModel):
    """Dados que o front-end precisa enviar para fazer login."""
    email: str = Field(pattern=PADRAO_EMAIL)
    senha: str = Field(min_length=1)  # no login só exigimos que não esteja vazia


# ---------- ENDPOINT 1: CADASTRO ----------

# @router.post -> o endpoint responde a requisições do tipo POST, no caminho /auth/cadastro.
# status_code=201 -> código de sucesso para "algo foi criado".
@router.post("/cadastro", status_code=status.HTTP_201_CREATED)
def cadastrar(dados: CadastroEntrada):
    """Cria um usuário no Firebase. A senha fica guardada de forma segura por lá."""

    # Antes de tentar, confere se a API está conectada ao Firebase.
    # Se não estiver (falta o firebase_credentials.json), avisa com clareza.
    # 503 significa "serviço indisponível".
    if not firebase_iniciado():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Firebase não configurado no servidor (falta o firebase_credentials.json)",
        )

    try:
        # Pede ao Firebase para criar o usuário.
        # O Firebase guarda a senha criptografada; nós nunca a armazenamos.
        usuario = auth.create_user(
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
            detail="Erro ao criar o usuário",
        )

    # Devolve os dados do usuário criado. NUNCA devolvemos a senha.
    return {"uid": usuario.uid, "email": usuario.email, "nome": usuario.display_name}


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

    # Depends(get_usuario_atual) roda o "porteiro" antes deste código.
    # Se o token for inválido, a função abaixo nem chega a ser executada
    # (o porteiro já respondeu 401).
    # Se for válido, "usuario" já chega preenchido com o uid e o e-mail.
    return usuario