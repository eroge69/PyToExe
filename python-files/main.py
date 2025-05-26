import pygame
import sys
import json
import os
import math  # Import math for angle calculations
import time  # Import time for managing shoot cooldown
import random  # Import random for enemy spawn

# Initialize Pygame
pygame.init()

# Constants
WIDTH = 1920
HEIGHT = 1080
SQUARE_SIZE = 50
PROJECTILE_SIZE = 10
PROJECTILE_SPEED = 0.8  # Réduit de 10 à 5

# Ajouter une constante pour le délai entre les tirs
SHOOT_COOLDOWN = 0.2  # 100ms entre chaque tir

ENEMY_SIZE = 50  # Taille des ennemis
ENEMY_SPEED = 0.2  # Réduit de 2 à 1
ENEMY_MAX_HEALTH = 3  # Points de vie des ennemis

# Ajouter avec les autres constantes
ENEMY_SPAWN_DELAY_MIN = 2.0  # Minimum 2 secondes entre les spawns
ENEMY_SPAWN_DELAY_MAX = 4.0  # Maximum 4 secondes entre les spawns

# Ajouter ces constantes au début du fichier avec les autres constantes
WEAPON_SIZE = 100
GREEN = (0, 255, 0)

# Colors
WHITE = (255, 255, 255)
ORANGE = (255, 165, 0)
BLACK = (0, 0, 0)
GRAY = (128, 128, 128)
LIGHT_BLUE = (100, 200, 255)
DARK_BLUE = (0, 100, 200)
LIGHT_GRAY = (200, 200, 200)
TRANSPARENT_BLACK = (0, 0, 0, 128)
CYAN = (0, 255, 255)
RED = (255, 0, 0)

# Ajouter les constantes SHOTGUN avant l'initialisation de l'écran
SHOTGUN_SPREAD = 30  # Angle de dispersion en degrés
SHOTGUN_PROJECTILES = 5  # Nombre de projectiles par tir
SHOTGUN_RANGE = 400  # Portée réduite en pixels
SHOTGUN_DAMAGE = 2  # Dégâts par projectile

# Ajouter ces constantes avec les autres en haut du fichier
RIFLE_COOLDOWN = 0.1  # Cooldown plus court entre les tirs (0.1 seconde)
RIFLE_RELOAD_COOLDOWN = 2.0  # Temps de rechargement (2 secondes)
RIFLE_MAG_SIZE = 60  # Taille du chargeur
RIFLE_DAMAGE = 1  # Dégâts par tir

# Create fullscreen window
screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
WIDTH, HEIGHT = screen.get_size()

# Calculate square position (center of screen)
square_x = WIDTH // 2 - SQUARE_SIZE // 2
square_y = HEIGHT // 2 - SQUARE_SIZE // 2

# Global variables for accounts
accounts = {}
current_account = None
projectiles = []
enemies = []  # Liste des ennemis

# Ajouter avec les autres variables globales
current_weapon = 'classic'
diamonds = 0

# Modifier le dictionnaire des armes
weapons = {
    'classic': {'owned': True, 'price': 0, 'damage': 1, 'range': float('inf')},
    'shotgun': {'owned': False, 'price': 50, 'damage': SHOTGUN_DAMAGE, 'range': SHOTGUN_RANGE}  # Shotgun non possédé par défaut
}

# Load existing accounts
try:
    with open('accounts.json', 'r') as f:
        accounts = json.load(f)
except:
    accounts = {}

def save_accounts():
    with open('accounts.json', 'w') as f:
        json.dump(accounts, f)

# Load logo image
LOGO_IMAGE = None
try:
    logo_path = os.path.join(os.path.dirname(__file__), "images", "logo.png")
    LOGO_IMAGE = pygame.image.load(logo_path)
    # Redimensionner l'image si nécessaire (ajustez la taille selon vos besoins)
    LOGO_IMAGE = pygame.transform.scale(LOGO_IMAGE, (600, 200))
except Exception as e:
    print(f"Erreur lors du chargement du logo: {e}")

# Load enemy image
ENEMY_IMAGE = None
try:
    enemy_path = os.path.join(os.path.dirname(__file__), "images", "enemy.png")
    ENEMY_IMAGE = pygame.image.load(enemy_path)
    ENEMY_IMAGE = pygame.transform.scale(ENEMY_IMAGE, (ENEMY_SIZE, ENEMY_SIZE))
except Exception as e:
    print(f"Erreur lors du chargement de l'image de l'ennemi: {e}")

