import json

from playwright.sync_api import expect


def preparar(page, candidaturas=None, status=200):
    page.add_init_script("localStorage.setItem('access_token', 'token-teste')")

    def responder(route):
        request = route.request
        headers = {'Access-Control-Allow-Origin': '*', 'Access-Control-Allow-Headers': '*',
                   'Access-Control-Allow-Methods': 'GET, OPTIONS'}
        if request.method == 'OPTIONS':
            route.fulfill(status=204, headers=headers)
            return
        codigo = 200
        if request.url.endswith('/auth/perfil'):
            dados = {'nome': 'Candidata Teste', 'tipo_usuario': 'usuario'}
        elif request.url.endswith('/candidatura/minhas'):
            assert request.headers['authorization'] == 'Bearer token-teste'
            dados = candidaturas if candidaturas is not None else []
            codigo = status
        else:
            dados = {'id_vaga': 2, 'titulo': 'Estágio React', 'cidade': 'Bauru'}
        route.fulfill(status=codigo, headers=headers, content_type='application/json',
                      body=json.dumps(dados))

    page.route('http://localhost:8000/**', responder)
    page.goto('http://localhost:5173/perfil?aba=candidaturas')


def test_candidaturas_listadas_no_perfil(page):
    preparar(page, [{'id_candidatura': 5, 'id_vaga': 2, 'status_candidatura': 'enviada'}])
    expect(page.get_by_role('heading', name='Estágio React')).to_be_visible()
    expect(page.get_by_text('Enviada', exact=True)).to_be_visible()
    expect(page.get_by_role('link', name='Ver vaga')).to_have_attribute('href', '/vaga/2')
    page.reload()
    expect(page.get_by_role('heading', name='Estágio React')).to_be_visible()


def test_sem_candidaturas(page):
    preparar(page)
    expect(page.get_by_text('Você ainda não se candidatou a nenhuma vaga.')).to_be_visible()
    expect(page.get_by_role('link', name='Encontrar vagas')).to_be_visible()


def test_erro_na_listagem(page):
    preparar(page, status=500)
    expect(page.get_by_role('alert')).to_contain_text('Não foi possível carregar suas candidaturas.')
    expect(page.get_by_role('button', name='Tentar novamente')).to_be_visible()
