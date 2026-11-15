
import json
from playwright.sync_api import Page, expect

BASE = "http://localhost:5173"
API = "http://127.0.0.1:8000/api/vagas"


def simular_vagas(page):
    vagas = [
        {
            "id_vaga": 101,
            "titulo": "Estágio em React",
            "empresa": "Empresa Teste",
            "descricao": "Desenvolvimento web",
            "local": "Bauru, SP"
        },
        {
            "id_vaga": 102,
            "titulo": "Estágio em Design",
            "empresa": "Empresa Exemplo",
            "descricao": "Criação de interfaces",
            "local": "São Paulo, SP"
        }
    ]

    page.route(
        API,
        lambda route: route.fulfill(
            status=200,
            content_type="application/json",
            headers={"Access-Control-Allow-Origin": "*"},
            body=json.dumps(vagas)
        )
    )


# Teste 1: navegar entre os links com Tab
def test_navegacao_com_tab(page: Page):
    simular_vagas(page)
    page.goto(BASE)

    page.locator(".area-logo-link").focus()
    page.keyboard.press("Tab")

    expect(
        page.locator("header .botao-primario")
    ).to_be_focused()

    page.keyboard.press("Tab")

    expect(
        page.locator("header .botao-secundario")
    ).to_be_focused()


# Teste 2: navegar pelos campos de login com Tab
def test_login_navegacao_teclado(page: Page):
    page.goto(f"{BASE}/login")

    email = page.get_by_placeholder("seu@email.com")
    senha = page.get_by_placeholder("Sua senha")

    email.focus()
    page.keyboard.press("Tab")

    expect(senha).to_be_focused()


# Teste 3: pesquisar pressionando Enter
def test_busca_com_enter(page: Page):
    simular_vagas(page)
    page.goto(BASE)

    expect(
        page.locator(".card-vaga-link")
    ).to_have_count(2)

    campo = page.get_by_placeholder(
        "Cargo, empresa ou palavra-chave"
    )

    campo.fill("Design")
    campo.press("Enter")

    expect(
        page.locator(".card-vaga-link")
    ).to_have_count(1)

    expect(
        page.locator(".badge-contador")
    ).to_have_text("1 vagas")


# Teste 4: abrir login usando Enter
def test_abrir_login_pelo_teclado(page: Page):
    simular_vagas(page)
    page.goto(BASE)

    entrar = page.locator("header .botao-secundario")

    entrar.focus()
    page.keyboard.press("Enter")

    expect(page).to_have_url(f"{BASE}/login")
