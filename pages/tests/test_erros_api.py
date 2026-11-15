
import json
from playwright.sync_api import Page, expect

BASE = "http://localhost:5173"
API = "http://127.0.0.1:8000"


def resposta_simulada(route, status, dados):
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


def preparar_cadastro(page):
    page.route(
        f"{API}/api/cursos",
        lambda route: resposta_simulada(
            route, 200,
            [{"id_curso": 1, "nome": "Administração"}]
        )
    )

    page.goto(f"{BASE}/cadastro")

    expect(
        page.locator('select[name="id_curso"] option[value="1"]')
    ).to_have_count(1)

    campos = {
        "Digite o seu nome": "Usuario Teste",
        "exemplo@email.com": "teste@exemplo.com",
        "Mínimo de 6 caracteres": "123456",
        "Repita a sua senha": "123456",
        "Ex: 11988888888": "11988888888",
        "Ex: 3": "3",
    }

    for placeholder, valor in campos.items():
        page.get_by_placeholder(placeholder).fill(valor)

    page.locator(
        'select[name="id_curso"]'
    ).select_option("1")


def preparar_login(page):
    page.goto(f"{BASE}/login")
    page.get_by_placeholder("seu@email.com").fill(
        "teste@exemplo.com"
    )
    page.get_by_placeholder("Sua senha").fill(
        "123456"
    )


def simular_vaga(page):
    vaga = {
        "id_vaga": 123,
        "titulo": "Estágio em Desenvolvimento",
        "empresa": "Empresa Teste",
        "descricao": "Desenvolvimento de aplicações web."
    }

    page.route(
        f"{API}/api/vagas/123",
        lambda route: resposta_simulada(route, 200, vaga)
    )


# 1. Login quando o servidor está indisponível
def test_login_sem_conexao(page: Page):
    page.route(
        "http://localhost:8080/auth/login",
        lambda route: route.abort("failed")
    )

    preparar_login(page)
    page.locator("form").get_by_role(
        "button", name="Entrar"
    ).click()

    expect(
        page.locator(".mensagem-alerta.erro")
    ).to_be_visible()


# 2. Login quando o servidor de perfil falha
def test_login_erro_ao_carregar_perfil(page: Page):
    page.route(
        "http://localhost:8080/auth/login",
        lambda route: resposta_simulada(
            route, 200,
            {"access_token": "token-teste"}
        )
    )

    page.route(
        "http://localhost:8080/api/perfil",
        lambda route: resposta_simulada(
            route, 500,
            {"detail": "Erro interno"}
        )
    )

    preparar_login(page)

    page.locator("form").get_by_role(
        "button", name="Entrar"
    ).click()

    expect(
        page.get_by_text("Erro ao carregar os dados do perfil.")
    ).to_be_visible()


# 3. Cadastro com e-mail já utilizado
def test_cadastro_email_duplicado(page: Page):
    page.route(
        f"{API}/auth/cadastro",
        lambda route: resposta_simulada(
            route, 409,
            {"detail": "Este e-mail já está cadastrado"}
        )
    )

    preparar_cadastro(page)

    page.get_by_role(
        "button", name="Cadastrar", exact=True
    ).click()

    expect(
        page.get_by_text("Este e-mail já está cadastrado")
    ).to_be_visible()


# 4. Cadastro sem conexão com o servidor
def test_cadastro_sem_conexao(page: Page):
    page.route(
        f"{API}/auth/cadastro",
        lambda route: route.abort("failed")
    )

    preparar_cadastro(page)

    page.get_by_role(
        "button", name="Cadastrar", exact=True
    ).click()

    expect(
        page.get_by_text("Não foi possível conectar ao servidor.")
    ).to_be_visible()


# 5. Erro interno ao carregar os detalhes da vaga
def test_erro_interno_detalhes(page: Page):
    page.route(
        f"{API}/api/vagas/123",
        lambda route: resposta_simulada(
            route, 500,
            {"detail": "Erro interno"}
        )
    )

    page.goto(f"{BASE}/vaga/123")

    expect(
        page.get_by_text("Erro ao carregar os detalhes da vaga.")
    ).to_be_visible()


# 6. Falha de conexão ao buscar uma vaga
def test_detalhes_sem_conexao(page: Page):
    page.route(
        f"{API}/api/vagas/123",
        lambda route: route.abort("failed")
    )

    page.goto(f"{BASE}/vaga/123")

    expect(
        page.get_by_text("Erro ao carregar os detalhes da vaga.")
    ).to_be_visible()


# 7. Falha de conexão ao realizar candidatura
def test_candidatura_sem_conexao(page: Page):
    simular_vaga(page)

    page.route(
        f"{API}/api/vagas/candidatar",
        lambda route: route.abort("failed")
    )

    mensagens = []

    def tratar_alerta(dialog):
        mensagens.append(dialog.message)
        dialog.dismiss()

    page.on("dialog", tratar_alerta)

    page.goto(f"{BASE}/vaga/123")

    expect(
        page.get_by_role("button", name="Candidatar-me a esta vaga")
    ).to_be_visible()

    with page.expect_event("dialog"):
        page.get_by_role(
            "button", name="Candidatar-me a esta vaga"
        ).click()

    assert mensagens == [
        "Erro de conexão com o servidor."
    ]
