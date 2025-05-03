import pygame
import random
import time

# Инициализация Pygame
pygame.init()

# Получение размеров экрана
screen_width = pygame.display.Info().current_w
screen_height = pygame.display.Info().current_h

# Создание окна без рамки
screen = pygame.display.set_mode((screen_width, screen_height), pygame.NOFRAME)

# Функция для создания "тоннеля"
def draw_tunnel(x, y, scale):
    # Захват изображения экрана
    screenshot = pygame.image.capture(screen)
    # Масштабирование изображения
    scaled_screenshot = pygame.transform.scale(screenshot, (int(screen_width * scale), int(screen_height * scale)))
    # Отображение масштабированного изображения
    screen.blit(scaled_screenshot, (x, y))

# Основной цикл
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Инверсия цветов (мигание)
    if random.random() < 0.1:
        screen.fill((255, 255, 255)) # Белый экран для имитации инверсии
    else:
        screen.fill((0, 0, 0)) # Черный экран

    # Рисование "тоннеля"
    num_clones = 5
    for i in range(num_clones):
        scale = 1 - (i * 0.15)
        x = (screen_width - screen_width * scale) / 2
        y = (screen_height - screen_height * scale) / 2
        draw_tunnel(x, y, scale)

    # Обновление экрана
    pygame.display.flip()
    time.sleep(0.05) # Небольшая задержка

# Завершение Pygame
pygame.quit()
