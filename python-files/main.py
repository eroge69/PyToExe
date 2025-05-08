from tkinter import ttk
from PIL import Image, ImageTk
from tkinter import messagebox
import os
import subprocess
import tkinter as tk
import time
import threading
from urllib.request import urlopen
from pymem import Pymem
from pymem.process import inject_dll_from_path
import psutil
import json
import requests
from datetime import datetime, timedelta

# Параметры
GITHUB_RAW_URL = "https://raw.githubusercontent.com/HappyProgs/hahatipolol/main/keys.json"
GITHUB_DLL_URL = "https://github.com/HappyProgs/Ice_ModCs2/releases/download/HappyProg/Ice_Mod_Cs2.dll"
DLL_PATH = r"C:\temp\Ice_Mod_Cs2.dll"
PROCESS_NAME = "cs2.exe"
CONFIG_FILE = "config.json"

# Функции

def load_key():
    try:
        with open(CONFIG_FILE, "r") as f:
            config = json.load(f)
            return config.get("key", "")
    except FileNotFoundError:
        return ""
    except json.JSONDecodeError:
        return ""

def save_key(key):
    try:
        with open(CONFIG_FILE, "w") as f:
            json.dump({"key": key}, f)
            return True
    except Exception as e:
        messagebox.showerror("Error", f"Failed to save key: {e}")
        return False

def validate_key(key):
    try:
        response = requests.get(GITHUB_RAW_URL)
        response.raise_for_status()
        keys_data = response.json()

        if key in keys_data:
            expiry_date_str = keys_data[key]
            # Добавляем проверку типа
            if isinstance(expiry_date_str, str):
                expiry_date = datetime.fromisoformat(expiry_date_str)
                if datetime.now() < expiry_date:
                    return True
                else:
                    return False
            else:
                messagebox.showerror("Error", "Invalid date format in keys file: must be a string.")
                return False
        else:
            return False
    except requests.exceptions.RequestException as e:
        messagebox.showerror("Error", f"Failed to fetch keys from GitHub: {e}")
        return False
    except json.JSONDecodeError:
        messagebox.showerror("Error", "Invalid JSON format in keys file.")
        return False
    except ValueError as e:
        messagebox.showerror("Error", f"Invalid date format: {e}")
        return False

def manage_dll():
    try:
        os.makedirs(os.path.dirname(DLL_PATH), exist_ok=True)
        with urlopen(GITHUB_DLL_URL) as response, open(DLL_PATH, "wb") as file:
            file.write(response.read())

        open_process = Pymems(PROCESS_NAME)
        inject_dll_from_path(open_process.process_handle, DLL_PATH)

        threading.Thread(target=lambda: wait_for_process_close(PROCESS_NAME, DLL_PATH), daemon=True).start()
        messagebox.showinfo("Success", "DLL injected successfully!")
        return True
    except Exception as e:
        messagebox.showerror("Error", f"Failed to inject DLL: {e}")
        return False

def wait_for_process_close(process_name, file_path):
    while any(proc.name().lower() == process_name.lower() for proc in psutil.process_iter()):
        time.sleep(0.1)
    try:
        os.remove(file_path)
    except Exception:
        pass

# Окна

