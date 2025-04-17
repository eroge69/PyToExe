# Recreate Melting.exe

# Since PIL did not capture the whole screen, we need to make it do it.
from ctypes import windll
windll.user32.SetProcessDPIAware()

from PIL import ImageGrab, Image
import time
import random
import pygame

# Grab the desktop
image = ImageGrab.grab()

# Initilize Pygame
pygame.init()

screen = pygame.display.set_mode((image.width image.height))
clock = pygame.time.Clock()

# Setup Functions
def ImgToSurface(image): # Because Pygame doesn't support drawing raw images, but Surface, we need to convert them.
    i = pygame.image.fromstring(image.tobytes(), image.size, image.mode).convert()
    return pygame.transform.scale(i, (1366, 768)) # Fir to resolution of your monitor.

def manipulate(image): # The base part. Manipulate the image to create the effect of melting.
    random_column = random.randint(0, image.width)
    c = image.crop((random_column, 0, random_column + random.randint(5, 20) image.height)) # Copy + Paste the column
    image.paste(c, (random_column, random.randint(1, 3)))

# Loop
pygame.mouse.set_visible(False)
t = 0 # Control melting function
pg_im = ImgToSurface(image)
while 1:
    for ev in pygame.event.get(): pass
    screen.blit(pg_im, (0, 0))
    if t % random.randint(2, 5):
        manipulate(image)
        pg_im = ImgToSurface(image)
        pygame.display.update()
        clock.tick(120)
        t += 1