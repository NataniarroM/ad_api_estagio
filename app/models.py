from sqlalchemy import Column, Integer, String, ForeignKey

from app.database import Base

# Modelos gerais usados para obter as informações do banco e armazená-los em cada sessão

class Usuario(Base):

    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True)
    nome = Column(String(100))

class Vaga(Base):

    __tablename__ = "vagas"

    id = Column(Integer, primary_key=True)
    nome = Column(String(100))

class Candidatura(Base):

    __tablename__ = "candidaturas"

    id = Column(Integer, primary_key=True)
    vaga_id = Column(Integer, ForeignKey("vagas.id"), nullable=False)
    usuario_id = Column(Integer, ForeignKey("usuario.id"), nullable=False)