import os
import time
from datetime import datetime
import pyautogui
from pynput import mouse, keyboard

# Set up the directory for saving screenshots
screenshot_dir = os.path.join(os.getcwd(), 'screenshots')
if not os.path.exists(screenshot_dir):
    os.makedirs(screenshot_dir)

# Global variables
actions = []
is_recording = False
last_action_time = None

def on_click(x, y, button, pressed):
    global last_action_time
    if is_recording and pressed and button == mouse.Button.left:
        current_time = time.time()
        if last_action_time is None:
            delay = 0
        else:
            delay = current_time - last_action_time
        actions.append({'type': 'click', 'position': (x, y), 'delay': delay})
        last_action_time = current_time

def on_press(key):
    global is_recording, last_action_time
    try:
        if key == keyboard.Key.f1:
            is_recording = not is_recording
            if is_recording:
                print("Recording started")
                actions.clear()
                last_action_time = None
            else:
                print("Recording stopped")
        elif is_recording and key.char == 's':
            current_time = time.time()
            if last_action_time is None:
                delay = 0
            else:
                delay = current_time - last_action_time
            actions.append({'type': 'screenshot', 'delay': delay})
            last_action_time = current_time
        elif key == keyboard.Key.f2:
            if not is_recording:
                playback()
        elif key == keyboard.Key.esc:
            mouse_listener.stop()
            keyboard_listener.stop()
    except AttributeError:
        pass

def playback():
    if not actions:
        print("No actions recorded")
        return
    print("Starting playback")
    for action in actions:
        time.sleep(action['delay'])
        if action['type'] == 'click':
            pyautogui.click(action['position'][0], action['position'][1])
        elif action['type'] == 'screenshot':
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
            filename = f"screenshot_{timestamp}.png"
            image = pyautogui.screenshot()
            image.save(os.path.join(screenshot_dir, filename))
    print("Playback finished")

# Instructions for the user
print("Instructions:")
print(" - Press F1 to start/stop recording")
print(" - During recording, click the mouse to record clicks")
print(" - Press 's' during recording to record a screenshot action")
print(" - Press F2 to start playback of the recorded actions")
print(" - Press Esc to exit the script")

# Set up and start the listeners
mouse_listener = mouse.Listener(on_click=on_click)
keyboard_listener = keyboard.Listener(on_press=on_press)

mouse_listener.start()
keyboard_listener.start()

mouse_listener.join()
keyboard_listener.join()