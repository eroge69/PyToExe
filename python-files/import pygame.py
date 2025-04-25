import pygame
import math
import random

pygame.init()

WIDTH, HEIGHT = 800, 600
win = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Strinova Educational ESP and Aim Assist")

WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 100, 255)
BLACK = (0, 0, 0)

player_pos = [WIDTH // 2, HEIGHT // 2]
player_size = 20
player_speed = 5

enemy_size = 20
enemy_count = 5
enemies = [[random.randint(0, WIDTH - enemy_size), random.randint(0, HEIGHT - enemy_size)] for _ in range(enemy_count)]

def get_closest_enemy(player, enemies):
    closest = None
    min_dist = float("inf")
    for enemy in enemies:
        dist = math.hypot(enemy[0] - player[0], enemy[1] - player[1])
        if dist < min_dist:
            min_dist = dist
            closest = enemy
    return closest

def aim_at_target(player, target, speed):
    dx = target[0] - player[0]
    dy = target[1] - player[1]
    distance = math.hypot(dx, dy)
    if distance == 0:
        return player
    dx /= distance
    dy /= distance
    player[0] += dx * speed
    player[1] += dy * speed
    return player

run = True
clock = pygame.time.Clock()
while run:
    clock.tick(60)
    win.fill(BLACK)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

    keys = pygame.key.get_pressed()
    if keys[pygame.K_w]: player_pos[1] -= player_speed
    if keys[pygame.K_s]: player_pos[1] += player_speed
    if keys[pygame.K_a]: player_pos[0] -= player_speed
    if keys[pygame.K_d]: player_pos[0] += player_speed

    pygame.draw.rect(win, BLUE, (*player_pos, player_size, player_size))

    for enemy in enemies:
        pygame.draw.rect(win, RED, (*enemy, enemy_size, enemy_size), 2)

    target = get_closest_enemy(player_pos, enemies)
    if target:
        pygame.draw.line(win, GREEN, (player_pos[0] + player_size // 2, player_pos[1] + player_size // 2),
                         (target[0] + enemy_size // 2, target[1] + enemy_size // 2), 2)
        player_pos = aim_at_target(player_pos, target, 1.5)  # Smooth aimbot effect

    pygame.display.update()

pygame.quit()