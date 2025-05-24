import pygame
import random

WIDTH = 400
HEIGHT = 500
WHITE = (255,255,255)
BLACK = (0,0,0)
RED = (255,0,0)
GREEN = (0,255,0)
BLUE = (0,0,255)
PINK = (255, 0, 255)
FPS = 7

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Snake party")
font = pygame.font.SysFont("Calibri", 16)
clock = pygame.time.Clock()


cell_size = 20 #размер одной клетки змейки
snake_speed = 5 #скорость змейки
snake_length = 3 #изначальный размер змейки
snake_length2 = 3
snake_body = [] #массив клеток змейки
snake_body2 = []
snake_direction = "right"
new_direction = "right"
snake_direction2 = "left"
new_direction2 = "left"
game_over_snake = 0

apple_rnd_x = random.randint(0,WIDTH - cell_size)
apple_rnd_y = random.randint(0,HEIGHT - cell_size)
apple_position = pygame.Rect(apple_rnd_x,apple_rnd_y,cell_size,cell_size)

for i in range (snake_length):
    snake_body.append(pygame.Rect((WIDTH//2) - (cell_size*i), HEIGHT//2, cell_size, cell_size))
for i in range (snake_length2):
    snake_body2.append(pygame.Rect((WIDTH//2) - (cell_size*i), HEIGHT//2, cell_size, cell_size))
    
running = True
while running:
    clock.tick(FPS)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    keys = pygame.key.get_pressed()
    if keys[pygame.K_RIGHT] and snake_direction != "left":
        new_direction = "right"
    elif keys[pygame.K_LEFT] and snake_direction != "right":
        new_direction = "left"
    elif keys[pygame.K_UP] and snake_direction != "down":
        new_direction = "up"
    elif keys[pygame.K_DOWN] and snake_direction != "up":
        new_direction = "down"

    if keys[pygame.K_d] and snake_direction2 != "left":
        new_direction2 = "right"
    elif keys[pygame.K_a] and snake_direction2 != "right":
        new_direction2 = "left"
    elif keys[pygame.K_w] and snake_direction2 != "down":
        new_direction2 = "up"
    elif keys[pygame.K_s] and snake_direction2 != "up":
        new_direction2 = "down"

    #отрисовка змейки
    for i in range (len(snake_body)):
        if i == 0:
            pygame.draw.circle(screen, BLUE, snake_body[i].center, cell_size/2)
        else:
            pygame.draw.circle(screen, BLUE, snake_body[i].center, cell_size/2)
            pygame.draw.circle(screen, (51,233,255), snake_body[i].center, cell_size/4)
    for i in range (len(snake_body2)):
            if i == 0:
                pygame.draw.circle(screen, PINK, snake_body2[i].center, cell_size/2)
            else:
                pygame.draw.circle(screen, PINK, snake_body2[i].center, cell_size/2)
                pygame.draw.circle(screen, (51,233,255), snake_body2[i].center, cell_size/4)


    #управление 
    snake_direction = new_direction
    if snake_direction == "up":
        snake_body.insert(0,pygame.Rect(snake_body[0].left ,
                                        snake_body[0].top - cell_size,
                                        cell_size, cell_size))
    elif snake_direction == "down":
        snake_body.insert(0,pygame.Rect(snake_body[0].left ,
                                        snake_body[0].top + cell_size,
                                        cell_size, cell_size))
    elif snake_direction == "left":
        snake_body.insert(0,pygame.Rect(snake_body[0].left - cell_size,
                                        snake_body[0].top,
                                        cell_size, cell_size))
    elif snake_direction == "right":
        snake_body.insert(0,pygame.Rect(snake_body[0].left + cell_size,
                                        snake_body[0].top,
                                        cell_size, cell_size))

    snake_direction2 = new_direction2
    if snake_direction2 == "up":
        snake_body2.insert(0,pygame.Rect(snake_body2[0].left ,
                                        snake_body2[0].top - cell_size,
                                        cell_size, cell_size))
    elif snake_direction2 == "down":
        snake_body2.insert(0,pygame.Rect(snake_body2[0].left ,
                                        snake_body2[0].top + cell_size,
                                        cell_size, cell_size))
    elif snake_direction2 == "left":
        snake_body2.insert(0,pygame.Rect(snake_body2[0].left - cell_size,
                                        snake_body2[0].top,
                                        cell_size, cell_size))
    elif snake_direction2 == "right":
        snake_body2.insert(0,pygame.Rect(snake_body2[0].left + cell_size,
                                        snake_body2[0].top,
                                        cell_size, cell_size))    
    #телепорт
    if snake_body[0].left < 0:
        snake_body[0].left += WIDTH
    elif snake_body[0].right > WIDTH:
        snake_body[0].right = 0
    elif snake_body[0].bottom > HEIGHT:
        snake_body[0].bottom = 0
    elif snake_body[0].top < 0:
        snake_body[0].top = HEIGHT

    if snake_body2[0].left < 0:
        snake_body2[0].left += WIDTH
    elif snake_body2[0].right > WIDTH:
        snake_body2[0].right = 0
    elif snake_body2[0].bottom > HEIGHT:
        snake_body2[0].bottom = 0
    elif snake_body2[0].top < 0:
        snake_body2[0].top = HEIGHT
    
    #проверка столкновения с самим собой
    for i in range(1, len(snake_body)):
        if snake_body[0].colliderect(snake_body[i]):
            game_over_snake = 1
            print(game_over_snake)
            running = False
    if snake_length2 > 4:
        for i in range(1, len(snake_body2)):
            if snake_body2[0].colliderect(snake_body2[i]):
                game_over_snake = 2
                print(game_over_snake2)
                running = False            
            
    #удаление хвоста  
    if len(snake_body) > snake_length:
        snake_body.pop()
    if len(snake_body2) > snake_length2:
        snake_body2.pop()

    #количество съеденых яблок
    score_rext = font.render(f"Съедено яблок: {snake_length - 3}", True, BLACK)
    screen.blit(score_rext, (WIDTH-140,10))
    score_rext2 = font.render(f"Съедено яблок: {snake_length2 - 3}", True, BLACK)
    screen.blit(score_rext2, (10,10))

    #отрисовка яблока
    pygame.draw.circle(screen, RED, apple_position.center, cell_size/2)
    #pygame.draw.rect(screen, BLACK, apple_position, 2)
    #pygame.draw.rect(screen, BLACK, snake_body[1], 2)

    #проверка столкновений
    if snake_body[0].colliderect(apple_position) == True:
        snake_length += 1
        apple_rnd_x = random.randint(0,WIDTH - cell_size)
        apple_rnd_y = random.randint(0,HEIGHT - cell_size)
        apple_position = pygame.Rect(apple_rnd_x,apple_rnd_y,cell_size,cell_size)
    if snake_body2[0].colliderect(apple_position) == True:
        snake_length2 += 1
        apple_rnd_x = random.randint(0,WIDTH - cell_size)
        apple_rnd_y = random.randint(0,HEIGHT - cell_size)
        apple_position = pygame.Rect(apple_rnd_x,apple_rnd_y,cell_size,cell_size)    
    
    pygame.display.flip()
    screen.fill(GREEN)

pygame.quit()
    




    
