#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import os
import time
import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, StaleElementReferenceException
from webdriver_manager.chrome import ChromeDriverManager

# ---------- CONFIGURACIÓN ----------
PORTAL_URL = "https://ejemplo.com/login"  # ⚠️ cambia al portal real
USUARIO_PORTAL = os.environ.get("USUARIO_PORTAL")
PASS_PORTAL = os.environ.get("PASS_PORTAL")

REMITENTE = "selfgeneratedcamilogonzalez@gmail.com"
DESTINATARIO = "cgonzalezo@lari.cl"
CLAVE_APP = os.environ.get("GMAIL_APP_PASS")

DOWNLOAD_FOLDER = os.environ.get("DOWNLOAD_FOLDER", "/github/home")

# ---------- FUNCIONES ----------
def esperar_elemento(driver, by, selector, tiempo=30, click=False):
    """Espera un elemento de forma robusta, lo devuelve o hace click."""
    for _ in range(3):  # reintenta si es stale
        try:
            elem = WebDriverWait(driver, tiempo).until(
                EC.presence_of_element_located((by, selector))
            )
            if click:
                driver.execute_script("arguments[0].click();", elem)
                return True
            return elem
        except (TimeoutException, StaleElementReferenceException):
            time.sleep(2)
    return None

def enviar_correo(archivo):
    mensaje = MIMEMultipart()
    mensaje["From"] = REMITENTE
    mensaje["To"] = DESTINATARIO
    mensaje["Subject"] = "Archivo Automático"

    cuerpo = MIMEText("Adjunto el archivo descargado automáticamente.", "plain")
    mensaje.attach(cuerpo)

    with open(archivo, "rb") as adj:
        parte = MIMEBase("application", "octet-stream")
        parte.set_payload(adj.read())
        encoders.encode_base64(parte)
        parte.add_header("Content-Disposition", f"attachment; filename={os.path.basename(archivo)}")
        mensaje.attach(parte)

    contexto = ssl.create_default_context()
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=contexto) as server:
        server.login(REMITENTE, CLAVE_APP)
        server.sendmail(REMITENTE, DESTINATARIO, mensaje.as_string())

# ---------- MAIN ----------
options = webdriver.ChromeOptions()
options.add_argument("--headless=new")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument(f"--user-data-dir={os.path.join(DOWNLOAD_FOLDER, 'profile')}")
options.add_experimental_option("prefs", {
    "download.default_directory": DOWNLOAD_FOLDER,
    "download.prompt_for_download": False,
    "download.directory_upgrade": True,
    "safebrowsing.enabled": True
})

driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)

try:
    driver.get(PORTAL_URL)

    # ---- LOGIN ----
    user_box = esperar_elemento(driver, By.ID, "usuario")  # ⚠️ ajusta selector
    pass_box = esperar_elemento(driver, By.ID, "password") # ⚠️ ajusta selector
    if user_box and pass_box:
        user_box.send_keys(USUARIO_PORTAL)
        pass_box.send_keys(PASS_PORTAL)
        login_btn = esperar_elemento(driver, By.ID, "loginBtn", click=True)  # ⚠️ ajusta selector
    else:
        raise Exception("No se encontró formulario de login")

    # ---- NAVEGACIÓN Y DESCARGA ----
    boton_descarga = esperar_elemento(driver, By.ID, "btnDescargar", click=True)  # ⚠️ ajusta selector
    time.sleep(15)  # espera descarga

    # ---- BUSCAR ARCHIVO ----
    list_of_files = [os.path.join(DOWNLOAD_FOLDER, f) for f in os.listdir(DOWNLOAD_FOLDER)]
    latest_file = max(list_of_files, key=os.path.getmtime)

    # ---- ENVIAR POR CORREO ----
    enviar_correo(latest_file)

finally:
    driver.quit()

