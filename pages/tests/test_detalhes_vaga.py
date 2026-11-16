
import json
from playwright.sync_api import Page, expect

URL = "http://localhost:5173/vaga/123"
API_VAGA = "http://localhost:8000/api/vagas/123"
API_CANDIDATURA = "http://localhost:8000/candidatura/"

VAGA = {
    "id_vaga": 123,
    "titulo": "Estágio em Desenvolvimento React",
    "empresa": "Empresa Teste",
    "local": "Bauru, SP",
    "tipo": "Remoto",
    "salario": "R$ 1.500",
    "descricao": "Desenvolvimento de aplicações web.",
    "requisitos": ["Conhecimentos em React", "Git"],
    "beneficios": ["Vale-transporte", "Seguro de vida"]
}


def responder(route, status, dados):
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


def simular_vaga(page, status=200, dados=None):
    page.add_init_script("localStorage.setItem('access_token', 'token-teste')")
    page.route(
        "http://localhost:8000/auth/perfil",
        lambda route: responder(route, 200, {"tipo_usuario": "usuario"})
    )
    if dados is None:
        dados = VAGA

    page.route(
        API_VAGA,
        lambda route: responder(route, status, dados)
    )


def test_exibir_detalhes_vaga(page: Page):
    simular_vaga(page)
    page.goto(URL)

    expect(
        page.get_by_role(
            "heading",
            name="Estágio em Desenvolvimento React"
        )
    ).to_be_visible()

    expect(
        page.get_by_text("Empresa Teste")
    ).to_be_visible()

    expect(
        page.get_by_text("Desenvolvimento de aplicações web.")
    ).to_be_visible()


def test_exibir_requisitos_e_beneficios(page: Page):
    simular_vaga(page)
    page.goto(URL)

    expect(
        page.get_by_text("Conhecimentos em React")
    ).to_be_visible()

    expect(
        page.get_by_text("Vale-transporte")
    ).to_be_visible()

    expect(
        page.get_by_text("Seguro de vida")
    ).to_be_visible()


def test_exibir_modalidade_e_salario(page: Page):
    simular_vaga(page)
    page.goto(URL)

    expect(
        page.locator(".badge.tipo")
    ).to_have_text("Remoto")

    expect(
        page.locator(".badge.bolsa")
    ).to_have_text("R$ 1.500")


def test_erro_ao_carregar_vaga(page: Page):
    simular_vaga(
        page,
        status=404,
        dados={"detail": "Vaga não encontrada"}
    )

    page.goto(URL)

    expect(
        page.get_by_text("Erro ao carregar os detalhes da vaga.")
    ).to_be_visible()


def test_candidatura_com_sucesso(page: Page):
    simular_vaga(page)
    requisicoes = []

    def responder_candidatura(route):
        if route.request.method == "POST":
            assert route.request.headers["authorization"] == "Bearer token-teste"
            requisicoes.append(
                json.loads(route.request.post_data)
            )

        responder(route, 201, {"mensagem": "Candidatura criada"})

    page.route(API_CANDIDATURA, responder_candidatura)

    page.goto(URL)

    page.get_by_role(
        "button", name="Candidatar-me a esta vaga"
    ).click()

    expect(
        page.get_by_text(
            "Candidatura realizada com sucesso!",
            exact=False
        )
    ).to_be_visible()

    assert len(requisicoes) == 1
    assert requisicoes[0] == {"id_vaga": 123}
    expect(page.get_by_role("link", name="Ver minhas candidaturas")).to_have_attribute(
        "href", "/perfil?aba=candidaturas"
    )


def test_candidatura_negada(page: Page):
    simular_vaga(page)

    page.route(
        API_CANDIDATURA,
        lambda route: responder(
            route, 403, {"detail": "Acesso negado"}
        )
    )

    mensagens = []

    def tratar_alerta(dialog):
        mensagens.append(dialog.message)
        dialog.dismiss()

    page.on("dialog", tratar_alerta)

    page.goto(URL)

    with page.expect_event("dialog"):
        page.get_by_role(
            "button", name="Candidatar-me a esta vaga"
        ).click()

    assert mensagens == [
        "Acesso negado"
    ]
