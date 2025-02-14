import requests


class GoogleImageSearch:
    def __init__(self, query, api_key):
        """
        Inizializza la classe con la query di ricerca e la API key.

        :param query: Testo della ricerca per immagini (es. "caffè italiano")
        :param api_key: La chiave API di SerpAPI
        """
        self.query = query
        self.api_key = api_key

    def get_image_url(self):
        """
        Esegue una ricerca di immagini su Google tramite SerpAPI e restituisce l'URL dell'immagine.

        :return: URL dell'immagine trovata o None se non ci sono risultati
        """
        url = "https://serpapi.com/search"

        params = {
            'engine': 'google_images',
            "q": self.query,  # La query di ricerca
            "tbm": "isch",  # Specifica che vogliamo immagini
            "api_key": self.api_key,  # La chiave API
            "num": 1  # Numero di immagini da restituire
        }

        # Fai la richiesta a SerpAPI
        response = requests.get(url, params=params)
        data = response.json()

        # Se sono presenti risultati di immagini, restituisci l'URL dell'immagine
        if "images_results" in data and len(data["images_results"]) > 0:
            return data["images_results"][0]["original"]
        return None  # Se non ci sono risultati

    def save_image(self, image_url, filename):
        """
        Scarica l'immagine da un URL e la salva nel filesystem.

        :param image_url: URL dell'immagine da scaricare
        :param filename: Nome del file in cui salvare l'immagine
        """
        try:
            # Richiesta per scaricare l'immagine
            response = requests.get(image_url)

            # Se la risposta è OK, salva l'immagine
            if response.status_code == 200:
                with open(filename, 'wb') as file:
                    file.write(response.content)
                print(f"Immagine salvata come {filename}")
            else:
                print("Errore nel download dell'immagine.")
        except Exception as e:
            print(f"Errore nel salvataggio dell'immagine: {e}")



