#!/usr/bin/env python
# coding: utf-8

# In[ ]:


from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.chrome.options import Options
from datetime import datetime, timedelta
import time
import os
import smtplib
from email.message import EmailMessage
import glob

# ----- Credenciales y URL -----
URL = "https://telefonica-cl.etadirect.com/"
USUARIO = os.getenv("USUARIO_PORTAL")
CONTRASENA = os.getenv("PASS_PORTAL")

# ----- Configuración correo -----
REMITENTE = "selfgeneratedcamilogonzalez@gmail.com"  # remitente fijo
DESTINATARIO = "cgonzalezo@lari.cl"                  # destinatario fijo
GMAIL_APP_PASS = os.getenv("GMAIL_APP_PASS")

# ----- Carpeta de descarga -----
DOWNLOAD_FOLDER = os.getenv("DOWNLOAD_FOLDER", "/github/home")

# ----- Configuración Chrome headless -----
chrome_options = Options()
chrome_options.add_argument("--headless")  # modo sin interfaz gráfica
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--window-size=1920x1080")

driver = webdriver.Chrome(options=chrome_options)
wait = WebDriverWait(driver, 20)

try:
    print("1. Accediendo a la página...")
    driver.get(URL)

    # LOGIN
    print("2. Ingreso de usuario y contraseña...")
    usuario_input = wait.until(EC.visibility_of_element_located((By.XPATH, "//input[@placeholder='Nombre de usuario']")))
    contrasena_input = wait.until(EC.visibility_of_element_located((By.XPATH, "//input[@placeholder='Contraseña']")))

    usuario_input.clear(); usuario_input.send_keys(USUARIO)
    contrasena_input.clear(); contrasena_input.send_keys(CONTRASENA)
    contrasena_input.send_keys(Keys.ENTER)

    time.sleep(2)

    # Manejo de alerta de sesión activa
    try:
        checkbox_sesion = driver.find_element(By.ID, "delsession")
        if not checkbox_sesion.is_selected():
            checkbox_sesion.click()
            print("✅ Checkbox de sesión activa marcado.")

        usuario_input = wait.until(EC.visibility_of_element_located((By.XPATH, "//input[@placeholder='Nombre de usuario']")))
        contrasena_input = wait.until(EC.visibility_of_element_located((By.XPATH, "//input[@placeholder='Contraseña']")))

        usuario_input.clear()
        usuario_input.send_keys(USUARIO)
        contrasena_input.clear()
        contrasena_input.send_keys(CONTRASENA)
        contrasena_input.send_keys(Keys.ENTER)
        print("🔄 Reingreso de credenciales realizado.")

    except NoSuchElementException:
        print("No se detectó alerta de sesión. Login normal.")

    # Esperar carga
    wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Vista')]")))
    print("Login exitoso.")

    # Abrir calendario
    fecha_hoy = datetime.now().strftime("%Y/%m/%d")
    fecha_element = wait.until(EC.element_to_be_clickable((By.XPATH, f"//*[contains(text(), '{fecha_hoy}')]")))
    fecha_element.click()

    # Día anterior
    ayer = datetime.now() - timedelta(days=1)
    dia_anterior = str(ayer.day)
    dia_btn = wait.until(EC.element_to_be_clickable((
        By.XPATH,
        f"//table[contains(@class,'ui-datepicker-calendar')]//td[not(contains(@class,'ui-datepicker-other-month'))]/a[text()='{dia_anterior}']"
    )))
    dia_btn.click()
    print("Día anterior seleccionado.")

    # Abrir vista
    vista_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Vista')]")))
    vista_btn.click()
    time.sleep(0.5)

    label_xpath = "//label[contains(normalize-space(.), 'Todos los datos de hijos')]"
    try:
        label = wait.until(EC.presence_of_element_located((By.XPATH, label_xpath)))
        driver.execute_script("arguments[0].click();", label)
        print("Casilla marcada.")
    except Exception as e:
        print("⚠️ No pude marcar la casilla:", e)

    # Aplicar
    try:
        aplicar_btn = driver.find_element(By.XPATH, "//button[contains(text(),'Aplicar')]")
        driver.execute_script("arguments[0].click();", aplicar_btn)
    except Exception:
        print("⚠️ No se pudo hacer clic en 'Aplicar'.")

    # Exportar
    acciones_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Acciones')]")))
    driver.execute_script("arguments[0].click();", acciones_btn)

    exportar_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Exportar')]")))
    driver.execute_script("arguments[0].click();", exportar_btn)
    print("✅ Datos exportados.")

    time.sleep(5)  # espera para que se genere el archivo

    # Enviar correo con archivo exportado
    list_of_files = glob.glob(os.path.join(DOWNLOAD_FOLDER, "*.xlsx"))
    if not list_of_files:
        raise FileNotFoundError("No se encontró ningún archivo .xlsx en la carpeta de descargas")

    latest_file = max(list_of_files, key=os.path.getctime)
    print("Archivo a enviar:", latest_file)

    msg = EmailMessage()
    msg['Subject'] = f"Reporte TOATCH1609 - {datetime.now().strftime('%Y-%m-%d')}"
    msg['From'] = REMITENTE
    msg['To'] = DESTINATARIO
    msg.set_content("Adjunto encontrarás el reporte diario.")

    with open(latest_file, "rb") as f:
        msg.add_attachment(
            f.read(),
            maintype="application",
            subtype="vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            filename=os.path.basename(latest_file)
        )

    with smtplib.SMTP("smtp.gmail.com", 587) as smtp:
        smtp.starttls()
        smtp.login(REMITENTE, GMAIL_APP_PASS)
        smtp.send_message(msg)

    print("✅ Correo enviado exitosamente a", DESTINATARIO)

except Exception as e:
    print("❌ Error en el proceso:", e)

finally:
    driver.quit()

