import firebase_admin
from firebase_admin import credentials

from app.config import settings


def iniciar_firebase():
    """Conecta a API ao Firebase usando o arquivo de credenciais."""
    try:
        # Se já foi iniciado antes, não faz de novo
        firebase_admin.get_app()
        return
    except ValueError:
        pass

    cred = credentials.Certificate(settings.FIREBASE_CREDENTIALS_PATH)
    firebase_admin.initialize_app(cred)