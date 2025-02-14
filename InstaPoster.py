import os
import re
import tempfile
import shutil
import time
import psutil
import signal
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
        self.setup_driver()

    def kill_chrome_processes(self):
        for proc in psutil.process_iter(['name']):
            try:
                if 'chrome' in proc.name().lower():
                    os.kill(proc.pid, signal.SIGTERM)
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass
        time.sleep(2)

    def clean_temp_dirs(self):
        if self.temp_dir and os.path.exists(self.temp_dir):
            try:
                shutil.rmtree(self.temp_dir)
            except Exception as e:
                print(f"Errore nella pulizia della directory temporanea: {e}")

    def setup_driver(self):
        self.kill_chrome_processes()
        self.clean_temp_dirs()

        # Crea una nuova directory temporanea con timestamp
        self.temp_dir = os.path.join(tempfile.gettempdir(), f'instagram_bot_{int(time.time())}')
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
        options.add_argument('--start-maximized')
        options.add_argument('--disable-extensions')
        options.add_argument('--disable-infobars')

        try:
            self.driver = webdriver.Chrome(service=service, options=options)
        except Exception as e:
            print(f"Errore nell'inizializzazione del driver: {e}")
            self.clean_temp_dirs()
            raise

    def wait_and_find_element(self, by, value, timeout=10):
        """Attende che un elemento sia presente e lo trova"""
        return WebDriverWait(self.driver, timeout).until(
            EC.presence_of_element_located((by, value))
        )

    def login(self):
        try:
            self.driver.get("https://www.instagram.com/accounts/login/")
            time.sleep(3)  # Attesa iniziale per il caricamento della pagina

            username_field = self.wait_and_find_element(By.NAME, "username")
            password_field = self.wait_and_find_element(By.NAME, "password")

            username_field.clear()
            username_field.send_keys(self.username)
            password_field.clear()
            password_field.send_keys(self.password)
            password_field.send_keys(Keys.RETURN)

            # Attendi che il login sia completato
            time.sleep(10)
        except Exception as e:
            print(f"Errore durante il login: {e}")
            raise

    def publish_post(self, image_path, caption):
        try:
            self.driver.get("https://www.instagram.com/")
            time.sleep(5)

            # Usa wait_and_find_element invece di find_element
            upload_icon = self.wait_and_find_element(
                By.CSS_SELECTOR, 'svg[aria-label="New post"]')
            upload_icon.click()
            time.sleep(2)

            post_button = self.wait_and_find_element(
                By.XPATH, '//span[text()="Post"]')
            post_button.click()
            time.sleep(2)

            upload_input = self.wait_and_find_element(
                By.XPATH, '//input[@type="file"]')
            self.driver.execute_script(
                "arguments[0].style.display = 'block';", upload_input)

            # Usa os.path.join per il percorso del file
            full_image_path = os.path.join(os.environ.get('GITHUB_WORKSPACE', ''), 'final_design.png')
            upload_input.send_keys(full_image_path)
            time.sleep(5)

            for step in ["Next", "Next", "Share"]:
                button = self.wait_and_find_element(
                    By.XPATH, f'//div[text()="{step}"]')
                button.click()
                time.sleep(3)

            caption_field = self.wait_and_find_element(
                By.XPATH, '//div[@aria-label="Write a caption..." and @contenteditable="true"]')
            caption_field.click()

            safe_caption = re.sub(r'[^\u0000-\uFFFF]', '', caption)
            caption_field.send_keys(safe_caption)

            time.sleep(5)
        except Exception as e:
            print(f"Errore durante la pubblicazione del post: {e}")
            raise

    def close_browser(self):
        try:
            if self.driver:
                self.driver.quit()
        finally:
            self.kill_chrome_processes()
            self.clean_temp_dirs()


class InstagramPoster:
    def __init__(self, chromedriver_path, username, password, image_path, caption):
        self.bot = InstagramBot(chromedriver_path, username, password)
        self.image_path = image_path
        self.caption = caption

    def post(self):
        try:
            self.bot.login()
            self.bot.publish_post(self.image_path, self.caption)
        finally:
            self.bot.close_browser()