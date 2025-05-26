import pygame
import random
import sys

# Initialize pygame
pygame.init()

# Window settings
WIDTH, HEIGHT = 400, 600
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Flappy Bird - Elegant Edition")

# Colors and fonts
BG_COLOR = (135, 206, 235)  # Sky blue
GROUND_HEIGHT = 100
PIPE_WIDTH = 70
PIPE_GAP = 150
FPS = 60

FONT = pygame.font.SysFont("Arial", 32)
SMALL_FONT = pygame.font.SysFont("Arial", 20)

# Bird class with flapping
class Bird:
    def __init__(self):
        self.x = 100
        self.y = HEIGHT // 2
        self.gravity = 0.4
        self.lift = -8
        self.velocity = 0
        self.flap_state = 0  # Toggle for flapping

    def update(self):
        self.velocity += self.gravity
        self.y += self.velocity

        if self.y > HEIGHT - GROUND_HEIGHT - 24:
            self.y = HEIGHT - GROUND_HEIGHT - 24
            self.velocity = 0

    def flap(self):
        self.velocity = self.lift
        self.flap_state = 1  # Show flap for a few frames

    def draw(self, win):
        color = (255, 255, 0)
        # Simulate wings by toggling ellipse shape
        if self.flap_state > 0:
            pygame.draw.polygon(win, (255, 215, 0), [(self.x+17, self.y+10), (self.x+34, self.y+4), (self.x+34, self.y+16)])
            self.flap_state -= 1
        else:
            pygame.draw.polygon(win, (255, 215, 0), [(self.x+17, self.y+10), (self.x+34, self.y+7), (self.x+34, self.y+13)])

        pygame.draw.ellipse(win, color, [self.x, self.y, 34, 24])
        pygame.draw.circle(win, (0, 0, 0), (self.x + 25, self.y + 8), 3)  # Eye

# Pipe class
class Pipe:
    def __init__(self, x):
        self.x = x
        self.height = random.randint(50, HEIGHT - PIPE_GAP - GROUND_HEIGHT - 50)
        self.top = pygame.Rect(self.x, 0, PIPE_WIDTH, self.height)
        self.bottom = pygame.Rect(self.x, self.height + PIPE_GAP, PIPE_WIDTH, HEIGHT)

    def update(self):
        self.x -= 3
        self.top.x = self.bottom.x = self.x

    def draw(self, win):
        pygame.draw.rect(win, (34, 139, 34), self.top)
        pygame.draw.rect(win, (34, 139, 34), self.bottom)

    def collide(self, bird):
        bird_rect = pygame.Rect(bird.x, bird.y, 34, 24)
        return bird_rect.colliderect(self.top) or bird_rect.colliderect(self.bottom)

# Drawing clouds
def draw_background(win):
    win.fill(BG_COLOR)
    for i in range(0, WIDTH, 120):
        cloud = pygame.Surface((100, 60), pygame.SRCALPHA)
        pygame.draw.ellipse(cloud, (255, 255, 255), [0, 0, 100, 60])
        win.blit(cloud, (i + (pygame.time.get_ticks() // 15 % 120), 50 + (i % 80)))

# Start screen
def start_screen():
    waiting = True
    while waiting:
        draw_background(WIN)
        title = FONT.render("Flappy Bird", True, (255, 255, 255))
        start_btn = SMALL_FONT.render("Click or Press Space to Start", True, (255, 255, 255))

        WIN.blit(title, (WIDTH//2 - title.get_width()//2, HEIGHT//2 - 50))
        WIN.blit(start_btn, (WIDTH//2 - start_btn.get_width()//2, HEIGHT//2 + 10))
        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if (event.type == pygame.MOUSEBUTTONDOWN) or (event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE):
                waiting = False

# Main gameplay
def main():
    clock = pygame.time.Clock()
    bird = Bird()
    pipes = [Pipe(WIDTH + 100)]
    score = 0
    run = True

    while run:
        clock.tick(FPS)
        bird.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if (event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE) or \
               (event.type == pygame.MOUSEBUTTONDOWN):
                bird.flap()

        # Move pipes
        add_pipe = False
        rem = []
        for pipe in pipes:
            pipe.update()
            if pipe.collide(bird):
                return  # Game over

            if pipe.x + PIPE_WIDTH < 0:
                rem.append(pipe)

            if not hasattr(pipe, "passed") and pipe.x < bird.x:
                pipe.passed = True
                add_pipe = True

        if add_pipe:
            score += 1
            pipes.append(Pipe(WIDTH + 100))

        for r in rem:
            pipes.remove(r)

        if bird.y >= HEIGHT - GROUND_HEIGHT - 24:
            return

        # Drawing
        draw_background(WIN)
        for pipe in pipes:
            pipe.draw(WIN)
        bird.draw(WIN)

        ground = pygame.Surface((WIDTH, GROUND_HEIGHT))
        ground.fill((222, 184, 135))
        WIN.blit(ground, (0, HEIGHT - GROUND_HEIGHT))

        score_text = FONT.render(f"Score: {score}", True, (255, 255, 255))
        WIN.blit(score_text, (10, 10))
        pygame.display.update()

# Game over screen
def game_over_screen():
    WIN.fill((0, 0, 0))
    game_over = FONT.render("Game Over!", True, (255, 0, 0))
    retry = SMALL_FONT.render("Click or Press Space to Restart", True, (255, 255, 255))
    WIN.blit(game_over, (WIDTH//2 - game_over.get_width()//2, HEIGHT//2 - 30))
    WIN.blit(retry, (WIDTH//2 - retry.get_width()//2, HEIGHT//2 + 10))
    pygame.display.update()

    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if (event.type == pygame.MOUSEBUTTONDOWN) or (event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE):
                waiting = False

# Game loop
if __name__ == "__main__":
    while True:
        start_screen()
        main()
        game_over_screen()
