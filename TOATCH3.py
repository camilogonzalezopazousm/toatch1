#!/usr/bin/env python
# coding: utf-8

# In[ ]:


from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException, NoSuchElementException
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
REMITENTE = "selfgeneratedcamilogonzalez@gmail.com"
DESTINATARIO = "cgonzalezo@lari.cl"
GMAIL_APP_PASS = os.getenv("GMAIL_APP_PASS")  # Secreto en GitHub Actions

# ----- Carpeta de descarga -----
DOWNLOAD_FOLDER = os.getenv("DOWNLOAD_FOLDER", "/github/home")  # ruta en GitHub Actions

driver = webdriver.Chrome()
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

        # Reingresar credenciales
        usuario_input = wait.until(EC.visibility_of_element_located((By.XPATH, "//input[@placeholder='Nombre de usuario']")))
        contrasena_input = wait.until(EC.visibility_of_element_located((By.XPATH, "//input[@placeholder='Contraseña']")))
        usuario_input.clear(); usuario_input.send_keys(USUARIO)
        contrasena_input.clear(); contrasena_input.send_keys(CONTRASENA)
        contrasena_input.send_keys(Keys.ENTER)
        print("🔄 Reingreso de credenciales tras alerta de sesión.")

    except NoSuchElementException:
        print("No se detectó alerta de sesión. Login completado normalmente.")

    # Esperar elemento post-login
    print("3. Esperando carga post-login...")
    wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Vista')]")))
    print("Login exitoso.")
    time.sleep(2)

    # Abrir calendario
    print("4. Seleccionando fecha actual...")
    fecha_hoy = datetime.now().strftime("%Y/%m/%d")
    fecha_element = wait.until(EC.element_to_be_clickable((By.XPATH, f"//*[contains(text(), '{fecha_hoy}')]")))
    fecha_element.click()

    # Día anterior
    ayer = datetime.now() - timedelta(days=1)
    dia_anterior = str(ayer.day)
    print(f"Buscando día anterior: {dia_anterior} en calendario...")
    dia_btn = wait.until(EC.element_to_be_clickable((
        By.XPATH,
        f"//table[contains(@class,'ui-datepicker-calendar')]//td[not(contains(@class,'ui-datepicker-other-month'))]/a[text()='{dia_anterior}']"
    )))
    dia_btn.click()
    print("Día anterior seleccionado.")
    time.sleep(1)

    # Abrir vista y marcar casilla
    print("5. Abriendo 'Vista' y seleccionando opción...")
    vista_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Vista')]")))
    vista_btn.click()
    time.sleep(0.5)

    label_xpath = "//label[contains(normalize-space(.), 'Todos los datos de hijos')]"

    def try_click_label(xpath):
        try:
            label = wait.until(EC.presence_of_element_located((By.XPATH, xpath)))
            driver.execute_script("arguments[0].scrollIntoView({block:'center'});", label)
            time.sleep(0.2)
            try: label.click(); return True
            except: pass
            try: driver.execute_script("arguments[0].click();", label); return True
            except: pass
            try:
                chk = label.find_element(By.XPATH, ".//input[@type='checkbox']")
                driver.execute_script("arguments[0].scrollIntoView(true);", chk)
                driver.execute_script("arguments[0].click();", chk)
                driver.execute_script("arguments[0].checked = true; arguments[0].dispatchEvent(new Event('change', {bubbles:true}));", chk)
                return True
            except: pass
            driver.execute_script("""
                var lbl = arguments[0];
                var i = lbl.querySelector('input[type=checkbox]');
                if(i){ i.checked = true; i.dispatchEvent(new Event('change', {bubbles:true})); }
            """, label)
            return True
        except TimeoutException:
            print("No se encontró el label con xpath:", xpath)
        except Exception as e:
            print("Excepción en try_click_label:", e)
        return False

    ok = try_click_label(label_xpath)
    if ok: print("Casilla marcada (confirmado).")
    else: print("⚠️ No pude marcar la casilla.")
    time.sleep(0.5)

    # Lógica aplicar
    try:
        label_elem = wait.until(EC.presence_of_element_located((By.XPATH, label_xpath)))
    except: label_elem = None

    applied = False
    if label_elem:
        try:
            container = label_elem.find_element(By.XPATH,
                "ancestor::div[contains(@class,'app-menu') or contains(@class,'dropdown') or contains(@class,'overlay') or contains(@class,'menu')][1]")
        except:
            try: container = driver.find_element(By.XPATH, "//div[contains(@class,'app-menu') and (contains(@class,'open') or contains(@class,'is-open'))]")
            except: container = None

        if container:
            try:
                aplicar_btn = container.find_element(By.XPATH, ".//button[normalize-space()='Aplicar' or contains(normalize-space(.),'Aplicar')]")
                try: aplicar_btn.click(); applied=True
                except:
                    try: driver.execute_script("arguments[0].scrollIntoView({block:'center'});arguments[0].click();", aplicar_btn); applied=True
                    except: pass
            except: pass

    if not applied:
        try:
            body = driver.find_element(By.TAG_NAME, "body")
            body.send_keys(Keys.ENTER)
            time.sleep(0.5)
            body.send_keys(Keys.ESCAPE)
        except: pass

    # Abrir acciones y exportar
    print("6️⃣ Abriendo 'Acciones' y exportando...")
    acciones_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Acciones')]")))
    driver.execute_script("arguments[0].scrollIntoView(true);", acciones_btn)
    driver.execute_script("arguments[0].click();", acciones_btn)

    exportar_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Exportar')]")))
    driver.execute_script("arguments[0].scrollIntoView(true);", exportar_btn)
    driver.execute_script("arguments[0].click();", exportar_btn)
    print("✅ Datos exportados exitosamente.")
    time.sleep(2)

    # ------------------------------
    # Enviar correo con el archivo exportado
    # ------------------------------
    try:
        list_of_files = glob.glob(os.path.join(DOWNLOAD_FOLDER, "*.xlsx"))
        if not list_of_files:
            raise FileNotFoundError("No se encontró ningún archivo .xlsx en la carpeta de descargas")
        latest_file = max(list_of_files, key=os.path.getctime)
        print("Archivo a enviar por correo:", latest_file)

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

        with smtplib.SMTP("smtp.gmail.com", 587) as smtp:
            smtp.starttls()
            smtp.login(REMITENTE, GMAIL_APP_PASS)
            smtp.send_message(msg)
        print("✅ Correo enviado exitosamente a", DESTINATARIO)

    except Exception as e:
        print

