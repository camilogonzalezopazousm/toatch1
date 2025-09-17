from playwright.sync_api import sync_playwright
from datetime import datetime, timedelta
import os

# ----- Credenciales y URL -----
URL = "https://telefonica-cl.etadirect.com/"
USUARIO = os.getenv("USUARIO_PORTAL", "22090589")
CONTRASENA = os.getenv("PASS_PORTAL", "Joaquin2012@")


def run(playwright):
    browser = playwright.chromium.launch(headless=True)
    context = browser.new_context(accept_downloads=True)
    page = context.new_page()

    print("1. Accediendo a la página...")
    page.goto(URL)

    # LOGIN
    print("2. Ingreso de usuario y contraseña...")
    page.fill("xpath=//input[@placeholder='Nombre de usuario']", USUARIO)
    page.fill("xpath=//input[@placeholder='Contraseña']", CONTRASENA)
    page.keyboard.press("Enter")

    # Manejo de alerta de sesión activa
    try:
        page.wait_for_selector("#delsession", timeout=3000)
        print("✅ Checkbox de sesión activa detectado.")
        page.check("#delsession")

        page.fill("xpath=//input[@placeholder='Nombre de usuario']", USUARIO)
        page.fill("xpath=//input[@placeholder='Contraseña']", CONTRASENA)
        page.keyboard.press("Enter")
        print("🔄 Reingreso de credenciales tras alerta.")
    except:
