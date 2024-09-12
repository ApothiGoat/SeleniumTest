import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.common.action_chains import ActionChains

def setup_driver(headless=True):
    chrome_options = Options()
    if headless:
        chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    service = Service(ChromeDriverManager().install())
    return webdriver.Chrome(service=service, options=chrome_options)

def login_certifact(driver, url, usuario, nit, clave):
    driver.get(url)
    print(f"Cargando URL: {url}")
    
    try:
        #Esperar a que la página se cargue completamente
        WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        
        print(f"Título de la página: {driver.title}")
        
        #Esperar a que los campos del formulario estén presentes y visibles
        usuario_field = WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.ID, ":r0:")))
        nit_field = WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.ID, ":r1:")))
        clave_field = WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.ID, ":r2:")))
        
        #Limpia campos antes de ingresar los datos
        usuario_field.clear()
        nit_field.clear()
        clave_field.clear()
        
        #Ingresar datos login
        usuario_field.send_keys(usuario)
        nit_field.send_keys(nit)
        clave_field.send_keys(clave)
        
        print("Formulario rellenado. Buscando el botón de inicio de sesión...")
        
        #Identificar le boton 
        button_locators = [
            (By.XPATH, "//button[contains(text(), 'Iniciar sesión')]"),
            (By.XPATH, "//button[@type='submit']"),
            (By.CSS_SELECTOR, "button[type='submit']"),
            (By.XPATH, "//form//button"),
        ]
        
        login_button = None
        for locator in button_locators:
            try:
                login_button = WebDriverWait(driver, 5).until(EC.element_to_be_clickable(locator))
                break
            except:
                continue
        
        if login_button:
            print("Botón de inicio de sesión encontrado. Intentando hacer clic...")
            
            #Hacer clic sobre el boton
            try:
                login_button.click()
            except:
                try:
                    ActionChains(driver).move_to_element(login_button).click().perform()
                except:
                    driver.execute_script("arguments[0].click();", login_button)
            
            print("Se intentó hacer clic en el botón 'Iniciar sesión'")
            
            #Esperar al dashboard para confirmar que se logró ingresar 
            try:
                WebDriverWait(driver, 20).until(lambda d: "dashboard" in d.current_url or len(d.find_elements(By.XPATH, "//div[contains(@class, 'dashboard-item')]")) > 0)
            except:
                print("No se detectó cambio a la página del dashboard")
        else:
            print("No se pudo encontrar el botón de inicio de sesión")
        
        #Verificar si el login fue exitoso
        if "dashboard" in driver.current_url:
            print("Login exitoso")
            print(f"URL actual: {driver.current_url}")
            
            #Intentar encontrar elementos que confirmen el inicio de sesión exitoso
            try:
                username_element = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, "//div[contains(@class, 'username')] | //span[contains(@class, 'user-name')]"))
                )
                print(f"Nombre de usuario encontrado: {username_element.text}")
            except:
                print("No se pudo encontrar el elemento con el nombre de usuario")
            
            #Imprimir los primeros elementos del dashboard
            dashboard_elements = driver.find_elements(By.XPATH, "//div[contains(@class, 'dashboard-item')] | //div[contains(@class, 'menu-item')]")
            print("Elementos del dashboard encontrados:")
            for element in dashboard_elements[:5]:  # Imprimir los primeros 5 elementos
                print(f"- {element.text}")
        else:
            print("Login aparentemente fallido")
            print(f"URL actual: {driver.current_url}")
            
            #Buscar mensajes de error
            try:
                error_message = driver.find_element(By.XPATH, "//div[contains(@class, 'error-message')] | //span[contains(@class, 'error')]")
                print(f"Mensaje de error encontrado: {error_message.text}")
            except:
                print("No se encontró un mensaje de error específico")
        
        #Imprimir el título de la página después del intento de login
        print(f"Título de la página después del intento de login: {driver.title}")
        
    except TimeoutException as e:
        print(f"Error de tiempo de espera: {e}")
        print(f"URL actual: {driver.current_url}")
    except NoSuchElementException as e:
        print(f"Elemento no encontrado: {e}")
    except Exception as e:
        print(f"Error inesperado: {e}")
    
    #Imprimir una parte del contenido de la página para depuración
    print(f"Fragmento del contenido de la página:\n{driver.page_source[:1000]}...")

def main():
    url = "http://dev.certifact.com.s3-website-us-east-1.amazonaws.com/mainDashboard"
    usuario = os.environ.get('USUARIO')
    nit = os.environ.get('NIT')
    clave = os.environ.get('CLAVE')
    
    if not all([usuario, nit, clave]):
        raise ValueError("Las credenciales no están configuradas correctamente en las variables de entorno.")
    
    driver = setup_driver(headless=True)
    try:
        login_certifact(driver, url, usuario, nit, clave)
    finally:
        driver.quit()

if __name__ == "__main__":
    main()