def show_injection_window():
    injection_window = tk.Toplevel(root)
    injection_window.geometry("309x290")
    injection_window.title("Ice_Mod Cs2 - Injection")
    injection_window.configure(bg="#181818")
    injection_window.wm_title("Ice_Mod Cs2 - Injection")

    injection_window.iconbitmap("icons/xz.ico")
    injection_window.overrideredirect(False)
    injection_window.resizable(False, False)
    injection_window.attributes("-alpha", 0.9)

    style = ttk.Style()
    style.configure("TFrame", background="#181818")
    style.configure("TLabel", background="#181818", foreground="white", font=("Arial", 12))
    style.configure("Game.TFrame", background="#252525", relief="flat")
    style.configure("TButton", font=("Arial", 12), background="gray11", foreground="gray11")
    style.map("TButton", background=[("active", "gray11")])
    style = ttk.Style()
    style.configure("Custom.TRadiobutton", background="#252525", foreground="#252525", font=("Arial", 12))
    style.map("Custom.TRadiobutton", background=[("active", "#252525")])

    frame = ttk.Frame(injection_window, style="TFrame")
    frame.pack(expand=True, fill="both", padx=10, pady=10)

    title_label = ttk.Label(frame, text="Ice_Mod Cs2", font=("Arial", 16, "bold"))
    title_label.pack(pady=(10, 2))

    subtitle_label = ttk.Label(frame, text="Injection Panel", font=("Arial", 10))
    subtitle_label.pack(pady=(0, 10))

    game_var = tk.StringVar(value="")

    def update_selection():
        if game_var.get():
            inject_button.config(state=tk.NORMAL)

    def add_game(parent, icon_path, name, value):
        game_frame = ttk.Frame(parent, style="Game.TFrame")
        game_frame.pack(fill="x", pady=5)

        img = Image.open(icon_path).resize((25, 25))
        icon = ImageTk.PhotoImage(img)

        icon_label = tk.Label(game_frame, image=icon, bg="#252525")
        icon_label.image = icon
        icon_label.pack(side="left", padx=10, pady=10)

        text_frame = ttk.Frame(game_frame, style="Game.TFrame")
        text_frame.pack(side="left", fill="x", expand=True)

        name_label = ttk.Label(text_frame, text=name, font=("Arial", 12, "bold"))
        name_label.pack(anchor="w")

        radio_btn = ttk.Radiobutton(game_frame, variable=game_var, value=value, command=update_selection, style="Custom.TRadiobutton")
        radio_btn.pack(side="right", padx=10)

    add_game(frame, "icons/cs2.ico", "Counter-Strike 2", "CS2")

    inject_button = ttk.Button(frame, text="Inject", command=manage_dll, style="TButton", state=tk.DISABLED)
    inject_button.pack(pady=25, anchor="s")

def show_key_window():
    key_window = tk.Toplevel(root)
    key_window.geometry("309x200")
    key_window.title("Ice_Mod Cs2 - Key Activation")
    key_window.configure(bg="#181818")
    key_window.wm_title("Ice_Mod Cs2 - Key Activation")

    key_window.iconbitmap("icons/xz.ico")
    key_window.overrideredirect(False)
    key_window.resizable(False, False)
    key_window.attributes("-alpha", 0.9)

    style = ttk.Style()
    style.configure("TFrame", background="#181818")
    style.configure("TLabel", background="#181818", foreground="white", font=("Arial", 12))
    style.configure("TButton", font=("Arial", 12), background="gray11", foreground="gray11")
    style.map("TButton", background=[("active", "gray11")])

    frame = ttk.Frame(key_window, style="TFrame")
    frame.pack(expand=True, fill="both", padx=10, pady=10)

    title_label = ttk.Label(frame, text="Ice_Mod Cs2 Loader", font=("Arial", 16, "bold"))
    title_label.pack(pady=(10, 2))

    key_label = ttk.Label(frame, text="Enter Key:", font=("Arial", 12))
    key_label.pack()

    key_entry = ttk.Entry(frame, width=30, font=("Arial", 12))
    key_entry.pack(pady=5)
    key_entry.insert(0, load_key())

    def activate_key():
        key = key_entry.get()
        if validate_key(key):
            if save_key(key):
                messagebox.showinfo("Success", "Key activated successfully!")
                key_window.destroy()
                show_injection_window()
            else:
                messagebox.showerror("Error", "Failed to save key.")
        else:
            messagebox.showerror("Error", "Invalid or expired key.")

    activate_button = ttk.Button(frame, text="Login", command=activate_key, style="TButton")
    activate_button.pack(pady=15)

# Главное окно

root = tk.Tk()
root.withdraw()
show_key_window()
root.mainloop()
