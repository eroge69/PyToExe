from pynput import mouse, keyboard
from pynput.mouse import Controller as MouseController, Button
from pynput.keyboard import Listener, KeyCode
import threading
import time

mouse_controller = MouseController()
burst_mode = False
bursting = False
toggle_key = KeyCode(char='f')  # You can change this to another key

def burst_click():
    global bursting
    while bursting:
        for _ in range(3):  # 3-shot burst
            mouse_controller.click(Button.left, 1)
            time.sleep(0.05)  # Delay between shots in a burst
        time.sleep(0.3)  # Delay between bursts

def on_click(x, y, button, pressed):
    global bursting
    if button == Button.left:
        if pressed and burst_mode:
            bursting = True
            threading.Thread(target=burst_click).start()
        else:
            bursting = False

def on_press(key):
    global burst_mode
    if key == toggle_key:
        burst_mode = not burst_mode
        print(f"Burst mode {'enabled' if burst_mode else 'disabled'}")

mouse_listener = mouse.Listener(on_click=on_click)
keyboard_listener = Listener(on_press=on_press)

mouse_listener.start()
keyboard_listener.start()

mouse_listener.join()
keyboard_listener.join()
