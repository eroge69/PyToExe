
from pynput.mouse import Listener, Controller, Button
import threading
import time
import keyboard  # For hotkey to exit

mouse = Controller()
running = False

# CONFIGURATION
MOVE_X = 0        # Horizontal adjustment (can be - or +)
MOVE_Y = 2        # Pixels to move down each step
DELAY = 0.01      # Delay between movements in seconds

def recoil_loop():
    global running
    while running:
        mouse.move(MOVE_X, MOVE_Y)
        time.sleep(DELAY)

def on_click(x, y, button, pressed):
    global running
    if button == Button.left:
        if pressed:
            running = True
            threading.Thread(target=recoil_loop, daemon=True).start()
        else:
            running = False

def start_listener():
    with Listener(on_click=on_click) as listener:
        listener.join()

def monitor_exit():
    # Press ESC to exit the script
    keyboard.wait('esc')
    print("Exiting...")
    exit(0)

# Start both threads
threading.Thread(target=start_listener, daemon=True).start()
monitor_exit()
