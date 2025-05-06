from customtkinter import *
from PIL import Image
import os
import toml
import asyncio
from telethon import TelegramClient, functions
from telethon.tl.functions.messages import ReportRequest
from telethon.tl.types import *
from threading import Thread
import time
from tkinter import messagebox
import threading
import logging
from concurrent.futures import ThreadPoolExecutor

# --- Конфигурация ---
class Config:
    def __init__(self):
        with open("config.toml") as file:
            self.data = toml.load(file)
        
        self.api_id = self.data["authorization"]["api_id"]
        self.api_hash = self.data["authorization"]["api_hash"]
        self.max_workers = self.data.get("settings", {}).get("max_workers", 5)
        self.default_delay = self.data.get("settings", {}).get("default_delay", 5)
        
config = Config()

# --- Логирование ---
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('report_log.txt'),
        logging.StreamHandler()
    ]
)

# --- Улучшенная система жалоб ---
class AdvancedReporter:
    REASON_MAP = {
        1: InputReportReasonSpam(),
        2: InputReportReasonViolence(),
        3: InputReportReasonPornography(),
        4: InputReportReasonChildAbuse(),
        5: InputReportReasonCopyright(),
        6: InputReportReasonGeoIrrelevant(),
        7: InputReportReasonFake(),
        8: InputReportReasonOther()
    }

    def __init__(self):
        self.active_tasks = 0
        self.success_count = 0
        self.fail_count = 0
        self.is_running = False
        self.executor = ThreadPoolExecutor(max_workers=config.max_workers)
        self.valid_sessions = []
        self.session_check_complete = False

    async def validate_sessions(self):
        """Проверка и загрузка рабочих сессий"""
        self.valid_sessions = []
        session_files = [f for f in os.listdir("tgaccs") if f.endswith('.session')]
        
        if not session_files:
            logging.warning("Не найдено файлов сессий в папке tgaccs")
            return False

        for session_file in session_files:
            session_path = os.path.join("tgaccs", session_file)
            try:
                async with TelegramClient(session_path, config.api_id, config.api_hash) as client:
                    if await client.is_user_authorized():
                        self.valid_sessions.append(session_file)
                        logging.info(f"✅ Сессия {session_file} готова")
                    else:
                        logging.warning(f"❌ Сессия {session_file} не авторизована")
            except Exception as e:
                logging.error(f"⚠️ Ошибка проверки сессии {session_file}: {str(e)}")
        
        logging.info(f"🔍 Итог: {len(self.valid_sessions)} рабочих сессий из {len(session_files)}")
        self.session_check_complete = True
        return len(self.valid_sessions) > 0

    async def send_single_report(self, client, chat_entity, message_id, reason, comment=""):
        """Отправка одной жалобы"""
        try:
            await client(ReportRequest(
                peer=chat_entity,
                id=[message_id],
                reason=reason,
                message=comment
            ))
            return True
        except Exception as e:
            logging.error(f"Ошибка в сессии {client.session.filename}: {str(e)}")
            return False
        finally:
            self.active_tasks -= 1

    async def process_account(self, session_file, chat_entity, message_id, reason, comment, delay):
        """Обработка одного аккаунта"""
        session_path = os.path.join("tgaccs", session_file)
        try:
            async with TelegramClient(session_path, config.api_id, config.api_hash) as client:
                # Двойная проверка авторизации
                if not await client.is_user_authorized():
                    logging.warning(f"🚫 Сессия {session_file} потеряла авторизацию")
                    return

                result = await self.send_single_report(client, chat_entity, message_id, reason, comment)
                if result:
                    self.success_count += 1
                    logging.info(f"📨 Успешная жалоба через {session_file}")
                else:
                    self.fail_count += 1

                if delay > 0:
                    await asyncio.sleep(delay)

        except Exception as e:
            logging.error(f"💥 Критическая ошибка в сессии {session_file}: {str(e)}")
            self.fail_count += 1

    async def start_mass_report(self, message_link, reason_num, comment="", delay=5):
        """Запуск массовой отправки жалоб"""
        if self.is_running:
            logging.warning("Отправка уже выполняется")
            return

        if not self.session_check_complete:
            if not await self.validate_sessions():
                logging.error("Нет рабочих сессий для отправки")
                return

        self.is_running = True
        self.success_count = 0
        self.fail_count = 0
        
        try:
            # Парсинг ссылки
            parts = message_link.strip().split('/')
            if len(parts) < 5:
                raise ValueError("Неверный формат ссылки")

            chat_username = parts[-2]
            message_id = int(parts[-1])

            # Получаем entity чата через первую рабочую сессию
            async with TelegramClient(os.path.join("tgaccs", self.valid_sessions[0]), 
                                   config.api_id, config.api_hash) as temp_client:
                chat_entity = await temp_client.get_entity(chat_username)

            reason = self.REASON_MAP.get(reason_num, InputReportReasonOther())
            
            # Запуск задач только для рабочих сессий
            tasks = []
            for session_file in self.valid_sessions:
                if not self.is_running:
                    break
                    
                self.active_tasks += 1
                task = asyncio.create_task(
                    self.process_account(session_file, chat_entity, message_id, reason, comment, delay)
                )
                tasks.append(task)

            await asyncio.gather(*tasks)

        except Exception as e:
            logging.error(f"Ошибка запуска: {str(e)}")
        finally:
            self.is_running = False
            logging.info(f"🏁 Завершено. Успешно: {self.success_count}, Ошибки: {self.fail_count}")

    def stop_mass_report(self):
        """Остановка отправки"""
        self.is_running = False
        logging.info("🛑 Остановка отправки...")

