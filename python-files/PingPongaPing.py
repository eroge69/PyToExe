#--------------- IMPORT ---------------
import pygame
import sys
import random
import math

pygame.init()
#--------------- VARIABLE ---------------
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("KnappPong")

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
font = pygame.font.SysFont(None, 36)

#--------------- CODE ---------------

BALL_SIZE = 20
ball = pygame.Rect(WIDTH//2, HEIGHT//2, BALL_SIZE, BALL_SIZE)
ball_speed = [random.choice([-4, 4]), random.choice([-4, 4])]

PADDLE_LENGTH = 100
PADDLE_THICKNESS = 15
PADDLE_SPEED = 6
AI_SPEED = 6

left_paddle = pygame.Rect(10, HEIGHT//2 - PADDLE_LENGTH//2, PADDLE_THICKNESS, PADDLE_LENGTH)
right_paddle = pygame.Rect(WIDTH - 10 - PADDLE_THICKNESS, HEIGHT//2 - PADDLE_LENGTH//2, PADDLE_THICKNESS, PADDLE_LENGTH)
top_paddle = pygame.Rect(WIDTH//2 - PADDLE_LENGTH//2, 10, PADDLE_LENGTH, PADDLE_THICKNESS)
bottom_paddle = pygame.Rect(WIDTH//2 - PADDLE_LENGTH//2, HEIGHT - 10 - PADDLE_THICKNESS, PADDLE_LENGTH, PADDLE_THICKNESS)

score_left = score_right = score_top = score_bottom = 0
clock = pygame.time.Clock()

right_ai_target = HEIGHT // 2
bottom_ai_target = WIDTH // 2

def reset_ball():
    ball.center = (WIDTH // 2, HEIGHT // 2)
    ball_speed[0] = random.choice([-4, 4])
    ball_speed[1] = random.choice([-4, 4])

def draw_scores():
    screen.blit(font.render(f"Left: {score_left}", True, WHITE), (20, HEIGHT//2 - 60))
    screen.blit(font.render(f"Right: {score_right}", True, WHITE), (WIDTH - 140, HEIGHT//2 - 60))
    screen.blit(font.render(f"Top: {score_top}", True, WHITE), (WIDTH//2 - 60, 40))
    screen.blit(font.render(f"Bottom: {score_bottom}", True, WHITE), (WIDTH//2 - 80, HEIGHT - 70))

def ai_behavior():
    global right_ai_target, bottom_ai_target

    if ball_speed[0] > 0:
        right_ai_target = ball.centery + random.randint(-30, 30)  # 30px Abweichung für Unsicherheit

    if right_paddle.centery < right_ai_target:
        right_paddle.y += AI_SPEED
    elif right_paddle.centery > right_ai_target:
        right_paddle.y -= AI_SPEED

    if ball_speed[1] > 0:
        bottom_ai_target = ball.centerx + random.randint(-30, 30)  # 30px Abweichung für Unsicherheit

    if bottom_paddle.centerx < bottom_ai_target:
        bottom_paddle.x += AI_SPEED
    elif bottom_paddle.centerx > bottom_ai_target:
        bottom_paddle.x -= AI_SPEED

def move_paddles(keys):
    if keys[pygame.K_w] and left_paddle.top > 0:
        left_paddle.y -= PADDLE_SPEED
    if keys[pygame.K_s] and left_paddle.bottom < HEIGHT:
        left_paddle.y += PADDLE_SPEED
    if keys[pygame.K_a] and top_paddle.left > 0:
        top_paddle.x -= PADDLE_SPEED
    if keys[pygame.K_d] and top_paddle.right < WIDTH:
        top_paddle.x += PADDLE_SPEED

def draw_dynamic():
    time = pygame.time.get_ticks() / 1000
    color = (
        int(127.5 + 127.5 * math.sin(time + 0)),
        int(127.5 + 127.5 * math.sin(time + 2)),
        int(127.5 + 127.5 * math.sin(time + 4))
    )
    screen.fill(color)

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    keys = pygame.key.get_pressed()
    move_paddles(keys)
    ai_behavior()

    ball.x += ball_speed[0]
    ball.y += ball_speed[1]

    if ball.colliderect(left_paddle) or ball.colliderect(right_paddle):
        ball_speed[0] *= -1
    if ball.colliderect(top_paddle) or ball.colliderect(bottom_paddle):
        ball_speed[1] *= -1

    if ball.left <= 0:
        score_left += 1
        reset_ball()
    elif ball.right >= WIDTH:
        score_right += 1
        reset_ball()
    elif ball.top <= 0:
        score_top += 1
        reset_ball()
    elif ball.bottom >= HEIGHT:
        score_bottom += 1
        reset_ball()

    draw_dynamic()

    pygame.draw.ellipse(screen, WHITE, ball)
    pygame.draw.rect(screen, WHITE, left_paddle)
    pygame.draw.rect(screen, WHITE, right_paddle)
    pygame.draw.rect(screen, WHITE, top_paddle)
    pygame.draw.rect(screen, WHITE, bottom_paddle)
    draw_scores()

    pygame.display.flip()
    clock.tick(60)