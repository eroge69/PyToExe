import tkinter as tk
from PIL import Image, ImageTk
import requests
import random
import threading
import time
import io
from playsound import playsound
import pystray
from pystray import MenuItem as item
import sys

# 🐾 Delay start between 2 to 4 hours (7200-14400 seconds)
time.sleep(random.randint(7200, 14400))

# 🐾 List of furry-friendly image URLs
furry_images = [
    "https://cdn.pixabay.com/photo/2017/02/20/18/03/cat-2083492_1280.jpg",
    "https://cdn.pixabay.com/photo/2016/11/29/05/08/animal-1867127_1280.jpg",
    "https://cdn.pixabay.com/photo/2016/02/19/10/00/animal-1209772_1280.jpg",
    "https://cdn.pixabay.com/photo/2015/11/03/09/03/cat-1022975_1280.jpg"
]

# 🐾 Path to your fun sound
sound_file = "meow.mp3"  # Make sure this file exists

def play_sound():
    try:
        playsound(sound_file)
    except Exception as e:
        print("Couldn't play sound:", e)

def fetch_image(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        image_data = io.BytesIO(response.content)
        pil_image = Image.open(image_data).resize((300, 200), Image.LANCZOS)
        return ImageTk.PhotoImage(pil_image)
    except Exception as e:
        print("Couldn't fetch image:", e)
        return None

def disable_close():
    pass

def move_window(window):
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    width, height = 300, 200
    x = random.randint(0, screen_width - width)
    y = random.randint(0, screen_height - height)
    window.geometry(f"{width}x{height}+{x}+{y}")
    window.after(1000, lambda: move_window(window))

def create_furry_window():
    win = tk.Toplevel()
    win.title("Learn Python!! OwO")
    win.overrideredirect(True)
    win.protocol("WM_DELETE_WINDOW", disable_close)

    image_url = random.choice(furry_images)
    bg_image = fetch_image(image_url)
    if bg_image:
        label_img = tk.Label(win, image=bg_image)
        label_img.image = bg_image
        label_img.place(x=0, y=0, relwidth=1, relheight=1)

    label = tk.Label(win, text="Learn Python!! OwO",
                     font=("Comic Sans MS", 16, "bold"),
                     fg="white", bg="black")
    label.pack(expand=True)

    move_window(win)
    play_sound()

def spawn_windows():
    while True:
        time.sleep(random.randint(900, 3600))  # 15 to 60 mins
        root.after(0, create_furry_window)

def on_exit(icon, item):
    icon.stop()
    root.quit()
    sys.exit()

def create_tray_icon():
    try:
        image = Image.new('RGB', (64, 64), color='black')
        icon = pystray.Icon("FurryApp", image, "Furry Python", menu=pystray.Menu(
            item('Exit', on_exit)
        ))
        icon.run()
    except Exception as e:
        print("Tray icon error:", e)

# 🐾 Main root window
root = tk.Tk()
root.title("Learn Python!! OwO")
root.overrideredirect(True)
root.protocol("WM_DELETE_WINDOW", disable_close)

main_image_url = random.choice(furry_images)
main_bg = fetch_image(main_image_url)
if main_bg:
    bg_label = tk.Label(root, image=main_bg)
    bg_label.image = main_bg
    bg_label.place(x=0, y=0, relwidth=1, relheight=1)

main_label = tk.Label(root, text="Learn Python!! OwO",
                      font=("Comic Sans MS", 16, "bold"),
                      fg="white", bg="black")
main_label.pack(expand=True)

move_window(root)
play_sound()

threading.Thread(target=spawn_windows, daemon=True).start()
threading.Thread(target=create_tray_icon, daemon=True).start()

root.mainloop()