
from playwright.sync_api import Page, expect

URL = "http://localhost:5173/login"


def test_exibir_login(page: Page):
    page.goto(URL)

    expect(
        page.get_by_role(
            "heading",
            name="Bem-vindo de volta!"
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
   
    page.route(
        "http://127.0.0.1:8000/api/login",
        lambda route: route.fulfill(
            status=200,
            content_type="application/json",
            body='{}'
        )
    )

    page.goto(URL)

    page.get_by_placeholder("seu@email.com").fill(
        "teste@exemplo.com"
    )

    page.get_by_placeholder("Sua senha").fill(
        "123456"
    )

    page.locator("form").get_by_role(
        "button", name="Entrar"
    ).click()

    expect(
        page.get_by_text("Login efetuado com sucesso!")
    ).to_be_visible()


def test_login_incorreto(page: Page):
    
    page.route(
        "http://127.0.0.1:8000/api/login",
        lambda route: route.fulfill(
            status=401,
            content_type="application/json",
            body='{"detail":"E-mail ou senha incorretos."}'
        )
    )

    page.goto(URL)

    page.get_by_placeholder("seu@email.com").fill(
        "teste@exemplo.com"
    )

    page.get_by_placeholder("Sua senha").fill(
        "senhaerrada"
    )

    page.locator("form").get_by_role(
        "button", name="Entrar"
    ).click()

    expect(
        page.get_by_text("E-mail ou senha incorretos.")
    ).to_be_visible()
