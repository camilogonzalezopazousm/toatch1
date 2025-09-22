from playwright.sync_api import sync_playwright
from datetime import datetime, timedelta
import os
import time

URL = "https://telefonica-cl.etadirect.com/"
USUARIO = os.getenv("USUARIO_PORTAL", "22090589")
CONTRASENA = os.getenv("PASS_PORTAL", "Joaquin2012@")


def run(playwright):
    browser = playwright.chromium.launch(headless=True)
    context = browser.new_context(accept_downloads=True)  # ✅ Permitir descargas
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
    print("Login exitoso.")

    # ABRIR CALENDARIO
    fecha_hoy = datetime.now().strftime("%Y/%m/%d")
    page.locator(f"//*[contains(text(), '{fecha_hoy}')]").first.click()

    # Seleccionar día anterior
    ayer = datetime.now() - timedelta(days=1)
    dia_anterior = str(ayer.day)
    print(f"Buscando día anterior: {dia_anterior}...")
    dia_locator = page.locator(
        f"//table[contains(@class,'ui-datepicker-calendar')]"
        f"//td[not(contains(@class,'ui-datepicker-other-month'))]/a[text()='{dia_anterior}']"
    )
    dia_locator.first.click()
    print("Día anterior seleccionado.")

    # ABRIR VISTA Y MARCAR CASILLA
    page.locator("//button[contains(., 'Vista')]").first.click()
    time.sleep(1)

    label_xpath = "//label[contains(normalize-space(.), 'Todos los datos de hijos')]"
    try:
        page.check(f"{label_xpath}//input", timeout=5000)
        print("✅ Casilla marcada.")
    except:
        print("⚠️ No se pudo marcar la casilla.")

    # CLIC EN APLICAR
    try:
        aplicar_btn = page.locator(
            "//button[normalize-space()='Aplicar' or contains(normalize-space(.),'Aplicar')]"
        )
        aplicar_btn.click(timeout=3000)
        print("✅ Cambios aplicados.")
    except:
        print("⚠️ No se pudo hacer clic en 'Aplicar'.")

   # ABRIR ACCIONES Y EXPORTAR
print("6️⃣ Abriendo 'Acciones' y exportando...")
page.locator("//button[contains(., 'Acciones')]").click()

with page.expect_download() as download_info:
    page.locator("//button[contains(., 'Exportar')]").click()
download = download_info.value

# Obtiene el nombre original que entrega el portal
nombre_archivo = download.suggested_filename
print(f"📂 Archivo descargado: {nombre_archivo}")

# Guardar con el nombre original
download.save_as(nombre_archivo)
print("✅ Datos exportados exitosamente.")

time.sleep(5)
context.close()
browser.close()



with sync_playwright() as playwright:
    run(playwright)
