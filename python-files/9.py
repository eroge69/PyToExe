import os
import time
import sys
import ctypes
import win32api
import win32con
import win32gui
from threading import Thread


# Проверяем, запущена ли программа с флешки
def is_running_from_usb():
    drive = os.path.abspath(sys.argv[0])[0:3]
    return win32api.GetDriveType(drive) == win32con.DRIVE_REMOVABLE


# Функция для ввода пароля
def type_password():
    time.sleep(1)  # Небольшая задержка перед вводом

    # Имитация нажатия клавиш
    password = "Zahar555@@"
    for char in password:
        # Определяем, нужно ли нажимать shift
        shift_needed = char.isupper() or char in '@'

        if shift_needed:
            ctypes.windll.user32.keybd_event(0x10, 0, 0, 0)  # Нажать Shift

        # Нажать клавишу
        vk_code = win32api.VkKeyScan(char)
        win32api.keybd_event(vk_code & 0xff, 0, 0, 0)
        win32api.keybd_event(vk_code & 0xff, 0, win32con.KEYEVENTF_KEYUP, 0)

        if shift_needed:
            ctypes.windll.user32.keybd_event(0x10, 0, win32con.KEYEVENTF_KEYUP, 0)  # Отпустить Shift


# Основная функция
def main():
    if not is_running_from_usb():
        print("Эта программа должна запускаться с USB-флешки.")
        return

    print("Программа готова вводить пароль при подключении флешки...")

    # Бесконечный цикл для проверки подключения флешки
    while True:
        drives = [chr(x) + ":" for x in range(65, 91) if os.path.exists(chr(x) + ":")]
        removable_drives = [d for d in drives if win32api.GetDriveType(d) == win32con.DRIVE_REMOVABLE]

        if len(removable_drives) > 1 or (
                len(removable_drives) == 1 and removable_drives[0] != os.path.abspath(sys.argv[0])[0:2]):
            # Если найдена другая флешка (не та, с которой запущена программа)
            active_window = win32gui.GetForegroundWindow()
            if active_window != 0:  # Если есть активное окно
                Thread(target=type_password).start()

        time.sleep(1)  # Проверка каждую секунду


if __name__ == "__main__":
    main()