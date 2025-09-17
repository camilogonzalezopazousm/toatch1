from playwright.sync_api import sync_playwright
from datetime import datetime, timedelta
import os
import time


URL = "https://telefonica-cl.etadirect.com/"
USUARIO = os.getenv("USUARIO_PORTAL", "22090589")
CONTRASENA = os.getenv("PASS_PORTAL", "Joaquin2012@")


def run(playwright):
    browser = playwright.chromium.launch(headless=True)
    context = browser.new_context()
    page = context.new_page()

    print("1. Accediendo a la página...")
    page.goto(URL)

    # LOGIN
    print("2. Ingreso de usuario y contraseña...")
    page.fill("//input[@placeholder='Nombre de usuario']", USUARIO)
    page.fill("//input[@placeholder='Contraseña']", CONTRASENA)
    page.keyboard.press("Enter")

    # Posible alerta de sesión activa
    try:
        page.wait_for_selector("#delsession", timeout=3000)
        page.check("#delsession")
        print("✅ Checkbox de sesión activa detectado.")

        # Reingreso de credenciales
        page.fill("//input[@placeholder='Nombre de usuario']", USUARIO)
        page.fill("//input[@placeholder='Contraseña']", CONTRASENA)
        page.keyboard.press("Enter")
        print("🔄 Reingreso de credenciales tras alerta.")
    except:
        print("No se detectó alerta de sesión.")

    # Esperar a que aparezca el botón Vista
    page.wait_for_selector("//button[contains(., 'Vista')]", timeout=20000)
    print("Login exito
