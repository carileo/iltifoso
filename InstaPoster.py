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
        print("Browser initialized successfully")

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
            print("Looking for username field...")
            username_input = self.wait.until(EC.presence_of_element_located((By.NAME, 'username')))
            print("OK username field...")
            print("Looking for PASSWORD field...")
            password_input = self.wait.until(EC.presence_of_element_located((By.NAME, 'password')))
            print("OK PASSWORD field...")
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
            print("Clicking login button...")
            time.sleep(10)  # Attesa per il completamento del login
            print("Login completed")
        except Exception as e:
            print(f"Errore durante il login: {str(e)}")
            self.driver.save_screenshot("login_error.png")
            raise


    def publish_post(self, image_path, caption):
        try:
            print("Starting post creation...")
            self.driver.get('https://www.instagram.com')
            time.sleep(5)

            print("Looking for create post button...")
            self.driver.save_screenshot("before_create_post.png")

            # Try different selectors for the create post button
            try:
                create_post_button = self.wait.until(EC.element_to_be_clickable(
                    (By.XPATH,
                     "//span[contains(@class, 'x1lliihq')]//*[local-name()='svg' and @aria-label='New post']")))
            except:
                print("First selector failed, trying alternative...")
                create_post_button = self.wait.until(EC.element_to_be_clickable(
                    (By.CSS_SELECTOR, "[aria-label='New post']")))

            print("Found create post button, clicking...")
            self.driver.execute_script("arguments[0].click();", create_post_button)
            time.sleep(3)

            self.driver.save_screenshot("after_create_button.png")

            print("Selecting post type...")
            post_button = self.wait.until(EC.element_to_be_clickable((By.XPATH, "//span[text()='Post']")))
            self.driver.execute_script("arguments[0].click();", post_button)
            time.sleep(3)

            print("Preparing to upload image...")
            file_input = self.wait.until(EC.presence_of_element_located((By.XPATH, "//input[@type='file']")))
            self.driver.execute_script("arguments[0].style.display = 'block';", file_input)

            absolute_path = os.path.abspath(image_path)
            print(f"Uploading image from: {absolute_path}")
            file_input.send_keys(absolute_path)
            time.sleep(5)

            print("Clicking through Next buttons...")
            for i in range(2):
                next_button = self.wait.until(EC.element_to_be_clickable((By.XPATH, "//div[text()='Next']")))
                self.driver.execute_script("arguments[0].click();", next_button)
                time.sleep(3)
                self.driver.save_screenshot(f"after_next_{i}.png")

            print("Adding caption...")
            caption_input = self.wait.until(EC.element_to_be_clickable(
                (By.XPATH, "//div[@aria-label='Write a caption...' and @contenteditable='true']")))
            self.driver.execute_script("arguments[0].click();", caption_input)
            caption_input.send_keys(caption)
            time.sleep(2)

            print("Sharing post...")
            share_button = self.wait.until(EC.element_to_be_clickable((By.XPATH, "//div[text()='Share']")))
            self.driver.execute_script("arguments[0].click();", share_button)
            time.sleep(10)

            print("Post published successfully!")
            self.driver.save_screenshot("post_success.png")

        except Exception as e:
            print(f"Failed to publish post: {str(e)}")
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




