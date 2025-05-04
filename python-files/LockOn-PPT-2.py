import psutil
import time
import subprocess
import os
import platform

def is_powerpoint_running():
    for process in psutil.process_iter(['name']):
        if process.info['name'].lower() == 'powerpnt.exe':
            return process.pid
    return None

def get_window_title(pid):
    try:
        if platform.system() == "Windows":
            import win32gui
            def callback(hwnd, titles):
                if win32gui.IsWindowVisible(hwnd) and win32gui.GetWindowThreadProcessId(hwnd)[1] == pid:
                    text = win32gui.GetWindowText(hwnd)
                    if "Slide Show" in text or "Слайдшоу" in text:
                        titles.append(text)
                return True
            titles = []
            win32gui.EnumWindows(callback, titles)
            return any(titles)
        return False
    except ImportError:
        print("Библиотеката 'pywin32' не е инсталирана. Работи само на Windows.")
        return False

def lock_account():
    if platform.system() == "Windows":
        subprocess.run(["rundll32.exe", "user32.dll,LockWorkStation"])
        print("Акаунтът беше заключен.")
    else:
        print("Заключването на акаунт се поддържа само на Windows.")

if __name__ == "__main__":
    timeout_seconds = 20 * 60  # 20 минути
    check_interval_seconds = 60  # 60 секунди
    slide_show_started = False
    start_time = None

    print("Скриптът следи за PowerPoint в режим на слайдшоу...")

    while True:
        powerpoint_pid = is_powerpoint_running()

        if powerpoint_pid:
            if get_window_title(powerpoint_pid):
                if not slide_show_started:
                    print("Режим на слайдшоу стартиран.")
                    slide_show_started = True
                    start_time = time.time()
                else:
                    elapsed_time = time.time() - start_time
                    if elapsed_time >= timeout_seconds:
                        print(f"Изминаха {timeout_seconds // 60} минути в режим на слайдшоу.")
                        lock_account()
                        slide_show_started = False
                        start_time = None
            else:
                if slide_show_started:
                    print("Режим на слайдшоу завършен.")
                    slide_show_started = False
                    start_time = None
        else:
            slide_show_started = False
            start_time = None

        time.sleep(check_interval_seconds)