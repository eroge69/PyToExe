import pygame
import random

# Initialize pygame
pygame.init()

# Screen dimensions
WIDTH, HEIGHT = 800, 600
CELL_SIZE = 40

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)

# Initialize screen
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Maze Game")

# Clock for controlling frame rate
clock = pygame.time.Clock()

# Generate a random maze
def generate_maze(rows, cols):
    maze = [[1 for _ in range(cols)] for _ in range(rows)]
    for _ in range(rows * cols // 4):
        x, y = random.randint(0, rows - 1), random.randint(0, cols - 1)
        maze[x][y] = 0
    return maze

# Draw the maze
def draw_maze(maze):
    for row in range(len(maze)):
        for col in range(len(maze[0])):
            color = WHITE if maze[row][col] == 1 else BLACK
            pygame.draw.rect(screen, color, (col * CELL_SIZE, row * CELL_SIZE, CELL_SIZE, CELL_SIZE))

# Main function
def main():
    rows, cols = HEIGHT // CELL_SIZE, WIDTH // CELL_SIZE
    maze = generate_maze(rows, cols)

    player_pos = [0, 0]
    target_pos = [random.randint(0, rows - 1), random.randint(0, cols - 1)]
    while maze[target_pos[0]][target_pos[1]] == 0:
        target_pos = [random.randint(0, rows - 1), random.randint(0, cols - 1)]

    score = 0
    running = True

    while running:
        screen.fill(BLACK)
        draw_maze(maze)

        # Draw player
        pygame.draw.rect(screen, GREEN, (player_pos[1] * CELL_SIZE, player_pos[0] * CELL_SIZE, CELL_SIZE, CELL_SIZE))

        # Draw target
        pygame.draw.rect(screen, RED, (target_pos[1] * CELL_SIZE, target_pos[0] * CELL_SIZE, CELL_SIZE, CELL_SIZE))

        # Display score
        font = pygame.font.Font(None, 36)
        score_text = font.render(f"Score: {score}", True, RED)
        screen.blit(score_text, (10, 10))

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        keys = pygame.key.get_pressed()
        if keys[pygame.K_UP] and player_pos[0] > 0 and maze[player_pos[0] - 1][player_pos[1]] == 1:
            player_pos[0] -= 1
        if keys[pygame.K_DOWN] and player_pos[0] < rows - 1 and maze[player_pos[0] + 1][player_pos[1]] == 1:
            player_pos[0] += 1
        if keys[pygame.K_LEFT] and player_pos[1] > 0 and maze[player_pos[0]][player_pos[1] - 1] == 1:
            player_pos[1] -= 1
        if keys[pygame.K_RIGHT] and player_pos[1] < cols - 1 and maze[player_pos[0]][player_pos[1] + 1] == 1:
            player_pos[1] += 1

        # Check if player reached the target
        if player_pos == target_pos:
            score += 1
            target_pos = [random.randint(0, rows - 1), random.randint(0, cols - 1)]
            while maze[target_pos[0]][target_pos[1]] == 0:
                target_pos = [random.randint(0, rows - 1), random.randint(0, cols - 1)]

        clock.tick(10)

    pygame.quit()

if __name__ == "__main__":
    main()
    