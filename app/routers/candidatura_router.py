from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import List

from app.database import get_db
from app.models import Candidatura, Usuario
from app.schemas import CandidaturaCreate, CandidaturaResponse
from app.seguranca import get_usuario_db

router = APIRouter(prefix="/candidaturas", tags=["Candidaturas"])

@router.post("/", response_model=CandidaturaResponse, status_code=status.HTTP_201_CREATED)
def criar_candidatura(
    candidatura: CandidaturaCreate,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_usuario_db)
):
    if usuario.tipo_usuario != "estudante":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Apenas estudantes podem se candidatar a vagas."
        )

    nova = Candidatura(id_usuario=usuario.id_usuario, **candidatura.model_dump())
    db.add(nova)
    try:
        db.commit()
        db.refresh(nova)
        return nova
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Você já se candidatou a esta vaga ou a vaga não existe."
        )

@router.get("/minhas", response_model=List[CandidaturaResponse])
def listar_minhas_candidaturas(
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_usuario_db)
):
    return db.query(Candidatura).filter(Candidatura.id_usuario == usuario.id_usuario).all()