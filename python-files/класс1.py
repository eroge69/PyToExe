import pygame

pygame.init()

width = 800
height = 600

#screen = pygame.display.set_mode((width, height))
screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
w, h = screen.get_size() 

normal_image = pygame.image.load('player.png')
normal_image = pygame.transform.scale(normal_image, (w, h))

screamer_image = pygame.image.load('screamer.png')
screamer_image = pygame.transform.scale(screamer_image, (w, h))


scream_sound = pygame.mixer.Sound('screamer.png')
scream_sound.set_volume(1)

running = True

while (running):
    screen.fill((255,255,255))
    screen.blit(normal_image, (0, 0))
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
             screen.blit(screamer_image, (0, 0))
             scream_sound.play
             pygame.display.flip()
             pygame.time.wait(2000)
            
            
    pygame.display.flip()
pygame.quit()
