from playwright.sync_api import sync_playwright
from datetime import datetime, timedelta
import time

def run(playwright):
    browser = playwright.chromium.launch(headless=True)  # headless=True para ejecución sin ventana
    context = browser.new_context()
    page = context.new_page()

    print("1. Accediendo a la página...")
    page.goto("https://telefonica-cl.etadirect.com/")

    # LOGIN
    print("2. Ingreso de usuario y contraseña...")
    page.fill("input[name='usuario']", "22090589")       # usuario real
    page.fill("input[name='password']", "Joaquin2012@")  # contraseña real

    # Checkbox "sesión activa"
    if page.locator("//input[@type='checkbox']").is_visible():
        print("✅ Checkbox de sesión activa detectado.")
        page.check("//input[@type='checkbox']")

    page.click("button:has-text('Ingresar')")
    page.wait_for_load_state("networkidle")
    print("✅ Login exitoso.")

    # ABRIR CALENDARIO
    print("3. Haciendo clic en la fecha actual para abrir calendario...")
    fecha_hoy = datetime.now().strftime("%Y/%m/%d")

    page.locator(
        f"//*[contains(text(), '{fecha_hoy}')]"
    ).first.click()
    time.sleep(1)

    # CALCULAMOS DÍA ANTERIOR
    ayer = datetime.now() - timedelta(days=1)
    dia_anterior = str(ayer.day)
    print(f"4. Buscando día anterior: {dia_anterior} en calendario...")

    # Seleccionar SOLO el primer match
    page.locator(
        f"//table[contains(@class,'ui-datepicker-calendar')]"
        f"//td[not(contains(@class,'ui-datepicker-other-month'))]/a[text()='{dia_anterior}']"
    ).first.click()

    print("✅ Día anterior seleccionado.")
    time.sleep(1)

    # CHECKBOX "Todos los datos de hijos"
    print("5. Marcando checkbox 'Todos los datos de hijos'...")
    checkbox = page.locator("//label[contains(normalize-space(.), 'Todos los datos de hijos')]/input")
    checkbox.check()
    print("✅ Checkbox marcado.")

    # BOTÓN APLICAR
    print("6. Haciendo clic en 'Aplicar'...")
    aplicar_btn = page.locator("//button[normalize-space()='Aplicar']")
    aplicar_btn.click()
    print("✅ Botón Aplicar clickeado.")

    # Espera breve
    time.sleep(3)

    # Cerrar
    print("7. Cerrando navegador...")
    context.close()
    browser.close()

with sync_playwright() as playwright:
    run(playwright)
