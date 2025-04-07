from pygame import *
import pygame
import sys
from random import randint as r
from time import sleep as s

# Инициализация библиотеки Pygame
pygame.init()
pygame.display.set_caption('Змейка|py')

# Настройки шрифта и экрана
font.init()
path = font.match_font("arial")
Font = font.Font(path, 25)
text = "Счёт: "
width, height = 1280, 720
clock = pygame.time.Clock()
screen = pygame.display.set_mode((width, height))
color = (139, 0, 255)

# Переменные для игрока, яблок и счета
leng = 0
x, y = 100, 100
size = 30
size_b = 20
speed = 3
dx, dy = speed, 0
x_b, y_b = r(0, width - size), r(0, height - size)
x_u, y_u = r(0, width - size), r(0, height - size)
count = 0
upgrade = False
snake_body = []
boo = False
running = True

def draw_snake(snake_body):
    for segment in snake_body:
        pygame.draw.rect(screen, color, (segment[0], segment[1], size, size))

while running:
    screen.fill((0, 0, 0))
    pygame.draw.circle(screen, (255, 0, 0), (x_b, y_b), 10)
    pygame.draw.rect(screen, color, (x, y, size, size))
    if upgrade == False:
        pygame.draw.rect(screen, (0, 0, 255), (x_u, y_u, size_b, size_b))

    x += dx
    y += dy

    # Обновление счета
    a = Font.render(text + str(count), True, (100, 100, 100))
    screen.blit(a, (10, 10))

    # Проверка на сбор яблок
    if x < x_b + size and x + size > x_b and y < y_b + size and y + size > y_b:
        count += 1
        leng += 10
        speed += 0.2

        x_b, y_b = r(0, width - size), r(0, height - size)
    if x < x_u + size and x + size > x_u and y < y_u + size and y + size > y_u:

        upgrade = True
        print(upgrade)
        count += 5
        speed += 2
        x_u, y_u = r(0, width - size), r(0, height - size)
    if upgrade == True:
        print(upgrade)

        if count % 10 != 0 and count & 5 != 0:
            print("Non")
            boo = True
    if boo == True:
        if count % 10 == 0:
            print("Boo")
            upgrade = False
            speed -= 2
            boo = False

    # Проверка на столкновение с краями
    if x < 0 or x > width or y < 0 or y > height:
        running = False

    # Обработка событий
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            pygame.quit()
            sys.exit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP and dy == 0:
                dx, dy = 0, -speed
            elif event.key == pygame.K_DOWN and dy == 0:
                dx, dy = 0, speed
            elif event.key == pygame.K_LEFT and dx == 0:
                dx, dy = -speed, 0
            elif event.key == pygame.K_RIGHT and dx == 0:
                dx, dy = speed, 0

    #Добавление тела змейки
    snake_body.append((x, y))
    #Ограничение длины змейки
    if len(snake_body) > leng :
        del snake_body[0]
    #Добавление смерти при столкновении головы с телом
    if (x, y) in snake_body[:-1]:
        running = False

    #Рисуем змейку
    draw_snake(snake_body)

    pygame.display.flip()
    clock.tick(60)

# Экран окончания игры
s(1)
a = Font.render("Вы проиграли!", True, (100, 100, 100))
screen.blit(a, (500, 300))
pygame.display.flip()
s(3)
