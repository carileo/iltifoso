from PIL import Image, ImageDraw, ImageFont
import requests
from io import BytesIO

class CanvaDesign:
    def __init__(self, template_path, image_path, title, subtitle, font_path="LeagueGothic-Regular.ttf", font_size=80):
        """
        Inizializza il design con template, immagine, titolo e sottotitolo.
        :param template_path: Percorso del template (PNG con trasparenza)
        :param image_path: Percorso dell'immagine da inserire sopra il template
        :param title: Titolo da inserire nel design
        :param subtitle: Sottotitolo da inserire nel design
        :param font_path: Percorso del file del font (opzionale)
        :param font_size: Dimensione del font per il testo (opzionale)
        """
        self.template_path = template_path
        self.image_path = image_path
        self.title = title
        self.subtitle = subtitle
        self.font_path = font_path
        self.font_size = font_size
        self.final_image = None

    def create_design(self):
        """
        Crea l'immagine finale con il template, l'immagine da inserire, e il testo.
        """
        # 📌 Caricare il template di Canva (deve avere aree trasparenti)
        template = Image.open(self.template_path).convert("RGBA")  # Assicura trasparenza

        # 📌 Caricare l'immagine da inserire
        overlay = Image.open(self.image_path).convert("RGBA")

        # 📌 Ridimensionare l'immagine da inserire per adattarla al template
        overlay = overlay.resize(template.size)

        # 📌 Creare una nuova immagine con lo sfondo e il template
        self.final_image = Image.new("RGBA", template.size)  # Crea una nuova immagine vuota
        self.final_image.paste(overlay, (0, 0))  # Inserisce l'immagine nello sfondo
        self.final_image.paste(template, (0, 0), template)  # Inserisce il template sopra mantenendo trasparenze

        # 📌 Aggiungere il testo (titolo e sottotitolo)
        draw = ImageDraw.Draw(self.final_image)
        font = ImageFont.truetype(self.font_path, self.font_size)  # Carica il font

        # Aggiungi il titolo
        title_position = (52.5, 798.7)  # Posizione del titolo
        draw.text(title_position, self.title, font=font, fill="white")

        # Aggiungi il sottotitolo
        subtitle_position = (52.5, 905.7)  # Posizione del sottotitolo
        draw.text(subtitle_position, self.subtitle, font=font, fill="white")

    def save_image(self, output_path="final_design.png"):
        """
        Salva l'immagine finale su disco.
        :param output_path: Percorso dove salvare l'immagine finale
        """
        if self.final_image:
            self.final_image.save(output_path, "PNG")
            print(f"✅ Immagine salvata con successo come {output_path}")
        else:
            print("❌ Immagine non creata! Esegui create_design() prima.")

# 📌 Esempio di utilizzo
if __name__ == "__main__":
    # Creazione del design
    template_path = "templatetrasparente.png"  # Cambia con il tuo template
    image_path = "imagetoinsert.png"  # Cambia con l'immagine che vuoi inserire
    title = "TITLE"
    subtitle = "SUBTITLE"

    # Creazione dell'oggetto CanvaDesign
    canva_design = CanvaDesign(template_path, image_path, title, subtitle)

    # Creazione dell'immagine
    canva_design.create_design()

    # Salvataggio dell'immagine finale
    canva_design.save_image("final_design.png")
