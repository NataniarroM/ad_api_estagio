
import json
from playwright.sync_api import Page, expect

URL = "http://localhost:5173/cadastrovaga"
API = "http://127.0.0.1:8000/api/vagas/"


def autenticar(page: Page, tipo="recrutador"):
    page.add_init_script(f"""
        if (window.location.origin === "http://localhost:5173") {{
            localStorage.setItem("access_token", "token-teste");
            localStorage.setItem("tipo_usuario", "{tipo}");
        }}
    """)


def preencher_vaga(page: Page):
    page.locator("#titulo").fill(
        "Estágio em Desenvolvimento Front-end"
    )
    page.locator("#local").fill("Bauru, SP")
    page.locator("#modalidade").select_option("Remoto")
    page.locator("#salario").fill("1500.50")
    page.locator("#descricao").fill(
        "Desenvolvimento de interfaces com React."
    )


def simular_publicacao(page: Page, status=201, dados=None):
    if dados is None:
        dados = {"id_vaga": 123}

    def responder(route):
        headers = {
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "POST, OPTIONS",
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

    page.route(API, responder)


# TESTE 1 - Acesso sem login
def test_acesso_sem_login(page: Page):
    page.goto(URL)

    expect(page).to_have_url(
        "http://localhost:5173/login"
    )


# TESTE 2 - Estudante não pode publicar vagas
def test_acesso_estudante(page: Page):
    autenticar(page, tipo="usuario")
    page.goto(URL)

    expect(page).to_have_url(
        "http://localhost:5173/"
    )


# TESTE 3 - Exibição do formulário
def test_exibir_cadastro_vaga(page: Page):
    autenticar(page)
    page.goto(URL)

    expect(
        page.get_by_role("heading", name="Publicar Nova Vaga")
    ).to_be_visible()

    expect(page.locator("#titulo")).to_be_visible()
    expect(page.locator("#local")).to_be_visible()
    expect(page.locator("#descricao")).to_be_visible()

    expect(
        page.get_by_role("button", name="Publicar Vaga")
    ).to_be_visible()


# TESTE 4 - Campos obrigatórios
def test_campos_obrigatorios(page: Page):
    autenticar(page)
    page.goto(URL)

    page.get_by_role(
        "button", name="Publicar Vaga"
    ).click()

    expect(
        page.locator("form :invalid")
    ).to_have_count(3)


# TESTE 5 - Seleção da modalidade
def test_selecionar_modalidade(page: Page):
    autenticar(page)
    page.goto(URL)

    modalidade = page.locator("#modalidade")

    expect(modalidade).to_have_value("Presencial")

    modalidade.select_option("Híbrido")
    expect(modalidade).to_have_value("Híbrido")

    modalidade.select_option("Remoto")
    expect(modalidade).to_have_value("Remoto")


# TESTE 6 - Publicação bem-sucedida
def test_publicar_vaga_com_sucesso(page: Page):
    autenticar(page)
    simular_publicacao(page)

    page.goto(URL)
    preencher_vaga(page)

    page.get_by_role(
        "button", name="Publicar Vaga"
    ).click()

    expect(
        page.get_by_text("Vaga publicada com sucesso!")
    ).to_be_visible()


# TESTE 7 - Publicação negada pela API
def test_publicar_vaga_sem_permissao(page: Page):
    autenticar(page)

    simular_publicacao(
        page,
        status=403,
        dados={"detail": "Sem permissão"}
    )

    page.goto(URL)
    preencher_vaga(page)

    page.get_by_role(
        "button", name="Publicar Vaga"
    ).click()

    expect(
        page.get_by_text(
            "Acesso negado: Apenas recrutadores podem publicar vagas."
        )
    ).to_be_visible()
