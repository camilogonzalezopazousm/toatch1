from playwright.sync_api import sync_playwright
from datetime import datetime, timedelta
import os
import time

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
        print("No se detectó alerta de sesión. Continuando...")

    # Esperar carga post login
    page.wait_for_selector("xpath=//button[contains(., 'Vista')]")
    print("Login exitoso.")

    # ABRIR CALENDARIO
    fecha_hoy = datetime.now().strftime("%Y/%m/%d")
    page.click(f"xpath=//*[contains(text(), '{fecha_hoy}')]")

    ayer = datetime.now() - timedelta(days=1)
    dia_anterior = str(ayer.day)
    print(f"Buscando día anterior: {dia_anterior}...")

    page.click(
        f"xpath=//table[contains(@class,'ui-datepicker-calendar')]"
        f"//td[not(contains(@class,'ui-datepicker-other-month'))]/a[text()='{dia_anterior}']"
    )
    print("Día anterior seleccionado.")

    # Abrir Vista
    page.click("xpath=//button[contains(., 'Vista')]")
    page.check("xpath=//label[contains(normalize-space(.), 'Todos los datos de hijos')]/input")
    page.click("xpath=//button[contains(., 'Aplicar')]")
    print("Casilla marcada y aplicada.")

    # Exportar datos
    page.click("xpath=//button[contains(., 'Acciones')]")
    with page.expect_download() as download_info:
        page.click("xpath=//button[contains(., 'Exportar')]")
    download = download_info.value
    download.save_as("exportado.xlsx")
    print("✅ Datos exportados exitosamente.")

    browser.close()


with sync_playwright() as playwright:
    run(playwright)
