import tkinter as tk
from tkinter import messagebox
import pygame
import ctypes
import os
import sys
from PIL import Image

# Resource path helper (for PyInstaller onefile builds)
def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS  # if running as bundled exe
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

def play_sound():
    pygame.mixer.init()
    pygame.mixer.music.load(resource_path("mail_jingle_alt.ogg"))
    pygame.mixer.music.play()

def set_wallpaper(image_path):
    bmp_path = os.path.splitext(image_path)[0] + '.bmp'
    img = Image.open(image_path)
    bmp_path_full = os.path.join(os.path.dirname(image_path), os.path.basename(bmp_path))
    img.save(bmp_path_full, "BMP")

    abs_path = os.path.abspath(bmp_path_full)
    ctypes.windll.user32.SystemParametersInfoW(20, 0, abs_path, 3)

def lock_pc():
    ctypes.windll.user32.LockWorkStation()

def on_yes(win):
    messagebox.showinfo("Passed", "Congrats! You passed the test. Don't be dumb.")

def on_no(win):
    play_sound()

    def after_sound():
        if pygame.mixer.music.get_busy():
            win.after(100, after_sound)
        else:
            set_wallpaper(resource_path("uh oh.jpg"))
            messagebox.showwarning(
                "Too Late",
                "Oh, ok. I guess Russia won't mind taking this other guy's info!\n"
                "By the way, we're selling the information associated with this IP. And locking this PC. And the sound means it was sent."
            )
            win.destroy()
            root.after(7000, lock_pc)  # 7-second delay before locking

    after_sound()

def on_closing():
    messagebox.showwarning("Nice Try", "Nuh-uh! You're not getting away THAT easy!")
    root.after(100, show_window)

def show_window():
    global root
    root = tk.Tk()
    root.title("IP Confirmation")

    label = tk.Label(root, text="Your IP address is: 134.49.44.115, correct?")
    label.pack(padx=20, pady=10)

    btn_frame = tk.Frame(root)
    btn_frame.pack(pady=10)

    yes_btn = tk.Button(btn_frame, text="Yes", command=lambda: on_yes(root), width=10)
    yes_btn.pack(side="left", padx=5)

    no_btn = tk.Button(btn_frame, text="No", command=lambda: on_no(root), width=10)
    no_btn.pack(side="right", padx=5)

    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.mainloop()

show_window()
