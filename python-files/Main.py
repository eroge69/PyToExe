import pygame as py
from time import time
import random
from random import randint

py.init()
py.mixer.init()

WIDTH, HEIGHT = 1080, 1080
WIN = py.display.set_mode((WIDTH, HEIGHT), py.FULLSCREEN | py.DOUBLEBUF)
py.display.set_caption("Carzutututu")

#sounda
engine_sound = py.mixer.Sound("assets/enginer.wav")
engine2_sound = py.mixer.Sound("assets/engineSH.wav")
turbo_sound = py.mixer.Sound("assets/turbo.wav")
turbo2_sound = py.mixer.Sound("assets/turbo2.wav")
turbo3_sound = py.mixer.Sound("assets/turbo3.wav")
engine_sound.set_volume(0.7)
engine2_sound.set_volume(0.5)
turbo_sound.set_volume(1.0)
turbo2_sound.set_volume(1.0)
turbo3_sound.set_volume(1.0)
engine_sound.play(-1)
soundr_list = [turbo_sound , turbo2_sound , turbo3_sound]
sound_paused = False
#background
bg = py.image.load("assets/road.png")
bg = py.transform.scale(bg, (WIDTH, HEIGHT)).convert()

#player
player_w, player_h = 100, 200
orginal_speed, upgrade_speed = 0.8, 0.0
player_speed = orginal_speed
player1x = WIDTH // 3
player1y = HEIGHT // 7
player1 = py.Rect((player1x , player1y ), (player_w, player_h))
player1_img = py.image.load("assets/player_car.png")
player1_img = py.transform.rotate(player1_img, 270)
player1_img = py.transform.scale(player1_img, (player_w, player_h)).convert_alpha()

#enemys
SpeedList = [0.1 , 1 , 2]
ENEMY_W, ENEMY_H = enemy_size = (100, 200)
enemy_speed = random.choice(SpeedList)
enemy_img = py.image.load('assets/enemy_car.png')
enemy_img = py.transform.scale(enemy_img, enemy_size).convert_alpha()
ENEMYS = [[WIDTH, randint(0, HEIGHT - ENEMY_H)]]
enemy_img = py.transform.rotate(player1_img, 360)

MAX_ENEMY_SPAWN = 12
MAX_ENEMY_SPAWN_TIME = 2
MIN_ENEMY_SPAWN_TIME = 1
LAST_ENEMY_SPAWN_TIME = time()
ENEMY_SPAWN_TIME = randint(MIN_ENEMY_SPAWN_TIME, MAX_ENEMY_SPAWN_TIME)

def draw():
    WIN.blit(bg, (0, road_y1))
    WIN.blit(bg, (0, road_y2))
    WIN.blit(player1_img, player1.topleft)
    #for enemy in ENEMYS:
        #WIN.blit(enemy_img, enemy_size)
    py.display.flip()
road_y1 = 0
road_y2 = -HEIGHT 
road_speed = 5  
def update_road():
    global road_y1, road_y2
    road_y1 -= road_speed
    road_y2 -= road_speed
    if road_y1 <= -HEIGHT:
        road_y1 = road_y2 + HEIGHT
    if road_y2 <= -HEIGHT:
        road_y2 = road_y1 + HEIGHT


def movement():
    global road_speed
    global current_speed
    current_speed = road_speed * 10
    current_speed = max(0, min(current_speed, 300))
    keys = py.key.get_pressed()
    if (keys[py.K_w] or keys[py.K_UP]) and player1.top > 0:
        player1.y -= player_speed
        road_speed -= 0.1
        current_speed -= 50
    if (keys[py.K_s] or keys[py.K_DOWN]) and player1.bottom < HEIGHT:
        player1.y += player_speed
        road_speed += 0.1
        current_speed += -60
    if (keys[py.K_d] or keys[py.K_RIGHT]) and player1.right:
        player1.x += player_speed
    if (keys[py.K_a] or keys[py.K_LEFT]) and player1.left > 0:
        player1.x -= player_speed

def keydown(event):
    global player_speed
    global sound_paused
    if event.key == py.K_SPACE:
        player_speed = upgrade_speed
    if event.key == py.K_s:
      engine2_sound.play()


def keyup(event):
    global player_speed
    global road_speed
    if event.key == py.K_SPACE:
        player_speed = orginal_speed
    if event.key == py.K_s:  
        engine2_sound.fadeout(500)
        random.choice(soundr_list).play()

#کیلومترعلی
kilometers = 0.0
current_speed = 0.0
def update_kilometer(delta_time):
    global kilometers
    kilometers += (current_speed * delta_time) / 3600

font = py.font.Font("assets/kmfont.ttf", 36)
def draw_kilometer():
    text = font.render(f"Kilometre: {current_speed:.2f} km", True, (255, 255, 255))
    WIN.blit(text, (10, 10)) 


def main():
    fps = 10000
    run = True
    clock = py.time.Clock()
    
    while run:
        delta_time = clock.tick(fps) / 1000.0
        WIN.fill((0, 0, 0))
        update_road()
        draw()
        draw_kilometer()
        py.display.flip()
        for event in py.event.get():
            if event.type == py.KEYDOWN:
                keydown(event)
                if event.key == py.K_ESCAPE:
                    run = False
                    break
            elif event.type == py.KEYUP:
                keyup(event)
            elif event.type == py.QUIT:
                run = False
                break
        
        movement()
        draw()
        update_road()
        update_kilometer(delta_time)
        WIN.fill((0, 0, 0))
        draw_kilometer()
        clock.tick(fps)
    
    py.quit()

main()
