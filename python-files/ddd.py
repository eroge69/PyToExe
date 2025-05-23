import pygame
import random
import time
import os
import requests
import json
import discordrpc
from discordrpc.button import Button
from pypresence import Presence
from PIL import Image, ImageSequence
import socket

# -----------------------------------------------------------------------------
# Fenêtre

pygame.init()

info = pygame.display.Info()
screen = pygame.display.set_mode((info.current_w, info.current_h), pygame.FULLSCREEN)
pygame.display.set_caption("[RNG🍀]Pet Collector XXL")

icon = pygame.image.load("gui/icon2.png")
pygame.display.set_icon(icon)

font_timer = pygame.font.Font("font/BackGroove.ttf", 30) if os.path.exists("font/BackGroove.ttf") else pygame.font.SysFont(None, 30)
button_image = pygame.image.load("gui/bouton.png")
button_rect = button_image.get_rect(center=(960, 865))
button_image = pygame.transform.scale(button_image, (500, 209))

inventory_button_image = pygame.image.load("gui/iconpet.png")
inventory_button_image = pygame.transform.scale(inventory_button_image, (150, 150))

inventory_button_rect = inventory_button_image.get_rect(center=(125, 540))


inventory_visible = False  

clock = pygame.time.Clock()
frame_index = 0
frame_rate = 100


def check_connection():
    try:
        socket.create_connection(("8.8.8.8", 53))  
        return True
    except OSError:
        return False

connected = check_connection()

def check_update():
    url = "https://github.com/Teamabeille/PetCollectorXXL/blob/main/version"  
    latest_version = requests.get(url).text.strip()

    current_version = "0.777"  # Change selon ta version actuelle

    if current_version != latest_version:
        print("Une mise à jour est disponible !")
        download_update()
    else:
        print("Le jeu est à jour.")

def download_update():
    update_url = "https://monserveur.com/monjeu.exe"  # Lien du nouvel .exe
    response = requests.get(update_url)

    with open("monjeu.exe", "wb") as f:
        f.write(response.content)

    print("Mise à jour terminée ! Relance le jeu.")

if connected:
    try:
        from pypresence import Presence
        client_id = 1362468309638971665
        rpc = Presence(client_id)
        rpc.connect()

        rpc.update(
            state="https://discord.gg/Y89ABSA3yX",
            details="A RNG game better than Pet Go 🔥",
            large_image="cat",
            large_text="Pet Collector XXL",
            small_image="pp",
            small_text="In dev",
            buttons=[
                {"label": "Tiktok", "url": "https://www.tiktok.com/@petcollectorxxl"},
                {"label": "Discord Server", "url": "https://discord.gg/Y89ABSA3yX"}
            ]
        )

        discord_rpc_enabled = True  # ✅ Doit être **dans** le bloc try

    except ImportError:  # ✅ Aligné avec `try`
        print("Discord RPC non trouvé. Désactivation...")
        discord_rpc_enabled = False

    except Exception as e:  # ✅ Aligné avec `try`
        print(f"Erreur lors de l'initialisation de Discord RPC : {e}")
        discord_rpc_enabled = True


    def send_webhook(url, message):
        try:
            requests.post(url, json=message)
        except requests.exceptions.RequestException:
            print("Échec de l'envoi du message webhook.")

else:
    print("Mode hors connexion activé. RPC et webhooks désactivés.")

# -----------------------------------------------------------------------------
# Pseudo


nickname_image = pygame.image.load("gui/nickname2.png")
nickname_image = pygame.transform.scale(nickname_image, (400, 100))


try:
    font = pygame.font.Font("font/BackGroove.ttf", 50)
except FileNotFoundError:
    print("La police 'Back Groove' n'a pas été trouvée. Utilisation de la police par défaut.")
    font = pygame.font.SysFont(None, 50)


nickname_color = (255, 0, 255)


nickname_text = ""
if os.path.exists("nickname.txt"):
    with open("nickname.txt", "r") as file:
        nickname_text = file.read().strip()


if not nickname_text:
    input_active = True
    while input_active:
        input_surface = font.render("Enter your pseudo :", True, (255, 255, 255))
        input_rect = input_surface.get_rect(center=(960, 400))
        screen.blit(input_surface, input_rect)

        nickname_surface = font.render(nickname_text, True, nickname_color)
        nickname_rect = nickname_surface.get_rect(center=(960, 500))
        screen.blit(nickname_surface, nickname_rect)

        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    input_active = False
                elif event.key == pygame.K_BACKSPACE:
                    nickname_text = nickname_text[:-1]
                else:
                    nickname_text += event.unicode

    # Sauvegarde du pseudo dans un fichier
    with open("nickname.txt", "w") as file:
        file.write(nickname_text)

