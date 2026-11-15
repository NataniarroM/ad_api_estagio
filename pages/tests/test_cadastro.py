
import json
from playwright.sync_api import Page, expect

URL = "http://localhost:5173/cadastro"


def simular_cursos(page):
    def responder(route):
        if route.request.method == "OPTIONS":
            route.fulfill(
                status=204,
                headers={
                    "Access-Control-Allow-Origin": "*",
                    "Access-Control-Allow-Methods": "GET, OPTIONS",
                    "Access-Control-Allow-Headers": "*",
                }
            )
        else:
            route.fulfill(
                status=200,
                content_type="application/json",
                headers={"Access-Control-Allow-Origin": "*"},
                body=json.dumps([
                    {"id_curso": 1, "nome": "Administração"}
                ])
            )

    page.route("**/api/cursos", responder)


def preencher_cadastro(page, confirmar="123456"):
    campos = {
        "Digite o seu nome": "Usuario Teste",
        "exemplo@email.com": "teste@exemplo.com",
        "Mínimo de 6 caracteres": "123456",
        "Repita a sua senha": confirmar,
        "Ex: 11988888888": "11988888888",
        "Ex: 3": "3",
    }

    for placeholder, valor in campos.items():
        page.get_by_placeholder(placeholder).fill(valor)

    page.locator('select[name="id_curso"]').select_option("1")


def test_exibir_cadastro(page: Page):
    page.goto(URL)

    expect(
        page.get_by_role("heading", name="Crie a sua conta")
    ).to_be_visible()

    expect(page.locator("form input")).to_have_count(6)
    expect(page.locator("form select")).to_have_count(1)


def test_cadastro_campos_obrigatorios(page: Page):
    page.goto(URL)

    page.get_by_role(
        "button", name="Cadastrar", exact=True
    ).click()

    expect(
        page.locator("form input:invalid")
    ).to_have_count(6)

    expect(
        page.locator("form select:invalid")
    ).to_have_count(1)


def test_cadastro_senhas_diferentes(page: Page):
    simular_cursos(page)
    page.goto(URL)

    preencher_cadastro(page, confirmar="654321")

    page.get_by_role(
        "button", name="Cadastrar", exact=True
    ).click()

    expect(
        page.get_by_text("As senhas não coincidem.")
    ).to_be_visible()


def test_selecionar_tipo_conta(page: Page):
    page.goto(URL)

    usuario = page.get_by_role(
        "button", name="Usuario", exact=True
    )
    recrutador = page.get_by_role(
        "button", name="Recrutador", exact=True
    )
    administrador = page.get_by_role(
        "button", name="Administrador", exact=True
    )

    expect(usuario).to_have_class("botao-tipo ativo")

    recrutador.click()
    expect(recrutador).to_have_class("botao-tipo ativo")

    administrador.click()
    expect(administrador).to_have_class("botao-tipo ativo")


def test_cadastro_com_sucesso(page: Page):
    simular_cursos(page)

    def responder_cadastro(route):
        headers = {
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "POST, OPTIONS",
            "Access-Control-Allow-Headers": "*",
        }

        if route.request.method == "OPTIONS":
            route.fulfill(status=204, headers=headers)
        else:
            route.fulfill(
                status=200,
                content_type="application/json",
                headers=headers,
                body="{}"
            )

    page.route(
        "http://127.0.0.1:8000/auth/cadastro",
        responder_cadastro
    )

    page.goto(URL)
    preencher_cadastro(page)

    page.get_by_role(
        "button", name="Cadastrar", exact=True
    ).click()

    expect(
        page.get_by_text("Conta criada com sucesso!")
    ).to_be_visible()
