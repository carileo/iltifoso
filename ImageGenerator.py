from PIL import Image, ImageDraw, ImageFont
import requests
from io import BytesIO

# 📌 1. Caricare il template di Canva (deve avere aree trasparenti)
template_path = "templatetrasparente.png"  # Sostituisci con il tuo file
template = Image.open(template_path).convert("RGBA")  # Assicura trasparenza

# 📌 2. Caricare l'immagine da inserire sotto (esempio: da URL)
image_path = "imagetoinsert.png"
overlay = Image.open(image_path).convert("RGBA")

# 📌 3. Ridimensionare l'immagine di sfondo per adattarla al template
overlay = overlay.resize(template.size)

# 📌 4. Creare una nuova immagine con sfondo + template
final_image = Image.new("RGBA", template.size)  # Crea una nuova immagine vuota
final_image.paste(overlay, (0, 0))  # Inserisce l'immagine nello sfondo
final_image.paste(template, (0, 0), template)  # Inserisce il template sopra mantenendo trasparenze

# 📌 5. Aggiungere testo sopra l'immagine
draw = ImageDraw.Draw(final_image)
font = ImageFont.truetype("LeagueGothic-Regular.ttf", 80)  # Personalizza il font
TITLE = "TITLE"
text_position = (52.5, 798.7)
draw.text(text_position, TITLE, font=font, fill="white")

SUBTITLE = "SUBTITLE"
text_position = (52.5, 905.7)
draw.text(text_position, SUBTITLE, font=font, fill="white")

# 📌 6. Salvare l'immagine finale
final_image.save("final_design.png", "PNG")
print("✅ Immagine generata con successo!")