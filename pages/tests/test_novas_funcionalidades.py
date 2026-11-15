
from playwright.sync_api import Page, expect

BASE = "http://localhost:5173"


def abrir_curriculo(page):
    page.goto(f"{BASE}/perfil")
    page.get_by_role(
        "button", name="Currículo", exact=True
    ).click()


def anexar_arquivo(page, nome, conteudo, mime):
    page.locator(
        ".input-arquivo-curriculo"
    ).set_input_files({
        "name": nome,
        "mimeType": mime,
        "buffer": conteudo
    })


# TESTE 1 - Abrir seção Currículo
def test_abrir_secao_curriculo(page: Page):
    abrir_curriculo(page)

    expect(
        page.get_by_role(
            "heading", name="Meu Currículo"
        )
    ).to_be_visible()

    expect(
        page.get_by_role(
            "button", name="Selecionar currículo"
        )
    ).to_be_visible()


# TESTE 2 - Anexar, visualizar e baixar PDF
def test_anexar_e_visualizar_pdf(page: Page):
    abrir_curriculo(page)

    anexar_arquivo(
        page,
        "curriculo-teste.pdf",
        b"%PDF-1.4\n%Arquivo de teste\n",
        "application/pdf"
    )

    expect(
        page.get_by_text("curriculo-teste.pdf")
    ).to_be_visible()

    page.get_by_role(
        "button", name="Visualizar PDF"
    ).click()

    expect(
        page.locator(".visualizador-curriculo")
    ).to_be_visible()

    expect(
        page.get_by_role("link", name="Baixar")
    ).to_have_attribute(
        "download", "curriculo-teste.pdf"
    )

    page.get_by_role(
        "button", name="Ocultar PDF"
    ).click()

    expect(
        page.locator(".visualizador-curriculo")
    ).to_have_count(0)


# TESTE 3 - Substituir e remover currículo
def test_substituir_e_remover_curriculo(page: Page):
    abrir_curriculo(page)

    anexar_arquivo(
        page,
        "primeiro.pdf",
        b"%PDF-1.4\n",
        "application/pdf"
    )

    expect(
        page.get_by_text("primeiro.pdf")
    ).to_be_visible()

    anexar_arquivo(
        page,
        "segundo.pdf",
        b"%PDF-1.4\n",
        "application/pdf"
    )

    expect(
        page.get_by_text("segundo.pdf")
    ).to_be_visible()

    expect(
        page.get_by_text("primeiro.pdf")
    ).to_have_count(0)

    page.get_by_role(
        "button", name="Remover"
    ).click()

    expect(
        page.get_by_role(
            "button", name="Selecionar currículo"
        )
    ).to_be_visible()


# TESTE 4 - Rejeitar formato inválido
def test_rejeitar_formato_invalido(page: Page):
    abrir_curriculo(page)

    anexar_arquivo(
        page,
        "imagem.png",
        b"arquivo de teste",
        "image/png"
    )

    expect(
        page.get_by_text(
            "Selecione um arquivo PDF, DOC ou DOCX."
        )
    ).to_be_visible()

    expect(
        page.get_by_role(
            "button", name="Selecionar currículo"
        )
    ).to_be_visible()


# TESTE 5 - Aceitar documento Word
def test_anexar_documento_word(page: Page):
    abrir_curriculo(page)

    anexar_arquivo(
        page,
        "curriculo.docx",
        b"documento de teste",
        "application/vnd.openxmlformats-officedocument"
        ".wordprocessingml.document"
    )

    expect(
        page.get_by_text("curriculo.docx")
    ).to_be_visible()

    expect(
        page.get_by_role("link", name="Baixar")
    ).to_have_attribute(
        "download", "curriculo.docx"
    )

    expect(
        page.locator(".visualizador-curriculo")
    ).to_have_count(0)


# TESTE 6 - Mostrar e ocultar senha no Login
def test_mostrar_ocultar_senha_login(page: Page):
    page.goto(f"{BASE}/login")

    campo = page.get_by_placeholder("Sua senha")
    campo.fill("123456")

    expect(campo).to_have_attribute(
        "type", "password"
    )

    page.get_by_role(
        "button", name="Mostrar senha"
    ).click()

    expect(campo).to_have_attribute(
        "type", "text"
    )

    page.get_by_role(
        "button", name="Ocultar senha"
    ).click()

    expect(campo).to_have_attribute(
        "type", "password"
    )


# TESTE 7 - Mostrar senhas no Cadastro
def test_mostrar_senhas_cadastro(page: Page):
    page.goto(f"{BASE}/cadastro")

    senha = page.get_by_placeholder(
        "Mínimo de 6 caracteres"
    )

    confirmacao = page.get_by_placeholder(
        "Repita a sua senha"
    )

    senha.fill("123456")
    confirmacao.fill("123456")

    expect(senha).to_have_attribute(
        "type", "password"
    )

    expect(confirmacao).to_have_attribute(
        "type", "password"
    )

    page.get_by_role(
        "button", name="Mostrar senha"
    ).first.click()

    expect(senha).to_have_attribute(
        "type", "text"
    )

    expect(confirmacao).to_have_attribute(
        "type", "password"
    )

    page.get_by_role(
        "button", name="Mostrar senha"
    ).click()

    expect(confirmacao).to_have_attribute(
        "type", "text"
    )
