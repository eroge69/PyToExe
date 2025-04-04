import keyboard as kb
import mouse as m
import time as t
import random
import pyautogui as keys
import threading

def art():
    print("...........................................................................")
    print(".=..@@@..=.@@...=.@@.@@@@@@@@=@@.==============.%@@..=.=@@@@@@@.@=...@@@-=.")
    print("...@@.@@.-.@@@@...@@....@@....@@.=============..@@@@....@.......@..@@...-=.")
    print("..#@..@@...@@.@@..@@.==.@@.==.@@.===.....-===..@@..@@...@@@@@@..@@@@...===.")
    print("..@@@@@@@..@@..%@.@@.==.@@.==.@@.===.@@@@-==:.@@@@@@@...@.......@..@@@...=.")
    print(".@@.....@@.@@.:..@@@.==.@@.==.@@.===.....-==:@@.....@@.+@.=====.@+...@@@.=.")
    print("....==-.......=-.....==....==....===========:...-==.......=====...-=:....=.")
    print(".......................................................By Vovancheg........")

art()

afk_running = False

def perform_action(action):
    if action == 1:
        m.click(button="left")
    elif action == 2:
        for _ in range(6):
            keys.keyDown('w')
            keys.keyUp('w')
    elif action == 3:
        for _ in range(6):
            keys.keyDown('a')
            keys.keyUp('a')
    elif action == 4:
        for _ in range(6):
            keys.keyDown('s')
            keys.keyUp('s')
    elif action == 5:
        for _ in range(6):
            keys.keyDown('d')
            keys.keyUp('d')
    elif action == 6:
        keys.keyDown('space')
        keys.keyUp('space')
    elif action == 7:
        keys.keyDown('ctrl')
        keys.keyUp('ctrl')
    elif action == 8:
        screen_width, screen_height = keys.size() 
        random_x = random.randint(0, screen_width)
        random_y = random.randint(0, screen_height)
        m.move(random_x, random_y, absolute=True, duration=0.5)

def AFK():
    global afk_running
    afk_running = True
    print("Режим Anti-AFK запущен.")
    while afk_running:
        ls = random.choice(range(1, 9))  
        perform_action(ls)
        t.sleep(random.uniform(1, 3))

def stop_afk():
    global afk_running
    afk_running = False
    print("Anti-AFK остановлен.")

def start_afk_thread():
    while True:
        kb.wait('F8')
        threading.Thread(target=AFK).start()
        kb.wait('F8')
        stop_afk()

print("Нажмите F8 для запуска Anti-AFK, F9 для остановки Anti-AFK.")
start_afk_thread()
