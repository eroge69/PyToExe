import pygame
import sys
import random

# 초기화
pygame.init()
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("세로형 자동차 레이싱 게임")
clock = pygame.time.Clock()

# 색상
GRAY = (50, 50, 50)
WHITE = (255, 255, 255)

# 이미지 크기 (세로형)
CAR_WIDTH, CAR_HEIGHT = 40, 80

# 플레이어 자동차 이미지 (세로 유지)
player_car_img = pygame.image.load("player_car.png")
player_car_img = pygame.transform.scale(player_car_img, (CAR_WIDTH, CAR_HEIGHT))
player_rect = player_car_img.get_rect(center=(WIDTH // 2, HEIGHT - 100))

# AI 차량 이미지들 불러오기 (세로 유지)
incoming_car_imgs = []
for i in range(1, 4):
    img = pygame.image.load(f"incoming_car_{i}.png")
    img = pygame.transform.scale(img, (CAR_WIDTH, CAR_HEIGHT))
    incoming_car_imgs.append(img)

# 콘 장애물 이미지
cone_img = pygame.image.load("cone.png")
cone_img = pygame.transform.scale(cone_img, (30, 30))

# 도로 그리기
def draw_road():
    pygame.draw.polygon(screen, GRAY, [
        (WIDTH // 2 - 180, HEIGHT),
        (WIDTH // 2 + 180, HEIGHT),
        (WIDTH // 2 + 60, 0),
        (WIDTH // 2 - 60, 0)
    ])

# AI 차량 클래스
class IncomingCar:
    def __init__(self):
        lane = random.choice([-100, 0, 100])
        self.x = WIDTH // 2 + lane
        self.y = -CAR_HEIGHT
        self.speed = 5
        self.image = random.choice(incoming_car_imgs)
        self.rect = self.image.get_rect(center=(self.x, self.y))

    def move(self):
        self.y += self.speed
        self.rect.centery = self.y

    def draw(self):
        screen.blit(self.image, self.rect)

# 콘 장애물 클래스
class ConeObstacle:
    def __init__(self):
        self.x = random.randint(WIDTH // 2 - 130, WIDTH // 2 + 130)
        self.y = -30
        self.speed = 5
        self.rect = cone_img.get_rect(center=(self.x, self.y))

    def move(self):
        self.y += self.speed
        self.rect.centery = self.y

    def draw(self):
        screen.blit(cone_img, self.rect)

# 게임 변수
incoming_cars = []
cones = []
spawn_timer = 0
cone_timer = 0
spawn_interval = random.randint(80, 130)
cone_interval = random.randint(100, 180)
game_over = False

# 메인 루프
while True:
    screen.fill(WHITE)
    draw_road()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    if not game_over:
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and player_rect.left > WIDTH // 2 - 160:
            player_rect.x -= 5
        if keys[pygame.K_RIGHT] and player_rect.right < WIDTH // 2 + 160:
            player_rect.x += 5

        # AI 차량 생성
        spawn_timer += 1
        if spawn_timer > spawn_interval:
            incoming_cars.append(IncomingCar())
            spawn_timer = 0
            spawn_interval = random.randint(80, 130)

        # 콘 생성
        cone_timer += 1
        if cone_timer > cone_interval:
            cones.append(ConeObstacle())
            cone_timer = 0
            cone_interval = random.randint(100, 180)

        # AI 차량 처리
        for car in incoming_cars[:]:
            car.move()
            car.draw()
            if car.rect.colliderect(player_rect):
                game_over = True
            if car.y > HEIGHT:
                incoming_cars.remove(car)

        # 콘 처리
        for cone in cones[:]:
            cone.move()
            cone.draw()
            if cone.rect.colliderect(player_rect):
                game_over = True
            if cone.y > HEIGHT:
                cones.remove(cone)

        # 플레이어 차량 그리기
        screen.blit(player_car_img, player_rect)
    else:
        font = pygame.font.SysFont(None, 72)
        text = font.render("Game Over", True, (255, 0, 0))
        screen.blit(text, (WIDTH // 2 - 150, HEIGHT // 2 - 40))

    pygame.display.update()
    clock.tick(60)