# Load player image
PLAYER_IMAGE = None
try:
    player_path = os.path.join(os.path.dirname(__file__), "images", "player.png")
    PLAYER_IMAGE = pygame.image.load(player_path)
    PLAYER_IMAGE = pygame.transform.scale(PLAYER_IMAGE, (SQUARE_SIZE, SQUARE_SIZE))
except Exception as e:
    print(f"Erreur lors du chargement de l'image du joueur: {e}")

# Load diamond image
DIAMOND_IMAGE = None
try:
    diamond_path = os.path.join(os.path.dirname(__file__), "images", "diamond.png")
    DIAMOND_IMAGE = pygame.image.load(diamond_path)
    DIAMOND_IMAGE = pygame.transform.scale(DIAMOND_IMAGE, (30, 30))  # Ajustez la taille selon vos besoins
except Exception as e:
    print(f"Erreur lors du chargement de l'image du diamant: {e}")

# Ajouter avec les autres chargements d'images
# Load button image
BUTTON_IMAGE = None
try:
    button_path = os.path.join(os.path.dirname(__file__), "images", "button.png")
    BUTTON_IMAGE = pygame.image.load(button_path)
    BUTTON_IMAGE = pygame.transform.scale(BUTTON_IMAGE, (70, 70))  # Même hauteur que les boutons
except Exception as e:
    print(f"Erreur lors du chargement de l'image du bouton: {e}")

# Ajouter ces constantes avec les autres
SKIN_SIZE = 100  # Taille des carrés de skins
YELLOW = (255, 255, 0)  # Couleur pour la sélection

# Modifier le dictionnaire des skins
skins = {
    'default': {'owned': True, 'price': 0},
    'jar jar binks': {'owned': False, 'price': 100},
    'yoda': {'owned': False, 'price': 200}
}

# Ajouter une variable globale pour le skin actif
current_skin = 'default'

# Load skin2 image (jar jar binks)
SKIN2_IMAGE = None
try:
    skin2_path = os.path.join(os.path.dirname(__file__), "images", "joueur2.png")
    SKIN2_IMAGE = pygame.image.load(skin2_path)
    SKIN2_IMAGE = pygame.transform.scale(SKIN2_IMAGE, (SKIN_SIZE, SKIN_SIZE))
except Exception as e:
    print(f"Erreur lors du chargement de l'image de Jar Jar Binks: {e}")

# Load skin3 image (yoda)
SKIN3_IMAGE = None
try:
    skin3_path = os.path.join(os.path.dirname(__file__), "images", "player3.png")
    SKIN3_IMAGE = pygame.image.load(skin3_path)
    SKIN3_IMAGE = pygame.transform.scale(SKIN3_IMAGE, (SKIN_SIZE, SKIN_SIZE))
except Exception as e:
    print(f"Erreur lors du chargement de l'image de Yoda: {e}")

