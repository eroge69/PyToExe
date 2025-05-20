import tkinter as tk
from tkinter import ttk
import pyautogui
import keyboard
import cv2
import numpy as np

# Настройка pyautogui
pyautogui.FAILSAFE = True
pyautogui.PAUSE = 0.1

# Переменная состояния окна
window_visible = False

def toggle_window():
    """Переключение видимости окна по клавише Insert."""
    global window_visible
    if not window_visible:
        root.deiconify()
        root.attributes('-topmost', True)
        window_visible = True
    else:
        root.withdraw()
        window_visible = False

def find_button_on_screen(button_image):
    """Поиск кнопки на экране с помощью OpenCV."""
    try:
        screenshot = pyautogui.screenshot()
        screen_gray = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2GRAY)
        button_img = cv2.imread(button_image, cv2.IMREAD_GRAYSCALE)
        if button_img is None:
            raise FileNotFoundError(f"Изображение {button_image} не найдено")

        screen_gray = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2GRAY)
        result = cv2.matchTemplate(screen_gray, button_img, cv2.TM_CCOEFF_NORMED)
        _, max_val, _, max_loc = cv2.minMaxLoc(result)

        threshold = 0.9
        locations = []
        while max_val >= threshold:
            x, y = max_loc
            w, h = button_img.shape[::-1]
            locations.append((x + w // 2, y + h // 2))

            mask = np.zeros_like(screen_gray)
            cv2.rectangle(mask, (x, y), (x + w, y + h), 255, -1)
            screen_gray &= ~mask
            result = cv2.matchTemplate(screen_gray, button_img, cv2.TM_CCOEFF_NORMED)
            _, max_val, _, max_loc = cv2.minMaxLoc(result)

        return locations
    except Exception as e:
        print(f"Ошибка в find_button_on_screen: {e}")
        return []

def press_key(key):
    """Нажатие и отпускание клавиши."""
    try:
        pyautogui.keyDown(key)
        pyautogui.sleep(1,5)  # Уменьшена задержка
        pyautogui.keyUp(key)
    except Exception as e:
        print(f"Ошибка в press_key: {e}")
        
def run_main_loop():
    """Основной цикл обработки с проверкой кнопок."""
    try:
        if enable_var.get():
            # Список всех 15 кнопок
            buttons_to_check = [
                'button1.png', 'button2.png', 'button3.png', 'button4.png', 'button5.png',
                'button6.png', 'button7.png', 'button8.png', 'button9.png', 'button10.png',
                'button11.png', 'button12.png', 'button13.png', 'button14.png', 'button15.png'
            ]
            # Словарь соответствия кнопок и клавиш
            key_to_press = {
                'button1.png': 'b', 'button2.png': 'd', 'button3.png': 'f', 'button4.png': 'h',
                'button5.png': 'q', 'button6.png': 'r', 'button7.png': 's', 'button8.png': 'v',
                'button9.png': 'w', 'button10.png': 'shift', 'button11.png': 'space',
                'button12.png': 'down', 'button13.png': 'left', 'button14.png': 'right',
                'button15.png': 'up'
            }

            for button in buttons_to_check:
                positions = find_button_on_screen(button)
                if positions:
                    print(f"Кнопка {button} найдена на позициях: {positions}")
                    if key := key_to_press.get(button):
                        press_key(key)

        # Проверка на выход по Esc
        if keyboard.is_pressed('esc'):
            root.quit()
            return

        root.after(1000, run_main_loop)
    except Exception as e:
        print(f"Ошибка в run_main_loop: {e}")
        root.after(1000, run_main_loop)

# Создание основного окна
root = tk.Tk()
root.title("Скрипт отслеживания")
root.geometry("300x150")
root.withdraw()  # Окно изначально скрыто

# Ползунок для включения/отключения
enable_var = tk.BooleanVar(value=False)
slider = ttk.Checkbutton(root, text="Включить скрипт", variable=enable_var)
slider.pack(pady=20)

# Метка состояния
status_label = ttk.Label(root, text="Скрипт выключен")
status_label.pack(pady=10)

def update_status():
    """Обновление метки состояния."""
    status_label.config(text="Скрипт включен" if enable_var.get() else "Скрипт выключен")
    root.after(100, update_status)

# Привязка клавиши Insert
keyboard.add_hotkey('insert', toggle_window)

# Запуск циклов
root.after(100, update_status)
root.after(1000, run_main_loop)

# Запуск главного цикла Tkinter
root.mainloop()