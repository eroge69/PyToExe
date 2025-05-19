import pygame
import sys

pygame.init()

Width, Height = 800, 600
Ground_y = Height - 50

White = (255, 255, 255)
Green = (0, 255, 0)
Blue = (0, 0, 255)

screen = pygame.display.set_mode((Width, Height))
pygame.display.set_caption("Платформер")
clock = pygame.time.Clock()


Gravity = 0.5
Jump_force = 20
Friction = 0.5


class Platform(pygame.sprite.Sprite):
    def __init__(self, X, Y, SizeX, SizeY, speed):
        super().__init__()
        self.image = pygame.Surface((SizeX, SizeY))
        self.image.fill((128, 128, 128))
        self.rect = self.image.get_rect()
        self.rect.centerx = X
        self.rect.centery = Y

        self.vel_x = speed

    def update(self):
        if self.rect.right > Width:
            self.rect.right = Width
            self.vel_x = -self.vel_x

        if self.rect.left < 0:
            self.rect.left = 0
            self.vel_x = -self.vel_x

        self.rect.centerx += self.vel_x

    def collide(self):
        pass

class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((50, 50))
        self.image.fill(White) # ... fill( (x, x, x) )
        self.rect = self.image.get_rect()
        self.rect.midbottom = (Width // 2, Ground_y)

        self.speed = 5
        self.on_ground = True
        self.on_platform = False

        self.vel_x = 0
        self.vel_y = 0

    def update(self, keys):
        # Гравитация
        self.vel_y += Gravity
        self.rect.y += self.vel_y

        if self.rect.top < 0:
            self.rect.top = 0
            self.vel_y = -self.vel_y / 2

        if self.rect.left < 0:
            self.rect.left = 0
            self.vel_x = -self.vel_x / 2

        if self.rect.right > Width:
            self.rect.right = Width
            self.vel_x = -self.vel_x / 2

        if self.rect.bottom > Ground_y:
            self.rect.bottom = Ground_y
            self.vel_y = -self.vel_y / 2

            self.on_ground = True
        else:
            self.on_ground = False

        if keys[pygame.K_LEFT]:
            self.vel_x = - self.speed
        elif keys[pygame.K_RIGHT]:
            self.vel_x = self.speed
        else:
            if self.vel_x > 0:
                self.vel_x -= Friction
                if self.vel_x < 0:
                    self.vel_x = 0
            if self.vel_x < 0:
                self.vel_x += Friction
                if self.vel_x > 0:
                    self.vel_x = 0

        self.rect.x += self.vel_x

    def jump(self):
        #if self.on_ground:
        self.vel_y = -Jump_force

        if self.on_platform == True:
            self.vel_y = Jump_force
        else:
            self.vel_y = -Jump_force


platform = Platform(400, 300, 300, 50, 0)
platform1 = Platform(200, 100, 100, 50, 2)

platforms = pygame.sprite.Group()

platforms.add(platform)
platforms.add(platform1)

player = Player()
all_sprite = pygame.sprite.Group(player)
all_sprite.add(platforms)

ground = pygame.Rect(0, Ground_y, Width, 50)

running = True

while running:
    clock.tick(60)
    keys = pygame.key.get_pressed()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                player.jump()

    for platform in pygame.sprite.spritecollide(player, platforms, False):
        if (player.rect.bottom <= platform.rect.top + 10
                and player.vel_y > 0):
            player.rect.bottom = platform.rect.top
            player.vel_y = 0
        if (player.rect.top <= platform.rect.bottom - 10
                and player.rect.bottom > platform.rect.bottom and player.vel_y < 0):
            player.rect.top = platform.rect.bottom
            player.vel_y = -player.vel_y

        if player.vel_x > 0:
            if (player.rect.right >= platform.rect.left
                    and player.rect.left < platform.rect.left):
                player.rect.right = platform.rect.left
                player.vel_x = 0

        elif player.vel_x < 0:
            if (player.rect.left <= platform.rect.right
                    and player.rect.right > platform.rect.right):
                player.rect.left = platform.rect.right
                player.vel_x = 0

    player.update(keys)
    platforms.update()

    screen.fill(Blue)
    pygame.draw.rect(screen, Green, ground)
    all_sprite.draw(screen)
    pygame.display.flip()

pygame.quit()
sys.exit()