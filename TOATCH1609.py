from playwright.sync_api import sync_playwright
from datetime import datetime, timedelta
import time

def run(playwright):
    browser = playwright.chromium.launch(headless=True)
    context = browser.new_context()
    page = context.new_page()

    print("1. Accediendo a la página...")
    page.goto("https://telefonica-cl.etadirect.com/")

    # LOGIN
    print("2. Ingreso de usuario y contraseña...")
    page.fill("input[name='usuario']", "22090589")      # usuario real
    page.fill("input[name='password']", "Joaquin2012@") # contraseña real

    # Checkbox "sesión activa"
    if page.locator("//input[@type='checkbox']").is_visible():
        print("✅ Checkbox de sesión activa detectado.")
        page.check("//input[@type='checkbox']")

    page.click("button:has-text('Ingresar')")
    print("🔄 Reingreso de credenciales tras alerta.")
    page.wait_for_load_state("networkidle")
    print("Login exitoso.")

    # ABRIR CALENDARIO
    print("4. Haciendo clic en la fecha actual para abrir calendario...")
    fecha_hoy = datetime.now().strftime("%Y/%m/%d")
    page.locator(
        f"//*[contains(text(), '{fecha_hoy}')]"
    ).nth(0).click()
    time.sleep(1)

    # CALCULAMOS DÍA ANTERIOR
    ayer = datetime.now() - timedelta(days=1)
    dia_anterior = str(ayer.day)
    print(f"Buscando día anterior: {dia_anterior} en calendario...")

    page.locator(
        f"//table[contains(@class,'ui-datepicker-calendar')]"
        f"//td[not(contains(@class,'ui-datepicker-other-month'))]/a[text()]()
