import os
import re
from selenium.webdriver.support import expected_conditions as EC

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
import time

from selenium.webdriver.support.wait import WebDriverWait


class InstagramBot:
    def __init__(self, chromedriver_path, username, password):
        """Inizializza il bot con il percorso di ChromeDriver, nome utente e password"""
        self.chromedriver_path = chromedriver_path
        self.username = username
        self.password = password

        # Crea un oggetto Service con il percorso di ChromeDriver
        #rewritechromedriver path
        # Usa il percorso del chromedriver che hai impostato in GitHub Actions

        chromedriver_path = os.environ.get("CHROMEDRIVER_PATH", "/usr/local/bin/chromedriver")

        service = Service(executable_path=chromedriver_path)

        # Crea un oggetto ChromeOptions per impostazioni specifiche
        options = webdriver.ChromeOptions()
        # Configurazioni specifiche per modalità headless
        options.add_argument('--headless=new')  # Usa la nuova modalità headless
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        ##aggiunta per configurazione yaml

        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--window-size=1920,1080')
        options.add_argument('--start-maximized')
        options.add_argument('--disable-notifications')

        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        # Avvia il browser
        self.driver = webdriver.Chrome(service=service, options=options)

        # Modifica le proprietà del webdriver per evitare il rilevamento
        self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

        self.wait = WebDriverWait(self.driver, 20)
    def login(self):
        try:
            # Carica la pagina di login
            self.driver.get('https://www.instagram.com/accounts/login')
            time.sleep(5)  # Attesa per il caricamento completo

            # Gestione dei cookie se necessario
            try:
                cookie_button = self.wait.until(
                    EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Accept')]")))
                cookie_button.click()
                time.sleep(2)
            except:
                pass

            # Login
            username_input = self.wait.until(EC.presence_of_element_located((By.NAME, 'username')))
            password_input = self.wait.until(EC.presence_of_element_located((By.NAME, 'password')))

            # Simula input umano
            for char in self.username:
                username_input.send_keys(char)
                time.sleep(0.1)
            time.sleep(0.5)

            for char in self.password:
                password_input.send_keys(char)
                time.sleep(0.1)

            # Click sul pulsante di login
            login_button = self.wait.until(EC.element_to_be_clickable((By.XPATH, "//button[@type='submit']")))
            self.driver.execute_script("arguments[0].click();", login_button)

            time.sleep(10)  # Attesa per il completamento del login

        except Exception as e:
            print(f"Errore durante il login: {str(e)}")
            self.driver.save_screenshot("login_error.png")
            raise

    def publish_post(self, image_path, caption):
        try:
            self.driver.get('https://www.instagram.com')
            time.sleep(5)

            # Click sull'icona per creare nuovo post
            create_post_button = self.wait.until(EC.element_to_be_clickable(
                (By.XPATH, "//span[contains(@class, 'x1lliihq')]//*[local-name()='svg' and @aria-label='New post']")))
            self.driver.execute_script("arguments[0].click();", create_post_button)
            time.sleep(3)

            # Seleziona tipo post
            post_button = self.wait.until(EC.element_to_be_clickable((By.XPATH, "//span[text()='Post']")))
            self.driver.execute_script("arguments[0].click();", post_button)
            time.sleep(3)

            # Upload immagine
            file_input = self.wait.until(EC.presence_of_element_located((By.XPATH, "//input[@type='file']")))
            self.driver.execute_script("arguments[0].style.display = 'block';", file_input)

            # Usa il percorso assoluto dell'immagine
            absolute_path = os.path.abspath(image_path)
            file_input.send_keys(absolute_path)
            time.sleep(5)

            # Click sui pulsanti Next
            for _ in range(2):
                next_button = self.wait.until(EC.element_to_be_clickable((By.XPATH, "//div[text()='Next']")))
                self.driver.execute_script("arguments[0].click();", next_button)
                time.sleep(3)

            # Inserisci caption
            caption_input = self.wait.until(EC.element_to_be_clickable(
                (By.XPATH, "//div[@aria-label='Write a caption...' and @contenteditable='true']")))
            self.driver.execute_script("arguments[0].click();", caption_input)

            # Simula input umano per la caption
            for char in caption:
                caption_input.send_keys(char)
                time.sleep(0.05)
            time.sleep(2)

            # Condividi post
            share_button = self.wait.until(EC.element_to_be_clickable((By.XPATH, "//div[text()='Share']")))
            self.driver.execute_script("arguments[0].click();", share_button)
            time.sleep(10)

        except Exception as e:
            print(f"Errore durante la pubblicazione: {str(e)}")
            self.driver.save_screenshot("post_error.png")
            raise

    def close_browser(self):
        """Chiudi il browser"""
        self.driver.quit()


# Classe per inviare un post
class InstagramPoster:
    def __init__(self, chromedriver_path, username, password, image_path, caption):
        self.bot = InstagramBot(chromedriver_path, username, password)
        self.image_path = image_path
        self.caption = caption

    def post(self):
        """Effettua il login e pubblica il post"""
        self.bot.login()  # Esegui il login
        self.bot.publish_post(self.image_path, self.caption)  # Pubblica il post
        self.bot.close_browser()  # Chiudi il browser