# --- GUI ---
class ReportApp(CTk):
    def __init__(self):
        super().__init__()
        self.reporter = AdvancedReporter()
        self.setup_ui()
        self.check_sessions_on_startup()
        
    def setup_ui(self):
        """Настройка интерфейса"""
        self.title("Advanced Telegram Reporter v2.0")
        self.geometry("1100x750")
        set_appearance_mode("dark")
        set_default_color_theme("dark-blue")

        # Основные фреймы
        self.main_frame = CTkFrame(self)
        self.main_frame.pack(fill=BOTH, expand=True, padx=10, pady=10)

        # Левая панель - управление
        self.control_frame = CTkFrame(self.main_frame, width=650)
        self.control_frame.pack(side=LEFT, fill=BOTH, expand=True, padx=5, pady=5)

        # Правая панель - информация
        self.info_frame = CTkFrame(self.main_frame, width=400)
        self.info_frame.pack(side=RIGHT, fill=BOTH, padx=5, pady=5)

        # Элементы управления
        self.setup_controls()
        
        # Элементы информации
        self.setup_info_panel()

    def setup_controls(self):
        """Настройка элементов управления"""
        # Заголовок
        CTkLabel(self.control_frame, text="Массовый репортинг", font=("Arial", 24, "bold")).pack(pady=15)

        # Поле для ссылки
        self.link_entry = CTkEntry(
            self.control_frame, 
            width=600,
            placeholder_text="Ссылка на сообщение (например: t.me/username/123)"
        )
        self.link_entry.pack(pady=10)

        # Причины жалоб
        CTkLabel(self.control_frame, text="Выберите причину жалобы:", font=("Arial", 14)).pack(pady=5)
        
        self.reason_var = IntVar(value=1)
        reasons_frame = CTkFrame(self.control_frame)
        reasons_frame.pack(pady=5)
        
        reasons = [
            ("1. Спам", 1),
            ("2. Насилие", 2),
            ("3. Порнография", 3),
            ("4. Детский контент", 4),
            ("5. Авторские права", 5),
            ("6. Несоответствие гео", 6),
            ("7. Фейк", 7),
            ("8. Другое", 8)
        ]
        
        for i, (text, value) in enumerate(reasons):
            if i % 2 == 0:
                frame = CTkFrame(reasons_frame)
                frame.pack(anchor="w", padx=10, pady=2)
            CTkRadioButton(frame, text=text, variable=self.reason_var, value=value).pack(side=LEFT, padx=5)

        # Комментарий
        CTkLabel(self.control_frame, text="Комментарий к жалобе:", font=("Arial", 14)).pack(pady=5)
        self.comment_entry = CTkTextbox(self.control_frame, width=600, height=120)
        self.comment_entry.pack(pady=5)

        # Настройки
        settings_frame = CTkFrame(self.control_frame)
        settings_frame.pack(pady=10)
        
        CTkLabel(settings_frame, text="Задержка (сек):").pack(side=LEFT, padx=5)
        self.delay_entry = CTkEntry(settings_frame, width=80)
        self.delay_entry.insert(0, str(config.default_delay))
        self.delay_entry.pack(side=LEFT, padx=5)

        # Кнопки
        btn_frame = CTkFrame(self.control_frame)
        btn_frame.pack(pady=15)
        
        self.start_btn = CTkButton(
            btn_frame, 
            text="🚀 Начать отправку", 
            font=("Arial", 14, "bold"),
            width=200,
            height=40,
            command=self.start_reporting
        )
        self.start_btn.pack(side=LEFT, padx=10)

        self.stop_btn = CTkButton(
            btn_frame, 
            text="🛑 Остановить", 
            font=("Arial", 14),
            fg_color="#d9534f", 
            hover_color="#c9302c",
            width=200,
            height=40,
            command=self.stop_reporting
        )
        self.stop_btn.pack(side=LEFT, padx=10)

        # Кнопка проверки сессий
        self.check_btn = CTkButton(
            self.control_frame,
            text="🔍 Проверить сессии",
            command=self.check_sessions_manual
        )
        self.check_btn.pack(pady=5)

    def setup_info_panel(self):
        """Настройка информационной панели"""
        # Статистика
        CTkLabel(self.info_frame, text="📊 Статистика", font=("Arial", 18, "bold")).pack(pady=10)
        
        stats_frame = CTkFrame(self.info_frame)
        stats_frame.pack(fill=X, padx=10, pady=5)
        
        self.session_label = CTkLabel(stats_frame, text="Всего сессий: 0", font=("Arial", 12))
        self.session_label.pack(anchor="w", pady=2)
        
        self.valid_session_label = CTkLabel(stats_frame, text="Рабочих сессий: 0", font=("Arial", 12))
        self.valid_session_label.pack(anchor="w", pady=2)
        
        self.success_label = CTkLabel(stats_frame, text="Успешных жалоб: 0", font=("Arial", 12))
        self.success_label.pack(anchor="w", pady=2)
        
        self.fail_label = CTkLabel(stats_frame, text="Неудачных жалоб: 0", font=("Arial", 12))
        self.fail_label.pack(anchor="w", pady=2)
        
        self.active_label = CTkLabel(stats_frame, text="Активных задач: 0", font=("Arial", 12))
        self.active_label.pack(anchor="w", pady=2)

        # Логи
        CTkLabel(self.info_frame, text="📝 Логи выполнения", font=("Arial", 16)).pack(pady=10)
        self.log_text = CTkTextbox(self.info_frame, width=380, height=400, font=("Consolas", 10))
        self.log_text.pack(pady=5)
        self.log_text.configure(state="disabled")

        # Хук для логирования в GUI
        class GUILogHandler(logging.Handler):
            def __init__(self, text_widget):
                super().__init__()
                self.text_widget = text_widget
                self.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))

            def emit(self, record):
                msg = self.format(record)
                self.text_widget.configure(state="normal")
                self.text_widget.insert("end", msg + "\n")
                self.text_widget.configure(state="disabled")
                self.text_widget.see("end")

        logging.getLogger().addHandler(GUILogHandler(self.log_text))

    def check_sessions_on_startup(self):
        """Проверка сессий при запуске"""
        def run_check():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                loop.run_until_complete(self.reporter.validate_sessions())
                self.update_stats()
            finally:
                loop.close()
        
        Thread(target=run_check, daemon=True).start()

    def check_sessions_manual(self):
        """Ручная проверка сессий"""
        self.start_btn.configure(state="disabled")
        self.check_btn.configure(state="disabled", text="🔍 Проверка...")
        
        def run_check():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                loop.run_until_complete(self.reporter.validate_sessions())
                self.update_stats()
                messagebox.showinfo("Проверка завершена", 
                                  f"Найдено {len(self.reporter.valid_sessions)} рабочих сессий")
            finally:
                loop.close()
                self.start_btn.configure(state="normal")
                self.check_btn.configure(state="normal", text="🔍 Проверить сессии")
        
        Thread(target=run_check, daemon=True).start()

    def start_reporting(self):
        """Запуск отправки жалоб"""
        message_link = self.link_entry.get()
        reason_num = self.reason_var.get()
        comment = self.comment_entry.get("1.0", "end").strip()
        
        try:
            delay = float(self.delay_entry.get() or config.default_delay)
            if delay < 0:
                raise ValueError("Задержка не может быть отрицательной")
        except ValueError:
            messagebox.showerror("Ошибка", "Некорректное значение задержки")
            return

        if not message_link:
            messagebox.showerror("Ошибка", "Введите ссылку на сообщение")
            return

        if not self.reporter.valid_sessions:
            messagebox.showerror("Ошибка", "Нет рабочих сессий для отправки")
            return

        self.start_btn.configure(state="disabled")
        self.stop_btn.configure(state="normal")
        
        # Запуск в отдельном потоке
        Thread(
            target=self.run_async_report, 
            args=(message_link, reason_num, comment, delay),
            daemon=True
        ).start()

    def run_async_report(self, message_link, reason_num, comment, delay):
        """Запуск асинхронной отправки"""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            loop.run_until_complete(
                self.reporter.start_mass_report(message_link, reason_num, comment, delay)
            )
        finally:
            loop.close()
            self.after(0, lambda: self.start_btn.configure(state="normal"))
            self.after(0, lambda: self.stop_btn.configure(state="disabled"))

    def stop_reporting(self):
        """Остановка отправки"""
        self.reporter.stop_mass_report()
        self.stop_btn.configure(state="disabled")

    def update_stats(self):
        """Обновление статистики"""
        session_files = [f for f in os.listdir("tgaccs") if f.endswith('.session')]
        self.session_label.configure(text=f"Всего сессий: {len(session_files)}")
        self.valid_session_label.configure(text=f"Рабочих сессий: {len(self.reporter.valid_sessions)}")
        self.success_label.configure(text=f"Успешных жалоб: {self.reporter.success_count}")
        self.fail_label.configure(text=f"Неудачных жалоб: {self.reporter.fail_count}")
        self.active_label.configure(text=f"Активных задач: {self.reporter.active_tasks}")
        self.after(1000, self.update_stats)

if __name__ == "__main__":
    app = ReportApp()
    app.update_stats()
    app.mainloop()