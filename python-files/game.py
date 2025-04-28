import pygame
import sys
import math

# Initialize Pygame
pygame.init()

# Screen setup (first define width/height!)
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Bouncing Ball Game")

# Load and scale background
background_image = pygame.image.load("Batman.jpg")
background_image = pygame.transform.scale(background_image, (WIDTH, HEIGHT))

# Fonts and Clock
font = pygame.font.SysFont(None, 36)
big_font = pygame.font.SysFont(None, 60)
clock = pygame.time.Clock()

# Colors for neon effect (bright, vivid colors)
NEON_GREEN = (57, 255, 20)
NEON_BLUE = (0, 255, 255)
NEON_PINK = (255, 20, 147)
WHITE = (255, 255, 255)
GRAY = (128, 128, 128)  # Define GRAY color

# Game variables
ball_radius = 10  # Smaller ball radius
ball_speed_x = 4
ball_speed_y = 4
paddle_width = 100
paddle_height = 10
paddle_speed = 7

# State
score = 0
running = True
in_menu = True
paused = False  # New variable to track pause state

# Button rects
new_game_btn = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2 - 60, 200, 50)
exit_btn = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2 + 10, 200, 50)

# Reset game function
def reset_game():
    global ball_x, ball_y, ball_speed_x, ball_speed_y
    global paddle_x, paddle_y, score
    ball_x = WIDTH // 2
    ball_y = HEIGHT // 2
    ball_speed_x = 4
    ball_speed_y = 4
    paddle_x = (WIDTH - paddle_width) // 2
    paddle_y = HEIGHT - 40
    score = 0

reset_game()

# Function to draw a neon glowing ball
def draw_glowing_ball(color, ball_x, ball_y, ball_radius):
    # Draw the "glow" behind the ball
    glow_radius = ball_radius + 10
    pygame.draw.circle(screen, color, (ball_x, ball_y), glow_radius)
    
    # Draw the actual ball on top
    pygame.draw.circle(screen, color, (ball_x, ball_y), ball_radius)

# Function to draw a neon glowing paddle
def draw_glowing_paddle(color, paddle_x, paddle_y, paddle_width, paddle_height):
    # Draw the "glow" behind the paddle
    glow_width = paddle_width + 10
    glow_height = paddle_height + 10
    pygame.draw.rect(screen, color, (paddle_x - 5, paddle_y - 5, glow_width, glow_height))
    
    # Draw the actual paddle on top
    pygame.draw.rect(screen, color, (paddle_x, paddle_y, paddle_width, paddle_height))

# Game loop
while running:
    screen.blit(background_image, (0, 0))
    mouse_pos = pygame.mouse.get_pos()
    click = False

    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            click = True

        if event.type == pygame.KEYDOWN:
            # Ctrl + R to restart
            if event.key == pygame.K_r and (pygame.key.get_mods() & pygame.KMOD_CTRL):
                reset_game()
            # Ctrl + P to pause/unpause
            if event.key == pygame.K_p and (pygame.key.get_mods() & pygame.KMOD_CTRL):
                paused = not paused  # Toggle paused state

    if in_menu:
        # Menu screen
        title = big_font.render("Bouncing Ball Game", True, WHITE)
        screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 100))

        # Draw buttons
        pygame.draw.rect(screen, NEON_GREEN, new_game_btn)
        pygame.draw.rect(screen, NEON_GREEN, exit_btn)

        new_text = font.render("New Game", True, WHITE)
        exit_text = font.render("Exit", True, WHITE)
        screen.blit(new_text, (new_game_btn.x + 40, new_game_btn.y + 10))
        screen.blit(exit_text, (exit_btn.x + 70, exit_btn.y + 10))

        # Click handling
        if new_game_btn.collidepoint(mouse_pos) and click:
            in_menu = False
            reset_game()
        if exit_btn.collidepoint(mouse_pos) and click:
            running = False

    else:
        if paused:
            # If the game is paused, display a paused message
            paused_text = big_font.render("PAUSED", True, WHITE)
            screen.blit(paused_text, (WIDTH // 2 - paused_text.get_width() // 2, HEIGHT // 2 - 30))
        else:
            # Paddle controls
            keys = pygame.key.get_pressed()
            if keys[pygame.K_LEFT] and paddle_x > 0:
                paddle_x -= paddle_speed
            if keys[pygame.K_RIGHT] and paddle_x < WIDTH - paddle_width:
                paddle_x += paddle_speed

            # Ball movement
            ball_x += ball_speed_x
            ball_y += ball_speed_y

            # Wall collision
            if ball_x - ball_radius <= 0 or ball_x + ball_radius >= WIDTH:
                ball_speed_x *= -1
            if ball_y - ball_radius <= 0:
                ball_speed_y *= -1

            # Paddle collision
            if (
                paddle_y <= ball_y + ball_radius <= paddle_y + paddle_height and
                paddle_x <= ball_x <= paddle_x + paddle_width
            ):
                ball_speed_y *= -1
                score += 1

                # Add spin effect based on where the ball hits the paddle
                hit_pos = (ball_x - paddle_x) / paddle_width  # value between 0 and 1
                ball_speed_x = (hit_pos - 0.5) * 10  # Adjust 10 for stronger/weaker spin

            # Ball missed — reset game
            if ball_y > HEIGHT:
                reset_game()

            # Color-changing ball (use a sine wave for smooth color transitions)
            time_passed = pygame.time.get_ticks() / 1000  # Time in seconds
            red = int(127 + 127 * math.sin(time_passed))  # Use sine for smooth transition
            green = int(127 + 127 * math.sin(time_passed + 2))  # Phase shift for variety
            blue = int(127 + 127 * math.sin(time_passed + 4))  # Another phase shift

            neon_color = (red, green, blue)  # Dynamic color based on time

            # Draw glowing ball and paddle with neon color
            draw_glowing_ball(neon_color, ball_x, ball_y, ball_radius)
            draw_glowing_paddle(NEON_BLUE, paddle_x, paddle_y, paddle_width, paddle_height)
            score_text = font.render(f"Score: {score}", True, WHITE)
            screen.blit(score_text, (10, 10))

            # Restart hint
            hint = font.render("Press Ctrl+R to Restart", True, GRAY)
            screen.blit(hint, (WIDTH - 290, HEIGHT - 40))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()
