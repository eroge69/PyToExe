import pygame
import sys
import random
import time
import math

pygame.init()

WIDTH, HEIGHT = 800, 600
WINDOW = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Realistic Pong")

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

PADDLE_WIDTH, PADDLE_HEIGHT = 10, 100
BALL_RADIUS = 10
PADDLE_SPEED = 7
BALL_SPEED_X, BALL_SPEED_Y = 5, 5
AI_SPEED = 6

left_paddle = pygame.Rect(50, HEIGHT // 2 - PADDLE_HEIGHT // 2, PADDLE_WIDTH, PADDLE_HEIGHT)
right_paddle = pygame.Rect(WIDTH - 50 - PADDLE_WIDTH, HEIGHT // 2 - PADDLE_HEIGHT // 2, PADDLE_WIDTH, PADDLE_HEIGHT)
ball = pygame.Rect(WIDTH // 2, HEIGHT // 2, BALL_RADIUS * 2, BALL_RADIUS * 2)
ball_vel_x, ball_vel_y = BALL_SPEED_X, BALL_SPEED_Y

score_font = pygame.font.SysFont("Arial", 36)
home_font = pygame.font.SysFont("Arial", 48)
pause_font = pygame.font.SysFont("Arial", 24)
left_score = 0
right_score = 0

try:
    bounce_sound = pygame.mixer.Sound("bounce.wav")
    score_sound = pygame.mixer.Sound("score.wav")
    hover_sound = pygame.mixer.Sound("hover.wav")
    select_sound = pygame.mixer.Sound("select.wav")
except pygame.error:
    bounce_sound = None
    score_sound = None
    hover_sound = None
    select_sound = None

try:
    pygame.mixer.music.load("background_music.mp3")
    pygame.mixer.music.play(-1, 0.0)
except pygame.error:
    pass
music_muted = False

try:
    win_sound = pygame.mixer.Sound("win.wav")
except pygame.error:
    win_sound = None

try:
    lose_sound = pygame.mixer.Sound("lose.wav")
except pygame.error:
    lose_sound = None

clock = pygame.time.Clock()
paused = False
win_screen = False
winner = None
hit_counter = 0
right_line_offset = 56
home_screen = True
instructions_screen = False
difficulty_screen = False
settings_screen = False  # Settings screen flag
ball_trail = []
invert_colors = False  # Color inversion flag
last_hovered_button = None

class Particle:
    def __init__(self, x, y, color):
        self.x = x + random.randint(-5, 5)
        self.y = y + random.randint(-5, 5)
        self.radius = random.randint(2, 4)
        self.lifetime = 30
        self.color = color

    def update(self):
        self.lifetime -= 1
        self.radius = max(0, self.radius - 0.1)
        self.y += random.uniform(-1, 1)
        self.x += random.uniform(-1, 1)

    def draw(self, surface, fg_color):
        if self.lifetime > 0:
            alpha = int(255 * (self.lifetime / 30))
            particle_surface = pygame.Surface((self.radius*2, self.radius*2), pygame.SRCALPHA)
            pygame.draw.circle(particle_surface, (*fg_color, alpha), (self.radius, self.radius), int(self.radius))
            surface.blit(particle_surface, (self.x - self.radius, self.y - self.radius))

particles = []
running = True
while running:
    clock.tick(60)
    
    # Set colors based on inversion setting
    bg_color = WHITE if invert_colors else BLACK
    fg_color = BLACK if invert_colors else WHITE

    mouse_pos = pygame.mouse.get_pos()
    hovered_button = None

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if home_screen:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if WIDTH // 2 - 100 <= mouse_pos[0] <= WIDTH // 2 + 100:
                    if HEIGHT // 2 - 40 <= mouse_pos[1] <= HEIGHT // 2 + 40:
                        if select_sound: select_sound.play()
                        home_screen = False
                        difficulty_screen = True
                    elif HEIGHT // 2 + 60 <= mouse_pos[1] <= HEIGHT // 2 + 100:
                        if select_sound: select_sound.play()
                        home_screen = False
                        instructions_screen = True
                    elif HEIGHT // 2 + 110 <= mouse_pos[1] <= HEIGHT // 2 + 150:  # Settings button
                        if select_sound: select_sound.play()
                        home_screen = False
                        settings_screen = True
                    elif HEIGHT // 2 + 160 <= mouse_pos[1] <= HEIGHT // 2 + 200:
                        if select_sound: select_sound.play()
                        running = False

        elif instructions_screen:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if (WIDTH // 2 - 100 <= mouse_pos[0] <= WIDTH // 2 + 100) and (HEIGHT // 2 + 100 <= mouse_pos[1] <= HEIGHT // 2 + 140):
                    if select_sound: select_sound.play()
                    instructions_screen = False
                    home_screen = True

        elif settings_screen:  # Settings screen logic
            if event.type == pygame.MOUSEBUTTONDOWN:
                if (WIDTH // 2 - 100 <= mouse_pos[0] <= WIDTH // 2 + 100) and (HEIGHT - 100 <= mouse_pos[1] <= HEIGHT - 60):
                    if select_sound: select_sound.play()
                    settings_screen = False
                    home_screen = True
                # Music toggle
                if (WIDTH // 2 - 150 <= mouse_pos[0] <= WIDTH // 2 + 150) and (HEIGHT // 2 - 50 <= mouse_pos[1] <= HEIGHT // 2):
                    if select_sound: select_sound.play()
                    music_muted = not music_muted
                    if music_muted:
                        pygame.mixer.music.pause()
                    else:
                        pygame.mixer.music.unpause()
                # Color inversion toggle    
                if (WIDTH // 2 - 150 <= mouse_pos[0] <= WIDTH // 2 + 150) and (HEIGHT // 2 + 30 <= mouse_pos[1] <= HEIGHT // 2 + 80):
                    if select_sound: select_sound.play()
                    invert_colors = not invert_colors

        elif difficulty_screen:
            if event.type == pygame.MOUSEBUTTONDOWN:
                for i in range(3):
                    rect_y = HEIGHT // 2 + i * 60
                    button_rect = pygame.Rect(WIDTH // 2 - 100, rect_y, 200, 50)
                    if button_rect.collidepoint(mouse_pos):
                        if select_sound: select_sound.play()
                        AI_SPEED = [2, 4, 10][i]
                        difficulty_screen = False

        elif event.type == pygame.MOUSEBUTTONDOWN:
            if (WIDTH - 80 <= mouse_pos[0] <= WIDTH - 40) and (20 <= mouse_pos[1] <= 60):
                paused = not paused
                if select_sound: select_sound.play()
            if (WIDTH - 150 <= mouse_pos[0] <= WIDTH - 110) and (20 <= mouse_pos[1] <= 60):
                music_muted = not music_muted
                if music_muted:
                    pygame.mixer.music.pause()
                else:
                    pygame.mixer.music.unpause()
                if select_sound: select_sound.play()

    if home_screen:
        WINDOW.fill(bg_color)
        time_now = time.time()
        bob_offset = int(10 * math.sin(time_now * 2))
        title_text = home_font.render("Realistic Pong", True, fg_color)
        WINDOW.blit(title_text, (WIDTH // 2 - title_text.get_width() // 2, HEIGHT // 6 + bob_offset))
        
        # Menu with Settings button
        labels = ["Start Game", "Instructions", "Settings", "Quit"]
        positions = [HEIGHT // 2 - 40, HEIGHT // 2 + 60, HEIGHT // 2 + 110, HEIGHT // 2 + 160]
        
        for i, (label, pos_y) in enumerate(zip(labels, positions)):
            rect = pygame.Rect(WIDTH // 2 - 100, pos_y, 200, 40)
            if rect.collidepoint(mouse_pos):
                hovered_button = label
            color = (150, 150, 150) if hovered_button == label else fg_color
            pygame.draw.rect(WINDOW, color, rect, 5, border_radius=10)

            text = score_font.render(label, True, fg_color)
            text_y = pos_y + (40 - text.get_height()) // 2  # Vertically center text in button
            WINDOW.blit(text, (WIDTH // 2 - text.get_width() // 2, text_y))

            
        pygame.display.flip()
        if hovered_button != last_hovered_button and hovered_button and hover_sound:
            hover_sound.play()
            last_hovered_button = hovered_button
        continue
    
    if settings_screen:  # Settings screen
        WINDOW.fill(bg_color)
        title = home_font.render("Settings", True, fg_color)
        WINDOW.blit(title, (WIDTH // 2 - title.get_width() // 2, HEIGHT // 4))
        
        # Music toggle
        music_status = "Music: " + ("OFF" if music_muted else "ON")
        music_text = score_font.render(music_status, True, fg_color)
        music_rect = pygame.Rect(WIDTH // 2 - 150, HEIGHT // 2 - 50, 300, 50)
        if music_rect.collidepoint(mouse_pos):
            hovered_button = "MusicToggle"
        color = (150, 150, 150) if hovered_button == "MusicToggle" else fg_color
        pygame.draw.rect(WINDOW, color, music_rect, 5, border_radius=10)
        music_text_y = HEIGHT // 2 - 50 + (50 - music_text.get_height()) // 2
        WINDOW.blit(music_text, (WIDTH // 2 - music_text.get_width() // 2, music_text_y))

        
        # Color inversion toggle
        invert_status = "Invert Colors: " + ("ON" if invert_colors else "OFF")
        invert_text = score_font.render(invert_status, True, fg_color)
        invert_rect = pygame.Rect(WIDTH // 2 - 150, HEIGHT // 2 + 30, 300, 50)
        if invert_rect.collidepoint(mouse_pos):
            hovered_button = "InvertToggle"
        color = (150, 150, 150) if hovered_button == "InvertToggle" else fg_color
        pygame.draw.rect(WINDOW, color, invert_rect, 5, border_radius=10)
        invert_text_y = HEIGHT // 2 + 30 + (50 - invert_text.get_height()) // 2
        WINDOW.blit(invert_text, (WIDTH // 2 - invert_text.get_width() // 2, invert_text_y))

        
        # Back button
        back_rect = pygame.Rect(WIDTH // 2 - 100, HEIGHT - 100, 200, 40)
        if back_rect.collidepoint(mouse_pos):
            hovered_button = "BackSettings"
        color = (150, 150, 150) if hovered_button == "BackSettings" else fg_color
        pygame.draw.rect(WINDOW, color, back_rect, 5, border_radius=10)
        back_text = score_font.render("Back", True, fg_color)
        back_text_y = HEIGHT - 100 + (40 - back_text.get_height()) // 2
        WINDOW.blit(back_text, (WIDTH // 2 - back_text.get_width() // 2, back_text_y))

        
        pygame.display.flip()
        if hovered_button != last_hovered_button and hovered_button and hover_sound:
            hover_sound.play()
            last_hovered_button = hovered_button
        continue

    if difficulty_screen:
        WINDOW.fill(bg_color)
        title = home_font.render("Select Difficulty", True, fg_color)
        WINDOW.blit(title, (WIDTH // 2 - title.get_width() // 2, HEIGHT // 4))
        button_labels = ["Easy", "Medium", "Hard"]
        for i, label in enumerate(button_labels):
            rect_y = HEIGHT // 2 + i * 60
            button_rect = pygame.Rect(WIDTH // 2 - 100, rect_y, 200, 50)
            if button_rect.collidepoint(mouse_pos):
                hovered_button = label
            color = (150, 150, 150) if hovered_button == label else fg_color
            pygame.draw.rect(WINDOW, color, button_rect, 5, border_radius=10)

            text = score_font.render(label, True, fg_color)
            text_rect = text.get_rect(center=button_rect.center)
            WINDOW.blit(text, text_rect)
            if button_rect.collidepoint(mouse_pos):
                hovered_button = label
        pygame.display.flip()
        if hovered_button != last_hovered_button and hovered_button and hover_sound:
            hover_sound.play()
            last_hovered_button = hovered_button
        continue
    
    if win_screen:
        WINDOW.fill(bg_color)
        win_text = home_font.render(f"{winner} Wins!", True, fg_color)
        WINDOW.blit(win_text, (WIDTH // 2 - win_text.get_width() // 2, HEIGHT // 3))

        # Define button rectangles
        home_button = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2, 200, 60)
        quit_button = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2 + 100, 200, 60)
        
        # Draw buttons
        home_color = (150, 150, 150) if home_button.collidepoint(mouse_pos) else fg_color
        quit_color = (150, 150, 150) if quit_button.collidepoint(mouse_pos) else fg_color
        
        pygame.draw.rect(WINDOW, home_color, home_button, 5, border_radius=10)
        pygame.draw.rect(WINDOW, quit_color, quit_button, 5, border_radius=10)
        
        # Button text
        home_text = score_font.render("Home", True, fg_color)
        quit_text = score_font.render("Quit", True, fg_color)
        
        WINDOW.blit(home_text, (home_button.centerx - home_text.get_width() // 2, 
                               home_button.centery - home_text.get_height() // 2))
        WINDOW.blit(quit_text, (quit_button.centerx - quit_text.get_width() // 2, 
                               quit_button.centery - quit_text.get_height() // 2))
        
        # Handle button hovers for sound effects
        if home_button.collidepoint(mouse_pos):
            hovered_button = "Home"
        elif quit_button.collidepoint(mouse_pos):
            hovered_button = "Quit"
        else:
            hovered_button = None
            
        # Handle click events
        if event.type == pygame.MOUSEBUTTONDOWN:
            if home_button.collidepoint(mouse_pos):
                if select_sound: select_sound.play()
                win_screen = False
                home_screen = True
                left_score = 0
                right_score = 0
                ball.center = (WIDTH // 2, HEIGHT // 2)
                ball_vel_x = BALL_SPEED_X
                ball_vel_y = BALL_SPEED_Y * random.choice([1, -1])
            elif quit_button.collidepoint(mouse_pos):
                if select_sound: select_sound.play()
                running = False

        pygame.display.flip()
        if hovered_button != last_hovered_button and hovered_button and hover_sound:
            hover_sound.play()
            last_hovered_button = hovered_button
        continue


    if instructions_screen:
        WINDOW.fill(bg_color)
        instructions = [
            "How to Play:",
            "Use W/S or ↑/↓ for left paddle.",
            "Right paddle moves automatically.",
            "The ball speeds up every 5 hits.",
            "Reach 10 Score to win.",
            "Click to go back to home screen."
        ]
        for i, line in enumerate(instructions):
            text = pause_font.render(line, True, fg_color)
            WINDOW.blit(text, (WIDTH // 2 - text.get_width() // 2, HEIGHT // 3 + i * 40 - 40))
        rect = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2 + 100, 200, 80)
        if rect.collidepoint(mouse_pos):
            hovered_button = "Exit"
        color = (150, 150, 150) if hovered_button == "Exit" else fg_color
        pygame.draw.rect(WINDOW, color, rect, 5, border_radius=10)
        exit_text = score_font.render("Exit", True, fg_color)
        WINDOW.blit(exit_text, (WIDTH // 2 - exit_text.get_width() // 2, HEIGHT // 2 + 120))
        if rect.collidepoint(mouse_pos):
            hovered_button = "Exit"
        pygame.display.flip()
        if hovered_button != last_hovered_button and hovered_button and hover_sound:
            hover_sound.play()
            last_hovered_button = hovered_button
        continue

    if paused:
        WINDOW.fill(bg_color)
        pygame.draw.rect(WINDOW, fg_color, pygame.Rect(WIDTH - 80, 20, 40, 40), 5, border_radius=5)
        pygame.draw.line(WINDOW, fg_color, (WIDTH - 65, 30), (WIDTH - 65, 50), 5)
        pygame.draw.line(WINDOW, fg_color, (WIDTH - right_line_offset, 30), (WIDTH - right_line_offset, 50), 5)
        pygame.draw.rect(WINDOW, fg_color, pygame.Rect(WIDTH - 150, 20, 50, 40), 5, border_radius=5)
        mute_text = pause_font.render("Mute" if not music_muted else "Unmute", True, fg_color)
        WINDOW.blit(mute_text, (WIDTH - 145, 30))
        home_button_rect = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2 + 50, 200, 60)
        if home_button_rect.collidepoint(mouse_pos):
            hovered_button = "HomePause"
        color = (150, 150, 150) if hovered_button == "HomePause" else fg_color
        pygame.draw.rect(WINDOW, color, home_button_rect, 5, border_radius=10)
        home_text = score_font.render("Home", True, fg_color)
        WINDOW.blit(home_text, (home_button_rect.centerx - home_text.get_width() // 2, home_button_rect.centery - home_text.get_height() // 2))
        credits_text = pause_font.render("Credits: Shawn (ME) hi josh", True, fg_color)
        WINDOW.blit(credits_text, (WIDTH // 3, HEIGHT // 3))
        if home_button_rect.collidepoint(mouse_pos):
            hovered_button = "HomePause"
            if pygame.mouse.get_pressed()[0]:
                if select_sound: select_sound.play()
                paused = False
                home_screen = True
                left_score = 0
                right_score = 0
                hit_counter = 0
                ball.center = (WIDTH // 2, HEIGHT // 2)
                ball_vel_x = BALL_SPEED_X
                ball_vel_y = BALL_SPEED_Y * random.choice([1, -1])
        pygame.display.flip()
        if hovered_button != last_hovered_button and hovered_button and hover_sound:
            hover_sound.play()
            last_hovered_button = hovered_button
        continue

    keys = pygame.key.get_pressed()
    if (keys[pygame.K_w] or keys[pygame.K_UP]) and left_paddle.top > 0:
        left_paddle.y -= PADDLE_SPEED
    if (keys[pygame.K_s] or keys[pygame.K_DOWN]) and left_paddle.bottom < HEIGHT:
        left_paddle.y += PADDLE_SPEED


    # Smooth AI paddle movement
    target_y = ball.centery - right_paddle.height // 2
    dy = target_y - right_paddle.y
    right_paddle.y += dy * (AI_SPEED / 60)  # AI_SPEED controls responsiveness now


    # Clamp within screen bounds
    if right_paddle.top < 0:
        right_paddle.top = 0
    if right_paddle.bottom > HEIGHT:
        right_paddle.bottom = HEIGHT


    ball.x += ball_vel_x
    ball.y += ball_vel_y

    ball_trail.append((ball.centerx, ball.centery))
    if len(ball_trail) > 10:  # Limit length
        ball_trail.pop(0)

    if ball.top <= 0 or ball.bottom >= HEIGHT:
        ball_vel_y *= -1
        particles.extend(Particle(ball.centerx, ball.centery, fg_color) for _ in range(15))
        if bounce_sound: bounce_sound.play()

    if ball.colliderect(left_paddle):
        ball_vel_x = abs(ball_vel_x)  # ensure ball goes right
        offset = (ball.centery - left_paddle.centery) / (PADDLE_HEIGHT / 2)
        ball_vel_y += offset * 2
        hit_counter += 1
        particles.extend(Particle(ball.centerx, ball.centery, fg_color) for _ in range(15))
        if bounce_sound: bounce_sound.play()

    elif ball.colliderect(right_paddle):
        ball_vel_x = -abs(ball_vel_x)  # ensure ball goes left
        offset = (ball.centery - right_paddle.centery) / (PADDLE_HEIGHT / 2)
        ball_vel_y += offset * 2
        hit_counter += 1
        particles.extend(Particle(ball.centerx, ball.centery, fg_color) for _ in range(15))
        if bounce_sound: bounce_sound.play()
        if hit_counter >= 5:
            ball_vel_x *= 1.1
            ball_vel_y *= 1.1
            hit_counter = 0

    if ball.left <= 0:
        right_score += 1
        if right_score >= 10:
            win_screen = True
            winner = "Right Player"
            if lose_sound: lose_sound.play()
        else:
            ball.center = (WIDTH // 2, HEIGHT // 2)
            ball_vel_x = BALL_SPEED_X
            ball_vel_y = BALL_SPEED_Y * random.choice([1, -1])
        if score_sound: score_sound.play()

    elif ball.right >= WIDTH:
        left_score += 1
        if left_score >= 10:
            win_screen = True
            winner = "Left Player"
            if win_sound: win_sound.play()
        else:
            ball.center = (WIDTH // 2, HEIGHT // 2)
            ball_vel_x = -BALL_SPEED_X
            ball_vel_y = BALL_SPEED_Y * random.choice([1, -1])
        if score_sound: score_sound.play()


    WINDOW.fill(bg_color)
    pygame.draw.rect(WINDOW, fg_color, left_paddle)
    pygame.draw.rect(WINDOW, fg_color, right_paddle)

    # Draw ball trail before drawing the ball
    for i, (x, y) in enumerate(ball_trail):
        trail_alpha = int(255 * (i / len(ball_trail)))
        trail_surface = pygame.Surface((BALL_RADIUS * 2, BALL_RADIUS * 2), pygame.SRCALPHA)
        pygame.draw.circle(trail_surface, (*fg_color, trail_alpha), (BALL_RADIUS, BALL_RADIUS), BALL_RADIUS)
        WINDOW.blit(trail_surface, (x - BALL_RADIUS, y - BALL_RADIUS))
    
    # Draw the ball itself
    pygame.draw.ellipse(WINDOW, fg_color, ball)

    pygame.draw.aaline(WINDOW, fg_color, (WIDTH // 2, 0), (WIDTH // 2, HEIGHT))
    left_text = score_font.render(str(left_score), True, fg_color)
    right_text = score_font.render(str(right_score), True, fg_color)
    WINDOW.blit(left_text, (WIDTH // 4, 20))
    WINDOW.blit(right_text, (WIDTH * 3 // 4, 20))
    pygame.draw.rect(WINDOW, fg_color, pygame.Rect(WIDTH - 80, 20, 40, 40), 5, border_radius=5)
    pygame.draw.line(WINDOW, fg_color, (WIDTH - 65, 30), (WIDTH - 65, 50), 5)
    pygame.draw.line(WINDOW, fg_color, (WIDTH - right_line_offset, 30), (WIDTH - right_line_offset, 50), 5)


    # Update and draw particles
    for particle in particles[:]:
        particle.update()
        if particle.lifetime <= 0:
            particles.remove(particle)
        else:
            particle.draw(WINDOW, fg_color)

    pygame.display.flip()

pygame.quit()
sys.exit()
