import os

import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
import re

from AiArticlesText import HashtagTextEnhancer
from InstaPoster import InstagramPoster
from MongoManager import MongoDBManager
from SerpImageGoogle import GoogleImageSearch
from articleManager import WebScraper
from imageGeneratorFile import CanvaDesign


# scraping logic
# Funzione per estrarre il numero da un URL
load_dotenv()

# Recupera le credenziali dall'ambiente
uri = os.getenv("MONGO_URI")
api_key = os.getenv("API_KEY")
username = os.getenv("INSTA_USERNAME")
password = os.getenv("INSTA_PASSWORD")
db_manager = MongoDBManager(uri, "ArticlesRead", "Article")
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36'
}
baseurl='https://www.tuttobari.com/'
page = requests.get(baseurl,headers=headers)
soup = BeautifulSoup(page.text,'html.parser')
links = soup.select('ul.list-unstyled a')
hrefs = [link['href'] for link in links]
# Estrai i numeri da tutti gli URL
def extract_number(hrefs):
    match = re.search(r'(\d+)$', hrefs)
    return int(match.group(1)) if match else None


numbers = [extract_number(url) for url in hrefs]
urlArticle=""
max_number = max(numbers)
document = db_manager.find_document({"idArticle": max_number})
for href in hrefs:
    if(extract_number(href)==max_number and document is None):
        urlArticle=href
        scraper = WebScraper(baseurl, headers)
        try:
            soup = scraper.get_parsed_page(urlArticle)
            paragraphs = soup.find_all("p")  # Trova tutti i tag <p>
            # Unisci il testo di tutti i <p> in un'unica stringa
            full_text = "\n".join([p.get_text(strip=True) for p in paragraphs])
            print(full_text)  # Stampa il testo estratto
            enhancer = HashtagTextEnhancer()
            testo_migliorato = enhancer.enhance_text(full_text)
            final_text = (
                f"{testo_migliorato.rewritten_text}\n\n"
                f"Hashtag: {' '.join(testo_migliorato.hashtags)}\n\n"
                f"Titolo: {testo_migliorato.title}\n"
                f"Sottotitolo: {testo_migliorato.subtitle}\n"
                f"description: {testo_migliorato.description}"
            )
            print(final_text)
            query = testo_migliorato.description   # Testo della ricerca
            image_search = GoogleImageSearch(query, api_key)
            image_url = image_search.get_image_url()

            if image_url:
                print(f"Immagine trovata: {image_url}")
                image_search.save_image(image_url, "new.jpg")
                # Creazione dell'oggetto CanvaDesign
                canva_design = CanvaDesign("templatetrasparente.png", "new.jpg", testo_migliorato.title, testo_migliorato.subtitle)

                # Creazione dell'immagine
                canva_design.create_design()

                # Salvataggio dell'immagine finale
                canva_design.save_image("final_design.png")
                # Inserisci le tue credenziali Instagram


                # Crea un'istanza di InstagramBot
                poster = InstagramPoster(
                    chromedriver_path="chromedriver-win32/chromedriver.exe",
                    # Sostituisci con il tuo percorso di ChromeDriver
                    username=username,
                    password=password,
                    image_path="final_design.png",
                    # Sostituisci con il percorso dell'immagine che vuoi caricare
                    caption=(f"{testo_migliorato.rewritten_text}\n\n"
                             f"{' '.join(testo_migliorato.hashtags)}\n\n")
                )

                # Esegui il post
                poster.post()

                # Specifica il percorso della foto e la didascalia
                photo_path = "final_design.png"  # Modifica con il percorso corretto
                caption = testo_migliorato.rewritten_text + " " + testo_migliorato.hastags

                new_document = {"idArticle": max_number, "url": urlArticle}
                doc_id = db_manager.insert_document(new_document)
                print(f"Documento inserito con ID: {doc_id}")

            else:
                print("Nessuna immagine trovata.")



        except Exception as e:
            print(f"Errore: {e}")

        print(href)
    else :continue














