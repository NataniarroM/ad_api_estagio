
from playwright.sync_api import Page, expect

URL = "http://localhost:5173/perfil"


def test_exibir_perfil(page: Page):
    page.goto(URL)

    expect(
        page.get_by_role("heading", name="Mariana Silva")
    ).to_be_visible()

    expect(
        page.get_by_text("mariana.silva@email.com")
    ).to_be_visible()


def test_abrir_edicao_perfil(page: Page):
    page.goto(URL)

    page.get_by_role(
        "button", name="Editar Perfil"
    ).click()

    expect(
        page.locator(".formulario-edicao input")
    ).to_have_count(4)


def test_cancelar_edicao_perfil(page: Page):
    page.goto(URL)

    page.get_by_role(
        "button", name="Editar Perfil"
    ).click()

    page.get_by_role(
        "button", name="Cancelar"
    ).click()

    expect(
        page.locator(".formulario-edicao")
    ).to_have_count(0)


def test_salvar_perfil(page: Page):
    page.goto(URL)

    page.get_by_role(
        "button", name="Editar Perfil"
    ).click()

    page.locator(
        ".formulario-edicao input"
    ).nth(0).fill("Usuario Teste")

    page.get_by_role(
        "button", name="Guardar Alterações"
    ).click()

    expect(
        page.get_by_role("heading", name="Usuario Teste")
    ).to_be_visible()

    expect(
        page.get_by_text("Perfil atualizado com sucesso!")
    ).to_be_visible()
