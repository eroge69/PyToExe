from pystray import Icon, Menu, MenuItem
from PIL import Image, ImageDraw
import pyautogui
import keyboard
import threading
import time
import tkinter as tk
from tkinter import simpledialog

# === Default Settings ===
macro_keys = ['2', '5', '6']
delay_between_keys = 0.05
delay_after_cycle = 0.1
macro_active = False
icon = None

# === Tray Icon Image ===
def create_image():
    image = Image.new('RGB', (64, 64), color=(30, 30, 30))
    draw = ImageDraw.Draw(image)
    draw.rectangle((20, 20, 44, 44), fill=(200, 200, 200))
    return image

# === Macro Loop ===
def macro_loop():
    global macro_active
    while True:
        if macro_active:
            for key in macro_keys:
                pyautogui.press(key)
                time.sleep(delay_between_keys)
            pyautogui.click()
            time.sleep(delay_after_cycle)

# === Side Mouse Button Toggle ===
def side_button_listener():
    global macro_active
    while True:
        if keyboard.is_pressed("xbutton1"):
            macro_active = not macro_active
            print("Macro Active:", macro_active)
            time.sleep(0.3)

# === GUI to Change Settings ===
def open_settings():
    def save_and_close():
        nonlocal keys_entry, between_entry, after_entry, window
        global macro_keys, delay_between_keys, delay_after_cycle
        keys = keys_entry.get().split(',')
        macro_keys = [key.strip() for key in keys]
        delay_between_keys = float(between_entry.get())
        delay_after_cycle = float(after_entry.get())
        print("Updated keys:", macro_keys)
        print("Delays:", delay_between_keys, delay_after_cycle)
        window.destroy()

    window = tk.Tk()
    window.title("Macro Settings")
    window.geometry("300x200")
    window.attributes('-topmost', True)

    tk.Label(window, text="Macro Keys (comma-separated):").pack(pady=5)
    keys_entry = tk.Entry(window)
    keys_entry.insert(0, ','.join(macro_keys))
    keys_entry.pack()

    tk.Label(window, text="Delay Between Keys (sec):").pack(pady=5)
    between_entry = tk.Entry(window)
    between_entry.insert(0, str(delay_between_keys))
    between_entry.pack()

    tk.Label(window, text="Delay After Cycle (sec):").pack(pady=5)
    after_entry = tk.Entry(window)
    after_entry.insert(0, str(delay_after_cycle))
    after_entry.pack()

    tk.Button(window, text="Save", command=save_and_close).pack(pady=10)
    window.mainloop()

# === Tray Menu Actions ===
def toggle_from_tray(icon, item):
    global macro_active
    macro_active = not macro_active

def exit_app(icon, item):
    icon.stop()

def setup_tray():
    global icon
    icon = Icon("Macro")
    icon.icon = create_image()
    icon.menu = Menu(
        MenuItem('Toggle Macro', toggle_from_tray),
        MenuItem('Settings', lambda icon, item: open_settings()),
        MenuItem('Exit', exit_app)
    )
    icon.run()

# === Main Entry Point ===
if __name__ == "__main__":
    # === Threads ===
    threading.Thread(target=macro_loop, daemon=True).start()
    threading.Thread(target=side_button_listener, daemon=True).start()
    setup_tray()