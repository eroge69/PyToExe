import pygame
import time
import random

# Initialize pygame
pygame.init()

# Screen settings
width, height = 600, 400
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Snake Game")

# Colors
black = (0, 0, 0)
white = (255, 255, 255)
green = (0, 255, 0)
red = (213, 50, 80)

# Snake settings
snake_block = 10
snake_speed = 15

# Fonts
font = pygame.font.SysFont("bahnschrift", 25)

# Function to display score
def show_score(score):
    value = font.render("Score: {score}", True, white)
    screen.blit(value, [10, 10])

# Game loop
def game_loop():
    game_over = False
    game_close = False

    x, y = width // 2, height // 2
    dx, dy = 0, 0
    
    snake_list = []
    length_of_snake = 1
    
    food_x = random.randrange(0, width - snake_block, 10)
    food_y = random.randrange(0, height - snake_block, 10)

    clock = pygame.time.Clock()
    
    while not game_over:
        while game_close:
            screen.fill(black)
            message = font.render("Game Over! Press C-Continue or Q-Quit", True, red)
            screen.blit(message, [width // 6, height // 3])
            show_score(length_of_snake - 1)
            pygame.display.update()

            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_q:
                        game_over = True
                        game_close = False
                    if event.key == pygame.K_c:
                        game_loop()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game_over = True
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT and dx == 0:
                    dx, dy = -snake_block, 0
                elif event.key == pygame.K_RIGHT and dx == 0:
                    dx, dy = snake_block, 0
                elif event.key == pygame.K_UP and dy == 0:
                    dx, dy = 0, -snake_block
                elif event.key == pygame.K_DOWN and dy == 0:
                    dx, dy = 0, snake_block
        
        x += dx
        y += dy
        
        if x >= width or x < 0 or y >= height or y < 0:
            game_close = True
        
        screen.fill(black)
        pygame.draw.rect(screen, green, [food_x, food_y, snake_block, snake_block])
        
        snake_head = []
        snake_head.append(x)
        snake_head.append(y)
        snake_list.append(snake_head)
        if len(snake_list) > length_of_snake:
            del snake_list[0]
        
        for segment in snake_list[:-1]:
            if segment == snake_head:
                game_close = True
        
        for part in snake_list:
            pygame.draw.rect(screen, white, [part[0], part[1], snake_block, snake_block])
        
        show_score(length_of_snake - 1)
        pygame.display.update()
        
        if x == food_x and y == food_y:
            food_x = random.randrange(0, width - snake_block, 10)
            food_y = random.randrange(0, height - snake_block, 10)
            length_of_snake += 1
        
        clock.tick(snake_speed)
    
    pygame.quit()
    quit()

game_loop()