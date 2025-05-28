import pygame
import random

# Ekran o‘lchamlari
WIDTH, HEIGHT = 300, 600
ROWS, COLS = 20, 10
BLOCK_SIZE = 30

# Ranglar
BLACK = (0, 0, 0)
GRAY = (50, 50, 50)
WHITE = (255, 255, 255)
COLORS = [
    (0, 255, 255),  # I
    (0, 0, 255),    # J
    (255, 165, 0),  # L
    (255, 255, 0),  # O
    (0, 255, 0),    # S
    (128, 0, 128),  # T
    (255, 0, 0)     # Z
]

# Figuralar
SHAPES = [
    [[1, 1, 1, 1]],                        # I
    [[1, 0, 0], [1, 1, 1]],               # J
    [[0, 0, 1], [1, 1, 1]],               # L
    [[1, 1], [1, 1]],                     # O
    [[0, 1, 1], [1, 1, 0]],               # S
    [[0, 1, 0], [1, 1, 1]],               # T
    [[1, 1, 0], [0, 1, 1]]                # Z
]

class Piece:
    def __init__(self, shape, color):
        self.shape = shape
        self.color = color
        self.x = COLS // 2 - len(shape[0]) // 2
        self.y = 0

    def rotate(self):
        self.shape = [list(row) for row in zip(*self.shape[::-1])]

def create_grid(locked_positions):
    grid = [[BLACK for _ in range(COLS)] for _ in range(ROWS)]
    for (x, y), color in locked_positions.items():
        grid[y][x] = color
    return grid

def valid_space(shape, x, y, grid):
    for i, row in enumerate(shape):
        for j, cell in enumerate(row):
            if cell:
                nx, ny = x + j, y + i
                if nx < 0 or nx >= COLS or ny >= ROWS or (ny >= 0 and grid[ny][nx] != BLACK):
                    return False
    return True

def clear_rows(grid, locked):
    cleared = 0
    for i in range(ROWS-1, -1, -1):
        if BLACK not in grid[i]:
            cleared += 1
            for j in range(COLS):
                del locked[(j, i)]
            for k in sorted(list(locked.keys()), key=lambda x: x[1])[::-1]:
                x, y = k
                if y < i:
                    locked[(x, y+1)] = locked.pop((x, y))
    return cleared

def draw_grid(surface, grid):
    for y in range(ROWS):
        for x in range(COLS):
            pygame.draw.rect(surface, grid[y][x], (x*BLOCK_SIZE, y*BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE))
    for y in range(ROWS):
        pygame.draw.line(surface, GRAY, (0, y*BLOCK_SIZE), (WIDTH, y*BLOCK_SIZE))
    for x in range(COLS):
        pygame.draw.line(surface, GRAY, (x*BLOCK_SIZE, 0), (x*BLOCK_SIZE, HEIGHT))

def draw_text_center(surface, text, size, color):
    font = pygame.font.SysFont("comicsans", size, bold=True)
    label = font.render(text, True, color)
    surface.blit(label, (WIDTH//2 - label.get_width()//2, HEIGHT//2 - label.get_height()//2))

def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Tetris – Azamat edition!")
    clock = pygame.time.Clock()

    locked = {}
    grid = create_grid(locked)

    current_piece = Piece(random.choice(SHAPES), random.choice(COLORS))
    next_piece = Piece(random.choice(SHAPES), random.choice(COLORS))

    fall_time = 0
    fall_speed = 0.5
    score = 0
    paused = False

    run = True
    while run:
        grid = create_grid(locked)
        fall_time += clock.get_rawtime()
        clock.tick()

        if not paused and fall_time / 1000 >= fall_speed:
            fall_time = 0
            current_piece.y += 1
            if not valid_space(current_piece.shape, current_piece.x, current_piece.y, grid):
                current_piece.y -= 1
                for i, row in enumerate(current_piece.shape):
                    for j, cell in enumerate(row):
                        if cell:
                            locked[(current_piece.x + j, current_piece.y + i)] = current_piece.color
                current_piece = next_piece
                next_piece = Piece(random.choice(SHAPES), random.choice(COLORS))
                score += clear_rows(grid, locked) * 100

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    if valid_space(current_piece.shape, current_piece.x - 1, current_piece.y, grid):
                        current_piece.x -= 1
                if event.key == pygame.K_RIGHT:
                    if valid_space(current_piece.shape, current_piece.x + 1, current_piece.y, grid):
                        current_piece.x += 1
                if event.key == pygame.K_DOWN:
                    if valid_space(current_piece.shape, current_piece.x, current_piece.y + 1, grid):
                        current_piece.y += 1
                if event.key == pygame.K_UP:
                    current_piece.rotate()
                    if not valid_space(current_piece.shape, current_piece.x, current_piece.y, grid):
                        for _ in range(3): current_piece.rotate()
                if event.key == pygame.K_p:
                    paused = not paused
                if event.key == pygame.K_r:
                    main()
                    return

        for i, row in enumerate(current_piece.shape):
            for j, cell in enumerate(row):
                if cell:
                    x = current_piece.x + j
                    y = current_piece.y + i
                    if y >= 0:
                        grid[y][x] = current_piece.color

        screen.fill(BLACK)
        draw_grid(screen, grid)

        # Ball
        font = pygame.font.SysFont("comicsans", 24)
        score_text = font.render(f"Ball: {score}", True, WHITE)
        screen.blit(score_text, (10, 10))

        if paused:
            draw_text_center(screen, "PAUZAGA QO‘YILDI", 36, WHITE)

        pygame.display.update()

    pygame.quit()

if __name__ == "__main__":
    main()
s