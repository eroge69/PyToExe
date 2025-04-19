import pygame
import sys
import random
import json
import os
from pygame import mixer

# Инициализация Pygame
pygame.init()
mixer.init()

# Константы
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60
GRAVITY = 0.5
JUMP_STRENGTH = -12
PLAYER_SPEED = 5

# Цвета
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (0, 0, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)

# Создание окна
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Сложный Платформер")
clock = pygame.time.Clock()

# Загрузка изображений и звуков
def load_image(name, scale=1):
    img = pygame.image.load(f"assets/images/{name}.png").convert_alpha()
    return pygame.transform.scale(img, (img.get_width() * scale, img.get_height() * scale))

def load_sound(name):
    return mixer.Sound(f"assets/sounds/{name}.wav")

# Класс игрока
class Player(pygame.sprite.Sprite):
    def init(self, x, y):
        super().init()
        self.image = load_image("player", 2)
        self.rect = self.image.get_rect(topleft=(x, y))
        self.velocity_y = 0
        self.jump_sound = load_sound("jump")
        self.health = 100

    def update(self, platforms, enemies):
        # Гравитация
        self.velocity_y += GRAVITY
        self.rect.y += self.velocity_y

        # Столкновения с платформами
        for platform in platforms:
            if self.rect.colliderect(platform.rect) and self.velocity_y > 0:
                self.rect.bottom = platform.rect.top
                self.velocity_y = 0

        # Управление
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            self.rect.x -= PLAYER_SPEED
        if keys[pygame.K_RIGHT]:
            self.rect.x += PLAYER_SPEED
        if keys[pygame.K_SPACE] and self.velocity_y == 0:
            self.velocity_y = JUMP_STRENGTH
            self.jump_sound.play()

        # Столкновения с врагами
        for enemy in enemies:
            if self.rect.colliderect(enemy.rect):
                self.health -= 10
                enemy.kill()

# Класс платформы
class Platform(pygame.sprite.Sprite):
    def init(self, x, y, width, height):
        super().init()
        self.image = pygame.Surface((width, height))
        self.image.fill(GREEN)
        self.rect = self.image.get_rect(topleft=(x, y))

# Класс врага
class Enemy(pygame.sprite.Sprite):
    def init(self, x, y, enemy_type="ground"):
        super().init()
        self.enemy_type = enemy_type
        if enemy_type == "flying":
            self.image = load_image("enemy_fly", 2)
        else:
            self.image = load_image("enemy_ground", 2)
        self.rect = self.image.get_rect(topleft=(x, y))
        self.direction = random.choice([-1, 1])
        self.speed = random.randint(2, 4)

    def update(self):
        self.rect.x += self.direction * self.speed
        if self.rect.left <= 0 or self.rect.right >= SCREEN_WIDTH:
            self.direction *= -1

# Класс игры
class Game:
    def init(self):
        self.player = None
        self.platforms = pygame.sprite.Group()
        self.enemies = pygame.sprite.Group()
        self.level = 1
        self.score = 0
        self.font = pygame.font.SysFont("Arial", 24)
        self.load_level(self.level)

    def load_level(self, level):
        # Генерация procedural-уровня
        self.platforms.empty()
        self.enemies.empty()

        # Грунт
        for x in range(0, SCREEN_WIDTH, 64):
            self.platforms.add(Platform(x, SCREEN_HEIGHT - 40, 64, 40))

        # Платформы
        for _ in range(10):
            x = random.randint(0, SCREEN_WIDTH - 100)
            y = random.randint(100, SCREEN_HEIGHT - 200)
            width = random.randint(50, 200)
            self.platforms.add(Platform(x, y, width, 20))

        # Враги
        for _ in range(5):
            x = random.randint(0, SCREEN_WIDTH - 50)
            y = random.randint(50, SCREEN_HEIGHT - 100)
            enemy_type = random.choice(["ground", "flying"])
            self.enemies.add(Enemy(x, y, enemy_type))
# Игрок
        if not self.player:
            self.player = Player(100, SCREEN_HEIGHT - 100)
        else:
            self.player.rect.topleft = (100, SCREEN_HEIGHT - 100)

    def save_game(self):
        data = {
            "level": self.level,
            "score": self.score,
            "health": self.player.health
        }
        with open("save.json", "w") as f:
            json.dump(data, f)

    def load_game(self):
        if os.path.exists("save.json"):
            with open("save.json", "r") as f:
                data = json.load(f)
                self.level = data["level"]
                self.score = data["score"]
                self.player.health = data["health"]
                self.load_level(self.level)

    def run(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.save_game()
                        running = False

            # Обновление
            self.player.update(self.platforms, self.enemies)
            self.enemies.update()

            # Отрисовка
            screen.fill(BLACK)
            self.platforms.draw(screen)
            self.enemies.draw(screen)
            screen.blit(self.player.image, self.player.rect)

            # UI
            health_text = self.font.render(f"Health: {self.player.health}", True, WHITE)
            level_text = self.font.render(f"Level: {self.level}", True, WHITE)
            screen.blit(health_text, (10, 10))
            screen.blit(level_text, (10, 40))

            pygame.display.update()
            clock.tick(FPS)

# Запуск игры
if name == "main":
    game = Game()
    game.run()
    pygame.quit()
    sys.exit()