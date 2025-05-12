import pygame
import math

# Impostazioni grafiche
WIDTH, HEIGHT = 800, 600
FPS = 60

# Colori
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)

# Costante gravitazionale normalizzata
G = 1.0

class Body:
    def __init__(self, x, y, vx, vy, color):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.fx = 0
        self.fy = 0
        self.color = color
        self.orbit = []

    def update_force(self, bodies):
        self.fx = self.fy = 0
        for other in bodies:
            if other is self:
                continue
            dx = other.x - self.x
            dy = other.y - self.y
            dist_sq = dx**2 + dy**2
            dist = math.sqrt(dist_sq)
            if dist_sq == 0:
                continue
            f = G / dist_sq
            self.fx += f * dx / dist
            self.fy += f * dy / dist

    def update(self, dt):
        self.vx += self.fx * dt
        self.vy += self.fy * dt
        self.x += self.vx * dt
        self.y += self.vy * dt

        #if len(self.orbit) > 1000:
        #    self.orbit.pop(0)
        self.orbit.append((self.x, self.y))

    def draw(self, screen):
        # Scala per la visualizzazione
        sx = int(self.x * 100 + WIDTH / 2)
        sy = int(self.y * 100 + HEIGHT / 2)
        pygame.draw.circle(screen, self.color, (sx, sy), 5)
        if len(self.orbit) > 2:
            path = [(int(x * 100 + WIDTH / 2), int(y * 100 + HEIGHT / 2)) for x, y in self.orbit]
            pygame.draw.lines(screen, self.color, False, path, 1)

# Inizializzazione Pygame
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Tre corpi - Orbita a forma di 8")
clock = pygame.time.Clock()

# Condizioni iniziali note dalla letteratura (unità normalizzate)
positions = [
   # (0.97000436, -0.24308753),
    (1, -0.3),
    (-0.97000436, 0.24308753),
    (0.0, 0.0)
]
velocities = [
    (0.4662036850, 0.4323657300),
    (0.4662036850, 0.4323657300),
    (-0.93240737, -0.86473146)
]
colors = [RED, BLUE, YELLOW]

# Creazione dei corpi
bodies = []
for i in range(3):
    body = Body(
        x=positions[i][0],
        y=positions[i][1],
        vx=velocities[i][0],
        vy=velocities[i][1],
        color=colors[i]
    )
    bodies.append(body)

# Loop principale
running = True
while running:
    time_speed = 10.0  # aumenta per velocizzare la simulazione
    dt = 0.001 * time_speed  # tempo simulato più piccolo per stabilità

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    screen.fill(BLACK)

    for body in bodies:
        body.update_force(bodies)
    for body in bodies:
        body.update(dt)
        body.draw(screen)

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
