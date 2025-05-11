import pygame
import random
import sys

# Инициализация Pygame
pygame.init()

# Константы
WIDTH, HEIGHT = 550, 300
NOWHITE = (75, 0, 130)
BLACK = (0, 0, 0)
FONT_COLOR = (147, 112, 219)
FONT = pygame.font.Font(None, 31)

# Создание окна
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('Угадай число')

# Функция для генерации нового числа
def generate_new_number():
    return random.randint(0, 10)

# Генерация случайного числа от 0 до 10
num = generate_new_number()

# Переменные игры
attempts = 0
input_text = ''
message = ''

# Загрузка и воспроизведение музыки
pygame.mixer.music.load("Menu.mp3")
pygame.mixer.music.play(-1)  # -1 означает бесконечное воспроизведение

def draw_text_with_outline(text, pos, outline_color, font_color):
    # Создаем текст для контура
    outline_surface = FONT.render(text, True, outline_color)
    # Создаем текст для основного цвета
    text_surface = FONT.render(text, True, font_color)

    # Рисуем контур (чуть смещен)
    screen.blit(outline_surface, (pos[0] - 1, pos[1]))  # вверх
    screen.blit(outline_surface, (pos[0] + 1, pos[1]))  # вниз
    screen.blit(outline_surface, (pos[0], pos[1] - 1))  # влево
    screen.blit(outline_surface, (pos[0], pos[1] + 1))  # вправо

    # Рисуем основной текст
    screen.blit(text_surface, pos)

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if event.type == pygame.KEYDOWN:
            # Обработка нажатий клавиш
            if event.key == pygame.K_RETURN:
                try:
                    guess = int(input_text)
                    attempts += 1
                    if guess < num:
                        message = "Слишком низкое число!"
                    elif guess > num:
                        message = "Слишком высокое число!"
                    else:
                        message = (f"Поздравляю! Ты угадал число {num} "
                                   f"за {attempts} попыток!")
                        # Генерируем новое число
                        num = generate_new_number()
                        attempts = 0  # Сбрасываем попытки
                except ValueError:
                    message = "Пожалуйста, введите число от 0 до 10."
                input_text = ''
            elif event.key == pygame.K_BACKSPACE:
                input_text = input_text[:-1]
            else:
                input_text += event.unicode

    # Отрисовка
    screen.fill(NOWHITE)

    draw_text_with_outline('Угадай число от 0 до 10:', (50, 50), BLACK, FONT_COLOR)
    draw_text_with_outline(input_text, (50, 100), BLACK, FONT_COLOR)
    draw_text_with_outline(message, (50, 150), BLACK, FONT_COLOR)
    draw_text_with_outline(f'Попытки: {attempts}', (50, 200), BLACK, FONT_COLOR)

    pygame.display.flip()
