# cursos_router.py
# CRUD dos cursos (a tabela "curso" do banco). Endereços (todos começam com /api):
#   GET    /api/cursos         -> lista os cursos            (público: o cadastro precisa dele)
#   GET    /api/cursos/{id}    -> mostra um curso            (público)
#   POST   /api/cursos         -> cria um curso              (só administrador)
#   PUT    /api/cursos/{id}    -> atualiza um curso          (só administrador)
#   DELETE /api/cursos/{id}    -> apaga um curso             (só administrador)
# CRUD = Create (POST), Read (GET), Update (PUT), Delete (DELETE).

from typing import List

# APIRouter: agrupa as rotas. Depends: roda uma função "porteiro" antes da rota.
# HTTPException: devolve erros HTTP com mensagem. status: nomes legíveis dos códigos HTTP.
from fastapi import APIRouter, Depends, HTTPException, status

# Session: a "conversa" com o banco de dados (cada requisição abre uma e fecha no final).
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Curso, Usuario
from app.schemas import CursoCreate, CursoResponse, CursoUpdate

# Porteiro que só deixa o administrador passar (ver app/seguranca.py).
from app.seguranca import exigir_administrador

# No main.py este router é registrado com prefix="/api", então o endereço final
# fica /api + /cursos = /api/cursos.
router = APIRouter(prefix="/cursos", tags=["Cursos"])


def buscar_curso_ou_404(db: Session, id_curso: int) -> Curso:
    """Procura o curso pelo id. Se não existir, já responde 404 ("não encontrado").

    Várias rotas precisam disso, então fica numa função só (evita repetir código).
    """
    curso = db.query(Curso).filter(Curso.id_curso == id_curso).first()
    if not curso:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Curso não encontrado.",
        )
    return curso


# ---------- READ: listar (público) ----------
# O caminho é "" (vazio) para o endereço ser exatamente /api/cursos, sem barra no final.
# É assim que o front-end (Cadastro.jsx) chama.
@router.get("", response_model=List[CursoResponse])
def listar_cursos(apenas_ativos: bool = True, db: Session = Depends(get_db)):
    """Lista os cursos em ordem alfabética.

    Por padrão mostra só os ATIVOS (é o que o formulário de cadastro quer).
    Para ver todos, inclusive os inativos: /api/cursos?apenas_ativos=false
    """
    consulta = db.query(Curso)
    if apenas_ativos:
        consulta = consulta.filter(Curso.ativo == True)  # noqa: E712 (o SQLAlchemy precisa do "== True")
    return consulta.order_by(Curso.nome).all()


# ---------- READ: buscar um (público) ----------
@router.get("/{id_curso}", response_model=CursoResponse)
def buscar_curso(id_curso: int, db: Session = Depends(get_db)):
    """Devolve um curso pelo id, ou 404 se não existir."""
    return buscar_curso_ou_404(db, id_curso)

# SSIX SEVENNNN
# ---------- CREATE: criar (só administrador) ----------
@router.post("", response_model=CursoResponse, status_code=status.HTTP_201_CREATED)
def criar_curso(
    dados: CursoCreate,                                       # corpo da requisição, já validado
    db: Session = Depends(get_db),
    admin: Usuario = Depends(exigir_administrador),           # porteiro: só administrador
):
    """Cria um curso novo."""
    # dados.model_dump() transforma o CursoCreate em dicionário: {"nome": ..., "nivel": ..., "ativo": ...}
    # e o ** espalha esse dicionário como argumentos do Curso(...).
    novo = Curso(**dados.model_dump())
    db.add(novo)       # coloca na fila para salvar
    db.commit()        # grava de verdade no banco
    db.refresh(novo)   # recarrega para pegar o id_curso gerado pelo banco
    return novo


# ---------- UPDATE: atualizar (só administrador) ----------
@router.put("/{id_curso}", response_model=CursoResponse)
def atualizar_curso(
    id_curso: int,
    dados: CursoUpdate,
    db: Session = Depends(get_db),
    admin: Usuario = Depends(exigir_administrador),
):
    """Atualiza só os campos que foram enviados."""
    curso = buscar_curso_ou_404(db, id_curso)

    # exclude_unset=True: só traz o que o front realmente enviou.
    # Assim, quem manda só {"ativo": false} não apaga o nome nem o nível.
    for campo, valor in dados.model_dump(exclude_unset=True).items():
        # Se mandarem "nome": null ou "nivel": null, ignoramos (esses campos são obrigatórios no banco).
        if valor is not None:
            setattr(curso, campo, valor)   # curso.nome = valor, curso.nivel = valor...

    db.commit()
    db.refresh(curso)
    return curso


# ---------- DELETE: apagar (só administrador) ----------
@router.delete("/{id_curso}", status_code=status.HTTP_204_NO_CONTENT)
def apagar_curso(
    id_curso: int,
    db: Session = Depends(get_db),
    admin: Usuario = Depends(exigir_administrador),
):
    """Apaga um curso. Os usuários desse curso NÃO são apagados:
    o banco coloca id_curso = NULL neles (regra ON DELETE SET NULL do schema.sql).
    """
    curso = buscar_curso_ou_404(db, id_curso)
    db.delete(curso)
    db.commit()
    # 204 = "deu certo, e não há conteúdo para devolver". Por isso não tem return.