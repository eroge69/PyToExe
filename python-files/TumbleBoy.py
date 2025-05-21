#	This file was created for the game "Tumble Boy", by
#	Bob Rost, Chris Jackson, Eben Myers, and Tom Corbett.
#	Please study it, learn from it, change it, and share it.

#import olpcgames
from source.Application import *
from source.Sound import *
from source.Constants import *
import sys, pygame, os
from pygame.locals import *

pygame.init()	#initialize all the media stuff
def main():
	screen = pygame.display.set_mode((int(SCREEN_SIZE[0]), int(SCREEN_SIZE[1])))
	LoadSounds()
	application = Application(screen)
	#game = Game(screen)	#the main game object
	#global sound
	#sound = LoadSound("minfadil.ogg") #please
	#sound = LoadSound("ainalhamam.ogg")
	#sound = LoadSound("data/welcome.wav")
	#sound.play()

	#game.LoadNextLevel()

	last_time = pygame.time.get_ticks() #milliseconds since app start
	while (not application.should_quit):
		#handle all inputs
		for event in pygame.event.get():
			#KEYDOWN event contains key(ascii value), unicode(typed char), mod(modifiers while pressed)
			if (event.type == pygame.QUIT):				sys.exit()
			elif (event.type == pygame.MOUSEMOTION):	application.MouseMoved(event.pos)
			elif (event.type == pygame.KEYDOWN):		application.KeyPressed(event.key)
			elif (event.type == pygame.KEYUP):			application.KeyReleased(event.key)

		#determine elapsed time, update game
		now = pygame.time.get_ticks()		#milliseconds since app start
		dt = (now - last_time) / 1000.0		#seconds since last update
		last_time = now						#prepare timer for next update
		application.Update(dt)

		#redraw the screen
		application.Draw()
		pygame.display.flip()

if __name__=="__main__":
	main()
