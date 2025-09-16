#!/usr/bin/env python
# coding: utf-8

# In[1]:


from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from datetime import datetime, timedelta
import time
import os

# ----- Credenciales y URL -----
URL = "https://telefonica-cl.etadirect.com/"
USUARIO = os.getenv("USUARIO_PORTAL", "22090589")
CONTRASENA = os.getenv("PASS_PORTAL", "Joaquin2012@")

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

    # Esperar unos segundos a que cargue la posible alerta de sesión
    time.sleep(2)

    # ----- Manejo de alerta de sesión activa -----
    try:
        checkbox_sesion = driver.find_element(By.ID, "delsession")
        if not checkbox_sesion.is_selected():
            checkbox_sesion.click()
            print("✅ Checkbox de sesión activa marcado.")

        # Reingresar credenciales
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

    # Esperar que cargue elemento principal
    print("3. Esperando carga post-login...")
    wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Vista')]")))
    print("Login exitoso.")

    time.sleep(2)

    # ABRIR CALENDARIO
    print("4. Haciendo clic en la fecha actual para abrir calendario...")
    fecha_hoy = datetime.now().strftime("%Y/%m/%d")
    fecha_element = wait.until(EC.element_to_be_clickable((By.XPATH, f"//*[contains(text(), '{fecha_hoy}')]")))
    fecha_element.click()

    # CALCULAMOS DÍA ANTERIOR
    ayer = datetime.now() - timedelta(days=1)
    dia_anterior = str(ayer.day)
    print(f"Buscando día anterior: {dia_anterior} en calendario...")

    # Esperar que el calendario esté visible y hacer clic en el día anterior
    dia_btn = wait.until(EC.element_to_be_clickable((
        By.XPATH,
        f"//table[contains(@class,'ui-datepicker-calendar')]"
        f"//td[not(contains(@class,'ui-datepicker-other-month'))]/a[text()='{dia_anterior}']"
    )))
    dia_btn.click()
    print("Día anterior seleccionado.")

    time.sleep(1)

    # ABRIR VISTA Y MARCAR CASILLA
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
            try:
                label.click()
                return True
            except Exception:
                pass
            try:
                driver.execute_script("arguments[0].click();", label)
                return True
            except Exception:
                pass
            try:
                chk = label.find_element(By.XPATH, ".//input[@type='checkbox']")
                driver.execute_script("arguments[0].scrollIntoView(true);", chk)
                driver.execute_script("arguments[0].click();", chk)
                driver.execute_script("arguments[0].checked = true; arguments[0].dispatchEvent(new Event('change', {bubbles:true}));", chk)
                return True
            except Exception:
                pass
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
    if not ok:
        print("⚠️ No pude marcar la casilla, revisa si está en un iframe o shadow DOM.")
    else:
        print("Casilla marcada (confirmado).")

    time.sleep(0.5)

    # ----------------------------
    # NUEVA LÓGICA ROBUSTA PARA "APLICAR"
    # ----------------------------
    try:
        label_elem = wait.until(EC.presence_of_element_located((By.XPATH, label_xpath)))
    except Exception as e:
        label_elem = None
        print("⚠️ No pude re-localizar el label tras marcarlo:", e)

    applied = False
    if label_elem:
        container = None
        try:
            container = label_elem.find_element(By.XPATH,
                "ancestor::div[contains(@class,'app-menu') or contains(@class,'dropdown') or contains(@class,'overlay') or contains(@class,'menu')][1]")
        except Exception:
            try:
                container = driver.find_element(By.XPATH, "//div[contains(@class,'app-menu') and (contains(@class,'open') or contains(@class,'is-open'))]")
            except Exception:
                container = None

        if container:
            try:
                aplicar_btn = container.find_element(By.XPATH, ".//button[normalize-space()='Aplicar' or contains(normalize-space(.),'Aplicar')]")
                try:
                    aplicar_btn.click()
                    applied = True
                    print("Intento: click() en 'Aplicar' dentro del contenedor.")
                except Exception:
                    try:
                        driver.execute_script("arguments[0].scrollIntoView({block:'center'});", aplicar_btn)
                        driver.execute_script("arguments[0].click();", aplicar_btn)
                        applied = True
                        print("Intento: execute_script click() en 'Aplicar'.")
                    except Exception:
                        try:
                            driver.execute_script("""
                                var btn = arguments[0];
                                function triggerMouseEvent(node, eventType) {
                                  var clickEvent = document.createEvent('MouseEvents');
                                  clickEvent.initEvent(eventType, true, true);
                                  node.dispatchEvent(clickEvent);
                                }
                                triggerMouseEvent(btn, 'mouseover');
                                triggerMouseEvent(btn, 'mousedown');
                                triggerMouseEvent(btn, 'mouseup');
                                btn.click();
                            """, aplicar_btn)
                            applied = True
                            print("Intento: dispatch de eventos y click() en 'Aplicar'.")
                        except Exception as e:
                            print("No se pudo forzar el click en 'Aplicar' dentro del contenedor:", e)
            except Exception as e:
                print("No se encontró el botón 'Aplicar' dentro del contenedor:", e)

        if not applied and container:
            try:
                container.send_keys(Keys.ENTER)
                time.sleep(0.5)
                applied = True
                print("Fallback: enviado ENTER al contenedor.")
            except Exception as e:
                print("Fallback: no se pudo enviar ENTER al contenedor:", e)

    if not applied:
        try:
            body = driver.find_element(By.TAG_NAME, "body")
            body.send_keys(Keys.ENTER)
            time.sleep(0.5)
            body.send_keys(Keys.ESCAPE)
            applied = True
            print("Fallback: enviado ENTER al body y ESCAPE.")
        except Exception as e:
            print("Fallback final: no se pudo enviar ENTER al body:", e)

    try:
        wait_short = WebDriverWait(driver, 3)
        wait_short.until(EC.invisibility_of_element_located((By.XPATH, "//div[contains(@class,'app-menu') and (contains(@class,'open') or contains(@class,'is-open'))]")))
        print("Verificación: el menú desplegable ya no está visible (posible aplicación).")
    except Exception:
        print("Verificación: el menú sigue visible o no se pudo comprobar su cierre. Revisa manualmente si se aplicaron los cambios.")

    time.sleep(1)

    # ABRIR ACCIONES Y EXPORTAR
    print("6️⃣ Abriendo 'Acciones' y exportando...")
    acciones_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Acciones')]")))
    driver.execute_script("arguments[0].scrollIntoView(true);", acciones_btn)
    driver.execute_script("arguments[0].click();", acciones_btn)

    exportar_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Exportar')]")))
    driver.execute_script("arguments[0].scrollIntoView(true);", exportar_btn)
    driver.execute_script("arguments[0].click();", exportar_btn)
    print("✅ Datos exportados exitosamente.")

except Exception as e:
    print("❌ Error durante ejecución:", e)

finally:
    time.sleep(5)
   


# In[ ]:




