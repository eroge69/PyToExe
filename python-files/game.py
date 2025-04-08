Python 3.11.9 (tags/v3.11.9:de54cf5, Apr  2 2024, 10:12:12) [MSC v.1938 64 bit (AMD64)] on win32
Type "help", "copyright", "credits" or "license()" for more information.
import pygame
import random

pygame.init()

# Настройки экрана
width = 800
height = 600
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Guess the Number")

# Цвета
white = (255, 255, 255)
black = (0, 0, 0)
green = (0, 255, 0)
red = (255, 0, 0)

# Шрифт
font = pygame.font.Font(None, 36)

# Число для угадывания
numbers = [str(i) for i in range(1, 11)]  # ["1", "2", ..., "10"]
secret_number = random.choice(numbers)
user_guess = ""  # Строка для ввода числа

# Состояние игры
game_state = "playing"  # "playing", "win", "lose"
message = "Guess a number from 1 to 10"

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN and game_state == "playing":
            if event.key == pygame.K_RETURN:
...                 if user_guess == secret_number:
...                     game_state = "win"
...                     message = "Correct!"
...                 else:
...                     game_state = "lose"
...                     message = f"Incorrect, it was {secret_number}"
...             elif event.key == pygame.K_BACKSPACE:
...                 user_guess = user_guess[:-1]
...             elif event.unicode.isdigit() and len(user_guess) < 2:  # Только цифры и макс. 2 символа
...                 user_guess += event.unicode
... 
...     # Отрисовка
...     screen.fill(black)
... 
...     # Отображение сообщения
...     message_surface = font.render(message, True, white)
...     message_rect = message_surface.get_rect(center=(width // 2, 50))
...     screen.blit(message_surface, message_rect)
... 
...     # Поле ввода
...     input_surface = font.render(user_guess, True, white)
...     input_rect = input_surface.get_rect(center=(width // 2, 150))
...     pygame.draw.rect(screen, white, (input_rect.x - 5, input_rect.y - 5, input_rect.width + 10, input_rect.height + 10), 2)  # Рамка
...     screen.blit(input_surface, input_rect)
... 
...     # Сообщение о результате
...     if game_state == "win":
...         result_color = green
...     elif game_state == "lose":
...         result_color = red
...     else:
...         result_color = white #Пока играем, цвет не важен
... 
...     pygame.display.flip()
... 
... pygame.quit()
SyntaxError: multiple statements found while compiling a single statement
