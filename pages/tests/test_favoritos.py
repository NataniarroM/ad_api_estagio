
import json
from playwright.sync_api import Page, expect

URL = "http://localhost:5173/favoritos"

VAGA = {
    "id_vaga": 123,
    "titulo": "Estágio em Desenvolvimento",
    "empresa": "Empresa Teste",
    "descricao": "Desenvolvimento de aplicações.",
    "salario": "R$ 1.500",
    "postado": "Hoje",
    "tags": ["React", "Frontend"]
}


def preparar_favoritos(page: Page):
    page.add_init_script(
        f"""localStorage.setItem(
            'vagasFavoritas',
            JSON.stringify([{json.dumps(VAGA)}])
        );"""
    )


def test_exibir_favoritos_vazios(page: Page):
    page.goto(URL)

    expect(
        page.get_by_role(
            "heading", name="Minhas Vagas Favoritas"
        )
    ).to_be_visible()

    expect(
        page.get_by_text(
            "Você ainda não favoritou nenhuma vaga."
        )
    ).to_be_visible()


def test_exibir_vaga_favorita(page: Page):
    preparar_favoritos(page)
    page.goto(URL)

    expect(
        page.get_by_role(
            "heading", name="Estágio em Desenvolvimento"
        )
    ).to_be_visible()


def test_remover_vaga_favorita(page: Page):
    preparar_favoritos(page)
    page.goto(URL)

    page.get_by_role(
        "button", name="Remover dos favoritos"
    ).click()

    expect(
        page.get_by_text(
            "Você ainda não favoritou nenhuma vaga."
        )
    ).to_be_visible()

    assert page.evaluate(
        "JSON.parse(localStorage.getItem('vagasFavoritas'))"
    ) == []


def test_voltar_para_vagas(page: Page):
    page.goto(URL)

    page.locator(".botao-voltar-favoritos").click()

    expect(page).to_have_url("http://localhost:5173/")
