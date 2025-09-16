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
from selenium.webdriver.chrome.service import Service

from datetime import datetime, timedelta
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email import encoders
import os
import time

# ==============================
# CONFIGURACIÓN SELENIUM
# ==============================
chrome_options = Options()
chrome_options.add_argument("--headless=new")   # sin interfaz gráfica
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--window-size=1920x1080")
chrome_options.add_argument("--disable-blink-features=AutomationControlled")
chrome_options.add_argument("--user-data-dir=/tmp/chrome-profile")  # directorio único

driver = webdriver.Chrome(options=chrome_options)

# ==============================
# VARIABLES
# ==============================
USUARIO = os.getenv("USUARIO_PORTAL")
CONTRASENA = os.getenv("PASS_PORTAL")
DOWNLOAD_FOLDER = os.getenv("DOWNLOAD_FOLDER", "/github/home")

GMAIL_USER = "selfgeneratedcamilogonzalez@gmail.com"
GMAIL_PASS = os.getenv("GMAIL_APP_PASS")
DESTINATARIO = "cgonzalezo@lari.cl"

# ==============================
# LÓGICA DEL SCRIPT
# ==============================
try:
    driver.get("https://URL_DE_TU_PORTAL")  # <-- reemplaza por la URL real
    wait = WebDriverWait(driver, 15)

    # Login
    usuario_input = wait.until(EC.presence_of_element_located((By.ID, "usuario")))
    contrasena_input = wait.until(EC.presence_of_element_located((By.ID, "contrasena")))

    usuario_input.clear()
    usuario_input.send_keys(USUARIO)
    contrasena_input.clear()
    contrasena_input.send_keys(CONTRASENA)
    contrasena_input.send_keys(Keys.ENTER)

    # Esperar a que se genere el archivo (ajusta según tu caso real)
    time.sleep(15)

    # Simulación: el archivo exportado debe estar en la carpeta de descargas
    # Reemplaza con la ruta real donde Selenium descarga el archivo
    list_of_files = [os.path.join(DOWNLOAD_FOLDER, f) for f in os.listdir(DOWNLOAD_FOLDER)]
    latest_file = max(list_of_files, key=os.path.getctime)

    print(f"Archivo encontrado: {latest_file}")

    # ==============================
    # ENVÍO DE CORREO
    # ==============================
    msg = MIMEMultipart()
    msg["From"] = GMAIL_USER
    msg["To"] = DESTINATARIO
    msg["Subject"] = "Archivo generado automáticamente"

    body = "Adjunto archivo exportado automáticamente desde GitHub Actions."
    msg.attach(MIMEText(body, "plain"))

    # Adjuntar archivo
    with open(latest_file, "rb") as adj:
        mime_base = MIMEBase("application", "octet-stream")
        mime_base.set_payload(adj.read())
        encoders.encode_base64(mime_base)
        mime_base.add_header("Content-Disposition", f"attachment; filename={os.path.basename(latest_file)}")
        msg.attach(mime_base)

    # Enviar correo vía Gmail
    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.starttls()
    server.login(GMAIL_USER, GMAIL_PASS)
    server.send_message(msg)
    server.quit()

    print("Correo enviado correctamente.")

except Exception as e:
    print(f"Error en el proceso: {e}")

finally:
    driver.quit()

