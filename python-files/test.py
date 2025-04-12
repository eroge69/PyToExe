import requests
import random
import time  # Importation du module time pour le délai
from faker import Faker
from datetime import datetime, timedelta

# Initialiser Faker pour générer des données aléatoires
faker = Faker()

# Fonction pour générer une date aléatoire
def random_iso_datetime():
    random_date = datetime.utcnow() - timedelta(days=random.randint(0, 365))
    random_time = random.randint(0, 86399)  # Nombre de secondes dans une journée
    final_date = random_date + timedelta(seconds=random_time, milliseconds=random.randint(0, 999))
    return final_date.strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'

# Fonction pour lire les emails depuis un fichier
def read_emails(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            emails = [line.strip() for line in file if line.strip()]
        return emails
    except FileNotFoundError:
        print("Erreur : Le fichier emails.txt est introuvable.")
        return []

# Charger les emails depuis le fichier
emails = read_emails('emails.txt')

# Vérifier si la liste d'emails est vide
if not emails:
    print("Aucun email trouvé dans emails.txt. Vérifiez le fichier et réessayez.")
    exit()

# Configuration de l'en-tête HTTP
headers = {
    'accept': 'application/json',
    'accept-language': 'en-US,en;q=0.9,ar;q=0.8,pt;q=0.7,fr;q=0.6,nl;q=0.5,de;q=0.4,it;q=0.3',
    'content-type': 'application/json',
    'origin': 'https://nxcfvd-wb.myshopify.com',
    'priority': 'u=1, i',
    'referer': 'https://nxcfvd-wb.myshopify.com/',
    'sec-ch-ua': '"Chromium";v="134", "Not:A-Brand";v="24", "Google Chrome";v="134"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'cross-site',
    'timezone': 'undefined',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36',
}

# Traiter chaque email du fichier
for email in emails:
    first_name = faker.first_name()
    last_name = faker.last_name()
    phone = "1" + "".join([str(random.randint(0, 9)) for _ in range(10)])
    country_code = random.randint(233, 233)  # Pays aléatoire
    created_at = random_iso_datetime()
    buyer_accepts_marketing = random.choice([True, False])  # Générer aléatoirement True ou False

    # Données de la commande
    json_data = {
        'order': {
            'created_at': created_at,
            'line_items': [
            {
                'product_id': 11909237539156,
                'variant_id': 51567760179540,
                'quantity': 1,
                'properties': {
                    '_orichi': 'nxcfvd-wb.myshopify.com_true_daomslajka@yopmail.com',
                },
                'shop_money': {
                    'amount': 500,
                    'currency_code': 'EUR',
                },
            },
        ],
            'customer_locale': 'en',
            'currency': 'EUR',
            'customer': {
                'email': email,
                'first_name': first_name,
                'last_name': last_name,
                'note': '',
                'phone': phone,
                'alternative_phone': '',
            },
            'email': email,
            'financial_status': 'pending',
            'shipping_address': {
                'first_name': first_name,
                'last_name': last_name,
                'phone': phone,
                'country': str(country_code),
                'province': '',
                'city': '',
                'address1': '',
                'zip': '',
            },
            'billing_address': {
                'first_name': first_name,
                'last_name': last_name,
                'phone': phone,
                'country': str(country_code),
                'province': '',
                'city': '',
                'address1': '',
                'zip': '',
            },
            'buyer_accepts_marketing': buyer_accepts_marketing,
            'shipping_lines': [],
        },
    }

    # Envoyer la requête POST
    try:
        response = requests.post(
            'https://cod.madgictracking.com/shops/nxcfvd-wb.myshopify.com/order-v2',
            headers=headers,
            json=json_data,
            timeout=10
        )
        print(f"Commande envoyée pour {email} ({first_name} {last_name}, {phone}, Pays: {country_code}, Marketing: {buyer_accepts_marketing}) → {response.status_code}: {response.text}")
    except requests.RequestException as e:
        print(f"Erreur pour {email}: {e}")
    
    # Pause d'une seconde entre chaque commande
    time.sleep(1)
