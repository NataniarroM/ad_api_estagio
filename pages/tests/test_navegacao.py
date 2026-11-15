
from playwright.sync_api import Page, expect

def test_pagina_login(page: Page):
    page.goto("http://localhost:5173/login")

    expect(page).to_have_url(
        "http://localhost:5173/login"
    )

def test_pagina_cadastro(page: Page):
    page.goto("http://localhost:5173/cadastro")

    expect(page).to_have_url(
        "http://localhost:5173/cadastro"
    )
