import time
import pygame
from tkinter import*
from tkinter import messagebox

pygame.init()
pygame.display.set_icon(pygame.image.load("Icon.png"))

screen = pygame.display.set_mode((1920, 1070))
pygame.display.set_caption("Установщик")
font = pygame.font.SysFont("Lucida Console", 100)
label = font.render("WinLock By German", 1, (150, 5, 5))

while True:
    for event in pygame.event.get() :
        if event.type == pygame.QUIT:
            pygame.quit()
            time.sleep(0.01)
            pygame.display.set_icon(pygame.image.load("Icon.png"))
            screen = pygame.display.set_mode((1920, 1080))
            pygame.display.set_caption("WinLock By German")
            messagebox.showerror("Ошибка!", "Твои данные полетели разработчику (Герману)")

    screen.fill((0, 0, 0))
    screen.blit(label, (50, 50))

    pygame.display.update()
