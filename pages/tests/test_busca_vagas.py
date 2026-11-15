
import json
import pytest
from playwright.sync_api import Page, expect

URL = "http://localhost:5173/"
API = "http://127.0.0.1:8000/api/vagas"

VAGAS = [
    {
        "id_vaga": 101,
        "titulo": "Estágio em React",
        "empresa": "Empresa Aurora",
        "descricao": "Desenvolvimento web",
        "local": "Bauru, SP"
    },
    {
        "id_vaga": 102,
        "titulo": "Estágio em Design",
        "empresa": "Empresa Horizonte",
        "descricao": "Criação de interfaces",
        "local": "São Paulo, SP"
    },
    {
        "id_vaga": 103,
        "titulo": "Estágio React Native",
        "empresa": "Agência Aurora",
        "descricao": "Desenvolvimento mobile",
        "local": "São Paulo, SP"
    }
]


def preparar_home(page):
    page.route(
        API,
        lambda route: route.fulfill(
            status=200,
            content_type="application/json",
            headers={"Access-Control-Allow-Origin": "*"},
            body=json.dumps(VAGAS)
        )
    )

    page.goto(URL)

    expect(
        page.locator(".card-vaga-link")
    ).to_have_count(3)


def pesquisar(page, texto="", local=""):
    page.get_by_placeholder(
        "Cargo, empresa ou palavra-chave"
    ).fill(texto)

    page.get_by_placeholder(
        "Cidade ou estado"
    ).fill(local)

    page.get_by_role(
        "button", name="Buscar", exact=True
    ).click()


# Testes 1 a 4: busca por diferentes filtros
@pytest.mark.parametrize(
    "texto,local,quantidade",
    [
        ("react", "", 2),
        ("aurora", "", 2),
        ("", "bauru", 1),
        ("REACT", "sao paulo", 1),
    ]
)
def test_filtros_de_busca(
    page: Page, texto, local, quantidade
):
    preparar_home(page)

    pesquisar(page, texto, local)

    expect(
        page.locator(".card-vaga-link")
    ).to_have_count(quantidade)

    expect(
        page.locator(".badge-contador")
    ).to_have_text(f"{quantidade} vagas")


# Teste 5: busca sem resultados
def test_busca_sem_resultados(page: Page):
    preparar_home(page)

    pesquisar(page, "vaga inexistente")

    expect(
        page.locator(".card-vaga-link")
    ).to_have_count(0)

    expect(
        page.locator(".badge-contador")
    ).to_have_text("0 vagas")


# Teste 6: limpar os filtros
def test_limpar_filtros(page: Page):
    preparar_home(page)

    pesquisar(page, "react", "bauru")

    expect(
        page.locator(".card-vaga-link")
    ).to_have_count(1)

    pesquisar(page)

    expect(
        page.locator(".card-vaga-link")
    ).to_have_count(3)
