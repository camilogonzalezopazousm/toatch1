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

    # -----------------------------
    # ABRIR "Vista" y marcar casilla
    # -----------------------------
    print("5. Abriendo 'Vista' y seleccionando opción...")
    page.click("xpath=//button[contains(., 'Vista')]")

    label_xpath = "//label[contains(normalize-space(.), 'Todos los datos de hijos')]"
    label = page.locator(label_xpath)

    # Función robusta para marcar la casilla
    def try_click_label():
        try:
            label.click(timeout=5000)
            return True
        except:
            pass
        try:
            label.evaluate("el => el.click()")
            return True
        except:
            pass
        try:
            checkbox = label.locator(".//input[@type='checkbox']")
            if checkbox.count() > 0:
                checkbox.evaluate(
                    "el => { el.checked = true; el.dispatchEvent(new Event('change', {bubbles:true})); }"
                )
                return True
        except:
            pass
        return False

    ok = try_click_label()
    if not ok:
        print("⚠️ No pude marcar la casilla, revisa si está en un shadow DOM.")
    else:
        print("✅ Casilla marcada.")

    # Aplicar
    try:
        aplicar_btn = page.locator(
    "//button[normalize-space()='Aplicar' or contains(normalize-space(.),'Aplicar')]"
)


        aplicar_btn.click(timeout=3000)
        print("✅ Cambios aplicados.")
    except:
        print("⚠️ No se pudo hacer clic en 'Aplicar'. Revisa manualmente.")

    # -----------------------------
    # Exportar datos
    # -----------------------------
    print("6️⃣ Abriendo 'Acciones' y exportando...")
    page.click("xpath=//button[contains(., 'Acciones')]")

    with page.expect_download() as download_info:
        page.click("xpath=//button[contains(., 'Exportar')]")
    download = download_info.value
    download.save_as("exportado.xlsx")
    print("✅ Datos exportados exitosamente.")

    browser.close()


with sync_playwright() as playwright:
    run(playwright)
