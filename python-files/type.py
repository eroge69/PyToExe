import keyboard
import threading
import pygame
import time

pygame.mixer.init()

last_played = 0  # Global variable to track last play time

def play_sound():
    global last_played
    now = time.time()
    if now - last_played >= 0.1:
        pygame.mixer.Sound('click.wav').play()
        last_played = now

def on_key(event):
    threading.Thread(target=play_sound, daemon=True).start()

keyboard.on_press(on_key)

print("Key sound background process running. Press ESC to stop.")
keyboard.wait('esc')