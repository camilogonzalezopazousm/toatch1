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
USUARIO = os.getenv("USUARIO_PORTAL", "22090589")
CONTRASENA = os.getenv("PASS_PORTAL", "Joaquin2012@")

# ----- Configuración correo -----
REMITENTE = os.getenv("EMAIL_OUTLOOK", "cgonzalezo@lari.cl")
OUTLOOK_PASS = os.getenv("OUTLOOK_PASS", "")  # GitHub Secret
DESTINATARIO = REMITENTE

# ----- Carpeta de descarga -----
DOWNLOAD_FOLDER = os.getenv("DOWNLOAD_FOLDER", "/github/home")  # GitHub Actions

# ----- Configuración Chrome headless para CI -----
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument(f"--user-data-dir=/tmp/selenium_{int(time.time())}")

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

    # Manejo de alerta de sesión
    try:
        checkbox_sesion = driver.find_element(By.ID, "delsession")
        if not checkbox_sesion.is_selected():
            checkbox_sesion.click()
            print("✅ Checkbox de sesión activa marcado.")

        # Reingreso de credenciales
        usuario_input = wait.until(EC.visibility_of_element_located((By.XPATH, "//input[@placeholder='Nombre de usuario']")))
        contrasena_input = wait.until(EC.visibility_of_element_located((By.XPATH, "//input[@placeholder='Contraseña']")))

        usuario_input.clear()
        usuario_input.send_keys(USUARIO)
        contrasena_input.clear()
        contrasena_input.send_keys(CONTRASENA)
        contrasena_input.send_keys(Keys.ENTER)
        print("🔄 Reingreso de credenciales realizado tras alerta de sesión.")

    except NoSuchElementException:
        print("No se detectó alerta de sesión. Login completado normalmente.")

    print("3. Esperando carga post-login...")
    wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Vista')]")))
    print("Login exitoso.")
    time.sleep(2)

    # Abrir calendario y seleccionar día anterior
    fecha_hoy = datetime.now().strftime("%Y/%m/%d")
    fecha_element = wait.until(EC.element_to_be_clickable((By.XPATH, f"//*[contains(text(), '{fecha_hoy}')]")))
    fecha_element.click()

    ayer = datetime.now() - timedelta(days=1)
    dia_anterior = str(ayer.day)

    dia_btn = wait.until(EC.element_to_be_clickable((
        By.XPATH,
        f"//table[contains(@class,'ui-datepicker-calendar')]//td[not(contains(@class,'ui-datepicker-other-month'))]/a[text()='{dia_anterior}']"
    )))
    dia_btn.click()
    time.sleep(1)

    # Abrir vista y marcar casilla
    vista_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Vista')]")))
    vista_btn.click()
    time.sleep(0.5)

    label_xpath = "//label[contains(normalize-space(.), 'Todos los datos de hijos')]"

    def try_click_label(xpath):
        try:
            label = wait.until(EC.presence_of_element_located((By.XPATH, xpath)))
            driver.execute_script("arguments[0].scrollIntoView({block:'center'});", label)
            try:
                label.click()
                return True
            except:
                pass
            try:
                driver.execute_script("arguments[0].click();", label)
                return True
            except:
                pass
            try:
                chk = label.find_element(By.XPATH, ".//input[@type='checkbox']")
                driver.execute_script("arguments[0].scrollIntoView(true);", chk)
                driver.execute_script("arguments[0].click();", chk)
                driver.execute_script("arguments[0].checked = true; arguments[0].dispatchEvent(new Event('change', {bubbles:true}));", chk)
                return True
            except:
                pass
            driver.execute_script("""
                var lbl = arguments[0];
                var i = lbl.querySelector('input[type=checkbox]');
                if(i){ i.checked = true; i.dispatchEvent(new Event('change', {bubbles:true})); }
            """, label)
            return True
        except:
            return False

    ok = try_click_label(label_xpath)
    if not ok:
        print("⚠️ No pude marcar la casilla.")
    else:
        print("Casilla marcada.")

    time.sleep(0.5)

    # Aplicar cambios
    try:
        label_elem = wait.until(EC.presence_of_element_located((By.XPATH, label_xpath)))
        container = label_elem.find_element(By.XPATH,
            "ancestor::div[contains(@class,'app-menu') or contains(@class,'dropdown') or contains(@class,'overlay') or contains(@class,'menu')][1]")
        aplicar_btn = container.find_element(By.XPATH, ".//button[normalize-space()='Aplicar' or contains(normalize-space(.),'Aplicar')]")
        aplicar_btn.click()
        time.sleep(0.5)
    except:
        pass

    # Acciones y exportar
    acciones_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Acciones')]")))
    driver.execute_script("arguments[0].scrollIntoView(true);", acciones_btn)
    driver.execute_script("arguments[0].click();", acciones_btn)

    exportar_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Exportar')]")))
    driver.execute_script("arguments[0].scrollIntoView(true);", exportar_btn)
    driver.execute_script("arguments[0].click();", exportar_btn)
    time.sleep(2)

    # ------------------------------
    # Enviar correo con el archivo exportado
    # ------------------------------
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
        msg.add_attachment(f.read(),
                           maintype="application",
                           subtype="vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                           filename=os.path.basename(latest_file))

    with smtplib.SMTP("smtp.office365.com", 587) as smtp:
        smtp.starttls()
        smtp.login(REMITENTE, OUTLOOK_PASS)
        smtp.send_message(msg)

    print("✅ Correo enviado a", DESTINATARIO)

except Exception as e:
    print("❌ Error durante ejecución:", e)

finally:
    driver.quit()

