from sqlalchemy import Column, Integer, String, ForeignKey, SmallInteger, Boolean, DateTime, Text, Numeric, Date
from sqlalchemy.sql import func

from app.database import Base

# Modelos gerais usados para obter as informações do banco e armazená-los em cada sessão

class Usuario(Base):

    __tablename__ = "usuario"

    id_usuario = Column(Integer, primary_key=True, index=True)
    id_curso = Column(Integer,
                      ForeignKey("curso.id_curso", ondelete="SET NULL"),
                      nullable=True)
    firebase_uid = Column(String(128), unique=True, nullable=False)

    nome = Column(String(150), nullable=False)
    email = Column(String(150), nullable=False, unique=True)
    senha_hash = Column(String(255), nullable=False)
    tipo_usuario = Column(String(20), nullable=False)
    telefone = Column(String(20))
    semestre = Column(SmallInteger) # Revisado por IA
    aluno = Column(Boolean, nullable=False, default=False)
    situacao_curso = Column(String(20))
    eh_entrevistador = Column(Boolean, nullable=False, default=False)
    criado_em = Column(DateTime, nullable=False, server_default=func.now()) # Gerado por IA


class Empresa(Base):

    __tablename__ = "empresa"

    id_empresa = Column(Integer, primary_key=True, index=True)
    id_usuario = Column(Integer,
                        ForeignKey("usuario.id_usuario", ondelete="RESTRICT"),
                        nullable=False, unique=True)
    
    razao_social = Column(String(150), nullable=False)
    nome_fantasia = Column(String(150, nullable=False))
    cnpj = Column(String(18), nullable=False, unique=True)
    cidade = Column(String(100), nullable=False)
    site = Column(String(255))


class Vaga(Base):

    __tablename__ = "vaga"

    id_vaga = Column(Integer, primary_key=True, index=True)
    id_empresa = Column(Integer,
                        ForeignKey("empresa.id_empresa", ondelete="RESTRICT"),
                        nullable=False, unique=True)

    titulo = Column(String(150), nullable=False)
    descricao = Column(Text, nullable=False)
    requisitos = Column(Text)
    modalidade = Column(String(20), nullable=False)
    bolsa = Column(Numeric(10, 2))
    carga_horaria = Column(SmallInteger, nullable=False)
    cidade = Column(String(100), nullable=False)
    data_publicacao = Column(Date, nullable=False)
    data_limite = Column(Date, nullable=False)
    status = Column(String(20), nullable=False, default="publicada")
    criado_em = Column(DateTime, nullable=False, server_default=func.now()) # Gerado por IA

class Candidatura(Base):

    __tablename__ = "candidaturas"

    id_candidatura = Column(Integer, primary_key=True, index=True)
    vaga_id = Column(Integer,
                     ForeignKey("vaga.id_vaga", ondelete="CASCADE"),
                     nullable=False)
    usuario_id = Column(Integer,
                        ForeignKey("usuario.id_usuario", ondelete="CASCADE"),
                        nullable=False)

    data_da_candidatura = Column(DateTime, nullable=False, server_default=func.now()) # Gerado por IA
    status = Column(String(20), nullable=False, default="enviada")
    curriculo_url = Column(String(500))


class Curso(Base):

    __tablename__ = "curso"

    id_curso = Column(Integer, primary_key=True, index=True)
    nome = Column(String(150), nullable=False)
    nivel = Column(String(20), nullable=False)
    ativo = Column(Boolean, nullable=False, default=True)