def game_loop():
    global square_x, square_y, current_rifle_ammo, last_reload_time
    
    projectiles.clear()
    enemies.clear()
    player_angle = 0
    last_shot_time = time.time()
    last_enemy_spawn = time.time()
    game_over = False
    game_over_time = 0
    
    # Initialiser les munitions du rifle
    current_rifle_ammo = RIFLE_MAG_SIZE
    last_reload_time = 0
    
    while True:
        current_time = time.time()
        
        if game_over:
            # Vider la file d'événements pendant l'écran game over
            pygame.event.get()
            
            # Afficher "GAME OVER" pendant 2 secondes
            screen.fill(WHITE)
            game_over_text = pygame.font.Font(None, 150).render("GAME OVER", True, RED)
            text_rect = game_over_text.get_rect(center=(WIDTH//2, HEIGHT//2))
            screen.blit(game_over_text, text_rect)
            pygame.display.flip()
            
            if current_time - game_over_time >= 2:
                return True  # Retour au menu
            continue
        
        # Spawn des ennemis
        if current_time - last_enemy_spawn >= random.uniform(ENEMY_SPAWN_DELAY_MIN, ENEMY_SPAWN_DELAY_MAX):
            # Choisir un côté aléatoire (0: haut, 1: droite, 2: bas, 3: gauche)
            side = random.randint(0, 3)
            
            if side == 0:  # Haut
                x = random.randint(0, WIDTH - ENEMY_SIZE)
                y = -ENEMY_SIZE
            elif side == 1:  # Droite
                x = WIDTH
                y = random.randint(0, HEIGHT - ENEMY_SIZE)
            elif side == 2:  # Bas
                x = random.randint(0, WIDTH - ENEMY_SIZE)
                y = HEIGHT
            else:  # Gauche
                x = -ENEMY_SIZE
                y = random.randint(0, HEIGHT - ENEMY_SIZE)
            
            # Calculer la direction vers le joueur
            dx = square_x - x
            dy = square_y - y
            length = math.sqrt(dx**2 + dy**2)
            dx = (dx / length) * ENEMY_SPEED  # Utiliser ENEMY_SPEED au lieu de 2
            dy = (dy / length) * ENEMY_SPEED  # Utiliser ENEMY_SPEED au lieu de 2
            
            enemies.append({
                'x': x,
                'y': y,
                'dx': dx,
                'dy': dy,
                'health': ENEMY_MAX_HEALTH  # Ajouter les points de vie
            })
            last_enemy_spawn = current_time
        
        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return True
        
        # Vérifier si le bouton gauche est maintenu
        mouse_buttons = pygame.mouse.get_pressed()
        if mouse_buttons[0]:  # Bouton gauche
            current_time = time.time()
            weapon_cooldown = RIFLE_COOLDOWN if current_weapon == 'rifle' else SHOOT_COOLDOWN
            
            if current_weapon == 'rifle':
                global current_rifle_ammo, last_reload_time
                # Vérifier si en rechargement
                if current_rifle_ammo == 0:
                    if current_time - last_reload_time >= RIFLE_RELOAD_COOLDOWN:
                        current_rifle_ammo = RIFLE_MAG_SIZE
                        last_reload_time = current_time
                    return
            
            if current_time - last_shot_time >= weapon_cooldown:
                mouse_x, mouse_y = pygame.mouse.get_pos()
                dx = mouse_x - (square_x + SQUARE_SIZE//2)
                dy = mouse_y - (square_y + SQUARE_SIZE//2)
                length = (dx**2 + dy**2)**0.5
                if length > 0:
                    if current_weapon == 'rifle':
                        # Tir du rifle
                        current_rifle_ammo -= 1
                        if current_rifle_ammo == 0:
                            last_reload_time = current_time
                        dx = (dx/length) * PROJECTILE_SPEED
                        dy = (dy/length) * PROJECTILE_SPEED
                        projectiles.append({
                            'x': square_x + SQUARE_SIZE//2,
                            'y': square_y + SQUARE_SIZE//2,
                            'dx': dx,
                            'dy': dy,
                            'angle': player_angle,
                            'damage': weapons['rifle']['damage'],
                            'range': weapons['rifle']['range'],
                            'distance': 0
                        })
                    elif current_weapon == 'shotgun':
                        # Tir en dispersion pour le shotgun
                        base_angle = math.degrees(math.atan2(-dy, dx))
                        for i in range(SHOTGUN_PROJECTILES):
                            spread_angle = base_angle + random.uniform(-SHOTGUN_SPREAD/2, SHOTGUN_SPREAD/2)
                            rad_angle = math.radians(spread_angle)
                            proj_dx = math.cos(rad_angle) * PROJECTILE_SPEED
                            proj_dy = -math.sin(rad_angle) * PROJECTILE_SPEED
                            projectiles.append({
                                'x': square_x + SQUARE_SIZE//2,
                                'y': square_y + SQUARE_SIZE//2,
                                'dx': proj_dx,
                                'dy': proj_dy,
                                'angle': spread_angle,
                                'damage': SHOTGUN_DAMAGE,
                                'range': SHOTGUN_RANGE,
                                'distance': 0
                            })
                    else:
                        # Tir normal pour l'arme classic
                        dx = (dx/length) * PROJECTILE_SPEED
                        dy = (dy/length) * PROJECTILE_SPEED
                        projectiles.append({
                            'x': square_x + SQUARE_SIZE//2,
                            'y': square_y + SQUARE_SIZE//2,
                            'dx': dx,
                            'dy': dy,
                            'angle': player_angle,
                            'damage': weapons['classic']['damage'],
                            'range': weapons['classic']['range'],
                            'distance': 0
                        })
                    last_shot_time = current_time

        # Calculer l'angle vers le curseur
        mouse_x, mouse_y = pygame.mouse.get_pos()
        dx = mouse_x - (square_x + SQUARE_SIZE//2)
        dy = mouse_y - (square_y + SQUARE_SIZE//2)
        player_angle = math.degrees(math.atan2(-dy, dx))
        
        # Mettre à jour les positions des projectiles
        for projectile in projectiles[:]:
            old_x = projectile['x']
            old_y = projectile['y']
            projectile['x'] += projectile['dx']
            projectile['y'] += projectile['dy']
            
            # Calculer la distance parcourue
            projectile['distance'] += ((projectile['x'] - old_x)**2 + (projectile['y'] - old_y)**2)**0.5
            
            # Supprimer les projectiles hors écran ou ayant dépassé leur portée
            if (projectile['x'] < 0 or projectile['x'] > WIDTH or 
                projectile['y'] < 0 or projectile['y'] > HEIGHT or
                projectile['distance'] > projectile['range']):
                projectiles.remove(projectile)
        
        # Mettre à jour la position des ennemis et vérifier les collisions
        for enemy in enemies[:]:
            enemy['x'] += enemy['dx']
            enemy['y'] += enemy['dy']
            
            # Vérifier les collisions avec les projectiles
            for projectile in projectiles[:]:
                if (projectile['x'] < enemy['x'] + ENEMY_SIZE and
                    projectile['x'] + PROJECTILE_SIZE > enemy['x'] and
                    projectile['y'] < enemy['y'] + ENEMY_SIZE and
                    projectile['y'] + PROJECTILE_SIZE > enemy['y']):
                    if projectile in projectiles:
                        projectiles.remove(projectile)
                    enemy['health'] -= 1
                    if enemy['health'] <= 0 and enemy in enemies:
                        enemies.remove(enemy)
                        accounts[current_account]['diamonds'] += 1  # Ajouter un diamant
                        save_accounts()  # Sauvegarder les changements
                        break
            
            # Vérifier la collision avec le joueur
            if (enemy['x'] < square_x + SQUARE_SIZE and
                enemy['x'] + ENEMY_SIZE > square_x and
                enemy['y'] < square_y + SQUARE_SIZE and
                enemy['y'] + ENEMY_SIZE > square_y):
                game_over = True
                game_over_time = current_time
                break
        
        # Clear screen
        screen.fill(WHITE)
        
        # Draw player
        player_img = None
        if current_skin == 'jar jar binks' and SKIN2_IMAGE:
            player_img = pygame.transform.scale(SKIN2_IMAGE, (SQUARE_SIZE, SQUARE_SIZE))
        elif current_skin == 'yoda' and SKIN3_IMAGE:
            player_img = pygame.transform.scale(SKIN3_IMAGE, (SQUARE_SIZE, SQUARE_SIZE))
        elif PLAYER_IMAGE:
            player_img = pygame.transform.scale(PLAYER_IMAGE, (SQUARE_SIZE, SQUARE_SIZE))
        
        if player_img:
            rotated_player = pygame.transform.rotate(player_img, player_angle)
            player_rect = rotated_player.get_rect(center=(square_x + SQUARE_SIZE//2, 
                                                        square_y + SQUARE_SIZE//2))
            screen.blit(rotated_player, player_rect)
        else:
            # Fallback au carré orange
            player_surface = pygame.Surface((SQUARE_SIZE, SQUARE_SIZE), pygame.SRCALPHA)
            pygame.draw.rect(player_surface, ORANGE, (0, 0, SQUARE_SIZE, SQUARE_SIZE))
            pygame.draw.line(player_surface, BLACK, 
                           (SQUARE_SIZE//2, SQUARE_SIZE//2),
                           (SQUARE_SIZE, SQUARE_SIZE//2), 3)
            
            rotated_player = pygame.transform.rotate(player_surface, player_angle)
            player_rect = rotated_player.get_rect(center=(square_x + SQUARE_SIZE//2, 
                                                        square_y + SQUARE_SIZE//2))
            screen.blit(rotated_player, player_rect)
        
        # Draw projectiles
        for projectile in projectiles:
            # Dessiner des projectiles orientés
            proj_surface = pygame.Surface((PROJECTILE_SIZE*2, PROJECTILE_SIZE), pygame.SRCALPHA)
            pygame.draw.rect(proj_surface, BLACK, (0, 0, PROJECTILE_SIZE*2, PROJECTILE_SIZE))
            rotated_proj = pygame.transform.rotate(proj_surface, projectile['angle'])
            proj_rect = rotated_proj.get_rect(center=(projectile['x'], projectile['y']))
            screen.blit(rotated_proj, proj_rect)
        
        # Draw enemies
        for enemy in enemies:
            if ENEMY_IMAGE:
                # Afficher l'image sans rotation
                enemy_rect = ENEMY_IMAGE.get_rect(center=(enemy['x'], enemy['y']))
                screen.blit(ENEMY_IMAGE, enemy_rect)
            else:
                # Fallback au carré cyan si pas d'image
                enemy_surface = pygame.Surface((ENEMY_SIZE, ENEMY_SIZE), pygame.SRCALPHA)
                pygame.draw.rect(enemy_surface, CYAN, (0, 0, ENEMY_SIZE, ENEMY_SIZE))
                screen.blit(enemy_surface, (enemy['x'], enemy['y']))
        
        # Draw enemies health bars
        for enemy in enemies:
            # Barre de vie
            health_bar_width = ENEMY_SIZE
            health_bar_height = 5
            health_ratio = enemy['health'] / ENEMY_MAX_HEALTH
            health_width = health_bar_width * health_ratio
            
            # Barre rouge (fond)
            pygame.draw.rect(screen, RED,
                           (int(enemy['x']), 
                            int(enemy['y'] - health_bar_height - 2),
                            health_bar_width,
                            health_bar_height))
            
            # Barre verte (vie restante)
            pygame.draw.rect(screen, (0, 255, 0),  # Vert
                           (int(enemy['x']), 
                            int(enemy['y'] - health_bar_height - 2),
                            int(health_width),
                            health_bar_height))
        
        pygame.display.flip()

def menu():
    font = pygame.font.Font(None, 74)
    title_font = pygame.font.Font(None, 100)
    
    button_width = 300
    button_height = 70
    button_spacing = 30
    square_button_size = button_height  # Taille du bouton carré
    
    total_height = (button_height * 3) + (button_spacing * 2)
    start_y = (HEIGHT - total_height) // 2
    
    buttons = {
        'play': pygame.Rect((WIDTH - button_width) // 2, start_y, button_width, button_height),
        'garage': pygame.Rect((WIDTH - button_width - square_button_size - 10) // 2, 
                            start_y + button_height + button_spacing, 
                            button_width, button_height),
        'square': pygame.Rect((WIDTH + button_width - 10) // 2, 
                            start_y + button_height + button_spacing,
                            square_button_size, square_button_size),
        'quit': pygame.Rect((WIDTH - button_width) // 2, 
                           start_y + (button_height + button_spacing) * 2, 
                           button_width, button_height)
    }
    
    hover_animations = {key: 0 for key in buttons}
    
    while True:
        screen.fill(WHITE)
        mouse_pos = pygame.mouse.get_pos()
        
        # Draw logo instead of text title
        if LOGO_IMAGE:
            logo_rect = LOGO_IMAGE.get_rect(center=(WIDTH//2, start_y - 100))
            screen.blit(LOGO_IMAGE, logo_rect)
        else:
            # Fallback au texte si l'image n'est pas chargée
            title = title_font.render("STAR WARS GAME", True, DARK_BLUE)
            screen.blit(title, (WIDTH//2 - title.get_width()//2, start_y - 150))
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                for key, button in buttons.items():
                    if button.collidepoint(mouse_pos):
                        if key == "quit":
                            pygame.quit()
                            sys.exit()
                        return key
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()

        # Update hover animations
        for key, button in buttons.items():
            if button.collidepoint(mouse_pos):
                hover_animations[key] = min(1.0, hover_animations[key] + 0.1)
            else:
                hover_animations[key] = max(0.0, hover_animations[key] - 0.1)
        
        # Draw buttons with animations
        texts = {'play': "PLAY", 'garage': "GARAGE", 'quit': "QUIT", 'square': ""}
        for key, button in buttons.items():
            if key == 'square':
                # Dessiner le bouton carré avec animation
                scale = 1.0 + (0.1 * hover_animations[key])
                scaled_size = int(square_button_size * scale)
                scaled_button = pygame.Rect(
                    button.centerx - scaled_size//2,
                    button.centery - scaled_size//2,
                    scaled_size, scaled_size
                )
                
                if BUTTON_IMAGE:
                    # Redimensionner l'image selon l'animation
                    scaled_image = pygame.transform.scale(BUTTON_IMAGE, (scaled_size, scaled_size))
                    screen.blit(scaled_image, scaled_button)
                else:
                    # Fallback avec animation
                    color = LIGHT_BLUE if hover_animations[key] > 0 else ORANGE
                    pygame.draw.rect(screen, color, scaled_button, border_radius=15)
                    pygame.draw.rect(screen, DARK_BLUE, scaled_button, 3, border_radius=15)
            else:
                # Le reste du code pour les autres boutons reste inchangé
                scale = 1.0 + (0.1 * hover_animations[key])
                scaled_width = int(button_width * scale)
                scaled_height = int(button_height * scale)
                scaled_button = pygame.Rect(
                    button.centerx - scaled_width//2,
                    button.centery - scaled_height//2,
                    scaled_width, scaled_height
                )
                
                color = LIGHT_BLUE if hover_animations[key] > 0 else ORANGE
                pygame.draw.rect(screen, color, scaled_button, border_radius=15)
                pygame.draw.rect(screen, DARK_BLUE, scaled_button, 3, border_radius=15)
                
                if texts[key]:  # Ne dessiner le texte que s'il existe
                    text = font.render(texts[key], True, BLACK)
                    screen.blit(text, (scaled_button.centerx - text.get_width()//2,
                                      scaled_button.centery - text.get_height()//2))
        
        pygame.display.flip()

def login_screen():
    font = pygame.font.Font(None, 74)
    title_font = pygame.font.Font(None, 100)
    
    input_box_width = 500
    input_box_height = 60
    button_width = 250
    button_height = 60
    
    username = ""
    password = ""
    message = ""
    input_active = "username"
    
    username_box = pygame.Rect((WIDTH - input_box_width) // 2, HEIGHT//3, input_box_width, input_box_height)
    password_box = pygame.Rect((WIDTH - input_box_width) // 2, HEIGHT//3 + 100, input_box_width, input_box_height)
    login_button = pygame.Rect((WIDTH - button_width*2 - 40) // 2, HEIGHT//3 + 200, button_width, button_height)
    register_button = pygame.Rect((WIDTH + 40) // 2, HEIGHT//3 + 200, button_width, button_height)
    
    while True:
        screen.fill(WHITE)
        
        # Draw title with shadow
        title = title_font.render("STAR WARS LOGIN", True, DARK_BLUE)
        shadow = title_font.render("STAR WARS LOGIN", True, LIGHT_GRAY)
        screen.blit(shadow, (WIDTH//2 - title.get_width()//2 + 3, HEIGHT//3 - 153))
        screen.blit(title, (WIDTH//2 - title.get_width()//2, HEIGHT//3 - 150))
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.MOUSEBUTTONDOWN:
                if username_box.collidepoint(event.pos):
                    input_active = "username"
                elif password_box.collidepoint(event.pos):
                    input_active = "password"
                elif login_button.collidepoint(event.pos):
                    if username in accounts and accounts[username]['password'] == password:
                        global current_account
                        current_account = username
                        return True
                    else:
                        message = "Invalid login!"
                elif register_button.collidepoint(event.pos):
                    if username and password:
                        if username not in accounts:
                            accounts[username] = {
                                'password': password,
                                'diamonds': 0
                            }
                            save_accounts()
                            current_account = username
                            return True
                        else:
                            message = "Username already exists!"
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_TAB:
                    input_active = "password" if input_active == "username" else "username"
                elif event.key == pygame.K_RETURN:
                    if username in accounts and accounts[username]['password'] == password:
                        current_account = username
                        return True
                elif event.key == pygame.K_BACKSPACE:
                    if input_active == "username":
                        username = username[:-1]
                    else:
                        password = password[:-1]
                else:
                    if input_active == "username":
                        username += event.unicode
                    else:
                        password += event.unicode
        
        # Draw input boxes with better style
        for box, active, text in [(username_box, input_active == "username", username),
                                (password_box, input_active == "password", "*" * len(password))]:
            color = LIGHT_BLUE if active else LIGHT_GRAY
            pygame.draw.rect(screen, color, box, border_radius=10)
            pygame.draw.rect(screen, DARK_BLUE, box, 3, border_radius=10)
            
            label = "Username:" if box == username_box else "Password:"
            label_text = font.render(label, True, BLACK)
            text_surface = font.render(text, True, BLACK)
            screen.blit(label_text, (box.x, box.y - 40))
            screen.blit(text_surface, (box.x + 10, box.y + 10))
        
        # Draw buttons with style
        for button, text in [(login_button, "Login"), (register_button, "Register")]:
            color = LIGHT_BLUE if button.collidepoint(pygame.mouse.get_pos()) else ORANGE
            pygame.draw.rect(screen, color, button, border_radius=10)
            pygame.draw.rect(screen, DARK_BLUE, button, 3, border_radius=10)
            
            text_surface = font.render(text, True, BLACK)
            screen.blit(text_surface, (button.centerx - text_surface.get_width()//2,
                                     button.centery - text_surface.get_height()//2))
        
        if message:
            message_text = font.render(message, True, (255, 0, 0))
            screen.blit(message_text, (WIDTH//2 - message_text.get_width()//2, HEIGHT//3 + 300))
        
        pygame.display.flip()

# Modifier la fonction garage_menu()
def garage_menu():
    global current_weapon  # Ajouter global pour modifier l'arme courante
    small_font = pygame.font.Font(None, 40)
    weapon_font = pygame.font.Font(None, 30)
    diamond_font = pygame.font.Font(None, 50)
    
    margin = 50
    spacing = 50
    
    weapon_spots = {
        'classic': pygame.Rect(margin, margin, WEAPON_SIZE, WEAPON_SIZE),
        'shotgun': pygame.Rect(margin + WEAPON_SIZE + spacing, margin, WEAPON_SIZE, WEAPON_SIZE)
    }
    
    while True:
        screen.fill(WHITE)
        
        # Dessiner le texte "Garage" en haut à droite
        garage_text = small_font.render("Garage", True, BLACK)
        text_rect = garage_text.get_rect(topright=(WIDTH - 20, 20))
        screen.blit(garage_text, text_rect)
        
        # Dessiner les armes
        for weapon_name, weapon_spot in weapon_spots.items():
            # Dessiner le cadre
            border_color = GREEN if weapons[weapon_name]['owned'] else RED
            pygame.draw.rect(screen, border_color, weapon_spot, 3)
            
            # Ajouter un fond jaune pour l'arme sélectionnée
            if weapon_name == current_weapon:
                pygame.draw.rect(screen, YELLOW, weapon_spot.inflate(-6, -6))
            
            # Dessiner le nom de l'arme
            name_text = weapon_font.render(weapon_name.upper(), True, BLACK)
            name_rect = name_text.get_rect(centerx=weapon_spot.centerx, bottom=weapon_spot.bottom + 30)
            screen.blit(name_text, name_rect)
            
            # Afficher le prix si l'arme n'est pas possédée
            if not weapons[weapon_name]['owned']:
                # Afficher l'icône du diamant
                if DIAMOND_IMAGE:
                    diamond_rect = DIAMOND_IMAGE.get_rect(
                        centerx=weapon_spot.centerx - 20,
                        centery=weapon_spot.bottom + 45
                    )
                    screen.blit(DIAMOND_IMAGE, diamond_rect)
                # Afficher le prix
                price_text = weapon_font.render(str(weapons[weapon_name]['price']), True, DARK_BLUE)
                price_rect = price_text.get_rect(
                    left=weapon_spot.centerx,
                    centery=weapon_spot.bottom + 45
                )
                screen.blit(price_text, price_rect)
        
        # Afficher les munitions du rifle si sélectionné
        if current_weapon == 'rifle':
            ammo_text = weapon_font.render(f"Ammo: {current_rifle_ammo}/{RIFLE_MAG_SIZE}", True, BLACK)
            ammo_rect = ammo_text.get_rect(centerx=WIDTH//2, top=20)
            screen.blit(ammo_text, ammo_rect)
        
        # Dessiner le nombre de diamants
        if DIAMOND_IMAGE:
            diamond_rect = DIAMOND_IMAGE.get_rect(centerx=WIDTH//2 - 50, bottom=HEIGHT - 20)
            screen.blit(DIAMOND_IMAGE, diamond_rect)
        diamonds_text = diamond_font.render(f"{accounts[current_account]['diamonds']}", True, DARK_BLUE)
        diamonds_rect = diamonds_text.get_rect(centerx=WIDTH//2 + 20, bottom=HEIGHT - 20)
        screen.blit(diamonds_text, diamonds_rect)
        
        # Gérer les événements
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return True
            if event.type == pygame.MOUSEBUTTONDOWN:
                # Vérifier si une arme a été cliquée
                for weapon_name, weapon_spot in weapon_spots.items():
                    if weapon_spot.collidepoint(event.pos) and weapons[weapon_name]['owned']:
                        current_weapon = weapon_name
        
        pygame.display.flip()

def square_menu():
    global current_skin  # Ajouter global pour modifier le skin courant
    small_font = pygame.font.Font(None, 40)
    skin_font = pygame.font.Font(None, 30)
    diamond_font = pygame.font.Font(None, 50)
    
    margin = 50
    spacing = 50
    
    # Créer les rectangles pour les skins
    skin_spots = {}
    for i, skin_name in enumerate(skins.keys()):
        skin_spots[skin_name] = pygame.Rect(
            margin + (SKIN_SIZE + spacing) * i,
            margin,
            SKIN_SIZE,
            SKIN_SIZE
        )
    
    while True:
        screen.fill(WHITE)
        
        # Dessiner le texte "Character Shop" en haut à droite
        shop_text = small_font.render("Character Shop", True, BLACK)
        text_rect = shop_text.get_rect(topright=(WIDTH - 20, 20))
        screen.blit(shop_text, text_rect)
        
        # Dessiner les skins
        for skin_name, skin_spot in skin_spots.items():
            # Dessiner le cadre
            border_color = GREEN if skins[skin_name]['owned'] else RED
            pygame.draw.rect(screen, border_color, skin_spot, 3)
            
            # Ajouter un fond jaune pour le skin sélectionné
            if skin_name == current_skin:
                pygame.draw.rect(screen, YELLOW, skin_spot.inflate(-6, -6))
            
            # Dessiner l'image du skin
            if skin_name == 'jar jar binks' and SKIN2_IMAGE:
                scaled_skin = pygame.transform.scale(SKIN2_IMAGE, (SKIN_SIZE, SKIN_SIZE))
                screen.blit(scaled_skin, skin_spot)
            elif skin_name == 'yoda' and SKIN3_IMAGE:
                scaled_skin = pygame.transform.scale(SKIN3_IMAGE, (SKIN_SIZE, SKIN_SIZE))
                screen.blit(scaled_skin, skin_spot)
            elif skin_name == 'default' and PLAYER_IMAGE:
                default_scaled = pygame.transform.scale(PLAYER_IMAGE, (SKIN_SIZE, SKIN_SIZE))
                screen.blit(default_scaled, skin_spot)
            
            # Dessiner le nom du skin
            name_text = skin_font.render(skin_name.upper(), True, BLACK)
            name_rect = name_text.get_rect(centerx=skin_spot.centerx, bottom=skin_spot.bottom + 30)
            screen.blit(name_text, name_rect)
            
            # Afficher le prix si le skin n'est pas possédé
            if not skins[skin_name]['owned']:
                # Afficher l'icône du diamant
                if DIAMOND_IMAGE:
                    diamond_rect = DIAMOND_IMAGE.get_rect(
                        centerx=skin_spot.centerx - 20,
                        centery=skin_spot.bottom + 45
                    )
                    screen.blit(DIAMOND_IMAGE, diamond_rect)
                # Afficher le prix
                price_text = skin_font.render(str(skins[skin_name]['price']), True, DARK_BLUE)
                price_rect = price_text.get_rect(
                    left=skin_spot.centerx,
                    centery=skin_spot.bottom + 45
                )
                screen.blit(price_text, price_rect)
        
        # Dessiner le nombre de diamants en bas de l'écran
        if DIAMOND_IMAGE:
            diamond_rect = DIAMOND_IMAGE.get_rect(centerx=WIDTH//2 - 50, bottom=HEIGHT - 20)
            screen.blit(DIAMOND_IMAGE, diamond_rect)
        diamonds_text = diamond_font.render(f"{accounts[current_account]['diamonds']}", True, DARK_BLUE)
        diamonds_rect = diamonds_text.get_rect(centerx=WIDTH//2 + 20, bottom=HEIGHT - 20)
        screen.blit(diamonds_text, diamonds_rect)
        
        # Gérer les événements
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return True
            if event.type == pygame.MOUSEBUTTONDOWN:
                # Vérifier si un skin a été cliqué
                for skin_name, skin_spot in skin_spots.items():
                    if skin_spot.collidepoint(event.pos):
                        if skins[skin_name]['owned']:
                            current_skin = skin_name  # Sélectionner le skin
                        elif accounts[current_account]['diamonds'] >= skins[skin_name]['price']:
                            accounts[current_account]['diamonds'] -= skins[skin_name]['price']
                            skins[skin_name]['owned'] = True
                            current_skin = skin_name  # Sélectionner automatiquement le skin acheté
                            save_accounts()
        
        pygame.display.flip()

# Modifier la partie dans main() qui gère les choix du menu
def main():
    while True:
        if not login_screen():
            break
            
        running = True
        while running:
            menu_choice = menu()
            if menu_choice == "play":
                game_result = game_loop()
                if not game_result:
                    running = False
            elif menu_choice == "garage":
                if not garage_menu():
                    running = False
            elif menu_choice == "square":  # Ajouter cette condition
                if not square_menu():
                    running = False
            else:  # quit
                running = False
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()