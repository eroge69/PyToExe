
import sys
import pygame
import math

pygame.init()

width, height = 600, 400
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Sürpriz")

white = (255, 255, 255)
red = (255, 0, 0)

font = pygame.font.SysFont("Arial", 48, bold=True)

clock = pygame.time.Clock()

angle = 0

running = True
while running:
    screen.fill(white)

    text = font.render("Seni Çok Seviyorum", True, red)
    text_rect = text.get_rect(center=(width // 2, height // 2))

    rotated_text = pygame.transform.rotate(text, angle)
    rotated_rect = rotated_text.get_rect(center=text_rect.center)

    screen.blit(rotated_text, rotated_rect)

    angle += 1
    if angle >= 360:
        angle = 0

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()
