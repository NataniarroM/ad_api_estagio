import json

import pytest
from playwright.sync_api import expect


def preparar(page, tipo='administrador', status_exclusao=204):
    chamadas = []
    page.add_init_script("localStorage.setItem('access_token', 'token-teste')")

    def responder(route):
        request = route.request
        headers = {'Access-Control-Allow-Origin': '*',
                   'Access-Control-Allow-Headers': '*',
                   'Access-Control-Allow-Methods': 'GET, DELETE, OPTIONS'}
        if request.method == 'OPTIONS':
            route.fulfill(status=204, headers=headers)
            return
        if request.method == 'DELETE':
            chamadas.append(request.url)
            dados = {'detail': 'Sem permissão'}
            route.fulfill(status=status_exclusao, headers=headers,
                          body='' if status_exclusao == 204 else json.dumps(dados),
                          content_type='application/json')
            return
        dados = ({'id_usuario': 42, 'tipo_usuario': tipo}
                 if request.url.endswith('/auth/perfil')
                 else {'id_vaga': 2, 'titulo': 'Vaga teste', 'descricao': 'Descrição'})
        route.fulfill(status=200, headers=headers, content_type='application/json',
                      body=json.dumps(dados))

    page.route('http://localhost:8000/**', responder)
    page.goto('http://localhost:5173/vaga/2')
    expect(page.get_by_role('heading', name='Vaga teste', exact=True)).to_be_visible()
    return chamadas


def test_admin_confirma_exclusao(page):
    chamadas = preparar(page)
    page.on('dialog', lambda dialog: dialog.accept())
    page.get_by_role('button', name='Excluir vaga', exact=True).click()
    expect(page).to_have_url('http://localhost:5173/')
    assert chamadas == ['http://localhost:8000/api/vagas/2']


def test_cancelar_nao_exclui(page):
    chamadas = preparar(page)
    page.on('dialog', lambda dialog: dialog.dismiss())
    page.get_by_role('button', name='Excluir vaga', exact=True).click()
    assert chamadas == []
    expect(page).to_have_url('http://localhost:5173/vaga/2')


def test_api_recusa_exclusao(page):
    preparar(page, status_exclusao=403)
    page.on('dialog', lambda dialog: dialog.accept())
    page.get_by_role('button', name='Excluir vaga', exact=True).click()
    expect(page.get_by_role('alert')).to_have_text('Sem permissão')
    expect(page).to_have_url('http://localhost:5173/vaga/2')


@pytest.mark.parametrize('tipo', ['recrutador', 'usuario'])
def test_outros_perfis_sem_exclusao(page, tipo):
    preparar(page, tipo)
    expect(page.get_by_role('button', name='Candidatar-me a esta vaga')).to_be_visible()
    expect(page.get_by_role('button', name='Excluir vaga', exact=True)).to_have_count(0)
