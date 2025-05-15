import pygame
import random
import sys

# --- Constantes ---
WIDTH, HEIGHT = 600, 600
CELL_SIZE = 20
GRID_WIDTH = WIDTH // CELL_SIZE
GRID_HEIGHT = HEIGHT // CELL_SIZE

# --- Couleurs ---
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 200, 0)
RED = (200, 0, 0)
DARK_GRAY = (30, 30, 30)
LIGHT_GRAY = (60, 60, 60)

# --- Initialisation ---
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()
font = pygame.font.SysFont("consolas", 24)

# --- Fonctions utilitaires ---
def draw_text(text, x, y, color=WHITE, center=False):
    img = font.render(text, True, color)
    if center:
        rect = img.get_rect(center=(x, y))
        screen.blit(img, rect)
    else:
        screen.blit(img, (x, y))

def draw_grid():
    for x in range(0, WIDTH, CELL_SIZE):
        pygame.draw.line(screen, LIGHT_GRAY, (x, 0), (x, HEIGHT))
    for y in range(0, HEIGHT, CELL_SIZE):
        pygame.draw.line(screen, LIGHT_GRAY, (0, y), (WIDTH, y))

def random_position():
    return [random.randint(0, GRID_WIDTH - 1), random.randint(0, GRID_HEIGHT - 1)]

# --- Menu principal ---
def show_menu():
    while True:
        screen.fill(DARK_GRAY)
        draw_text("SNAKE 2D (REALISTE)", WIDTH // 2, HEIGHT // 3, GREEN, center=True)
        draw_text("Appuie sur ESPACE pour jouer", WIDTH // 2, HEIGHT // 2, WHITE, center=True)
        draw_text("Appuie sur ÉCHAP pour quitter", WIDTH // 2, HEIGHT // 2 + 40, WHITE, center=True)
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    return
                elif event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()

# --- Jeu principal ---
def run_game():
    snake = [[GRID_WIDTH // 2, GRID_HEIGHT // 2]]
    direction = [1, 0]  # droite
    apple = random_position()
    score = 0
    speed = 10

    running = True
    while running:
        clock.tick(speed)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        keys = pygame.key.get_pressed()
        if keys[pygame.K_UP] and direction != [0, 1]:
            direction = [0, -1]
        elif keys[pygame.K_DOWN] and direction != [0, -1]:
            direction = [0, 1]
        elif keys[pygame.K_LEFT] and direction != [1, 0]:
            direction = [-1, 0]
        elif keys[pygame.K_RIGHT] and direction != [-1, 0]:
            direction = [1, 0]

        # Avancer
        head = [snake[0][0] + direction[0], snake[0][1] + direction[1]]
        snake.insert(0, head)

        # Collision avec pomme
        if head == apple:
            score += 1
            apple = random_position()
        else:
            snake.pop()

        # Collision mur ou soi-même
        if (
            head[0] < 0 or head[0] >= GRID_WIDTH or
            head[1] < 0 or head[1] >= GRID_HEIGHT or
            head in snake[1:]
        ):
            return score  # Fin de partie

        # Affichage
        screen.fill(BLACK)
        draw_grid()
        for segment in snake:
            pygame.draw.rect(screen, GREEN, (segment[0] * CELL_SIZE, segment[1] * CELL_SIZE, CELL_SIZE, CELL_SIZE))
        pygame.draw.rect(screen, RED, (apple[0] * CELL_SIZE, apple[1] * CELL_SIZE, CELL_SIZE, CELL_SIZE))
        draw_text(f"Score: {score}", 10, 10)
        pygame.display.flip()

# --- Boucle principale ---
while True:
    show_menu()
    final_score = run_game()
    screen.fill(DARK_GRAY)
    draw_text("GAME OVER", WIDTH // 2, HEIGHT // 2 - 30, RED, center=True)
    draw_text(f"Score final: {final_score}", WIDTH // 2, HEIGHT // 2, WHITE, center=True)
    draw_text("Appuie sur ESPACE pour rejouer", WIDTH // 2, HEIGHT // 2 + 40, WHITE, center=True)
    draw_text("ÉCHAP pour quitter", WIDTH // 2, HEIGHT // 2 + 70, WHITE, center=True)
    pygame.display.flip()

    # Attente entrée
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    waiting = False
                elif event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()






































































































