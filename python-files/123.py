import subprocess
import sys

# Функция для установки библиотек
def install(package):
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])

# Проверка и установка необходимых библиотек
try:
    import mss
except ImportError:
    print("Библиотека 'mss' не найдена. Устанавливаю...")
    install('mss')
    import mss

try:
    import numpy as np
except ImportError:
    print("Библиотека 'numpy' не найдена. Устанавливаю...")
    install('numpy')
    import numpy as np

try:
    import pyautogui
except ImportError:
    print("Библиотека 'pyautogui' не найдена. Устанавливаю...")
    install('pyautogui')
    import pyautogui

try:
    import keyboard
except ImportError:
    print("Библиотека 'keyboard' не найдена. Устанавливаю...")
    install('keyboard')
    import keyboard

import time
import threading

# Параметры мониторинга
green_color = np.array([35, 168, 83])  # Зеленый цвет (RGB)
white_color = np.array([255, 255, 255])  # Белый цвет (RGB)
region = {"top": 584, "left": 814, "width": 150, "height": 320}  # Область экрана
hotkey = "space"  # Клавиша при пересечении
extra_key = "e"  # Клавиша для периодического нажатия
tolerance = 53  # Допуск по цвету
check_offset = 5  # Количество пикселей вверх для проверки белого
pre_press_delay = 0.05  # Задержка перед нажатием (сек.)
extra_key_delay = 11  # Интервал нажатия 'e' (сек.)
start_stop_key = "F8"  # Клавиша для запуска/остановки
running = False  # Флаг работы скрипта

# Функция для быстрого сравнения цветов
def is_color_match(pixel, target, tolerance):
    return np.all(np.abs(pixel - target) <= tolerance)

def check_screen():
    """Сканирует область, ищет самый верхний зеленый цвет и проверяет белый выше."""
    with mss.mss() as sct:
        screenshot = sct.grab(region)
        img = np.array(screenshot)[:, :, :3]  # Преобразуем в массив RGB

        # Создаем карту зеленых пикселей
        green_mask = np.all(np.abs(img - green_color) <= tolerance, axis=-1)

        # Находим самый верхний зеленый пиксель в каждом столбце
        green_positions = np.argmax(green_mask, axis=0)  # Первое вхождение True по оси Y

        # Проверяем белый цвет выше найденного зеленого
        for x in range(img.shape[1]):  # Проходим по столбцам
            y = green_positions[x]  # Верхний зеленый пиксель в этом столбце
            if y > 0 and y - check_offset >= 0:  # Проверяем, есть ли место для поиска выше
                if is_color_match(img[y - check_offset, x], white_color, tolerance):
                    screen_x = region["left"] + x
                    screen_y = region["top"] + y
                    print(f"⚠ Белый цвет найден над зелёным ({screen_x}, {screen_y - 5})! "
                          f"Жду {pre_press_delay} сек. перед нажатием {hotkey}")

                    time.sleep(pre_press_delay)  # ⏳ Ожидание перед нажатием
                    pyautogui.press(hotkey)  # Нажатие клавиши
                    return True
    return False

def monitor():
    """Основной цикл мониторинга экрана."""
    global running
    while running:
        check_screen()
        time.sleep(0.01)  # Очень быстрая проверка (100 раз в секунду)

def press_extra_key():
    """Функция для нажатия 'E' каждые 11 секунд."""
    global running
    while running:
        print(f"🔄 Нажатие '{extra_key}' (каждые {extra_key_delay} сек.)")
        pyautogui.press(extra_key)
        time.sleep(extra_key_delay)

def toggle_running():
    """Функция для включения/выключения мониторинга."""
    global running
    if running:
        print("⛔ Мониторинг остановлен")
        running = False
    else:
        print("✅ Мониторинг запущен")
        running = True
        threading.Thread(target=monitor, daemon=True).start()
        threading.Thread(target=press_extra_key, daemon=True).start()

# Назначаем клавишу для запуска/остановки
keyboard.add_hotkey(start_stop_key, toggle_running)

print(f"🔴 Нажмите {start_stop_key} для запуска/остановки скрипта.")
keyboard.wait()  # Ожидаем нажатий клавиш