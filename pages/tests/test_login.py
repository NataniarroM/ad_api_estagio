
import json
from playwright.sync_api import Page, expect

URL = "http://localhost:5173/login"


def simular_resposta(page, url, status, dados):
    def responder(route):
        headers = {
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
            "Access-Control-Allow-Headers": "*",
        }

        if route.request.method == "OPTIONS":
            route.fulfill(status=204, headers=headers)
        else:
            route.fulfill(
                status=status,
                content_type="application/json",
                headers=headers,
                body=json.dumps(dados)
            )

    page.route(url, responder)


def preencher_login(page, senha="123456"):
    page.get_by_placeholder("seu@email.com").fill(
        "teste@exemplo.com"
    )
    page.get_by_placeholder("Sua senha").fill(senha)


def test_exibir_login(page: Page):
    page.goto(URL)

    expect(
        page.get_by_role(
            "heading", name="Bem-vindo de volta!"
        )
    ).to_be_visible()

    expect(
        page.get_by_placeholder("seu@email.com")
    ).to_be_visible()

    expect(
        page.get_by_placeholder("Sua senha")
    ).to_be_visible()


def test_login_campos_obrigatorios(page: Page):
    page.goto(URL)

    page.locator("form").get_by_role(
        "button", name="Entrar"
    ).click()

    expect(
        page.locator("form input:invalid")
    ).to_have_count(2)


def test_login_com_sucesso(page: Page):
    simular_resposta(
        page,
        "http://localhost:8080/auth/login",
        200,
        {"access_token": "token-teste"}
    )

    simular_resposta(
        page,
        "http://localhost:8080/api/perfil",
        200,
        {"tipo": "usuario"}
    )

    page.goto(URL)
    preencher_login(page)

    page.locator("form").get_by_role(
        "button", name="Entrar"
    ).click()

    expect(page).to_have_url("http://localhost:5173/")

    assert page.evaluate(
        "localStorage.getItem('access_token')"
    ) == "token-teste"


def test_login_incorreto(page: Page):
    simular_resposta(
        page,
        "http://localhost:8080/auth/login",
        401,
        {"detail": "E-mail ou senha incorretos."}
    )

    page.goto(URL)
    preencher_login(page, senha="senhaerrada")

    page.locator("form").get_by_role(
        "button", name="Entrar"
    ).click()

    expect(
        page.get_by_text("E-mail ou senha incorretos.")
    ).to_be_visible()
