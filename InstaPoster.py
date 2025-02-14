import os
import re
import time
import tempfile
import shutil
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, ElementClickInterceptedException


class InstagramBotHeadless:
    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.driver = None
        self.temp_dir = None
        self.setup_driver()

    def setup_driver(self):
        """Configura il driver Chrome in modalità headless"""
        try:
            # Crea una directory temporanea per i dati utente
            self.temp_dir = tempfile.mkdtemp()

            options = Options()
            options.add_argument('--headless')  # Abilita modalità headless
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument(f'--user-data-dir={self.temp_dir}')
            options.add_argument('--window-size=1920,1080')  # Importante per elementi visibili
            options.add_argument('--disable-notifications')
            options.add_argument('--disable-gpu')
            options.add_argument('--disable-software-rasterizer')

            # Aggiungi user agent mobile per migliore compatibilità
            options.add_argument(
                '--user-agent=Mozilla/5.0 (iPhone; CPU iPhone OS 14_0_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 Instagram 170.0.0.30.255 (iPhone13,2; iOS 14_0_1; en_US; en-US; scale=3.00; 1170x2532; 264572602)')

            # Disabilita la modalità di automazione
            options.add_argument('--disable-blink-features=AutomationControlled')
            options.add_experimental_option('excludeSwitches', ['enable-automation'])
            options.add_experimental_option('useAutomationExtension', False)

            service = Service()
            self.driver = webdriver.Chrome(service=service, options=options)

            # Maschera ancora meglio l'automazione
            self.driver.execute_cdp_cmd('Network.setUserAgentOverride', {
                "userAgent": 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_0_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 Instagram 170.0.0.30.255'
            })

            # Maschera webdriver
            self.driver.execute_script(
                "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

        except Exception as e:
            print(f"Errore nella configurazione del driver: {e}")
            self.cleanup()
            raise

    def wait_and_find_element(self, by, value, timeout=20):
        """Attende e trova un elemento con gestione errori migliorata"""
        try:
            element = WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((by, value))
            )
            return element
        except TimeoutException:
            print(f"Timeout nel trovare l'elemento: {value}")
            # Salva screenshot per debug
            self.driver.save_screenshot(f"error_screenshot_{int(time.time())}.png")
            raise
        except Exception as e:
            print(f"Errore nel trovare l'elemento {value}: {e}")
            raise

    def login(self):
        """Effettua il login su Instagram"""
        try:
            print("Inizializzazione login...")
            self.driver.get("https://www.instagram.com/accounts/login/")
            time.sleep(5)  # Attesa per caricamento pagina

            # Login
            username_field = self.wait_and_find_element(By.NAME, "username")
            password_field = self.wait_and_find_element(By.NAME, "password")

            username_field.send_keys(self.username)
            password_field.send_keys(self.password)
            password_field.send_keys(Keys.RETURN)

            # Attendi il completamento del login
            time.sleep(8)

            # Verifica login
            try:
                self.wait_and_find_element(By.CSS_SELECTOR, "[aria-label='New post']", timeout=10)
                print("Login completato con successo")
            except Exception as e:
                print("Possibile errore nel login, verifica le credenziali")
                raise

        except Exception as e:
            print(f"Errore durante il login: {e}")
            self.driver.save_screenshot(f"login_error_{int(time.time())}.png")
            raise

    def publish_post(self, image_path, caption):
        """Pubblica un post su Instagram"""
        try:
            print("Inizio processo di pubblicazione...")

            # Verifica che il file esista
            if not os.path.exists(image_path):
                raise FileNotFoundError(f"Immagine non trovata: {image_path}")

            # Vai alla home di Instagram
            self.driver.get("https://www.instagram.com")
            time.sleep(5)

            # Trova e clicca il pulsante nuovo post
            new_post_button = self.wait_and_find_element(
                By.CSS_SELECTOR, "[aria-label='New post']")
            new_post_button.click()
            time.sleep(3)

            # Carica l'immagine
            file_input = self.wait_and_find_element(By.CSS_SELECTOR, "input[type='file']")
            file_input.send_keys(os.path.abspath(image_path))
            time.sleep(5)

            # Clicca i pulsanti Next
            for _ in range(2):
                next_button = self.wait_and_find_element(By.XPATH, "//button[text()='Next']")
                next_button.click()
                time.sleep(3)

            # Inserisci la caption
            caption_field = self.wait_and_find_element(
                By.CSS_SELECTOR, "[aria-label='Write a caption...']")
            caption_field.send_keys(caption)
            time.sleep(2)

            # Pubblica
            share_button = self.wait_and_find_element(By.XPATH, "//button[text()='Share']")
            share_button.click()

            # Attendi il completamento
            time.sleep(10)
            print("Post pubblicato con successo")

        except Exception as e:
            print(f"Errore durante la pubblicazione: {e}")
            self.driver.save_screenshot(f"publish_error_{int(time.time())}.png")
            raise

    def cleanup(self):
        """Pulisce le risorse"""
        try:
            if self.driver:
                self.driver.quit()
            if self.temp_dir and os.path.exists(self.temp_dir):
                shutil.rmtree(self.temp_dir, ignore_errors=True)
        except Exception as e:
            print(f"Errore durante la pulizia: {e}")


def post_to_instagram(username, password, image_path, caption):
    """Funzione wrapper per pubblicare su Instagram"""
    bot = None
    try:
        bot = InstagramBotHeadless(username, password)
        bot.login()
        bot.publish_post(image_path, caption)
        print("Processo completato con successo")
    except Exception as e:
        print(f"Errore durante il processo: {e}")
        raise
    finally:
        if bot:
            bot.cleanup()


# Esempio di utilizzo
if __name__ == "__main__":
    username = os.environ.get("INSTAGRAM_USERNAME")
    password = os.environ.get("INSTAGRAM_PASSWORD")
    image_path = "path/to/your/image.jpg"
    caption = "Your caption here #instagram #post"

    post_to_instagram(username, password, image_path, caption)