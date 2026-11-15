from pydantic import BaseModel, ConfigDict, Field
from typing import Optional
from datetime import date
from decimal import Decimal

# --- SCHEMAS DE EMPRESA ---
class EmpresaCreate(BaseModel):
    nome_fantasia: str = Field(..., min_length=1, max_length=150, pattern=r"\S")
    razao_social: Optional[str] = Field(None, max_length=150)
    cnpj: Optional[str] = Field(None, max_length=18)
    cidade: Optional[str] = Field(None, max_length=100)
    site: Optional[str] = None

class EmpresaResponse(EmpresaCreate):
    id_empresa: int
    id_usuario: int

    class Config:
        from_attributes = True


# --- SCHEMAS DE VAGA ---
class VagaCreate(BaseModel):
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
    status_vaga: Optional[str] = None

class VagaResponse(VagaCreate):
    id_vaga: int
    id_empresa: int
    status_vaga: str

    class Config:
        from_attributes = True


# --- SCHEMAS DE CANDIDATURA ---
class CandidaturaCreate(BaseModel):
    id_vaga: int
    curriculo_url: Optional[str] = None

class CandidaturaResponse(CandidaturaCreate):
    id_candidatura: int
    id_usuario: int
    status_candidatura: str

    class Config:
        from_attributes = True

#  SIX SEVENNNN

# --- SCHEMAS DE CURSO ---
# Os 3 níveis aceitos pelo banco (CHECK da tabela curso no schema.sql).

NIVEIS_CURSO = "^(tecnologo|bacharelado|licenciatura)$"

class CursoCreate(BaseModel):
    """Dados que o front envia para CRIAR um curso."""
    nome: str = Field(..., min_length=2, max_length=150)   # entre 2 e 150 letras
    nivel: str = Field(..., pattern=NIVEIS_CURSO)          # só tecnologo, bacharelado ou licenciatura
    ativo: bool = True                                     # se não vier, o curso nasce ativo

class CursoUpdate(BaseModel):
    """Dados para ATUALIZAR um curso. Todos opcionais: só muda o que for enviado."""
    nome: Optional[str] = Field(None, min_length=2, max_length=150)
    nivel: Optional[str] = Field(None, pattern=NIVEIS_CURSO)
    ativo: Optional[bool] = None

class CursoResponse(CursoCreate):
    """O que a API devolve: os mesmos campos do CursoCreate + o id gerado pelo banco."""
    id_curso: int

    # Permite montar a resposta direto a partir do objeto do banco (Curso).
    model_config = ConfigDict(from_attributes=True)
