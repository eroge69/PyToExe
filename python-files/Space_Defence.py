import pygame
import sys
import random

pygame.init()
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Space Defense")
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 40)

# Kolory
WHITE = (255, 255, 255)
RED = (255, 50, 50)
GREEN = (50, 255, 50)
BLUE = (100, 100, 255)
BLACK = (0, 0, 0)
GRAY = (100, 100, 100)

# Obiekty
player_img = pygame.Surface((50, 30))
player_img.fill(GREEN)
enemy_img = pygame.Surface((40, 30))
enemy_img.fill(RED)
bullet_img = pygame.Surface((5, 10))
bullet_img.fill(WHITE)
boss_img = pygame.Surface((150, 80))
boss_img.fill((200, 0, 200))

heart_img = pygame.Surface((25, 25))
pygame.draw.polygon(heart_img, RED, [(12, 5), (22, 5), (25, 15), (12, 24), (0, 15), (3, 5)])

class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = player_img
        self.rect = self.image.get_rect(center=(WIDTH // 2, HEIGHT - 50))
        self.speed = 6
        self.lives = 3

    def update(self, keys):
        if keys[pygame.K_LEFT] and self.rect.left > 0:
            self.rect.x -= self.speed
        if keys[pygame.K_RIGHT] and self.rect.right < WIDTH:
            self.rect.x += self.speed

class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = enemy_img
        self.rect = self.image.get_rect(topleft=(x, y))

class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, direction, color, speed=8):
        super().__init__()
        self.image = bullet_img.copy()
        self.image.fill(color)
        self.rect = self.image.get_rect(center=(x, y))
        self.speed = speed * direction

    def update(self):
        self.rect.y += self.speed
        if self.rect.bottom < 0 or self.rect.top > HEIGHT:
            self.kill()

class Boss(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = boss_img
        self.rect = self.image.get_rect(center=(WIDTH // 2, 100))
        self.health = 25
        self.shoot_timer = 0

    def update(self):
        self.shoot_timer += 1

    def shoot(self):
        if self.shoot_timer > 30:
            self.shoot_timer = 0
            return Bullet(self.rect.centerx, self.rect.bottom, 1, RED, speed=7)
        return None

def draw_hearts(lives):
    for i in range(lives):
        screen.blit(heart_img, (WIDTH - 30 * (i + 1), HEIGHT - 40))

def draw_boss_health(health):
    max_width = 300
    pygame.draw.rect(screen, GRAY, (WIDTH // 2 - 150, 20, max_width, 20))
    current_width = max_width * (health / 25)
    pygame.draw.rect(screen, RED, (WIDTH // 2 - 150, 20, current_width, 20))

def create_enemies():
    enemies = pygame.sprite.Group()
    for i in range(5):
        x = 100 + i * 140
        y = 100
        enemies.add(Enemy(x, y))
    return enemies

def show_message(text, color):
    screen.fill(BLACK)
    msg = font.render(text, True, color)
    screen.blit(msg, (WIDTH // 2 - msg.get_width() // 2, HEIGHT // 2 - msg.get_height() // 2))
    pygame.display.flip()

def game_loop():
    level = 1
    while True:
        result = run_level(level)
        if result == "gameover":
            show_message("GAME OVER", RED)
            pygame.time.wait(2000)
            level = 1
        elif result == "next":
            level += 1
        elif result == "win":
            show_message("THE END", GREEN)
            pygame.time.wait(3000)
            return

def run_level(level):
    player = Player()
    player_group = pygame.sprite.Group(player)
    enemies = create_enemies() if level < 6 else pygame.sprite.Group()
    player_bullets = pygame.sprite.Group()
    enemy_bullets = pygame.sprite.Group()
    shoot_cooldown = 0
    enemy_shoot_timer = 0
    boss = Boss() if level == 6 else None
    running = True

    while running:
        clock.tick(60)
        screen.fill(BLACK)
        keys = pygame.key.get_pressed()

        # Zdarzenia
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE and shoot_cooldown == 0:
                bullet = Bullet(player.rect.centerx, player.rect.top, -1, BLUE)
                player_bullets.add(bullet)
                shoot_cooldown = 20

        shoot_cooldown = max(0, shoot_cooldown - 1)
        enemy_shoot_timer += 1

        if level < 6 and enemy_shoot_timer >= 60 - level * 5:
            enemy_shoot_timer = 0
            if enemies:
                shooter = random.choice(enemies.sprites())
                bullet = Bullet(shooter.rect.centerx, shooter.rect.bottom, 1, RED, speed=4 + level * 2)
                enemy_bullets.add(bullet)

        if level == 6:
            boss.update()
            shot = boss.shoot()
            if shot:
                enemy_bullets.add(shot)

        # Aktualizacja
        player.update(keys)
        player_bullets.update()
        enemy_bullets.update()

        # Kolizje z przeciwnikami
        for bullet in player_bullets:
            if level < 6:
                hit = pygame.sprite.spritecollide(bullet, enemies, True)
                if hit:
                    bullet.kill()
            else:
                if boss and boss.rect.colliderect(bullet.rect):
                    boss.health -= 1
                    bullet.kill()
                    if boss.health <= 0:
                        return "win"

        # Trafienie gracza
        for b in enemy_bullets:
            if player.rect.colliderect(b.rect):
                b.kill()
                player.lives -= 1
                if player.lives == 0:
                    return "gameover"

        if level < 6 and not enemies:
            return "next"

        # Rysowanie
        player_group.draw(screen)
        enemies.draw(screen)
        player_bullets.draw(screen)
        enemy_bullets.draw(screen)

        screen.blit(font.render(f"Level: {level}", True, WHITE), (10, 10))
        draw_hearts(player.lives)
        if level == 6 and boss:
            screen.blit(boss.image, boss.rect)
            draw_boss_health(boss.health)

        pygame.display.flip()

# Start
game_loop()
pygame.quit()
sys.exit()
