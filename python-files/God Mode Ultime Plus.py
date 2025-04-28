from urllib.request import urlopen
from urllib.parse import urljoin
from html.parser import HTMLParser
import csv
import re

# Liste des URLs des dossiers contenant les images
urls = [
    "https://www.chronodiffusion2.be/inno/bauhaus/",
    "https://www.chronodiffusion2.be/inno/boss-jewelry/",
    "https://www.chronodiffusion2.be/inno/boss/",
    "https://www.chronodiffusion2.be/inno/calvin-klein-jewelry/",
    "https://www.chronodiffusion2.be/inno/calvin-klein-watches/",
    "https://www.chronodiffusion2.be/inno/casio/",
    "https://www.chronodiffusion2.be/inno/hugo-boss/",
    "https://www.chronodiffusion2.be/inno/hugo/",
    "https://www.chronodiffusion2.be/inno/iron-annie/",
    "https://www.chronodiffusion2.be/inno/lacoste-jewelry/",
    "https://www.chronodiffusion2.be/inno/lacoste/",
    "https://www.chronodiffusion2.be/inno/pontiac/",
    "https://www.chronodiffusion2.be/inno/river-woods/",
    "https://www.chronodiffusion2.be/inno/scuderia-ferrari/",
    "https://www.chronodiffusion2.be/inno/timex/",
    "https://www.chronodiffusion2.be/inno/tommy-hilfiger-jewelry/",
    "https://www.chronodiffusion2.be/inno/tommy-hilfiger-watches/",
    "https://www.chronodiffusion2.be/inno/welder/",
    "https://www.chronodiffusion2.be/inno/withings/",
    "https://www.chronodiffusion2.be/inno/zeppelin/"
]

# Parser pour extraire les liens des images .jpg
class ImageParser(HTMLParser):
    def __init__(self, base_url):
        super().__init__()
        self.base_url = base_url
        self.jpg_images = []

    def handle_starttag(self, tag, attrs):
        if tag == "a":
            attrs = dict(attrs)
            href = attrs.get("href")
            if href and href.lower().endswith(".jpg"):  # Vérifie si c'est une image .jpg
                absolute_url = urljoin(self.base_url, href)
                self.jpg_images.append(absolute_url)

# Fonction pour extraire la base du nom (avant le premier underscore ou .jpg)
def extract_base_name(url):
    filename = url.split('/')[-1]
    base_name = re.split(r'_\d+|\.jpg', filename, maxsplit=1)[0]
    return base_name

# Fonction pour extraire le numéro de variante (0 pour l'image principale)
def extract_variant_number(url):
    filename = url.split('/')[-1]
    match = re.search(r'_(\d+)\.jpg$', filename)
    if match:
        return int(match.group(1))
    else:
        return 0  # Image principale sans suffixe

# Dictionnaire pour regrouper toutes les images trouvées
grouped_images = {}

# Traiter toutes les URLs
for url in urls:
    print(f"🔹 Traitement de {url}")
    try:
        with urlopen(url) as response:
            html_bytes = response.read()
            html = html_bytes.decode("utf-8", errors="ignore")
    except Exception as e:
        print(f"❌ Erreur lors du chargement du dossier {url} :", e)
        continue

    # Créer un parser pour extraire les images .jpg
    parser = ImageParser(url)
    parser.feed(html)

    if parser.jpg_images:
        print(f"✅ {len(parser.jpg_images)} images trouvées dans {url}")

        for img_url in parser.jpg_images:
            base_name = extract_base_name(img_url)
            if base_name not in grouped_images:
                grouped_images[base_name] = []
            grouped_images[base_name].append(img_url)
    else:
        print(f"⚠️ Aucune image .jpg trouvée dans {url}")

# Maintenant, écrire tout dans un seul fichier CSV
if grouped_images:
    print("✅ Génération du fichier CSV 'images_liste.csv'...")

    with open("images_liste.csv", mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)

        for images in grouped_images.values():
            sorted_images = sorted(images, key=extract_variant_number)
            writer.writerow(sorted_images)

    print("✅ Fichier CSV 'images_liste.csv' créé avec succès.")
else:
    print("⚠️ Aucune image trouvée dans l'ensemble des dossiers.")