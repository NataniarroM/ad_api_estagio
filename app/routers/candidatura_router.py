from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import List

from app.database import get_db
from app.models import Candidatura
from app.schemas import CandidaturaCreate, CandidaturaResponse

router = APIRouter(prefix="/candidaturas", tags=["Candidaturas"])

@router.post("/", response_model=CandidaturaResponse, status_code=status.HTTP_201_CREATED)
def criar_candidatura(candidatura: CandidaturaCreate, db: Session = Depends(get_db)):
    nova = Candidatura(**candidatura.model_dump())
    db.add(nova)
    try:
        db.commit()
        db.refresh(nova)
        return nova
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Usuário já candidatado nesta vaga ou dados inválidos."
        )

@router.get("/usuario/{id_usuario}", response_model=List[CandidaturaResponse])
def listar_candidaturas_usuario(id_usuario: int, db: Session = Depends(get_db)):
    return db.query(Candidatura).filter(Candidatura.id_usuario == id_usuario).all()