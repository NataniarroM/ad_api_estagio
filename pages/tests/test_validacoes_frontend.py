
import json
from playwright.sync_api import Page, expect

BASE = "http://localhost:5173"
API = "http://127.0.0.1:8000"


def simular_cursos(page, cursos):
    page.route(
        f"{API}/api/cursos",
        lambda route: route.fulfill(
            status=200,
            content_type="application/json",
            headers={"Access-Control-Allow-Origin": "*"},
            body=json.dumps(cursos)
        )
    )


def preencher_cadastro(page, confirmar_senha="123456"):
    campos = {
        "Digite o seu nome": "Usuario Teste",
        "exemplo@email.com": "teste@exemplo.com",
        "Mínimo de 6 caracteres": "123456",
        "Repita a sua senha": confirmar_senha,
        "Ex: 11988888888": "11988888888",
        "Ex: 3": "3",
    }

    for campo, valor in campos.items():
        page.get_by_placeholder(campo).fill(valor)


# 1. Não permitir login com e-mail inválido
def test_login_email_invalido(page: Page):
    envios = []

    def verificar_login(route):
        envios.append(route.request.url)
        route.fulfill(
            status=200,
            content_type="application/json",
            body="{}"
        )

    page.route(
        "http://localhost:8080/auth/login",
        verificar_login
    )

    page.goto(f"{BASE}/login")

    page.get_by_placeholder("seu@email.com").fill(
        "email-invalido"
    )
    page.get_by_placeholder("Sua senha").fill("123456")

    page.locator("form").get_by_role(
        "button", name="Entrar"
    ).click()

    expect(
        page.locator('input[type="email"]:invalid')
    ).to_have_count(1)

    assert envios == []


# 2. Senhas diferentes não devem enviar cadastro
def test_senhas_diferentes_nao_enviam_cadastro(page: Page):
    simular_cursos(
        page,
        [{"id": 1, "nome": "Administração"}]
    )

    envios = []

    def verificar_cadastro(route):
        envios.append(route.request.post_data)
        route.fulfill(
            status=201,
            content_type="application/json",
            body="{}"
        )

    page.route(
        f"{API}/auth/cadastro",
        verificar_cadastro
    )

    page.goto(f"{BASE}/cadastro")

    expect(
        page.locator('select[name="id_curso"] option[value="1"]')
    ).to_have_count(1)

    preencher_cadastro(page, confirmar_senha="654321")
    page.locator('select[name="id_curso"]').select_option("1")

    page.get_by_role(
        "button", name="Cadastrar", exact=True
    ).click()

    expect(
        page.get_by_text("As senhas não coincidem.")
    ).to_be_visible()

    assert envios == []


# 3. Impedir envio quando não há curso selecionado
def test_cadastro_sem_curso(page: Page):
    simular_cursos(page, [])

    envios = []

    def verificar_cadastro(route):
        envios.append(route.request.post_data)
        route.fulfill(status=201, body="{}")

    page.route(
        f"{API}/auth/cadastro",
        verificar_cadastro
    )

    page.goto(f"{BASE}/cadastro")
    preencher_cadastro(page)

    page.get_by_role(
        "button", name="Cadastrar", exact=True
    ).click()

    expect(
        page.locator('select[name="id_curso"]:invalid')
    ).to_have_count(1)

    assert envios == []


# 4. Navegação entre login e cadastro

def test_navegacao_login_cadastro(page: Page):
    simular_cursos(page, [])

    page.goto(f"{BASE}/login")

    page.get_by_role(
        "link", name="Cadastre-se"
    ).click()

    expect(page).to_have_url(f"{BASE}/cadastro")

    page.locator("main").get_by_role(
        "link", name="Entrar", exact=True
    ).click()

    expect(page).to_have_url(f"{BASE}/login")
