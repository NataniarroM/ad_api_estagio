
import json
from playwright.sync_api import Page, expect

URL = "http://localhost:5173/"
API = "http://127.0.0.1:8000/api/vagas"

VAGAS = [
    {
        "id_vaga": 101,
        "titulo": "Estágio em React",
        "empresa": "Empresa Teste",
        "descricao": "Desenvolvimento de interfaces web.",
        "local": "Bauru, SP",
        "salario": "R$ 1.500",
        "postado": "Hoje",
        "tags": ["React", "JavaScript"]
    },
    {
        "id_vaga": 102,
        "titulo": "Estágio em Design",
        "empresa": "Empresa Exemplo",
        "descricao": "Criação de interfaces digitais.",
        "local": "São Paulo, SP",
        "salario": "R$ 1.200",
        "postado": "Ontem",
        "tags": ["Figma", "UI/UX"]
    }
]


def simular_vagas(page, vagas=None):
    if vagas is None:
        vagas = VAGAS

    def responder(route):
        route.fulfill(
            status=200,
            content_type="application/json",
            headers={
                "Access-Control-Allow-Origin": "*"
            },
            body=json.dumps(vagas)
        )

    page.route(API, responder)


def test_exibir_vagas_na_home(page: Page):
    simular_vagas(page)
    page.goto(URL)

    expect(
        page.get_by_role("heading", name="Estágio em React")
    ).to_be_visible()

    expect(
        page.get_by_role("heading", name="Estágio em Design")
    ).to_be_visible()

    expect(
        page.locator(".card-vaga-link")
    ).to_have_count(2)


def test_contador_de_vagas(page: Page):
    simular_vagas(page)
    page.goto(URL)

    expect(
        page.locator(".badge-contador")
    ).to_have_text("2 vagas")


def test_lista_de_vagas_vazia(page: Page):
    simular_vagas(page, [])
    page.goto(URL)

    expect(
        page.locator(".badge-contador")
    ).to_have_text("0 vagas")

    expect(
        page.locator(".card-vaga-link")
    ).to_have_count(0)


def test_abrir_detalhes_da_vaga(page: Page):
    simular_vagas(page)

    page.route(
        f"{API}/101",
        lambda route: route.fulfill(
            status=200,
            content_type="application/json",
            headers={"Access-Control-Allow-Origin": "*"},
            body=json.dumps(VAGAS[0])
        )
    )

    page.goto(URL)

    page.locator(".card-vaga-link").first.click()

    expect(page).to_have_url(
        "http://localhost:5173/vaga/101"
    )

    expect(
        page.get_by_role("heading", name="Estágio em React")
    ).to_be_visible()


def test_favoritar_vaga(page: Page):
    simular_vagas(page)
    page.goto(URL)

    cartao = page.locator(".card-vaga-link").first

    cartao.locator(
        'button[title="Salvar nos favoritos"]'
    ).click()

    expect(
        cartao.locator(
            'button[title="Remover dos favoritos"]'
        )
    ).to_be_visible()

    favoritos = page.evaluate(
        "JSON.parse(localStorage.getItem('vagasFavoritas'))"
    )

    assert len(favoritos) == 1
    assert favoritos[0]["id_vaga"] == 101


def test_desfavoritar_vaga(page: Page):
    simular_vagas(page)
    page.goto(URL)

    cartao = page.locator(".card-vaga-link").first

    cartao.locator(
        'button[title="Salvar nos favoritos"]'
    ).click()

    cartao.locator(
        'button[title="Remover dos favoritos"]'
    ).click()

    favoritos = page.evaluate(
        "JSON.parse(localStorage.getItem('vagasFavoritas'))"
    )

    assert favoritos == []


def test_navegar_para_favoritos(page: Page):
    simular_vagas(page)
    page.goto(URL)

    page.locator(
        'button[title="Ver Favoritos"]'
    ).click()

    expect(page).to_have_url(
        "http://localhost:5173/favoritos"
    )

    expect(
        page.get_by_role(
            "heading", name="Minhas Vagas Favoritas"
        )
    ).to_be_visible()


def test_navegar_para_perfil(page: Page):
    simular_vagas(page)
    page.goto(URL)

    page.locator(
        'button[title="Ver Perfil"]'
    ).click()

    expect(page).to_have_url(
        "http://localhost:5173/perfil"
    )

    expect(
        page.get_by_role("heading", name="Mariana Silva")
    ).to_be_visible()

