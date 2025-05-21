import pygame

pygame.init()

clock = pygame.time.Clock()

screen = pygame.display.set_mode((600, 300))
pygame.display.set_caption('Red Square')
pygame.display.set_icon(pygame.image.load('pygame/Red Square/icon/icon.png').convert_alpha())

player = pygame.Surface((50, 50))
player.fill('red')

bg = pygame.image.load('pygame/Red Square/bg/bg.png').convert_alpha()

main_menu_text1_x = 175
main_menu_text1_y = 50
main_menu_text2_x = 225
main_menu_text2_y = 125
main_menu_text3_x = 230
main_menu_text3_y = 200

main_menu_text = pygame.font.Font('pygame/Red Square/text/SCE-PS3RodinLATINBold.ttf', 40)
main_menu_text1 = main_menu_text.render('Red Square', True, 'red')
main_menu_text2 = main_menu_text.render('Играть', True, 'grey')
main_menu_text3 = main_menu_text.render('Выйти', True, 'grey')
main_menu_text2_rect = main_menu_text2.get_rect(topleft = (main_menu_text2_x, main_menu_text2_y))
main_menu_text3_rect = main_menu_text3.get_rect(topleft = (main_menu_text3_x, main_menu_text3_y))

player_x = 50
player_y = 100
player_speed = 3

player.get_rect(topleft = (player_x, player_y))

EXIT = True
game = False

while EXIT:
    
    screen.fill((50, 50, 50))
    screen.blit(main_menu_text1, (main_menu_text1_x, main_menu_text1_y))
    screen.blit(main_menu_text2, (main_menu_text2_x, main_menu_text2_y))
    screen.blit(main_menu_text3, (main_menu_text3_x, main_menu_text3_y))
    
    mouse = pygame.mouse.get_pos()
    if main_menu_text2_rect.collidepoint(mouse) and pygame.mouse.get_pressed()[0]:
        game = True
    elif main_menu_text3_rect.collidepoint(mouse) and pygame.mouse.get_pressed()[0]:
        EXIT = False
        
    keys = pygame.key.get_pressed()
    if keys[pygame.K_RSHIFT]:
        game = False
    
    if game:
        screen.blit(bg, (0, 0))
        screen.blit(player, (player_x, player_y))
            
        if keys[pygame.K_RIGHT]:
            player_x += player_speed
        elif keys[pygame.K_LEFT]:
            player_x -= player_speed
        elif keys[pygame.K_UP]:
            player_y -= player_speed
        elif keys[pygame.K_DOWN]:
            player_y += player_speed
        
        if player_x > 550:
            player_x -= player_speed
        elif player_x < 0:
            player_x += player_speed
        elif player_y > 250:
            player_y -= player_speed
        elif player_y < 0:
            player_y += player_speed
        
        
 
    pygame.display.update()
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            EXIT = False
            
    clock.tick(60)  
          