from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest
from fastapi import HTTPException

from app.routers.empresas_router import criar_empresa
from app.routers.vagas_router import deletar_vaga
from app.schemas import EmpresaCreate
from pydantic import ValidationError


@pytest.mark.parametrize('tipo', ['recrutador', 'administrador'])
def test_cadastrar_empresa_apenas_com_nome(tipo):
    db = MagicMock()
    dados = EmpresaCreate(nome_fantasia='Minha empresa')
    empresa = criar_empresa(dados, db, SimpleNamespace(id_usuario=42, tipo_usuario=tipo))
    assert empresa.nome_fantasia == 'Minha empresa'
    assert empresa.cnpj is None
    assert empresa.cidade is None
    assert empresa.razao_social is None
    db.commit.assert_called_once()


@pytest.mark.parametrize('nome', ['', '   '])
def test_empresa_exige_nome_preenchido(nome):
    with pytest.raises(ValidationError):
        EmpresaCreate(nome_fantasia=nome)


@pytest.mark.parametrize('tipo', ['recrutador', 'administrador'])
def test_criar_empresa_vincula_a_conta_autorizada(tipo):
    db = MagicMock()
    dados = EmpresaCreate(razao_social='Empresa LTDA', nome_fantasia='Empresa',
                          cnpj='12.345.678/0001-90', cidade='Bauru')
    empresa = criar_empresa(dados, db, SimpleNamespace(id_usuario=42, tipo_usuario=tipo))
    assert empresa.id_usuario == 42
    assert empresa.cnpj == dados.cnpj
    db.add.assert_called_once_with(empresa)
    db.commit.assert_called_once()


def test_estudante_nao_cadastra_empresa():
    db = MagicMock()
    dados = EmpresaCreate(razao_social='Empresa LTDA', nome_fantasia='Empresa',
                          cnpj='12.345.678/0001-90', cidade='Bauru')
    with pytest.raises(HTTPException) as erro:
        criar_empresa(dados, db, SimpleNamespace(id_usuario=42, tipo_usuario='usuario'))
    assert erro.value.status_code == 403
    db.add.assert_not_called()


@pytest.mark.parametrize('tipo', ['recrutador', 'usuario'])
def test_exclusao_de_vaga_negada_para_nao_administrador(tipo):
    db = MagicMock()
    db.query.return_value.filter.return_value.first.return_value = SimpleNamespace(id_vaga=1)
    with pytest.raises(HTTPException) as erro:
        deletar_vaga(1, db, SimpleNamespace(id_usuario=42, tipo_usuario=tipo))
    assert erro.value.status_code == 403
    db.delete.assert_not_called()
    db.commit.assert_not_called()


def test_administrador_pode_excluir_vaga():
    db = MagicMock()
    vaga = SimpleNamespace(id_vaga=1)
    db.query.return_value.filter.return_value.first.return_value = vaga
    deletar_vaga(1, db, SimpleNamespace(id_usuario=42, tipo_usuario='administrador'))
    db.delete.assert_called_once_with(vaga)
    db.commit.assert_called_once()
