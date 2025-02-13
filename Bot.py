from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
import time

# Imposta il percorso di ChromeDriver
chromedriver_path = "chromedriver-win32/chromedriver.exe"  # Sostituisci con il percorso reale

# Crea un oggetto Service con il percorso di ChromeDriver
service = Service(executable_path=chromedriver_path)

# Avvia il browser Chrome
options = webdriver.ChromeOptions()
options.add_argument('--disable-notifications')  # Disabilita le notifiche del browser

# Apre il browser con il ChromeDriver
driver = webdriver.Chrome(service=service, options=options)


# Funzione per effettuare il login su Instagram
def login(username, password):
    driver.get("https://www.instagram.com/accounts/login/")

    time.sleep(2)

    # Trova i campi per il login
    username_field = driver.find_element(By.NAME, "username")
    password_field = driver.find_element(By.NAME, "password")

    # Inserisci le credenziali
    username_field.send_keys(username)
    password_field.send_keys(password)

    # Premi il tasto Enter per fare login
    password_field.send_keys(Keys.RETURN)

    time.sleep(5)  # Attendi che la pagina carichi


# Funzione per pubblicare un post
def publish_post(image_path, caption):
    # Vai alla pagina di creazione post
    driver.get("https://www.instagram.com/create/style/")

    time.sleep(2)

    # Trova e carica il file immagine
    upload_button = driver.find_element(By.XPATH, '//input[@type="file"]')
    upload_button.send_keys(image_path)

    time.sleep(3)

    # Aggiungi la descrizione del post
    caption_field = driver.find_element(By.XPATH, '//textarea[@aria-label="Write a caption…"]')
    caption_field.send_keys(caption)

    # Clicca sul pulsante "Condividi"
    share_button = driver.find_element(By.XPATH, '//button[text()="Share"]')
    share_button.click()

    time.sleep(5)  # Attendi che il post venga pubblicato


# Esegui il login
login("iltifosobarese", "Piccipallina1!")

# Pubblica un post
publish_post("C:/path/to/your/image.jpg", "Questa è una didascalia per il mio post!")

# Chiudi il browser
driver.quit()
