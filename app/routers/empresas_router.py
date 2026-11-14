from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import List

from app.database import get_db
from app.models import Empresa, Usuario
from app.schemas import EmpresaCreate, EmpresaResponse
from app.seguranca import get_usuario_db

router = APIRouter(prefix="/empresas", tags=["Empresas"])

@router.post("/", response_model=EmpresaResponse, status_code=status.HTTP_201_CREATED)
def criar_empresa(
    dados: EmpresaCreate,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_usuario_db)
):
    if usuario.tipo_usuario != "empresa":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Apenas usuários do tipo 'empresa' podem cadastrar dados empresariais."
        )

    nova_empresa = Empresa(id_usuario=usuario.id_usuario, **dados.model_dump())
    db.add(nova_empresa)
    try:
        db.commit()
        db.refresh(nova_empresa)
        return nova_empresa
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Este usuário já possui empresa vinculada ou o CNPJ já está cadastrado."
        )

@router.get("/", response_model=List[EmpresaResponse])
def listar_empresas(db: Session = Depends(get_db)):
    return db.query(Empresa).all()

@router.get("/{id_empresa}", response_model=EmpresaResponse)
def buscar_empresa(id_empresa: int, db: Session = Depends(get_db)):
    empresa = db.query(Empresa).filter(Empresa.id_empresa == id_empresa).first()
    if not empresa:
        raise HTTPException(status_code=404, detail="Empresa não encontrada.")
    return empresa