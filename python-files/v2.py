import time
import psutil
from pynput import keyboard, mouse
import win32gui

idle_threshold = 1260  # seconds
last_activity_time = time.time()

def get_foreground_window_title():
    hwnd = win32gui.GetForegroundWindow()
    return win32gui.GetWindowText(hwnd)

def is_roblox_focused():
    title = get_foreground_window_title()
    return "roblox" in title.lower()

def is_roblox_running():
    for proc in psutil.process_iter(['name']):
        if proc.info['name'] and "roblox" in proc.info['name'].lower():
            return proc
    return None

def get_readable_key(key):
    special_keys = {
        keyboard.Key.ctrl: "Ctrl",
        keyboard.Key.ctrl_l: "Ctrl",
        keyboard.Key.ctrl_r: "Ctrl",
        keyboard.Key.alt: "Alt",
        keyboard.Key.alt_l: "Alt",
        keyboard.Key.alt_r: "Alt",
        keyboard.Key.cmd: "Cmd",
        keyboard.Key.cmd_l: "Cmd",
        keyboard.Key.cmd_r: "Cmd",
        keyboard.Key.shift: "Shift",
        keyboard.Key.shift_l: "Shift",
        keyboard.Key.shift_r: "Shift",
        keyboard.Key.esc: "Escape",
        keyboard.Key.tab: "Tab",
        keyboard.Key.enter: "Enter",
        keyboard.Key.space: "Space",
        keyboard.Key.backspace: "Backspace",
        keyboard.Key.up: "Arrow Up",
        keyboard.Key.down: "Arrow Down",
        keyboard.Key.left: "Arrow Left",
        keyboard.Key.right: "Arrow Right",
        keyboard.Key.f1: "F1",
        keyboard.Key.f2: "F2",
        keyboard.Key.f3: "F3",
        keyboard.Key.f4: "F4",
        # add more if needed
    }

    if isinstance(key, keyboard.Key):
        return special_keys.get(key, str(key))
    elif hasattr(key, 'char') and key.char is not None:
        return key.char
    else:
        return str(key)

def get_readable_button(button):
    mapping = {
        mouse.Button.left: "Left Mouse Button",
        mouse.Button.right: "Right Mouse Button",
        mouse.Button.middle: "Middle Mouse Button"
    }
    return mapping.get(button, str(button))

def on_key_press(key):
    global last_activity_time
    if is_roblox_focused():
        readable = get_readable_key(key)
        print(f"User pressed key: {readable}. Resetting stopwatch to 0.00.")
        last_activity_time = time.time()

def on_click(x, y, button, pressed):
    global last_activity_time
    if pressed and is_roblox_focused():
        readable = get_readable_button(button)
        print(f"User clicked: {readable}. Resetting stopwatch to 0.00.")
        last_activity_time = time.time()

keyboard_listener = keyboard.Listener(on_press=on_key_press)
keyboard_listener.start()

mouse_listener = mouse.Listener(on_click=on_click)
mouse_listener.start()

try:
    while True:
        time.sleep(1)
        roblox_proc = is_roblox_running()
        current_time = time.time()

        idle_duration = current_time - last_activity_time
        print(f"Idle time since last Roblox activity: {idle_duration:.2f} seconds")

        if roblox_proc:
            if idle_duration >= idle_threshold:
                print("Idle threshold reached. Killing Roblox.")
                roblox_proc.kill()
                break
            else:
                if not is_roblox_focused():
                    print("Roblox is running, but not focused.")
        else:
            print("Roblox is not running.")
            last_activity_time = current_time
except KeyboardInterrupt:
    print("\nScript interrupted by user. Exiting gracefully...")
