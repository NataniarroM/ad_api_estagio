
from playwright.sync_api import Page, expect

URL = "http://localhost:5173/cadastro"


def test_exibir_cadastro(page: Page):
    page.goto(URL)

    expect(
        page.get_by_role(
            "heading",
            name="Crie a sua conta"
        )
    ).to_be_visible()

    expect(
        page.get_by_placeholder("Digite o seu nome")
    ).to_be_visible()

    expect(
        page.get_by_placeholder("exemplo@email.com")
    ).to_be_visible()

    expect(
        page.get_by_placeholder("Mínimo de 6 caracteres")
    ).to_be_visible()

    expect(
        page.get_by_placeholder("Repita a sua senha")
    ).to_be_visible()


def test_cadastro_campos_obrigatorios(page: Page):
    page.goto(URL)

    page.get_by_role(
        "button", name="Cadastrar", exact=True
    ).click()

    expect(
        page.locator("form input:invalid")
    ).to_have_count(4)


def test_cadastro_senhas_diferentes(page: Page):
    page.goto(URL)

    page.get_by_placeholder("Digite o seu nome").fill(
        "Usuario Teste"
    )

    page.get_by_placeholder("exemplo@email.com").fill(
        "teste@exemplo.com"
    )

    page.get_by_placeholder("Mínimo de 6 caracteres").fill(
        "123456"
    )

    page.get_by_placeholder("Repita a sua senha").fill(
        "654321"
    )

    page.get_by_role(
        "button", name="Cadastrar", exact=True
    ).click()

    expect(
        page.get_by_text("As senhas não coincidem.")
    ).to_be_visible()


def test_selecionar_tipo_conta(page: Page):
    page.goto(URL)

    usuario = page.get_by_role(
        "button", name="Usuário", exact=True
    )
    recrutador = page.get_by_role(
        "button", name="Recrutador", exact=True
    )
    administrador = page.get_by_role(
        "button", name="Administrador", exact=True
    )

    expect(usuario).to_have_class(
        "botao-tipo ativo"
    )

    recrutador.click()
    expect(recrutador).to_have_class(
        "botao-tipo ativo"
    )

    administrador.click()
    expect(administrador).to_have_class(
        "botao-tipo ativo"
    )


def test_cadastro_com_sucesso(page: Page):

    page.route(
        "http://127.0.0.1:8000/auth/cadastro",
        lambda route: route.fulfill(
            status=200,
            content_type="application/json",
            body='{}'
        )
    )

    page.goto(URL)

    page.get_by_placeholder("Digite o seu nome").fill(
        "Usuario Teste"
    )

    page.get_by_placeholder("exemplo@email.com").fill(
        "teste@exemplo.com"
    )

    page.get_by_placeholder("Mínimo de 6 caracteres").fill(
        "123456"
    )

    page.get_by_placeholder("Repita a sua senha").fill(
        "123456"
    )

    page.get_by_role(
        "button", name="Cadastrar", exact=True
    ).click()

    expect(
        page.get_by_text("Conta criada com sucesso!")
    ).to_be_visible()
