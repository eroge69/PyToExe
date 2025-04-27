import pygame
import sys
import random
import math

# Initialize Pygame
pygame.init()

# Settings
WIDTH, HEIGHT = 800, 600
DISPLAYSURF = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("حرکت بين موانع")

# Colors
WHITE = (255, 255, 255)
RED = (255, 0, 0)

# IMAGE Paths
image1 = 'C:/Users/USER/Documents/game-iauctb/image/background1.jpg'
bird_image_path = 'C:/Users/USER/Documents/game-iauctb/image/red-bird.png'
obstacle_image_path = 'C:/Users/USER/Documents/game-iauctb/image/pig_failed.png'

# Load images
background_image = pygame.image.load(image1)
background_image = pygame.transform.scale(background_image, (WIDTH, HEIGHT))
bird_image = pygame.image.load(bird_image_path)
obstacle_image = pygame.image.load(obstacle_image_path)
obstacle_image = pygame.transform.scale(obstacle_image, (100, 100))

# Load background music
#pygame.mixer.music.load('C:/Users/USER/Documents/game-iauctb/sounds/angry-birds.ogg')
# Path to your music file
#pygame.mixer.music.play(-1)  # Loop the music indefinitely

# Player class
class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.velocity = 5
        self.score = 0
        self.level = 1

    def draw(self, win):
        win.blit(bird_image, (self.x - bird_image.get_width() // 2, self.y - bird_image.get_height() // 2))

# Obstacle class
class Obstacle:
    def __init__(self, x, y, velocity):
        self.x = x
        self.y = y
        self.velocity = velocity

    def draw(self, win):
        win.blit(obstacle_image, (self.x - obstacle_image.get_width() // 2, self.y - obstacle_image.get_height() // 2))

    def move(self, speed_change):
        self.x -= self.velocity + speed_change

def create_obstacles(level):
    obstacles = []
    for _ in range(5 + level):  # Increase number of obstacles with level
        obstacle_x = random.randint(WIDTH, 2 * WIDTH)
        obstacle_y = random.randint(30, HEIGHT - 30)
        obstacle_velocity = random.randint(1, 5)
        obstacles.append(Obstacle(obstacle_x, obstacle_y, obstacle_velocity))
    return obstacles

def show_instructions():
    font = pygame.font.Font(None, 36)
    instructions = [
        "Instructions:",
        "Use arrow keys to move the bird.",
        "Avoid the obstacles.",
        "Press any mouse button to go back to the menu."
    ]
    
    while True:
        DISPLAYSURF.fill(WHITE)
        for i, line in enumerate(instructions):
            text = font.render(line, True, RED)
            DISPLAYSURF.blit(text, (50, 50 + i * 40))
        
        pygame.display.update()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                return

def main_menu():
    font = pygame.font.Font(None, 74)
    title_text = font.render("Main Menu", True, RED)
    options = ["Start Game", "Instructions", "Quit"]
    option_rects = []

    while True:
        DISPLAYSURF.fill(WHITE)
        DISPLAYSURF.blit(title_text, (WIDTH // 2 - title_text.get_width() // 2, 50))
        
        for i, option in enumerate(options):
            option_text = font.render(option, True, RED)
            rect = option_text.get_rect(center=(WIDTH // 2, 150 + i * 60))
            option_rects.append(rect)
            DISPLAYSURF.blit(option_text, rect)
        
        pygame.display.update()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                for i, rect in enumerate(option_rects):
                    if rect.collidepoint(mouse_pos):
                        if i == 0:  # Start Game
                            return "start"
                        elif i == 1:  # Instructions
                            show_instructions()
                        elif i == 2:  # Quit
                            pygame.quit()
                            sys.exit()

def run_game():
    player = Player(250, 250)
    level = 1
    obstacles = create_obstacles(level)
    clock = pygame.time.Clock()
    speed_change = 0
    running = True

    while running:
        clock.tick(60)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            player.x -= player.velocity
        if keys[pygame.K_RIGHT]:
            player.x += player.velocity
        if keys[pygame.K_UP]:
            player.y -= player.velocity
        if keys[pygame.K_DOWN]:
            player.y += player.velocity

        # Move obstacles
        for obstacle in obstacles:
            obstacle.move(speed_change)
            if obstacle.x < -15:
                obstacle.x = WIDTH + random.randint(50, 200)
                obstacle.y = random.randint(30, HEIGHT - 30)
                obstacle.velocity = random.randint(1, 5)
                player.score += 1  # Increment score for avoiding an obstacle

        # Check collision with obstacles
        for obstacle in obstacles:
            distance = math.sqrt((player.x - obstacle.x) ** 2 + (player.y - obstacle.y) ** 2)
            if distance < 25 + 15:  # Collision with obstacles
                show_game_over(player.score)
                return

        # Check for level up
        if player.score >= level * 6:  # Level up condition
            level += 1
            obstacles = create_obstacles(level)  # Create more obstacles for next level

        # Draw everything on the screen
        DISPLAYSURF.fill(WHITE)
        DISPLAYSURF.blit(background_image, (0, 0))
        for obstacle in obstacles:
            obstacle.draw(DISPLAYSURF)
        player.draw(DISPLAYSURF)

        # Draw score and level
        font = pygame.font.Font(None, 36)
        score_text = font.render(f"Score: {player.score}  Level: {level}", True, RED)
        DISPLAYSURF.blit(score_text, (10, 10))

        pygame.display.update()

def show_game_over(score):
    font = pygame.font.Font(None, 74)
    game_over_text = font.render("Game Over", True, RED)
    score_text = font.render(f"Score: {score}", True, RED)
    DISPLAYSURF.fill(WHITE)
    DISPLAYSURF.blit(game_over_text, (WIDTH // 2 - game_over_text.get_width() // 2, HEIGHT // 2 - 40))
    DISPLAYSURF.blit(score_text, (WIDTH // 2 - score_text.get_width() // 2, HEIGHT // 2 + 20))
    pygame.display.update()
    pygame.time.delay(3000)  # Display for 3 seconds

# Main loop
if __name__ == "__main__":
    while True:
        menu_choice = main_menu()
        if menu_choice == "start":
            run_game()