import time
import threading
from pynput.keyboard import Controller

# Ожидание нажатия Enter перед запуском программы
input("Нажмите Enter, чтобы начать...")

# Пауза перед запуском
time.sleep(2)

keyboard = Controller()

def press_key_sequence(key, times, interval, repeat_interval):
    while True:
        for _ in range(times):
            keyboard.press(key)
            time.sleep(0.05)  # Короткая задержка для регистрации нажатия
            keyboard.release(key)
            time.sleep(interval)
        time.sleep(repeat_interval - (times * interval))

def press_2():
    press_key_sequence("2", 3, 1.2, 30)

def press_7():
    press_key_sequence("7", 1, 0, 5.5)

# Запускаем потоки для одновременной работы
threading.Thread(target=press_2, daemon=True).start()
threading.Thread(target=press_7, daemon=True).start()

# Бесконечный цикл для работы потоков
while True:
    time.sleep(1)
