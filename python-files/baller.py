import pygame
import random
import math
pygame.init()
screen = pygame.display.set_mode((500, 500 ))  
pygame.display.set_caption("Baller") 

WHITE = (255, 255, 255)  
BLUE = (0, 0, 255)
BLACK=(0,0,0)
RED = (255, 0, 0)
class Circle:
    def __init__(self, center, radius, thickness, color):
        self.center = center
        self.radius = radius
        self.thickness = thickness
        self.color = color
       

    def draw(self):
        pygame.draw.circle(screen, self.color, self.center, self.radius, self.thickness)

def check_collision(ball_x, ball_y, ball_radius, circle_radius):
    distance = math.sqrt((ball_x - 250) ** 2 + (ball_y - 250) ** 2)
    
    return distance >= ball_radius + circle_radius-20

ball_x = random.randint(100,200)
ball_y = random.randint(100,200)
ball_radius = 10
ball_speed_x = 0.1
ball_speed_y = 0.1

running = True
circles = []
timer = 1500
gravity = 0
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    timer+=1
    if timer >= 1500:
        circles.append(Circle(
        center=(250, 250),
        radius=300,
        thickness=5,
        color=(random.randrange(0, 255), random.randrange(0, 255), random.randrange(0, 255))
        ))
        timer =0
    screen.fill(BLACK)

    for c in circles:
        c.draw()
        c.radius = c.radius-0.01

    gravity+=0.0002
    
    ball_x += ball_speed_x
    ball_y += ball_speed_y*gravity
    first_c = circles[0]
    if check_collision(ball_x, ball_y, ball_radius, first_c.radius):
        dx = ball_x - 250
        dy = ball_y - 250
        distance = math.sqrt(dx ** 2 + dy ** 2)

        if distance != 0:
            dx /= distance
            dy /= distance

        overlap = ball_radius + first_c.radius - distance
        ball_x -= dx * overlap
        ball_y -= dy * overlap
        gravity=random.uniform(-0.5,0.5)
        ball_speed_x *= -1 
        ball_speed_y *= -1 
        circles.pop(0)
    
    pygame.draw.circle(screen, WHITE, (int(ball_x), int(ball_y)), ball_radius)
    pygame.display.flip()

pygame.quit()
