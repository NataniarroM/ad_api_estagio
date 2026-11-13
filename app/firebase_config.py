# ---------------------------------------------------------------------------
# firebase_config.py
#
# Este arquivo faz a CONEXÃO da nossa API com o Firebase.
#
# Como funciona a autenticação do projeto, em resumo:
#   - O Firebase guarda os usuários e as senhas (de forma segura, com criptografia).
#     Por isso o nosso banco de dados NÃO guarda senha nenhuma.
#   - A nossa API conversa com o Firebase para cadastrar usuários e conferir tokens.
#   - Para ter permissão de conversar com o Firebase como "administrador", a API usa
#     o arquivo de credenciais (firebase_credentials.json).
# ---------------------------------------------------------------------------

# "firebase_admin" é a biblioteca oficial do Firebase para servidores (Admin SDK).
import firebase_admin

# "credentials" lê o arquivo JSON com a chave de administrador.
from firebase_admin import credentials

# "settings" tem as configurações do projeto (lidas do arquivo .env).
from app.config import settings


def firebase_iniciado():
    """Diz se a API já está conectada ao Firebase (True = sim, False = não)."""
    try:
        # get_app() devolve a conexão com o Firebase, se ela já existir.
        firebase_admin.get_app()
        return True
    except ValueError:
        # Se a conexão ainda não existe, o Firebase dá um ValueError.
        # Nesse caso a resposta é "não iniciado".
        return False


def iniciar_firebase():
    """Conecta a API ao Firebase usando o arquivo de credenciais."""

    # Se já está conectado, não faz nada. Isso evita conectar duas vezes,
    # o que daria erro.
    if firebase_iniciado():
        return

    # Lê o arquivo JSON indicado no .env (FIREBASE_CREDENTIALS_PATH).
    # Se o arquivo não existir, aqui dá erro (FileNotFoundError).
    cred = credentials.Certificate(settings.FIREBASE_CREDENTIALS_PATH)

    # Faz a conexão de verdade. Depois disso, as funções do firebase_admin
    # (criar usuário, conferir token...) passam a funcionar.
    firebase_admin.initialize_app(cred)