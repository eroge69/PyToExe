import pygame
import random
import os
import sys
import time
from pygame import mixer

# Инициализация Pygame
pygame.init()
mixer.init()

# Настройки экрана
info = pygame.display.Info()
screen = pygame.display.set_mode((info.current_w, info.current_h), pygame.FULLSCREEN)
WIDTH, HEIGHT = screen.get_size()
pygame.display.set_caption("ULTRA BRUTAL STRIKE 2D")
clock = pygame.time.Clock()

# Загрузка звуков
try:
    punch_sound = mixer.Sound("C:/Users/gulee/Downloads/mixkit-impact-of-a-strong-punch-2155.mp3")
    kill_sound = mixer.Sound("C:/Users/gulee/Downloads/Voicy_My Empire .mp3")
    hyper_sound = mixer.Sound(buffer=bytearray(100))
    grab_sound = mixer.Sound(buffer=bytearray(100))
    throw_sound = mixer.Sound(buffer=bytearray(100))
except:
    print("Звуки не найдены! Создаю заглушки...")
    punch_sound = mixer.Sound(buffer=bytearray(100))
    kill_sound = mixer.Sound(buffer=bytearray(100))
    hyper_sound = mixer.Sound(buffer=bytearray(100))
    grab_sound = mixer.Sound(buffer=bytearray(100))
    throw_sound = mixer.Sound(buffer=bytearray(100))

# Кровавые следы
blood_stains = []

def add_blood_stain(x, y, intensity=1):
    for _ in range(int(5 * intensity)):
        blood_stains.append((
            x + random.randint(-20, 20),
            y + random.randint(-20, 20),
            random.randint(3, 8),
            random.randint(180, 255)
        ))

# Игрок
player = {
    "x": WIDTH // 2,
    "y": HEIGHT // 2,
    "size": 30,
    "speed": 5,
    "hyper_speed": 15,
    "health": 5000,
    "max_health": 5000,
    "damage": 50,
    "color": (0, 100, 255),
    "hyper_color": (255, 0, 255),
    "attack_cooldown": 0,
    "attack_range": 50,
    "is_hyper": False,
    "hyper_time": 0,
    "hyper_cooldown": 0,
    "hyper_duration": 20,
    "hyper_cooldown_time": 20,
    "grabbed_enemy": None,
    "grab_cooldown": 0,
    "throw_power": 15
}

# Враги
enemies = []
wave_size = 3

def spawn_enemies(count):
    for _ in range(count):
        enemies.append({
            "x": random.randint(100, WIDTH - 100),
            "y": random.randint(100, HEIGHT - 100),
            "size": 25,
            "speed": 2,
            "health": 100,
            "damage": 50,
            "color": (200, 0, 0),
            "bullets": [],
            "shoot_cooldown": 0,
            "shoot_delay": 1000,
            "is_grabbed": False,
            "throw_dx": 0,
            "throw_dy": 0
        })

def enemy_ai(enemy):
    if enemy["is_grabbed"] or enemy["throw_dx"] != 0 or enemy["throw_dy"] != 0:
        return
    
    dx = player["x"] - enemy["x"]
    dy = player["y"] - enemy["y"]
    dist = max(1, (dx**2 + dy**2)**0.5)
    
    enemy["x"] += dx / dist * enemy["speed"]
    enemy["y"] += dy / dist * enemy["speed"]
    
    now = pygame.time.get_ticks()
    if now - enemy["shoot_cooldown"] > enemy["shoot_delay"]:
        enemy["shoot_cooldown"] = now
        enemy["bullets"].append({
            "x": enemy["x"],
            "y": enemy["y"],
            "dx": dx / dist * 7,
            "dy": dy / dist * 7,
            "damage": enemy["damage"]
        })

def play_death_video():
    try:
        os.startfile("C:/Users/gulee/Downloads/Invincible 1x08 Omni Man vs his son Mark. Final Scene Episode.mp4")
    except:
        print("Не удалось воспроизвести видео!")

def activate_hyper_mode():
    current_time = time.time()
    if not player["is_hyper"] and current_time - player["hyper_cooldown"] > player["hyper_cooldown_time"]:
        player["is_hyper"] = True
        player["hyper_time"] = current_time
        hyper_sound.play()
        return True
    return False

def update_hyper_mode():
    current_time = time.time()
    if player["is_hyper"] and current_time - player["hyper_time"] > player["hyper_duration"]:
        player["is_hyper"] = False
        player["hyper_cooldown"] = current_time

