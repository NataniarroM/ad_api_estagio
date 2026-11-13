from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from firebase_admin import auth
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Usuario

# Faz o Swagger mostrar o botão "Authorize" para colar o token
bearer = HTTPBearer()


def get_usuario_atual(credenciais: HTTPAuthorizationCredentials = Depends(bearer)):
    """Confere o token enviado no header Authorization: Bearer <token>.

    Use nos endpoints que precisam de login:
        usuario: dict = Depends(get_usuario_atual)
    """
    token = credenciais.credentials

    try:
        dados = auth.verify_id_token(token)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido ou expirado",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return {"uid": dados["uid"], "email": dados.get("email")}

def get_usuario_db(
    usuario_firebase: dict = Depends(get_usuario_atual),
    db: Session = Depends(get_db),
) -> Usuario:
    #Valida o token no Firebase e busca o registro correspondente na tabela usuario.
    usuario = db.query(Usuario).filter(Usuario.firebase_uid == usuario_firebase["uid"]).first()
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuário autenticado no Firebase, mas não cadastrado no banco de dados.",
        )
    return usuario