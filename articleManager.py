import requests
from bs4 import BeautifulSoup


class WebScraper:
    def __init__(self, base_url, headers=None):
        """
        Inizializza il WebScraper con un'URL di base e opzioni per gli headers.
        :param base_url: URL di base del sito web
        :param headers: Dizionario con gli headers della richiesta HTTP
        """
        self.base_url = base_url
        self.headers = headers if headers else {}

    def get_parsed_page(self, next_page_relative_url):
        """
        Effettua una richiesta GET per ottenere e analizzare la pagina HTML.
        :param next_page_relative_url: URL relativo della pagina da caricare
        :return: Oggetto BeautifulSoup con il parsing della pagina
        """
        page = requests.get(self.base_url + next_page_relative_url, headers=self.headers)
        if page.status_code == 200:
            return BeautifulSoup(page.text, 'html.parser')
        else:
            raise Exception(f"Errore nel caricamento della pagina: {page.status_code}")