
import json
import pytest
from playwright.sync_api import Page, expect

BASE = "http://localhost:5173"


def simular_vagas(page):
    page.route(
        "http://127.0.0.1:8000/api/vagas",
        lambda route: route.fulfill(
            status=200,
            content_type="application/json",
            headers={"Access-Control-Allow-Origin": "*"},
            body=json.dumps([])
        )
    )


def verificar_sem_rolagem_horizontal(page, largura):
    medidas = page.evaluate("""() => ({
        tela: window.innerWidth,
        documento: document.documentElement.scrollWidth
    })""")

    assert medidas["documento"] <= medidas["tela"] + 1, (
        f"Layout ultrapassou a tela de {largura}px: "
        f"documento com {medidas['documento']}px"
    )


# Testes 1, 2 e 3: home em três resoluções
@pytest.mark.parametrize(
    "largura,altura",
    [
        (1440, 900),
        (1280, 800),
        (1024, 768),
    ]
)
def test_home_responsiva(page: Page, largura, altura):
    page.set_viewport_size({
        "width": largura,
        "height": altura
    })

    simular_vagas(page)
    page.goto(BASE)

    expect(
        page.get_by_role(
            "heading", name="Encontre seu próximo estágio"
        )
    ).to_be_visible()

    expect(
        page.locator(".badge-contador")
    ).to_have_text("0 vagas")

    verificar_sem_rolagem_horizontal(page, largura)


# Teste 4: login em tela menor de desktop
def test_login_responsivo(page: Page):
    largura = 1024
    page.set_viewport_size({
        "width": largura,
        "height": 768
    })

    page.goto(f"{BASE}/login")

    expect(
        page.get_by_placeholder("seu@email.com")
    ).to_be_visible()

    expect(
        page.get_by_placeholder("Sua senha")
    ).to_be_visible()

    verificar_sem_rolagem_horizontal(page, largura)


# Teste 5: cadastro em tela menor de desktop
def test_cadastro_responsivo(page: Page):
    largura = 1024
    page.set_viewport_size({
        "width": largura,
        "height": 768
    })

    page.goto(f"{BASE}/cadastro")

    expect(
        page.get_by_role("heading", name="Crie a sua conta")
    ).to_be_visible()

    expect(
        page.locator('select[name="id_curso"]')
    ).to_be_visible()

    verificar_sem_rolagem_horizontal(page, largura)