date = time.strftime("%Y-%m-%d %H:%M:%S")
if connected:
    def player_join(nickname_text, date):
        player_webhook_url = "https://discord.com/api/webhooks/1374818795494965392/WvcCJi0qHxkgzoIE5N-ojHf3HmaoSnnxaE8aWtcTJT0btDimcwFv8Y5iwyaibvybxTQA"
        message = {
            "embeds": [{
                "title": "👤 Une personne vient de lancer son jeu ! 👤",
                "description": f"🚀 「 ✦ {nickname_text} ✦ 」 vient de lancer son jeu 👋!",
                "color": 16711680,
                "thumbnail": {
                    "url": "https://emojibook.org/wp-content/uploads/2022/03/1-1-80.png"
                },
                "footer": {
                    "text": "Merci à lui de jouer au jeu ! 🔥"
                }
            }]
        }
        send_webhook(player_webhook_url, message)

#-----------------------------------------------------------------------------------------
# Roll count

# Charger l'image de la GUI Roll
roll_gui_image = pygame.image.load("gui/roll.png")
roll_gui_image = pygame.transform.scale(roll_gui_image, (175, 175))  
roll_gui_rect = roll_gui_image.get_rect(center=(650, 100))
roll_counter = 0 

font_roll = pygame.font.Font("font/BackGroove.ttf", 40) if os.path.exists("font/BackGroove.ttf") else pygame.font.SysFont(None, 40)



#-----------------------------------------------------------------------------------------
# Inventaire

current_page = 0  
pets_per_page = 5  


rarity_order = { 
    "Cat": 1,
    "Dog": 2,
    "Rabbit": 3,
    "Parrot": 4,
    "Axoltotl": 5,
    "Bear" : 6,
    "Golden Fish" : 7,
    "Green Fish" : 8,
    "Blue Fish" : 9,
    "Mac Cat" : 10,
    "Mac Dog" : 11,
    "Shark" : 12,
    "Ghost" :13,
    "Đ̷̷͝͠Σ̷̷̏͠P̷̷̾͡Я̷̷̋͞Ξ̷̷̌̽Ś̷̷͠S̷̷̓͠I̷̷̽̑Ω̷̷͆̾N̷̷̓̋": 100

} 



class PetInventory:
    def __init__(self, name, rarity, date_obtained, image_path, quantity=1): 
        self.name = name
        self.rarity = rarity
        self.date_obtained = date_obtained
        self.image_path = image_path
        self.quantity = quantity  

inventory = []

def save_inventory():
    data = {
        "roll_counter": roll_counter,  
        "inventory": [{
            "name": pet.name,
            "rarity": pet.rarity,
            "date_obtained": pet.date_obtained,
            "image_path": pet.image_path,
            "quantity": pet.quantity
        } for pet in inventory]
    }
    with open("inventory.json", "w") as file:
        json.dump(data, file, indent=4)



def load_inventory():
    global inventory, roll_counter
    if os.path.exists("inventory.json"):
        try:
            with open("inventory.json", "r") as file:
                data = json.load(file)
                
                roll_counter = data.get("roll_counter", 0)  
                inventory = [
                    PetInventory(
                        pet["name"],
                        pet["rarity"],
                        pet["date_obtained"],
                        pet["image_path"] if os.path.exists(pet.get("image_path", "")) else "pet/default.png",
                        pet.get("quantity", 1)
                    )
                    for pet in data.get("inventory", [])
                ]
        except (json.JSONDecodeError, FileNotFoundError):
            print("Erreur lors du chargement de l'inventaire. Réinitialisation...")
            inventory = []
            roll_counter = 0  



load_inventory()  
inventory.sort(key=lambda pet: rarity_order.get(pet.name, 999))  # trie


inventory_width, inventory_height = 900, 650  # Dimensions de l'inventaire
inventory_x = (screen.get_width() - inventory_width) // 2  # Centrer horizontalement
inventory_y = (screen.get_height() - inventory_height) // 2  # Centrer verticalement
inventory_rect = pygame.Rect(inventory_x, inventory_y, inventory_width, inventory_height)

prev_button_rect = pygame.Rect(inventory_x + 20, inventory_y + inventory_height - 60, 200, 50)
next_button_rect = pygame.Rect(inventory_x + inventory_width - 215, inventory_y + inventory_height - 60, 200, 50)

