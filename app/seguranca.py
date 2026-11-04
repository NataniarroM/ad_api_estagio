# ---------------------------------------------------------------------------
# seguranca.py
#
# Este arquivo tem o "porteiro" da API: uma função que confere se quem está
# chamando um endpoint tem um token de login válido.
#
# Como usar em QUALQUER endpoint que precise de login (qualquer colega pode usar):
#
#     from fastapi import Depends
#     from app.seguranca import get_usuario_atual
#
#     @router.get("/vagas")
#     def listar_vagas(usuario: dict = Depends(get_usuario_atual)):
#         # Se chegou aqui, o usuário está logado.
#         # usuario["uid"] e usuario["email"] dizem quem ele é.
#         ...
#
# Se o token estiver ausente ou inválido, o FastAPI responde com erro ANTES de
# executar o código do endpoint.
# ---------------------------------------------------------------------------

# logging: biblioteca do Python para escrever mensagens no terminal (os "logs").
import logging

# Depends: recurso do FastAPI para "rodar uma função antes do endpoint".
# HTTPException: usada para devolver erros HTTP (como 401).
# status: tem os códigos HTTP com nomes legíveis (ex: HTTP_401_UNAUTHORIZED).
from fastapi import Depends, HTTPException, status

# HTTPBearer: lê o cabeçalho "Authorization: Bearer <token>" da requisição.
# HTTPAuthorizationCredentials: o objeto que guarda o token lido.
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

# "auth" é a parte do Firebase que sabe conferir tokens de login.
from firebase_admin import auth

# Cria o "caderno de anotações" da API. Usamos o mesmo do servidor (uvicorn),
# então as mensagens aparecem no terminal onde o "docker compose up" está rodando.
logger = logging.getLogger("uvicorn.error")

# Cria o leitor de token. Ele também faz o Swagger (/docs) mostrar o botão
# "Authorize", onde colamos o token para testar endpoints protegidos.
# Se a requisição vier SEM o cabeçalho Authorization, o FastAPI já recusa sozinho.
bearer = HTTPBearer()


def get_usuario_atual(credenciais: HTTPAuthorizationCredentials = Depends(bearer)):
    """Confere o token enviado no header Authorization: Bearer <token>.

    Devolve um dicionário com o uid e o e-mail do usuário logado.
    """

    # Pega só o texto do token (sem a palavra "Bearer").
    token = credenciais.credentials

    try:
        # O Firebase confere se o token é verdadeiro (assinatura), se não expirou
        # (cada token dura cerca de 1 hora) e se pertence ao nosso projeto.
        # Se estiver tudo certo, devolve os dados do usuário que estão dentro do token.
        dados = auth.verify_id_token(token)
    except Exception as erro:
        # Qualquer problema (token falso, expirado, mal formado...) cai aqui.
        # Anotamos o MOTIVO REAL no terminal (só quem mantém a API vê isso).
        # Assim, quando der erro, dá para descobrir a causa sem adivinhar.
        logger.warning("Falha ao validar token: %s: %s", type(erro).__name__, str(erro)[:200])

        # Para quem chamou a API, devolvemos 401 ("não autenticado") com uma
        # mensagem propositalmente genérica, para não dar pistas a quem tenta invadir.
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido ou expirado",
            # Cabeçalho padrão que informa ao cliente qual tipo de login a API espera.
            headers={"WWW-Authenticate": "Bearer"},
        )

    # "uid" é o identificador único do usuário no Firebase.
    # É ele que o banco de dados deve guardar (coluna firebase_uid da tabela usuario).
    # dados.get("email") evita erro caso o token venha sem e-mail.
    return {"uid": dados["uid"], "email": dados.get("email")}