def grab_enemy():
    current_time = time.time()
    if player["grabbed_enemy"] is None and current_time - player["grab_cooldown"] > 0.5:
        for enemy in enemies:
            if enemy["is_grabbed"]:
                continue
                
            dx = enemy["x"] - player["x"]
            dy = enemy["y"] - player["y"]
            distance = (dx**2 + dy**2)**0.5
            
            if distance < player["attack_range"]:
                enemy["is_grabbed"] = True
                player["grabbed_enemy"] = enemy
                grab_sound.play()
                return True
    return False

def throw_enemy():
    if player["grabbed_enemy"]:
        enemy = player["grabbed_enemy"]
        enemy["is_grabbed"] = False
        
        mouse_x, mouse_y = pygame.mouse.get_pos()
        dx = mouse_x - player["x"]
        dy = mouse_y - player["y"]
        dist = max(1, (dx**2 + dy**2)**0.5)
        
        enemy["throw_dx"] = dx / dist * player["throw_power"]
        enemy["throw_dy"] = dy / dist * player["throw_power"]
        
        player["grabbed_enemy"] = None
        player["grab_cooldown"] = time.time()
        throw_sound.play()
        return True
    return False

# Первая волна врагов
spawn_enemies(wave_size)

# Основной игровой цикл
running = True
kills = 0
wave = 1
font = pygame.font.SysFont("Arial", 36)

