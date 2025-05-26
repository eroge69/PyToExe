import pygame
from src.main import settings as st
from src.main.menu.GameOverMenu import GameOverMenu
from src.main.menu.Menu import Menu
from src.main.SaveManager import SaveManager
from src.main.Game import Game
from src.main.menu.Cinematic import IntroCinematic

# Initialize Pygame
pygame.init()
pygame.display.set_caption(st.WINDOW_TITLE)

save_manager = SaveManager()
menu = Menu()
game = Game(save_manager)
game_over_menu = GameOverMenu()
game_over = False
intro_cinematic = IntroCinematic()

def main():
    running = True
    quit_menu = False
    clock = pygame.time.Clock()
    running_game = False
    
    while running:
        if not pygame.get_init():
            return False
        events = pygame.event.get()

        if game.game_end:
            return False

        # Handle game over menu
        if not running_game and quit_menu is True:
            game.stop()
            game_over_menu.draw()
            for event in events:
                if event.type == pygame.QUIT:
                    running = False
                    return False
            selected_option_restart = game_over_menu.update(events)
            if selected_option_restart == "Quitter":
                running = False
                return False
            elif selected_option_restart == "Réessayer":
                running_game = game.start(running, continue_game=True)
                quit_menu = True
                if not pygame.get_init():
                    return False
                break
            
            pygame.display.flip()
            continue

        for event in events:
            if event.type == pygame.QUIT:
                running = False
                return False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:  # Press 'Enter' to bypass intro and start new game
                    menu.current_screen = len(menu.intro_screens)  # Skip intro screens
                    break
        
        if not quit_menu:
            menu.draw()
            selected_option = menu.update(events)
            if selected_option == "Start":
                # Show intro cinematic before starting the game
                intro_cinematic.start()
                while not intro_cinematic.finished:
                    intro_cinematic.draw()
                    intro_cinematic.update()
                    pygame.display.flip()
                    clock.tick(60)
                    # Allow skipping the cinematic
                    for event in pygame.event.get():
                        if event.type == pygame.KEYDOWN or event.type == pygame.QUIT:
                            intro_cinematic.finished = True
                            pygame.mixer.music.stop()
                            break
                
                running_game = game.start(running, continue_game=False)
                quit_menu = True
    
            elif selected_option == "Continue":
                running_game = game.start(running, continue_game=True)
                quit_menu = True
            
        if pygame.get_init():
            pygame.display.flip()
            clock.tick(60)
        
    pygame.quit()

if __name__ == "__main__":
    main()
