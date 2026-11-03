from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from firebase_admin import auth

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
