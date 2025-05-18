import pygame
import random

pygame.init()


# Colors
white = (255, 255, 255)
red = (255, 0, 0)
black = (0, 0, 0)

# Creating window
screen_width = 400
screen_height = 500
gameWindow = pygame.display.set_mode((screen_width, screen_height))

#the bg image
bgimg = pygame.image.load("bg.jpg")
bgimg = pygame.transform.scale(bgimg, (screen_width, screen_height)).convert_alpha()
# Game Title
pygame.display.set_caption("Snakes")
pygame.display.update()



clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 25)

def text_screen(text, color, x, y):
    screen_text = font.render(text, True, color)
    gameWindow.blit(screen_text, [x,y])


def plot_snake(gameWindow, color, snk_list, snake_size):
    for x,y in snk_list:
        pygame.draw.rect(gameWindow, color, [x, y, snake_size, snake_size])

#Welcome page
def welcome():
    exit_game= False
    while not exit_game:
        gameWindow.fill(white)
        text_screen("Welcome to Snakes",black,0,0)
        text_screen("Tap Space to start",black,0,100)
        for event in pygame.event.get():
            if event == pygame.QUIT:
                exit_game=True
                
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_w:
                    pygame.quit()
                    quit()
                if event.key == pygame.K_SPACE:
                     #playing the GAME
                    pygame.mixer.init()
                    gameloop()
            pygame.display.update()
            clock.tick(25)

# Game Loop
def gameloop():

    # Game specific variables

    exit_game = False
    game_over = False
    snake_x = 45
    snake_y = 55
    velocity_x = 0
    with open("hiscore.txt","r") as f:
        hiscore = f.read()
    velocity_y = 0
    food_x = random.randint(20, screen_width/2)
    food_y = random.randint(20, screen_height/2)
    score = 0
    init_velocity = 3.5
    snake_size = 20
    fps = 25
    snk_list = []
    snk_length = 1

    while not exit_game:
        
        if game_over:
            with open("hiscore.txt","w") as f:
                f.write(str(hiscore))
            gameWindow.fill(white)
            text_screen("Game Over! Tap Enter to play again.",red,0,0)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    exit_game = True
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        
                        gameloop()
        else:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    exit_game = True

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RIGHT:
                        velocity_x = init_velocity
                        velocity_y = 0

                    if event.key == pygame.K_LEFT:
                        velocity_x = - init_velocity
                        velocity_y = 0

                    if event.key == pygame.K_UP:
                        velocity_y = - init_velocity
                        velocity_x = 0

                    if event.key == pygame.K_DOWN:
                        velocity_y = init_velocity
                        velocity_x = 0
                    #Cheat code -1
                    
                    if event.key == pygame.K_s:
                        score+=10
                    #Cheat code -2

                    if event.key == pygame.K_q:
                        game_over=True
                        pygame.mixer.music.load('gameover.mp3')
                        pygame.mixer.music.play()
            snake_x = snake_x + velocity_x
            snake_y = snake_y + velocity_y

            if abs(snake_x - food_x)<15 and abs(snake_y - food_y)<15:
                score +=10
                food_x = random.randint(20, screen_width / 2)
                food_y = random.randint(20, screen_height / 2)
                snk_length +=5
                #Hi score
                if score>int(hiscore):
                    hiscore = score
            gameWindow.fill(white)
            gameWindow.blit(bgimg, (0, 0))
            text_screen("Score: " + str(score)+ " Hiscore : " + str(hiscore), white, 5, 5)
            pygame.draw.rect(gameWindow, red, [food_x, food_y, snake_size, snake_size])

            head = []
            head.append(snake_x)
            head.append(snake_y)
            snk_list.append(head)

            if len(snk_list)>snk_length:
                del snk_list[0]
            #Collision with wall
            if snake_x<0 or snake_x>screen_width or snake_y<0 or snake_y>screen_height:
                game_over = True
                pygame.mixer.music.load('gameover.mp3')
                pygame.mixer.music.play()
            #Collision with body
            if head in snk_list[:-1]:
                game_over = True
                pygame.mixer.music.load('gameover.mp3')
                pygame.mixer.music.play()
                #print("gameover")
            # pygame.draw.rect(gameWindow, black, [snake_x, snake_y, snake_size, snake_size])
            plot_snake(gameWindow, black, snk_list, snake_size)
        pygame.display.update()
        clock.tick(fps)

    pygame.quit()
    quit()
welcome()
