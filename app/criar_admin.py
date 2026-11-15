# ---------------------------------------------------------------------------
# criar_admin.py
#
# Cria (ou promove) um usuário ADMINISTRADOR. Por segurança, o administrador NÃO
# pode ser criado pelo cadastro público (/auth/cadastro): se pudesse, qualquer
# pessoa se cadastraria como administrador. Por isso existe este comando.
#
# Como usar (com o Docker rodando):
#     docker compose exec api python -m app.criar_admin admin@email.com "Nome do Admin"
#
# A senha é pedida no terminal (ela não aparece na tela).
#
# Pode rodar quantas vezes quiser, sem estragar nada:
#   - se o e-mail já existe no Firebase, ele é reaproveitado (a senha não muda);
#   - se o usuário já existe no banco, ele só é promovido a administrador.
# ---------------------------------------------------------------------------

import getpass   # pede a senha no terminal sem mostrá-la na tela
import sys       # lê os argumentos digitados na linha de comando

from firebase_admin import auth
from sqlalchemy.orm import Session

from app.database import Sessao
from app.firebase_config import iniciar_firebase
from app.models import Usuario


def garantir_usuario_no_firebase(email: str, nome: str, pedir_senha):
    """Devolve o usuário do Firebase com esse e-mail. Se não existir, cria.

    pedir_senha é uma função que devolve a senha; só é chamada se for preciso criar.
    """
    try:
        usuario_fb = auth.get_user_by_email(email)    # procura pelo e-mail
        print("Este e-mail já existe no Firebase. Vou reaproveitá-lo (a senha não muda).")
        return usuario_fb
    except auth.UserNotFoundError:
        # Não existe ainda: cria com a senha informada.
        return auth.create_user(email=email, password=pedir_senha(), display_name=nome)


def promover_no_banco(db: Session, uid: str, email: str, nome: str) -> Usuario:
    """Garante que o usuário existe no banco com tipo_usuario = "administrador"."""
    # firebase_uid é o que liga o usuário do Firebase à linha da tabela usuario.
    usuario = db.query(Usuario).filter(Usuario.firebase_uid == uid).first()

    if usuario:
        usuario.tipo_usuario = "administrador"       # já existe: só promove
    else:
        usuario = Usuario(                           # não existe: cria a linha
            firebase_uid=uid,
            nome=nome,
            email=email,
            senha_hash="GERENCIADO_PELO_FIREBASE",   # a senha de verdade fica só no Firebase
            tipo_usuario="administrador",
        )
        db.add(usuario)

    db.commit()
    db.refresh(usuario)
    return usuario


def pedir_senha_no_terminal() -> str:
    """Pergunta a senha duas vezes e confere se são iguais e têm pelo menos 6 caracteres."""
    senha = getpass.getpass("Senha do administrador (mínimo 6 caracteres): ")
    repetida = getpass.getpass("Repita a senha: ")
    if senha != repetida or len(senha) < 6:
        print("As senhas não são iguais, ou têm menos de 6 caracteres. Nada foi criado.")
        sys.exit(1)
    return senha


def main():
    # sys.argv guarda o que foi digitado: [nome_do_script, e-mail, nome]
    if len(sys.argv) != 3:
        print('Uso: python -m app.criar_admin EMAIL "NOME DO ADMIN"')
        sys.exit(1)
    email, nome = sys.argv[1], sys.argv[2]

    try:
        iniciar_firebase()   # conecta ao Firebase com o firebase_credentials.json
    except Exception as erro:
        print(f"Não consegui conectar ao Firebase: {erro}")
        print("Confira se o firebase_credentials.json está na raiz do projeto.")
        sys.exit(1)

    usuario_fb = garantir_usuario_no_firebase(email, nome, pedir_senha_no_terminal)

    db = Sessao()
    try:
        usuario = promover_no_banco(db, usuario_fb.uid, email, nome)
    finally:
        db.close()

    print(f"Pronto! {usuario.email} agora é administrador (id_usuario = {usuario.id_usuario}).")


# Só roda o main() quando o arquivo é executado como comando (python -m app.criar_admin).
if __name__ == "__main__":
    main()