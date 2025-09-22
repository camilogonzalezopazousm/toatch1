import os
import time
from datetime import datetime, timedelta
from playwright.sync_api import sync_playwright

# Diccionario de meses en español con mayúscula inicial
MESES_ES = {
    1: "Enero",
    2: "Febrero",
    3: "Marzo",
    4: "Abril",
    5: "Mayo",
    6: "Junio",
    7: "Julio",
    8: "Agosto",
    9: "Septiembre",
    10: "Octubre",
    11: "Noviembre",
    12: "Diciembre",
}

# Credenciales desde variables de entorno
USUARIO = os.getenv("USUARIO_PORTAL", "22090589")
PASSWORD = os.getenv("PASS_PORTAL", "Joaquin2012@")

# Carpeta de descargas
DOWNLOAD_DIR = os.path.join(os.getcwd(), "descargas")
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

def run(playwright):
    print("1. Accediendo a la página...")
    browser = playwright.chromium.launch(headless=True)
    context = browser.new_context(accept_downloads=True)
    page = context.new_page()

    page.goto("https://srienlinea.sii.cl/")

    # Login
    print("2. Ingreso de usuario y contraseña...")
    page.fill('input[name="rutcntr"]', USUARIO)
    page.fill('input[name="clave"]', PASSWORD)
    page.click('input[type="submit"]')

    # Checkbox sesión activa
    try:
        checkbox = page.locator("text=No cerrar sesión automáticamente")
        if checkbox.is_visible():
            checkbox.check()
            print("✅ Checkbox de sesión activa detectado.")
    except:
        pass

    # Si pide reingresar credenciales
    if page.locator("text=Ingrese nuevamente sus credenciales").is_visible():
        print("🔄 Reingreso de credenciales tras alerta.")
        page.fill('input[name="rutcntr"]', USUARIO)
        page.fill('input[name="clave"]', PASSWORD)
        page.click('input[type="submit"]')

    print("Login exitoso.")

    # Calcular día anterior
    hoy = datetime.now()
    ayer = hoy - timedelta(days=1)

    dia = ayer.day
    mes_actual = MESES_ES[ayer.month]
    mes_anterior = MESES_ES[(ayer.month - 1) if ayer.month > 1 else 12]

    fecha_buscar = f"{dia} {mes_actual}"
    fecha_alternativa = f"{dia} {mes_anterior}"

    print(f"📅 Buscando día anterior: {fecha_buscar} (fallback: {fecha_alternativa})...")

    # Intentar hacer clic en el calendario
    try:
        page.click(f"//*[contains(text(), '{fecha_buscar}')]")
        print(f"✅ Fecha encontrada: {fecha_buscar}")
    except:
        print(f"⚠️ No se encontró {fecha_buscar}, probando con {fecha_alternativa}...")
        page.click(f"//*[contains(text(), '{fecha_alternativa}')]")
        print(f"✅ Fecha alternativa encontrada: {fecha_alternativa}")

    # Botón exportar
    page.click("text=Exportar")

    # Esperar descarga
    with page.expect_download() as download_info:
        page.click("text=Exportar a Excel")
    download = download_info.value
    ruta_final = os.path.join(DOWNLOAD_DIR, "exportado.xlsx")
    download.save_as(ruta_final)

    print(f"📂 Archivo exportado: {ruta_final}")

    context.close()
    browser.close()

if __name__ == "__main__":
    with sync_playwright() as playwright:
        run(playwright)
