from pydantic import BaseModel, Field
from typing import Optional
from datetime import date
from decimal import Decimal

# --- SCHEMAS DE EMPRESA ---
class EmpresaCreate(BaseModel):
    id_usuario: int
    razao_social: str = Field(..., max_length=150)
    nome_fantasia: str = Field(..., max_length=150)
    cnpj: str = Field(..., max_length=18)
    cidade: str = Field(..., max_length=100)
    site: Optional[str] = None

class EmpresaResponse(EmpresaCreate):
    id_empresa: int

    class Config:
        from_attributes = True


# --- SCHEMAS DE VAGA ---
class VagaCreate(BaseModel):
    id_empresa: int
    titulo: str = Field(..., max_length=150)
    descricao: str
    requisitos: Optional[str] = None
    modalidade: str = Field(..., pattern="^(presencial|hibrida|remota)$")
    bolsa: Optional[Decimal] = Field(None, ge=0)
    carga_horaria: int = Field(..., gt=0)
    cidade: str = Field(..., max_length=100)
    data_publicacao: date
    data_limite: date

class VagaUpdate(BaseModel):
    titulo: Optional[str] = None
    descricao: Optional[str] = None
    requisitos: Optional[str] = None
    modalidade: Optional[str] = None
    bolsa: Optional[Decimal] = None
    carga_horaria: Optional[int] = None
    cidade: Optional[str] = None
    data_limite: Optional[date] = None
    status: Optional[str] = None

class VagaResponse(VagaCreate):
    id_vaga: int
    status: str

    class Config:
        from_attributes = True


# --- SCHEMAS DE CANDIDATURA ---
class CandidaturaCreate(BaseModel):
    id_usuario: int
    id_vaga: int
    curriculo_url: Optional[str] = None

class CandidaturaResponse(CandidaturaCreate):
    id_candidatura: int
    status: str

    class Config:
        from_attributes = True