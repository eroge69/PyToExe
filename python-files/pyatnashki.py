import pygame
import random

# Константы
SIZE = 4  # Размер поля 4x4
TILE_SIZE = 100
MARGIN = 5
WIDTH, HEIGHT = SIZE * TILE_SIZE, SIZE * TILE_SIZE

# Цвета
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)

# Инициализация Pygame
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Пятнашки")
font = pygame.font.Font(None, 50)

def shuffle_tiles():
    tiles = list(range(1, SIZE**2)) + [None]
    random.shuffle(tiles)
    return tiles

def draw_board(tiles):
    screen.fill(WHITE)
    for i in range(SIZE):
        for j in range(SIZE):
            value = tiles[i * SIZE + j]
            if value:
                x, y = j * TILE_SIZE, i * TILE_SIZE
                pygame.draw.rect(screen, GRAY, (x, y, TILE_SIZE - MARGIN, TILE_SIZE - MARGIN))
                text = font.render(str(value), True, BLACK)
                screen.blit(text, (x + TILE_SIZE//3, y + TILE_SIZE//3))
    pygame.display.flip()

def find_empty(tiles):
    index = tiles.index(None)
    return index // SIZE, index % SIZE

def move_tile(tiles, x, y):
    empty_x, empty_y = find_empty(tiles)
    if (abs(empty_x - x) == 1 and empty_y == y) or (abs(empty_y - y) == 1 and empty_x == x):
        tiles[empty_x * SIZE + empty_y], tiles[x * SIZE + y] = tiles[x * SIZE + y], tiles[empty_x * SIZE + empty_y]

def check_win(tiles):
    return tiles[:-1] == list(range(1, SIZE**2))

def get_tile_clicked(pos):
    x, y = pos
    return y // TILE_SIZE, x // TILE_SIZE

tiles = shuffle_tiles()
running = True
while running:
    draw_board(tiles)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            tile_x, tile_y = get_tile_clicked(event.pos)
            move_tile(tiles, tile_x, tile_y)
            if check_win(tiles):
                print("Вы выиграли!")
pygame.quit()
