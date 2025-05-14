import pygame
import sys
from random import randint
import tkinter as tk

root = tk.Tk()
wid = root.winfo_screenwidth()
hei = root.winfo_screenheight()
root.destroy()

pygame.init()

screen = pygame.display.set_mode((wid, hei))
clock = pygame.time.Clock()

screen.fill((0, 0, 0))

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
            break
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            pygame.quit()
            sys.exit()
            break
    color = (randint(0,255), randint(0, 255), randint(0, 255))
    l = randint(0, wid)
    t = randint(0, hei)
    w = randint(10, 500)
    h = randint(10, 500)
    
    pygame.draw.rect(screen, color, pygame.Rect(l, t, w, h))

    pygame.display.flip()
    clock.tick(60)