while running:
    screen.fill((10, 10, 20))
    
    # Обновление режимов
    update_hyper_mode()
    
    # Обработка событий
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
            elif event.key == pygame.K_r:
                activate_hyper_mode()
            elif event.key == pygame.K_t:
                if player["grabbed_enemy"] is None:
                    grab_enemy()
                else:
                    throw_enemy()
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            for enemy in enemies[:]:
                if enemy["is_grabbed"]:
                    continue
                    
                dx = enemy["x"] - player["x"]
                dy = enemy["y"] - player["y"]
                distance = (dx**2 + dy**2)**0.5
                
                if distance < player["attack_range"]:
                    punch_sound.play()
                    add_blood_stain(enemy["x"], enemy["y"], 1.5)
                    
                    enemy["health"] -= player["damage"]
                    if enemy["health"] <= 0:
                        kills += 1
                        kill_sound.play()
                        add_blood_stain(enemy["x"], enemy["y"], 3)
                        if player["grabbed_enemy"] == enemy:
                            player["grabbed_enemy"] = None
                        enemies.remove(enemy)
                        player["health"] = min(player["max_health"], player["health"] + 50)
    
    # Управление игроком
    keys = pygame.key.get_pressed()
    current_speed = player["hyper_speed"] if player["is_hyper"] else player["speed"]
    
    if keys[pygame.K_a] and player["x"] > player["size"]:
        player["x"] -= current_speed
    if keys[pygame.K_d] and player["x"] < WIDTH - player["size"]:
        player["x"] += current_speed
    if keys[pygame.K_w] and player["y"] > player["size"]:
        player["y"] -= current_speed
    if keys[pygame.K_s] and player["y"] < HEIGHT - player["size"]:
        player["y"] += current_speed
    
    # Гиперрежим: убийство при касании
    if player["is_hyper"]:
        for enemy in enemies[:]:
            dx = enemy["x"] - player["x"]
            dy = enemy["y"] - player["y"]
            distance = (dx**2 + dy**2)**0.5
            
            if distance < player["size"] + enemy["size"]:
                kills += 1
                kill_sound.play()
                add_blood_stain(enemy["x"], enemy["y"], 5)
                enemies.remove(enemy)
                player["health"] = min(player["max_health"], player["health"] + 50)
    
    # Захваченный враг
    if player["grabbed_enemy"]:
        enemy = player["grabbed_enemy"]
        enemy["x"] = player["x"] + player["size"] + enemy["size"]
        enemy["y"] = player["y"]
    
    # Брошенные враги
    for enemy in enemies[:]:
        if enemy["throw_dx"] != 0 or enemy["throw_dy"] != 0:
            enemy["x"] += enemy["throw_dx"]
            enemy["y"] += enemy["throw_dy"]
            
            # Столкновения с другими врагами
            for other in enemies[:]:
                if other == enemy:
                    continue
                    
                dx = other["x"] - enemy["x"]
                dy = other["y"] - enemy["y"]
                distance = (dx**2 + dy**2)**0.5
                
                if distance < enemy["size"] + other["size"]:
                    kills += 1
                    kill_sound.play()
                    add_blood_stain(other["x"], other["y"], 5)
                    enemies.remove(other)
                    player["health"] = min(player["max_health"], player["health"] + 50)
            
            # Границы экрана
            if (enemy["x"] < -50 or enemy["x"] > WIDTH + 50 or 
                enemy["y"] < -50 or enemy["y"] > HEIGHT + 50):
                enemy["throw_dx"] = 0
                enemy["throw_dy"] = 0
    
    # ИИ врагов
    for enemy in enemies:
        enemy_ai(enemy)
    
    # Пули врагов
    for enemy in enemies[:]:
        for bullet in enemy["bullets"][:]:
            bullet["x"] += bullet["dx"]
            bullet["y"] += bullet["dy"]
            
            dx = bullet["x"] - player["x"]
            dy = bullet["y"] - player["y"]
            distance = (dx**2 + dy**2)**0.5
            
            if distance < player["size"]:
                player["health"] -= bullet["damage"]
                add_blood_stain(player["x"], player["y"], 1)
                enemy["bullets"].remove(bullet)
                if player["health"] <= 0:
                    play_death_video()
                    running = False
            elif (bullet["x"] < 0 or bullet["x"] > WIDTH or 
                  bullet["y"] < 0 or bullet["y"] > HEIGHT):
                enemy["bullets"].remove(bullet)
    
    # Новая волна
    if len(enemies) == 0:
        wave += 1
        wave_size += 1
        spawn_enemies(wave_size)
        if wave > 1:
            player["health"] = min(player["max_health"], player["health"] + 200)
    
    # Отрисовка крови
    for stain in blood_stains:
        x, y, size, alpha = stain
        blood_color = (150 + random.randint(0, 50), 0, 0, alpha)
        blood_surface = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
        pygame.draw.circle(blood_surface, blood_color, (size, size), size)
        screen.blit(blood_surface, (x-size, y-size))
    
    # Отрисовка игрока
    player_color = player["hyper_color"] if player["is_hyper"] else player["color"]
    pygame.draw.circle(screen, player_color, (int(player["x"]), int(player["y"])), player["size"])
    
    # Отрисовка врагов
    for enemy in enemies:
        color = (255, 165, 0) if enemy["is_grabbed"] else enemy["color"]
        pygame.draw.circle(screen, color, (int(enemy["x"]), int(enemy["y"])), enemy["size"])
        
        for bullet in enemy["bullets"]:
            pygame.draw.circle(screen, (255, 200, 0), (int(bullet["x"]), int(bullet["y"])), 5)
    
    # Связь с захваченным врагом
    if player["grabbed_enemy"]:
        enemy = player["grabbed_enemy"]
        pygame.draw.line(screen, (255, 255, 255), 
                        (player["x"], player["y"]), 
                        (enemy["x"], enemy["y"]), 2)
    
    # Интерфейс
    current_time = time.time()
    
    # HP, убийства, волны
    health_text = font.render(f"HP: {player['health']}", True, (0, 255, 0) if player["health"] > 2500 else (255, 0, 0))
    kills_text = font.render(f"Убийств: {kills}", True, (255, 255, 255))
    wave_text = font.render(f"Волна: {wave}", True, (255, 255, 255))
    grab_text = font.render(f"Захват: {'T (отпустить)' if player['grabbed_enemy'] else 'T (захватить)'}", True, (255, 255, 255))
    
    screen.blit(health_text, (20, 20))
    screen.blit(kills_text, (20, 60))
    screen.blit(wave_text, (20, 100))
    screen.blit(grab_text, (20, 140))
    
    # Гиперрежим
    if player["is_hyper"]:
        remaining_time = max(0, player["hyper_duration"] - (current_time - player["hyper_time"]))
        hyper_text = font.render(f"Гиперрежим: {remaining_time:.1f}с", True, (255, 0, 255))
        screen.blit(hyper_text, (WIDTH - 200, 20))
    elif current_time - player["hyper_cooldown"] < player["hyper_cooldown_time"]:
        cooldown = max(0, player["hyper_cooldown_time"] - (current_time - player["hyper_cooldown"]))
        hyper_text = font.render(f"Перезарядка: {cooldown:.1f}с", True, (150, 150, 150))
        screen.blit(hyper_text, (WIDTH - 200, 20))
    
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()