import os
import re
import tempfile
import shutil
import time
import psutil
import signal
import subprocess
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class InstagramBot:
    def __init__(self, chromedriver_path, username, password):
        self.chromedriver_path = chromedriver_path
        self.username = username
        self.password = password
        self.temp_dir = None
        self.driver = None
        self.workspace = os.environ.get('GITHUB_WORKSPACE', '')
        self.clean_environment()
        self.setup_driver()

    def clean_environment(self):
        """Pulizia aggressiva dell'ambiente"""
        try:
            if os.name == 'nt':  # Windows
                subprocess.run(['taskkill', '/F', '/IM', 'chrome.exe'], stderr=subprocess.DEVNULL)
                subprocess.run(['taskkill', '/F', '/IM', 'chromedriver.exe'], stderr=subprocess.DEVNULL)
            else:  # Linux/Mac
                subprocess.run(['pkill', '-f', 'chrome'], stderr=subprocess.DEVNULL)
                subprocess.run(['pkill', '-f', 'chromedriver'], stderr=subprocess.DEVNULL)
        except Exception:
            pass

        temp_locations = [
            tempfile.gettempdir(),
            '/tmp',
            '/var/tmp'
        ]

        for temp_loc in temp_locations:
            try:
                for item in os.listdir(temp_loc):
                    if 'chrome' in item.lower() or 'selenium' in item.lower():
                        full_path = os.path.join(temp_loc, item)
                        try:
                            if os.path.isfile(full_path):
                                os.remove(full_path)
                            elif os.path.isdir(full_path):
                                shutil.rmtree(full_path, ignore_errors=True)
                        except Exception:
                            pass
            except Exception:
                continue

        time.sleep(2)

    def setup_driver(self):
        """Inizializza il driver con impostazioni ottimizzate"""
        try:
            timestamp = str(int(time.time() * 1000))
            random_suffix = os.urandom(8).hex()
            self.temp_dir = os.path.join(
                tempfile.gettempdir(),
                f'chrome_temp_{timestamp}_{random_suffix}'
            )
            os.makedirs(self.temp_dir, exist_ok=True)

            chromedriver_path = os.environ.get("CHROMEDRIVER_PATH", "/usr/local/bin/chromedriver")
            service = Service(executable_path=chromedriver_path)

            options = webdriver.ChromeOptions()
            options.add_argument(f'--user-data-dir={self.temp_dir}')
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--disable-gpu')
            options.add_argument('--disable-notifications')
            options.add_argument('--window-size=1920,1080')
            options.add_argument('--disable-extensions')
            options.add_argument('--disable-infobars')
            options.add_argument('--disable-browser-side-navigation')
            options.add_argument('--disable-features=TranslateUI')
            options.add_argument('--disable-blink-features=AutomationControlled')
            options.add_argument('--disable-web-security')
            options.add_argument('--no-first-run')
            options.add_argument('--no-default-browser-check')
            options.add_argument('--no-startup-window')
            options.add_argument('--start-maximized')

            max_retries = 3
            for attempt in range(max_retries):
                try:
                    self.driver = webdriver.Chrome(service=service, options=options)
                    break
                except Exception as e:
                    print(f"Tentativo {attempt + 1} fallito: {str(e)}")
                    self.clean_environment()
                    if attempt == max_retries - 1:
                        raise
                    time.sleep(5)

        except Exception as e:
            print(f"Errore nell'inizializzazione del driver: {e}")
            self.clean_environment()
            raise

    def wait_and_find_element(self, by, value, timeout=20):
        """Attende che un elemento sia presente e lo trova con retry"""
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                element = WebDriverWait(self.driver, 5).until(
                    EC.presence_of_element_located((by, value))
                )
                return element
            except Exception as e:
                if time.time() - start_time >= timeout:
                    print(f"Elemento non trovato dopo {timeout} secondi: {value}")
                    raise
                time.sleep(1)
                continue

    def login(self):
        """Effettua il login su Instagram con gestione errori avanzata"""
        try:
            self.driver.get("https://www.instagram.com/accounts/login/")
            time.sleep(5)  # Attesa iniziale per caricamento completo

            try:
                # Gestione cookie popup se presente
                cookie_button = self.driver.find_elements(By.XPATH,
                                                          "//button[contains(text(), 'Accept') or contains(text(), 'Allow')]")
                if cookie_button:
                    cookie_button[0].click()
                    time.sleep(2)
            except Exception:
                pass  # Ignora se non trova il popup dei cookie

            username_field = self.wait_and_find_element(By.NAME, "username")
            password_field = self.wait_and_find_element(By.NAME, "password")

            # Pulisci i campi prima dell'inserimento
            username_field.clear()
            time.sleep(1)
            username_field.send_keys(self.username)
            time.sleep(1)

            password_field.clear()
            time.sleep(1)
            password_field.send_keys(self.password)
            time.sleep(1)

            password_field.send_keys(Keys.RETURN)

            # Attendi che il login sia completato verificando elementi della home
            self.wait_and_find_element(By.CSS_SELECTOR, '[aria-label="Home"]', timeout=30)
            time.sleep(5)  # Attesa addizionale per caricamento completo

        except Exception as e:
            print(f"Errore durante il login: {e}")
            # Salva screenshot per debug
            try:
                self.driver.save_screenshot(f"login_error_{int(time.time())}.png")
            except Exception:
                pass
            raise

    def publish_post(self, image_path, caption):
        """Pubblica un post su Instagram con gestione errori avanzata"""
        try:
            # Vai alla home e attendi caricamento completo
            self.driver.get("https://www.instagram.com/")
            time.sleep(5)

            # Clic su nuovo post con retry
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    upload_icon = self.wait_and_find_element(
                        By.CSS_SELECTOR, 'svg[aria-label="New post"]')
                    upload_icon.click()
                    break
                except Exception as e:
                    if attempt == max_retries - 1:
                        raise
                    time.sleep(2)

            post_button = self.wait_and_find_element(
                By.XPATH, '//span[text()="Post"]')
            post_button.click()
            time.sleep(2)

            # Gestione upload file
            upload_input = self.wait_and_find_element(
                By.XPATH, '//input[@type="file"]')
            self.driver.execute_script(
                "arguments[0].style.display = 'block';", upload_input)

            # Verifica percorso immagine
            full_image_path = os.path.join(self.workspace, image_path)
            print(f"Tentativo di caricare l'immagine da: {full_image_path}")

            if not os.path.exists(full_image_path):
                raise FileNotFoundError(f"File non trovato: {full_image_path}")

            upload_input.send_keys(full_image_path)
            time.sleep(5)

            # Gestione dei passaggi di pubblicazione
            for step in ["Next", "Next", "Share"]:
                button = self.wait_and_find_element(
                    By.XPATH, f'//div[text()="{step}"]')
                button.click()
                time.sleep(3)

                if step == "Next":  # Verifica che il passaggio sia completato
                    try:
                        WebDriverWait(self.driver, 10).until(
                            EC.presence_of_element_located((By.XPATH, f'//div[text()="{step}"]'))
                        )
                    except Exception:
                        pass  # Procedi se il bottone non è più visibile

            # Gestione caption
            caption_field = self.wait_and_find_element(
                By.XPATH, '//div[@aria-label="Write a caption..." and @contenteditable="true"]')
            caption_field.click()

            # Pulisci e formatta la caption
            safe_caption = re.sub(r'[^\u0000-\uFFFF]', '', caption)
            caption_field.send_keys(safe_caption)

            # Attendi completamento pubblicazione
            time.sleep(10)

        except Exception as e:
            print(f"Errore durante la pubblicazione del post: {e}")
            print(f"Directory corrente: {os.getcwd()}")
            print(f"Contenuto della directory di lavoro:")
            for root, dirs, files in os.walk(self.workspace):
                print(f"\nDirectory: {root}")
                for d in dirs:
                    print(f"  Dir: {d}")
                for f in files:
                    print(f"  File: {f}")

            # Salva screenshot per debug
            try:
                self.driver.save_screenshot(f"publish_error_{int(time.time())}.png")
            except Exception:
                pass
            raise

    def close_browser(self):
        """Chiudi il browser e pulisci l'ambiente"""
        try:
            if self.driver:
                self.driver.quit()
        except Exception:
            pass
        finally:
            self.clean_environment()
            if self.temp_dir and os.path.exists(self.temp_dir):
                try:
                    shutil.rmtree(self.temp_dir, ignore_errors=True)
                except Exception:
                    pass


class InstagramPoster:
    def __init__(self, chromedriver_path, username, password, image_path, caption):
        """Inizializza il poster con gestione errori"""
        try:
            self.bot = InstagramBot(chromedriver_path, username, password)
            self.image_path = image_path
            self.caption = caption
            print(f"InstagramPoster inizializzato con successo")
        except Exception as e:
            print(f"Errore nell'inizializzazione di InstagramPoster: {e}")
            raise

    def post(self):
        """Esegue la pubblicazione del post con gestione errori completa"""
        try:
            print("Inizio processo di pubblicazione...")
            self.bot.login()
            print("Login completato con successo")

            self.bot.publish_post(self.image_path, self.caption)
            print("Post pubblicato con successo")

        except Exception as e:
            print(f"Errore durante il processo di pubblicazione: {e}")
            raise
        finally:
            try:
                print("Chiusura delle risorse...")
                self.bot.close_browser()
                print("Risorse chiuse con successo")
            except Exception as e:
                print(f"Errore durante la chiusura delle risorse: {e}")