inventory_title_surface = font.render("INVENTORY", True, (0, 0, 0))  # Titre en noir
inventory_title_rect = inventory_title_surface.get_rect(center=(inventory_x + inventory_width // 2, inventory_y + 30))

xxl_button_rect = pygame.Rect(inventory_x + inventory_width - 110, inventory_y + 10, 100, 50)


# -----------------------------------------------------------------------------
# Roll & Pet

commun_pet = [ ("pet/cat.png", "Cat", (255, 255, 255), "1/2", 50, (300, 300)), 
             ("pet/dog.png", "Dog", (255, 255, 255), "1/3", 33.3333, (300, 300)), 
             ("pet/rabbit.png", "Rabbit", (255, 255, 255), "1/4", 25, (300, 350)), 
             ("pet/parrot.png", "Parrot", (255, 255, 255), "1/10", 10, (300, 300)), 
             ("pet/axolotl.png", "Axolotl", (255, 255, 255), "1/16", 6.25, (350, 300)), 
             ("pet/bear.png", "Bear", (255, 255, 255), "1/24", 4.166, (300, 300)), 
             ("pet/cat_mcdo.png", "Mac Cat", (255, 255, 0), "1/500", 0.2, (350, 300)), 
             ("pet/dog_mcdo.png", "Mac Dog", (255, 255, 0), "1/525", 0.1905, (300, 300)), 
             ("pet/ghost.png", "Ghost", (100, 100, 100), "1/700", 0.1428, (300, 300)),
             ("pet/BigMaskot.png", "Big Maskot", (0, 0, 0), "1/1 000", 0.1, (300, 300)),
             ("pet/hippomelon.png", "Hippomelon", (0, 255, 0), "1/6 900", 0.0145, (300, 300)) ] 



rainy_pet = [ ("pet/fish_golden.png", "Golden Fish", (255, 255, 255), "1/275", 0.3636, (300, 300)), 
            ("pet/fish_green.png", "Green Fish", (255, 255, 255), "1/350", 0.2857, (300, 300)), 
            ("pet/fish_blue.png", "Blue Fish", (255, 255, 255), "1/425", 0.2353, (300, 300)), 
            ("pet/shark.png", "Shark", (255, 255, 255), "1/750 ", 0.1333, (300, 300)), 
            ("pet/shark_whale.png", "Whale Shark", (255, 255, 255), "1/1 300", 0.0769, (350, 350)) ]

snow_pet =  [ ("pet/cat_snow.png", "Snow Cat", (255, 255, 255), "1/920", 0.1087, (300, 300)),
            ("pet/dog_snow.png", "Snow Dog", (255, 255, 255), "1/1 1 275", 0.0784, (300, 300)),
            ("pet/rabbit_white.png", "Snow Bunny", (255, 255, 255), "1/1 315", 0.0760, (300, 350)),
            ("pet/bear_polar.png", "Polar Bear", (255, 255, 255), "1/1 700", 0.0588, (300, 300)),
            ("pet/pinguin.png", "Penguin", (0,0,0), "1/2 750", 0.03636, (300,300)) ]

comet_pet = [ ("pet/cat_galaxy.png", "Galaxy Cat", (10, 10, 255), "1/3 500", 0.0286, (300, 300)),
            ("pet/axolotl_cosmic.png", "Cosmic Axolotl", (255, 255, 0), "1/15 000", 0.0067, (300, 300)) ]

volcano_pet = [ ("pet/hellrock.png", "Hell Rock", (255, 255, 0), "1/2 000", 0.05, (300, 300)) ]


image_data = commun_pet + rainy_pet + snow_pet + comet_pet + volcano_pet + [    
    # Secret (x 1) 
    ("pet/banana.png", "Banana", (100, 0, 100), "???", 0.0000000667, (300, 300)),
    ("pet/hippomelon_irl.png", "RTX Hippomelon", (0, 255, 0), "???", 0.0001, (300,300)),
    ("pet/oppression.png", "Ơ̶͂P̶̛͗P̸̓̏R̴̿̀Ê̵̓S̶̄̓S̴̓ION", (200, 200, 200), "1/10 000 000", 0, (1700,1200)),
    ("pet/1NE.png", "1NE", (255,255,255), "1/3 300 000", 0.00000303, (300,300)),
    ("pet/zer0.png", "ZER0", (255,255,255), "1/10 000 000", 0.00002857, (300,300))
]


image_objects = [
    (pygame.transform.scale(pygame.image.load(img), resolution), name, color, chance, weight, img, resolution)  
    for img, name, color, chance, weight, resolution in image_data
]

selected_image = None
selected_name = ""
selected_color = (255, 255, 255)
selected_chance = ""
last_click_time = 0
cooldown_seconds = 0
pet_display_time = 0
display_duration = 600

import requests

def send_discord_message(nickname, pet_name, pet_chance, date_obtained, image_path):
    pet_webhook_url = "https://discord.com/api/webhooks/1374816604986151023/8V1Pi98J_FsTT37I1RnRbqrhByR76XP4_4_3qFfskXAMbeVJBRk8g7sWcN0HczgJvRcb"

    message = {
        "embeds": [
            {
                "title": "🎉 Un pet ultra rare vient d'être roll ! 🎉",
                "description": f"🚀 「 ✦ {nickname} ✦ 」 vient de roll **un pet universel 🌌** avec une chance de +10k 🍀!",
                "color": 16711680,
                "thumbnail": {
                    "url": f"https://imgur.com/RWEXems"
                },
                "fields": [
                    {
                        "name": "🐾 Pet obtenu",
                        "value": f"**{pet_name}**",
                        "inline": True
                    },
                    {
                        "name": "🎲 Chance",
                        "value": f"**{pet_chance}**",
                        "inline": True
                    },
                    {
                        "name": "📅 Date du roll",
                        "value": f"__{date_obtained}__",
                        "inline": False
                    }
                ],
                "footer": {
                    "text": "Bonne chance pour les prochains rolls ! 🔥"
                }
            }
        ]
    }

    response = requests.post(pet_webhook_url, json=message)

def screen_shake(screen, intensity=100, duration=2):
    # tremblement
    start_time = time.time()
    while time.time() - start_time < duration:
        shake_x = random.randint(-intensity, intensity)
        shake_y = random.randint(-intensity, intensity)
        screen.blit(selected_biome, (shake_x, shake_y))
        pygame.display.update()
        time.sleep(0.05)

def background_shake(screen, intensity=100, duration=2):

    start_time = time.time()
    while time.time() - start_time < duration:
        shake_x = random.randint(-intensity, intensity)
        shake_y = random.randint(-intensity, intensity)
        screen.blit(pygame.image.load("gui/cutscene2.png"), (shake_x, shake_y))
        pygame.display.update()
        time.sleep(0.05)

def background_shake2(screen, intensity=100, duration=2):
    
    start_time = time.time()
    while time.time() - start_time < duration:
        shake_x = random.randint(-intensity, intensity)
        shake_y = random.randint(-intensity, intensity)
        screen.blit(pygame.image.load("gui/cutscene3.png"), (shake_x, shake_y))
        pygame.display.update()
        time.sleep(0.05)

def check_pet_event(screen, weight):
    # affichage
    pygame.mixer.init()
    if weight <= 0.1:
        pygame.mixer.music.load("music/cutscene.mp3")
        pygame.mixer.music.play()

        screen_shake(screen, intensity=50, duration=2)
        cutscene1 = pygame.image.load("gui/cutscene1.png")
        screen.blit(cutscene1, (0, 0))
        pygame.display.update()
        time.sleep(2)

        if weight <= 0.2:
            background_shake(screen, intensity=40, duration=1)
            pygame.display.update()
            time.sleep(0)

            if weight <= 0.01:
                background_shake2(screen, intensity=40, duration=1)
                pygame.display.update()
                time.sleep(0)
        pygame.mixer.music.stop()

def roll_pet():
    global selected_image, selected_name, selected_color, selected_chance, pet_display_time, roll_counter  

    possible_pets = [img for img in image_objects]
    depression_obtained = any(pet.name == "Đ̷̷͝͠Σ̷̷̏͠P̷̷̾͡Я̷̷̋͞Ξ̷̷̌̽Ś̷̷͠S̷̷̓͠I̷̷̽̑Ω̷̷͆̾N̷̷̓̋" for pet in inventory)

    updated_image_objects = []
    for img in image_objects:
        img = list(img)  
        if img[1] == "Ơ̶͂P̶̛͗P̸̓̏R̴̿̀Ê̵̓S̶̄̓S̴̓IΩ̷̷͆̾N" and depression_obtained:
            img[4] = 0.0001  # changement de chance
        updated_image_objects.append(tuple(img))  

    # Mise à jour de image_objects
    image_objects[:] = updated_image_objects

    selected_image, selected_name, selected_color, selected_chance, weight, image_path, selected_size = random.choices(
        image_objects, weights=[img[4] for img in image_objects]
    )[0]

    pet_display_time = time.time()
    roll_counter += 1  
 

    for pet in inventory:
        if pet.name == selected_name:
            pet.quantity += 1  # quantité
            save_inventory()  # save
            break
    else:
        new_pet = PetInventory(selected_name, selected_chance, time.strftime("%Y-%m-%d %H:%M:%S"), image_path)
        inventory.append(new_pet)
        save_inventory() 
    if connected: 
        if weight < 0.01:
            send_discord_message(nickname_text, selected_name, selected_chance, time.strftime("%Y-%m-%d %H:%M:%S"), image_path)
        if selected_name == "░▒█CΔT█▒░":
            send_discord_message(nickname_text, selected_name, selected_chance, time.strftime("%Y-%m-%d %H:%M:%S"), image_path)
        elif selected_name == "D̵̰́Ø̶̨̎G̷̡̅":
            send_discord_message(nickname_text, selected_name, selected_chance, time.strftime("%Y-%m-%d %H:%M:%S"), image_path) 
        elif selected_name == "Cat":
            send_discord_message(nickname_text, selected_name, selected_chance, time.strftime("%Y-%m-%d %H:%M:%S"), image_path) 
    check_pet_event(screen, weight)
    

# -----------------------------------------------------------------------------
# Biome


biome_data = [
    ("gui/bg2.png", "music/PS99.mp3", 50, 600),
    ("gui/rainy.png", "music/rainy.mp3", 25, 720),
    ("gui/snowybiome.png", "music/PS99.mp3", 15, 780),
    ("gui/cometbiome.png", "music/PS99.mp3", 1.25, 900),
    ("gui/volcano.png", "music/PS99.mp3", 0.15015, 900),
    ("gui/glitchbiome.gif", "music/glitch.mp3", 0.01, 180)
]

biome_object = [
    (pygame.transform.scale(pygame.image.load(img), (1920, 1080)), img, music, weight, duration) 
    for img, music, weight, duration in biome_data
]


# first biome
selected_biome = pygame.transform.scale(pygame.image.load(biome_data[0][0]), (1920, 1080))
selected_music = biome_data[0][1]
biome_duration = biome_data[0][3]
last_background_change = time.time()

# changer la musique
pygame.mixer.music.load(selected_music)
pygame.mixer.music.play(-1)


date = time.strftime("%Y-%m-%d %H:%M:%S")
def glitch_annonced(nickname_text, date):
    webhook_url = "https://discord.com/api/webhooks/1374818720031178802/jkVGL-f-ZAbctoU7wk-K5NURppvx4YQyK2DX_Cmg0Xr7oN2e8TxE06-Lwsnmwxq6DSGX"

    message = {
        "embeds": [
            {
                "title": "⚠︎⃤ Une personne vient d'avoir le Glitch Biome ! ⚠︎⃤",
                "description": f"🚀 「 ✦ {nickname_text} ✦ 」 vient d'obtenir le **G̷̡̍͝L̷̡̏̾I̷̡͐͠T̷̡̒͘C̷̡̑͘H̷̡̾̌  B̷̡͆̾Ǐ̷̡͌O̷̡͗̐M̷̡̏̎E̷̡͑͘  �** avec la probabilité de 1/10 000 🍀!",
                "color": 16711680,
                "thumbnail": {
                    "url": "https://i.imgur.com/koTrrrD.png"
                },
                "fields": [
                            {
                        "name": "⏳ Durée",
                        "value": "**3 Minutes**",
                        "inline": True
                    },
                    {
                        "name": "🎲 Chance",
                        "value": "**1/10 000**",
                        "inline": True
                    },
                    {
                        "name": "📅 Date de l'apparaîtion",
                        "value": f"__{date}__",
                        "inline": False
                    }
                ],
                "footer": {
                    "text": "Bonne chance pour les prochains biomes ! 🔥"
                }
            }
        ]
    }
    response = requests.post(webhook_url, json=message)

def volcano_annonced(nickname_text, date):
    webhook_url = "https://discord.com/api/webhooks/1374818720031178802/jkVGL-f-ZAbctoU7wk-K5NURppvx4YQyK2DX_Cmg0Xr7oN2e8TxE06-Lwsnmwxq6DSGX"

    message = {
        "embeds": [
            {
                "title": "🌋 Une personne vient d'avoir le Volcano Biome ! 🌋",
                "description": f"🚀 「 ✦ {nickname_text} ✦ 」 vient d'obtenir le **Volcano Biome 🌋** avec la probabilité de 1/666 🍀!",
                "color": 16711680,
                "thumbnail": {
                    "url": "https://imgur.com/l2o9F62"
                },
                "fields": [
                            {
                        "name": "⏳ Durée",
                        "value": "**15 Minutes**",
                        "inline": True
                    },
                    {
                        "name": "🎲 Chance",
                        "value": "**1/666**",
                        "inline": True
                    },
                    {
                        "name": "📅 Date de l'apparaîtion",
                        "value": f"__{date}__",
                        "inline": False
                    }
                ],
                "footer": {
                    "text": "Bonne chance pour les prochains biomes ! 🔥"
                }
            }
        ]
    }
    response = requests.post(webhook_url, json=message)

def comet_annonced(nickname_text, date):
    webhook_url = "https://discord.com/api/webhooks/1374818720031178802/jkVGL-f-ZAbctoU7wk-K5NURppvx4YQyK2DX_Cmg0Xr7oN2e8TxE06-Lwsnmwxq6DSGX"

    message = {
        "embeds": [
            {
                "title": "☄️ Une personne vient d'avoir le Comet Biome ! ☄️",
                "description": f"🚀 「 ✦ {nickname_text} ✦ 」 vient d'obtenir le **Comet Biome ⭐** avec la probabilité de 1/80 🍀!",
                "color": 16711680,
                "thumbnail": {
                    "url": "https://imgur.com/a/TDt0qb9"
                },
                "fields": [
                            {
                        "name": "⏳ Durée",
                        "value": "**15 Minutes**",
                        "inline": True
                    },
                    {
                        "name": "🎲 Chance",
                        "value": "**1/80**",
                        "inline": True
                    },
                    {
                        "name": "📅 Date de l'apparaîtion",
                        "value": f"__{date}__",
                        "inline": False
                    }
                ],
                "footer": {
                    "text": "Bonne chance pour les prochains biomes ! 🔥"
                }
            }
        ]
    }
    response = requests.post(webhook_url, json=message)

selected_biome_name = biome_data[0][0]  

def roll_biome():
    global selected_biome, selected_music, last_background_change, biome_duration, selected_biome_name

    selected = random.choices(biome_object, weights=[biome[3] for biome in biome_object])[0]
    selected_biome = selected[0]
    selected_music = selected[2]
    biome_duration = selected[4]
    selected_biome_name = selected[1]  
    last_background_change = time.time()

    pygame.mixer.music.load(selected_music)
    pygame.mixer.music.play(-1)

glitchbiome = "gui/glitchbiome.gif"
glitch = Image.open(glitchbiome)
animed = [pygame.image.fromstring(frame.convert("RGB").tobytes(), frame.size, "RGB") for frame in ImageSequence.Iterator(glitch)]


class Particle:
    def __init__(self, image_path, x, y, speed_x, speed_y, scale_factor=2):
        self.image = pygame.image.load(image_path)
        original_size = self.image.get_size()
        new_size = (int(original_size[0] * scale_factor), int(original_size[1] * scale_factor))
        self.image = pygame.transform.scale(self.image, new_size)  # Agrandissement
        self.rect = self.image.get_rect(center=(x, y))
        self.speed_x = speed_x
        self.speed_y = speed_y

    def update(self):
        self.rect.y += self.speed_y  # Gravité
        self.rect.x += self.speed_x  # Effet de vent

        if self.rect.top > info.current_h or self.rect.left > info.current_w or self.rect.right < 0:
            self.rect.y = random.randint(-50, -10)
            self.rect.x = random.randint(0, info.current_w)
            self.speed_x = random.uniform(-0.5, 0.5)
            self.speed_y = random.uniform(10, 10)

    def draw(self, screen):
        screen.blit(self.image, self.rect)



particles = []


# -----------------------------------------------------------------------------
# boucle

running = True
while running:
    current_time = time.time()
    time_remaining = max(0, cooldown_seconds - (current_time - last_click_time))
    # Vérification et mise à jour du biome après la durée définie
    if current_time - last_background_change >= biome_duration:
        roll_biome()
        if connected:
            if selected_biome_name == "gui/glitchbiome.gif":
                glitch_annonced(nickname_text, date)
            if selected_biome_name == "gui/volcano.png":
                volcano_annonced(nickname_text, date)
            if selected_biome_name == "gui/cometbiome.png":
                comet_annonced(nickname_text, date)


        if selected_biome_name == "gui/bg2.png":
            image_data = commun_pet + rainy_pet + snow_pet + comet_pet + volcano_pet + [

            # Secret
            ("pet/banana.png", "Banana", (100, 0, 100), "???", 0.0000000667, (300, 300)),
            ("pet/hippomelon_irl.png", "RTX Hippomelon", (0, 255, 0), "???", 0.0001, (300,300)),
            ("pet/1NE.png", "1NE", (255,255,255), "1/3 300 000", 0.00000303, (300,300)),
            ("pet/zer0.png", "ZER0", (255,255,255), "1/10 000 000", 0.00002857, (300,300)) ]
            image_objects = [
            (pygame.transform.scale(pygame.image.load(img), resolution), name, color, chance, weight, img, resolution)  
            for img, name, color, chance, weight, resolution in image_data
            ]


        elif selected_biome_name == "gui/rainy.png":
            image_data = commun_pet + snow_pet + comet_pet + volcano_pet + [

            # Rainy
            ("pet/fish_golden.png", "Golden Fish", (255, 255, 255), "1/275", 0.3636, (300, 300)),
            ("pet/fish_green.png", "Green Fish", (255, 255, 255), "1/350", 0.2857, (300, 300)),
            ("pet/fish_blue.png", "Blue Fish", (255, 255, 255), "1/425", 0.2353, (300, 300)),
            ("pet/shark.png", "Shark", (255, 255, 255), "1/750 ", 0.1333, (300, 300)),
            ("pet/shark_whale.png", "Whale Shark", (255, 255, 255), "1/1 300", 0.0769, (350, 350)) ]
            image_objects = [
            (pygame.transform.scale(pygame.image.load(img), resolution), name, color, chance, weight, img, resolution)  
            for img, name, color, chance, weight, resolution in image_data
            ]
            particle_image = "gui/particles/rain.png"
            particles = [Particle(particle_image, random.randint(0, info.current_w), random.randint(-50, info.current_h), random.uniform(-0.2, 0.2), random.uniform(10, 10), scale_factor=0.05) for _ in range(150)]
        
        elif selected_biome_name == "gui/snowybiome.png":
            image_data = commun_pet + rainy_pet + comet_pet + volcano_pet + [

            # Snowy
            ("pet/cat_snow.png", "Snow Cat", (255, 255, 255), "1/920", 0.1087, (300, 300)),
            ("pet/dog_snow.png", "Snow Dog", (255, 255, 255), "1/1 1 275", 0.0784, (300, 300)),
            ("pet/rabbit_white.png", "Snow Bunny", (255, 255, 255), "1/1 315", 0.0760, (300, 350)),
            ("pet/bear_polar.png", "Polar Bear", (255, 255, 255), "1/1 700", 0.0588, (300, 300))
            #("pet/pinguin", "Penguin", (0,0,0), "1/2 750", 0.03636, (300,300)) 
            ]
            image_objects = [
            (pygame.transform.scale(pygame.image.load(img), resolution), name, color, chance, weight, img, resolution)  
            for img, name, color, chance, weight, resolution in image_data
            ]
            particle_image = "gui/particles/snow.png"
            particles = [Particle(particle_image, random.randint(0, info.current_w), random.randint(-50, info.current_h), random.uniform(-0.2, 0.2), random.uniform(5, 5), scale_factor=0.5) for _ in range(100)]

        elif selected_biome_name == "gui/comet.png":
            image_data = commun_pet + rainy_pet + snow_pet + volcano_pet + [

            # Comet
            ("pet/axolotl_cosmic.png", "Cosmic Axolotl", (255, 255, 0), "1/15 000", 0.0067, (300, 300)),
            ("pet/cat_galaxy.png", "Galaxy Cat", (10, 10, 255), "1/15 000", 0.0067, (300, 300)) ]
            image_objects = [
            (pygame.transform.scale(pygame.image.load(img), resolution), name, color, chance, weight, img, resolution)  
            for img, name, color, chance, weight, resolution in image_data
            ]
        
        elif selected_biome_name == "gui/volcano.png":

            # Volcano
            image_data = commun_pet + rainy_pet + snow_pet + comet_pet + [
            ("pet/hellrock.png", "Hell Rock", (255, 255, 0), "1/2 000", 0.05, (300, 300)) ]
            image_objects

        
        elif selected_biome_name == "gui/glitchbiome.gif":
            image_data = commun_pet + rainy_pet + snow_pet + comet_pet + volcano_pet + [

            # Glitch 
            ("pet/cat_missed.png", "m̷̮̾̆͠ǐ̵̠̀̽͊̕ͅs̶͇̖͙͉͖̋̄͂̌̉s̷̹̱̖̆̆į̵̹̺͙̝͆̄͌̋̂n̶̮̖̟͙̑͐͘̕͠ğ̷̛̹̖́̔ ̸̥̯̗͊͛̕̚͝c̶̯̰̖̥͎̀̄͊̈́̊a̷̹̰̩̅̉͗̾̊͜ṱ̷̰͉̌̅͐̾̋", (150, 0, 150), "1/500", 0.2, (300,300)),
            ("pet/cat_glitched.png", "░▒█CΔT█▒░", (0, 150, 0), "1/1 000", 0.1, (300, 300)),
            ("pet/dog_glitched.png", "D̵̰́Ø̶̨̎G̷̡̅", (0, 150, 0), "1/5 000", 0.02, (300, 300)),
            ("pet/depression.png", "Đ̷̷͝͠Σ̷̷̏͠P̷̷̾͡Я̷̷̋͞Ξ̷̷̌̽Ś̷̷͠S̷̷̓͠I̷̷̽̑Ω̷̷͆̾N̷̷̓̋", (0, 150, 0), "1/100 000", 0.001, (1500, 1040)),
            ("pet/oppression.png", "Ơ̶͂P̶̛͗P̸̓̏R̴̿̀Ê̵̓S̶̄̓S̴̓IΩ̷̷͆̾N", (200, 200, 200), "1/10 000 000", 0, (1700,1200)) 
            ]
            image_objects = [
            (pygame.transform.scale(pygame.image.load(img), resolution), name, color, chance, weight, img, resolution)  
            for img, name, color, chance, weight, resolution in image_data
            ]

    # event
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
            elif event.key == pygame.K_F11:
                if screen.get_flags() & pygame.FULLSCREEN:
                    screen = pygame.display.set_mode((1920, 1000))
                else:
                    screen = pygame.display.set_mode((1920, 1080), pygame.FULLSCREEN)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if button_rect.collidepoint(event.pos) and (current_time - last_click_time > cooldown_seconds):
                roll_pet()
                last_click_time = current_time
            elif inventory_button_rect.collidepoint(event.pos):
                inventory_visible = not inventory_visible  
            
            elif inventory_visible:
                if prev_button_rect.collidepoint(event.pos) and current_page > 0:
                    current_page -= 1  
                elif next_button_rect.collidepoint(event.pos) and (current_page + 1) * pets_per_page < len(inventory):
                    current_page += 1  
            if inventory_visible and xxl_button_rect.collidepoint(event.pos):
                inventory_visible = False  

    if selected_biome_name == glitchbiome:
        screen.blit(animed[frame_index], (0, 0))
        frame_index = (frame_index + 1) % len(animed)
        clock.tick(1000 // frame_rate) 
        pygame.display.update()

    # affichage
    screen.blit(selected_biome, (0, 0))
    screen.blit(nickname_image, nickname_image.get_rect(center=(960, 100)))
    nickname_surface = font.render(nickname_text, True, nickname_color)
    screen.blit(nickname_surface, nickname_surface.get_rect(center=(960, 100))) 

    timer_surface = font_timer.render(f"{time_remaining:.1f}s", True, (255, 255, 255))
    timer_rect = timer_surface.get_rect(center=(button_rect.centerx, button_rect.top - 30))
    screen.blit(timer_surface, timer_rect)


    if selected_image and time.time() - pet_display_time < display_duration:
        screen.blit(selected_image, selected_image.get_rect(center=(960, 540)))
        if selected_name == "░▒█CΔT█▒░":
            text_surface = pygame.font.Font("font/Base.otf", 50).render(f"You rolled a {selected_name}!", True, selected_color)
        elif selected_name == "D̵̰́Ø̶̨̎G̷̡̅":
            text_surface = pygame.font.Font("font/Base.otf", 50).render(f"You rolled a {selected_name}!", True, selected_color)
        elif selected_name == "Đ̷̷͝͠Σ̷̷̏͠P̷̷̾͡Я̷̷̋͞Ξ̷̷̌̽Ś̷̷͠S̷̷̓͠I̷̷̽̑Ω̷̷͆̾N̷̷̓̋":
            text_surface = pygame.font.Font("font/Base.otf", 50).render(f"You rolled a {selected_name}!", True, selected_color) 
        else:
            text_surface = font.render(f"You rolled a {selected_name}!", True, selected_color)

        screen.blit(text_surface, text_surface.get_rect(center=(960, 300)))
        chance_surface = font.render(f"Chance : {selected_chance}", True, selected_color)
        screen.blit(chance_surface, chance_surface.get_rect(center=(960, 350)))

    screen.blit(button_image, button_rect)
    screen.blit(inventory_button_image, inventory_button_rect) 

    for particle in particles:
        particle.update()
        particle.draw(screen)

    if inventory_visible:
        pygame.draw.rect(screen, (255, 255, 255), inventory_rect, border_radius=20) # blanc
        pygame.draw.rect(screen, (0, 20, 255), inventory_rect, 5, border_radius=20)  # bleu
        
        xxl_button_rect = pygame.Rect(inventory_x + inventory_width - 130, inventory_y + 10, 120, 70)  
        pygame.draw.rect(screen, (255, 0, 20), xxl_button_rect, border_radius=30)  # rouge
        xxl_text = font.render("XXL", True, (255, 255, 255))
        xxl_text_rotated = pygame.transform.rotate(xxl_text, 15)  # Rotation de 35 degrés
        screen.blit(xxl_text_rotated, xxl_text_rotated.get_rect(center=xxl_button_rect.center))

        y_offset = inventory_rect.y + 80  
        x_image = inventory_rect.x + 50   
        x_text = x_image + 100            
        start_index = current_page * pets_per_page
        end_index = start_index + pets_per_page
        pets_to_display = sorted(inventory[start_index:end_index], key=lambda pet: rarity_order.get(pet.name, 999))

        pygame.draw.rect(screen, (0, 255, 10), prev_button_rect, border_radius=15)  # vert
        pygame.draw.rect(screen, (0, 10, 255), next_button_rect, border_radius=15)  # bleu

        prev_text = font.render("Prev", True, (255, 255, 255))
        next_text = font.render("Next", True, (255, 255, 255))

        screen.blit(prev_text, prev_text.get_rect(center=prev_button_rect.center))
        screen.blit(next_text, next_text.get_rect(center=next_button_rect.center))
        
        screen.blit(inventory_title_surface, inventory_title_rect)

        for pet in pets_to_display:
            pet_surface = font.render(f"{pet.name} ({pet.rarity}) x{pet.quantity}", True, (0, 0, 0))

            try:
                pet_image = pygame.transform.scale(pygame.image.load(pet.image_path), (75, 75))
                screen.blit(pet_image, (x_image, y_offset))
            except pygame.error:
                print(f"Image introuvable: {pet.image_path}")

            screen.blit(pet_surface, (x_text, y_offset + 20))
        
            y_offset += 100 

    # roll
    screen.blit(roll_gui_image, roll_gui_rect)

    # roll number
    counter_text = font_roll.render(f"{roll_counter}", True, (0, 0, 0))
    counter_rect = counter_text.get_rect(center=roll_gui_rect.center)
    screen.blit(counter_text, counter_rect)

    save_inventory()
    pygame.display.update()
    
    clock.tick(60)  

pygame.quit()