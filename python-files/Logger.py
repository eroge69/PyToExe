import os
import time
import datetime
import ctypes
import tkinter as tk
from tkinter import filedialog
import threading

# === Пути для логов и конфига ===
CONFIG_DIR = os.path.expanduser("~\\AppData\\Local\\FocusLogger")  # Отдельная папка для конфига
CONFIG_FILE = os.path.join(CONFIG_DIR, "config.txt")

# === Создание папки для конфига, если её нет ===
os.makedirs(CONFIG_DIR, exist_ok=True)

def load_config():
    """Загружает путь для логов из config.txt"""
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            path = f.read().strip()
            if os.path.isdir(path):
                return path
    return os.path.expanduser("~/Documents")

def save_config(path):
    """Сохраняет выбранный путь в config.txt"""
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        f.write(path)

def get_active_window_title():
    """Получает заголовок активного окна"""
    hwnd = ctypes.windll.user32.GetForegroundWindow()
    buffer = ctypes.create_unicode_buffer(512)
    ctypes.windll.user32.GetWindowTextW(hwnd, buffer, 512)
    return buffer.value if buffer.value else "Рабочий стол"

def select_folder():
    """Открывает диалог для выбора папки и сохраняет её в config.txt"""
    global log_folder
    folder = filedialog.askdirectory()
    if folder:
        log_folder = folder
        save_config(log_folder)  # ✅ Сохраняем путь
        settings_label.config(text=f"Папка логов: {log_folder}")

def start_logging():
    """Запускает логгер, записывающий активные окна"""
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    log_file = os.path.join(log_folder, f"focus-log-{today}.txt")
    toggle_button.config(text="Остановить", fg="red")

    last_window = ""
    while logging_active:
        active_title = get_active_window_title()
        if active_title != last_window:
            timestamp = datetime.datetime.now().strftime("%H:%M:%S")
            with open(log_file, "a", encoding="utf-8") as f:
                f.write(f"{timestamp} - Фокус: {active_title}\n")
            last_window = active_title
        time.sleep(0.5)

def toggle_logging():
    """Переключает логирование (Вкл/Выкл)"""
    global logging_active
    if logging_active:
        logging_active = False
        toggle_button.config(text="Запустить", fg="green")
    else:
        logging_active = True
        threading.Thread(target=start_logging, daemon=True).start()

def open_settings():
    """Открывает окно настроек"""
    settings_window = tk.Toplevel(root)
    settings_window.title("Настройки")
    settings_window.geometry("300x150")

    global settings_label
    settings_label = tk.Label(settings_window, text=f"Папка логов: {log_folder}", wraplength=250)
    settings_label.pack(pady=10)

    btn_select = tk.Button(settings_window, text="Выбрать папку", command=select_folder)
    btn_select.pack(pady=5)

# === Запуск программы ===
root = tk.Tk()
root.title("Логгер фокуса")
root.geometry("300x150")

log_folder = load_config()  # ✅ Загружаем путь из `config.txt`
logging_active = False

btn_settings = tk.Button(root, text="Настройки", command=open_settings)
btn_settings.pack(pady=10)

toggle_button = tk.Button(root, text="Запустить", fg="green", command=toggle_logging)
toggle_button.pack(pady=10)

root.mainloop()
