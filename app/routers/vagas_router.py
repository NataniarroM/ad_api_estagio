from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from sqlalchemy.exc import IntegrityError

from app.database import get_db
from app.models import Vaga
from app.schemas import VagaCreate, VagaUpdate, VagaResponse

router = APIRouter(prefix="/vagas", tags=["Vagas"])

@router.post("/", response_model=VagaResponse, status_code=status.HTTP_201_CREATED)
def criar_vaga(vaga: VagaCreate, db: Session = Depends(get_db)):
    nova_vaga = Vaga(**vaga.model_dump())
    db.add(nova_vaga)
    try:
        db.commit()
        db.refresh(nova_vaga)
        return nova_vaga
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Não foi possível criar a vaga. Verifique se o id_empresa existe e se data_limite >= data_publicacao.")

@router.get("/", response_model=List[VagaResponse])
def listar_vagas(db: Session = Depends(get_db)):
    return db.query(Vaga).all()

@router.get("/{id_vaga}", response_model=VagaResponse)
def buscar_vaga(id_vaga: int, db: Session = Depends(get_db)):
    vaga = db.query(Vaga).filter(Vaga.id_vaga == id_vaga).first()
    if not vaga:
        raise HTTPException(status_code=404, detail="Vaga não encontrada.")
    return vaga

@router.put("/{id_vaga}", response_model=VagaResponse)
def atualizar_vaga(id_vaga: int, dados: VagaUpdate, db: Session = Depends(get_db)):
    vaga = db.query(Vaga).filter(Vaga.id_vaga == id_vaga).first()
    if not vaga:
        raise HTTPException(status_code=404, detail="Vaga não encontrada.")
    
    for campo, valor in dados.model_dump(exclude_unset=True).items():
        setattr(vaga, campo, valor)
        
    db.commit()
    db.refresh(vaga)
    return vaga

@router.delete("/{id_vaga}", status_code=status.HTTP_204_NO_CONTENT)
def deletar_vaga(id_vaga: int, db: Session = Depends(get_db)):
    vaga = db.query(Vaga).filter(Vaga.id_vaga == id_vaga).first()
    if not vaga:
        raise HTTPException(status_code=404, detail="Vaga não encontrada.")
    
    db.delete(vaga)
    db.commit()