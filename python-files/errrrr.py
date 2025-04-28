import tkinter as tk
import random
import subprocess
import platform
import sys

def create_shaking_window():
    """Создает трясущееся окно, которое нельзя закрыть или свернуть."""
    window = tk.Tk()
    window.title("Трясущееся окно")

    # Отключаем кнопки свернуть и закрыть
    window.overrideredirect(True)  # Убирает заголовок окна, включая кнопки

    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()

    window_width = 400
    window_height = 400

    # Случайная начальная позиция
    x = random.randint(0, screen_width - window_width)
    y = random.randint(0, screen_height - window_height)

    window.geometry(f"{window_width}x{window_height}+{x}+{y}")

    def shake():
        """Функция для создания эффекта тряски."""
        dx = random.randint(-500, 500)
        dy = random.randint(-500, 500)

        current_x = window.winfo_x()
        current_y = window.winfo_y()

        # Проверка, чтобы окно не выходило за пределы экрана
        new_x = max(0, min(current_x + dx, screen_width - window_width))
        new_y = max(0, min(current_y + dy, screen_height - window_height))

        window.geometry(f"+{new_x}+{new_y}")
        window.after(200, shake)

    shake()
    return window

# Создаем 50 трясущихся окон
windows = []
for _ in range(200):
    windows.append(create_shaking_window())

# Скрываем консоль (только для Windows)
if platform.system() == "Windows":
    import ctypes
    ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 0) # 0 - SW_HIDE

# Запускаем главный цикл tkinter
tk.mainloop()