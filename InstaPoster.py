import re

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
import time

class InstagramBot:
    def __init__(self, chromedriver_path, username, password):
        """Inizializza il bot con il percorso di ChromeDriver, nome utente e password"""
        self.chromedriver_path = chromedriver_path
        self.username = username
        self.password = password

        # Crea un oggetto Service con il percorso di ChromeDriver
        service = Service(executable_path=self.chromedriver_path)

        # Crea un oggetto ChromeOptions per impostazioni specifiche
        options = webdriver.ChromeOptions()
        options.add_argument('--disable-notifications')  # Disabilita le notifiche del browser

        # Avvia il browser
        self.driver = webdriver.Chrome(service=service, options=options)

    def login(self):
        """Effettua il login su Instagram"""
        self.driver.get("https://www.instagram.com/accounts/login/")
        time.sleep(2)

        # Trova i campi per il login
        username_field = self.driver.find_element(By.NAME, "username")
        password_field = self.driver.find_element(By.NAME, "password")

        # Inserisci le credenziali
        username_field.send_keys(self.username)
        password_field.send_keys(self.password)

        # Premi il tasto Enter per fare login
        password_field.send_keys(Keys.RETURN)
        time.sleep(10)  # Attendi che la pagina carichi

    def publish_post(self, image_path, caption):
        """Pubblica un post con l'immagine e la didascalia fornita"""
        # Vai alla home per assicurarti di essere loggato
        self.driver.get("https://www.instagram.com/")
        time.sleep(5)

        # Clicca sull'icona "+" per creare un nuovo post
        upload_icon = self.driver.find_element(By.CSS_SELECTOR, 'svg[aria-label="New post"]')
        upload_icon.click()
        time.sleep(2)
        post_button = self.driver.find_element(By.XPATH, '//span[text()="Post"]')
        post_button.click()
        time.sleep(2)
        # Usa JavaScript per rendere visibile l'input file nascosto
        upload_input = self.driver.find_element(By.XPATH, '//input[@type="file"]')
        self.driver.execute_script("arguments[0].style.display = 'block';", upload_input)
        basepath= 'C:\\Vittoria\\Proposte\\it\\ig\\';
        # Carica l'immagine
        upload_input.send_keys(basepath+"final_design.png")
        time.sleep(5)

        # Clicca su "Avanti"
        next_button = self.driver.find_element(By.XPATH, '//div[text()="Next"]')
        next_button.click()
        time.sleep(3)
        # Clicca su "Avanti"
        next_button = self.driver.find_element(By.XPATH, '//div[text()="Next"]')
        next_button.click()
        time.sleep(5)
        # Inserisci la didascalia
        caption_field = self.driver.find_element(By.XPATH,'//div[@aria-label="Write a caption..." and @contenteditable="true"]')
        caption_field.click()  # Clicca sul campo per attivarlo


        # Funzione per rimuovere caratteri non BMP
        def remove_non_bmp_chars(text):
            return re.sub(r'[^\u0000-\uFFFF]', '', text)



        # Rimuove i caratteri non BMP
        safe_caption = remove_non_bmp_chars(caption)
        caption_field.send_keys(safe_caption)
        # Clicca su "Condividi"
        share_button = self.driver.find_element(By.XPATH, '//div[text()="Share"]')
        share_button.click()
        time.sleep(5)  # Attendi che il post venga pubblicato

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

def main():
    # Configurazioni per il bot
    poster = InstagramPoster(
                    chromedriver_path="chromedriver-win32/chromedriver.exe",
                    # Sostituisci con il tuo percorso di ChromeDriver
                    username="iltifosobarese",
                    password="Piccipallina1!",
                    image_path="final_design.png",
                    # Sostituisci con il percorso dell'immagine che vuoi caricare
                    caption="test"
                )

                # Esegui il post
    poster.post()



if __name__ == "__main__":
    main()