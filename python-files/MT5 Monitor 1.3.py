import MetaTrader5 as mt5
from datetime import datetime, timedelta
import tkinter as tk
from tkinter import ttk, Menu, messagebox

class AccountInfoApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("MT5 Monitor 1.0")
        self.geometry("800x600")
        
        # Цветовая схема и шрифты
        style = ttk.Style()
        style.theme_use("clam")  # Выбор темы стиля
        style.configure("TLabel", foreground="black", background="#EFEFEF", font=("Segoe UI", 16))  # Основной текст
        style.configure("TFrame", background="#EFEFEF")  # Фон рамки
        style.configure("TButton", relief="flat", borderwidth=0, highlightthickness=0, anchor="center", padding=10)
        style.map("TButton", background=[("active", "#FFDDCC")], foreground=[("active", "black")])  # Эффект при наведении
        
        # Главное меню с пунктом "Настройки"
        menu_bar = Menu(self)
        settings_menu = Menu(menu_bar, tearoff=False)
        settings_menu.add_command(label="Настроить подключение...", command=self.open_settings_window)
        menu_bar.add_cascade(label="Настройки", menu=settings_menu)
        self.config(menu=menu_bar)
        
        # Фрейм для отображения основной информации
        main_frame = ttk.Frame(self, padding="10")
        main_frame.pack(expand=True, fill=tk.BOTH)
        
        # Название брокера и номер счёта
        self.broker_info_var = tk.StringVar(value="Загрузка...")
        ttk.Label(main_frame, textvariable=self.broker_info_var, font=("Calibri", 16, "bold")).pack(pady=10)
        
        # Таблица для отображения ключевых показателей
        table_frame = ttk.Frame(main_frame)
        table_frame.pack(fill=tk.X, pady=10)
        
        columns = ('Field', 'Value')
        self.treeview = ttk.Treeview(table_frame, columns=columns, show='headings', selectmode="none", height=6)
        self.treeview.heading('Field', text='Параметр')
        self.treeview.heading('Value', text='Значение')
        self.treeview.column('Field', minwidth=0, width=200, stretch=tk.NO)
        self.treeview.column('Value', minwidth=0, width=300, stretch=tk.YES)
        self.treeview.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.treeview.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.treeview.configure(yscrollcommand=scrollbar.set)
        
        # Область для отображения истории прибыли
        self.profits_text = tk.Text(main_frame, height=10, width=80, wrap=tk.WORD, font=("Calibri", 16))
        self.profits_text.pack(fill=tk.BOTH, expand=True)
        self.profits_text.config(state=tk.DISABLED)
        
        # Вспомогательные переменные
        self.server = "mt5-ecn.roboforex.com:443"
        self.login = "77014035"
        self.password = "tN1Ylk11@"
        self.update_interval_ms = 100  # Интервал обновления по умолчанию
        self.is_connected = False

    def clear_result_area(self):
        """Очистка области вывода"""
        self.profits_text.config(state=tk.NORMAL)
        self.profits_text.delete(1.0, tk.END)
        self.profits_text.config(state=tk.DISABLED)

    def start_auto_update(self):
        """Начинает цикл автообновления данных"""
        if self.is_connected:
            self.update_data()

    def stop_auto_update(self):
        """Останавливает цикл автообновления данных"""
        self.is_connected = False

    def update_data(self):
        """Автоматически обновляет данные каждые UPDATE_INTERVAL_MS мс."""
        if self.is_connected:
            try:
                account_info = mt5.account_info()
                if account_info is None:
                    raise ValueError("Нет информации о счёте!")
                
                # Обновляем заголовок окна
                self.broker_info_var.set(f"MT5 Monitor 1.0 | Брокер: {account_info.company}, Счет: {account_info.login} | {datetime.now():%Y-%m-%d %H:%M:%S}")
                
                # Чистка старой информации в таблице
                for item in self.treeview.get_children():
                    self.treeview.delete(item)
                
                # Вставка новой информации
                data_rows = [
                    ["Баланс", f"{account_info.balance:.2f}$"],
                    ["Средства", f"{account_info.equity:.2f}$"],
                    ["Уровень маржи", f"{account_info.margin_level:.2f}%"],
                    ["Прибыль", f"{account_info.profit:.2f}$"],
                    ["Просадка (плавающая)", f"{account_info.equity - account_info.balance:.2f}$"]
                ]
                for row in data_rows:
                    self.treeview.insert("", tk.END, values=row)
                
                # Сбор данных по истории прибыли
                start_time = datetime.now() - timedelta(days=30)
                end_time = datetime.now()
                all_deals = mt5.history_deals_get(start_time, end_time)
                
                if len(all_deals) > 0:
                    profits = {
                        "today": sum(d.profit for d in all_deals if d.time_msc >= datetime.now().replace(hour=0, minute=0, second=0).timestamp()*1000),
                        "yesterday": sum(d.profit for d in all_deals if d.time_msc >= (datetime.now() - timedelta(days=1)).replace(hour=0, minute=0, second=0).timestamp()*1000 and d.time_msc < datetime.now().replace(hour=0, minute=0, second=0).timestamp()*1000),
                        "week": sum(d.profit for d in all_deals if d.time_msc >= (datetime.now() - timedelta(days=7)).timestamp()*1000),
                        "month": sum(d.profit for d in all_deals if d.time_msc >= (datetime.now().replace(day=1)).timestamp()*1000),
                        "total": sum(d.profit for d in all_deals),
                    }
                else:
                    profits = {"today": 0, "yesterday": 0, "week": 0, "month": 0, "total": 0}
                
                # Форматированный вывод истории прибыли
                profit_lines = [
                    f" Сегодня: {profits['today']:.2f}$",
                    f" Вчера: {profits['yesterday']:.2f}$",
                    f" За неделю: {profits['week']:.2f}$",
                    f" За месяц: {profits['month']:.2f}$",
                    f" Всего: {profits['total']:.2f}$",
                ]
                
                self.clear_result_area()
                self.profits_text.config(state=tk.NORMAL)
                self.profits_text.insert(tk.END, "История прибыли:\n")
                self.profits_text.insert(tk.END, "\n")
                self.profits_text.insert(tk.END, "\n".join(profit_lines) + "\n")
                self.profits_text.config(state=tk.DISABLED)
            
            except Exception as err:
                messagebox.showerror("Ошибка", f"Что-то пошло не так: {err}")
        
        # Повторное планирование следующего обновления
        self.after(self.update_interval_ms, self.update_data)

    def display_account_info(self, account_info):
        pass  # Удалили старый метод, теперь таблица обновляется автоматически в update_data

    def display_profits(self, profits):
        pass  # Аналогично, таблица и текстовое поле обновляются автоматически

    def open_settings_window(self):
        """Открывает окно настроек"""
        settings_win = tk.Toplevel(self)
        settings_win.title("Настройки подключения")
        settings_win.geometry("600x250")
        
        frame_settings = ttk.Frame(settings_win, padding="10")
        frame_settings.pack(expand=True, fill=tk.BOTH)
        
        label_server = ttk.Label(frame_settings, text="Адрес сервера (включая порт):", font=("Arial", 10))
        label_server.grid(row=0, column=0, sticky='w', padx=(10, 0))
        entry_server = ttk.Entry(frame_settings, width=40, font=("Arial", 10))
        entry_server.grid(row=0, column=1, pady=5)
        entry_server.insert(0, self.server)
        
        label_login = ttk.Label(frame_settings, text="Логин:", font=("Arial", 10))
        label_login.grid(row=1, column=0, sticky='w', padx=(10, 0))
        entry_login = ttk.Entry(frame_settings, width=40, font=("Arial", 10))
        entry_login.grid(row=1, column=1, pady=5)
        entry_login.insert(0, self.login)
        
        label_password = ttk.Label(frame_settings, text="Пароль:", font=("Arial", 10))
        label_password.grid(row=2, column=0, sticky='w', padx=(10, 0))
        entry_password = ttk.Entry(frame_settings, show="*", width=40, font=("Arial", 10))
        entry_password.grid(row=2, column=1, pady=5)
        entry_password.insert(0, self.password)
        
        label_update_interval = ttk.Label(frame_settings, text="Интервал обновления (мс):", font=("Arial", 10))
        label_update_interval.grid(row=3, column=0, sticky='w', padx=(10, 0))
        entry_update_interval = ttk.Entry(frame_settings, width=40, font=("Arial", 10))
        entry_update_interval.grid(row=3, column=1, pady=5)
        entry_update_interval.insert(0, str(self.update_interval_ms))
        
        save_button = ttk.Button(frame_settings, text="Сохранить и закрыть", command=lambda: self.save_settings(entry_server.get(), entry_login.get(), entry_password.get(), entry_update_interval.get()))
        save_button.grid(row=4, columnspan=2, pady=20)

    def save_settings(self, new_server, new_login, new_password, new_interval):
        """Сохраняет введённые настройки и закрывает окно настроек"""
        try:
            self.server = new_server
            self.login = new_login
            self.password = new_password
            self.update_interval_ms = int(new_interval)
            if self.update_interval_ms <= 0:
                raise ValueError("Интервал обновления должен быть положительным числом!")
        except ValueError as ve:
            messagebox.showerror("Ошибка", f"Некорректный интервал обновления: {ve}")
            return
        
        # Попытка подключения и начало обновления данных
        try:
            if not mt5.initialize(login=int(self.login), password=self.password, server=self.server):
                error_code = mt5.last_error()
                raise ValueError(f"Ошибка инициализации! Код ошибки: {error_code}")
            
            self.is_connected = True
            self.start_auto_update()
            messagebox.showinfo("Успех", "Настройки сохранены и обновление данных началось.")
        except Exception as err:
            messagebox.showerror("Ошибка", f"Что-то пошло не так: {err}")

if __name__ == "__main__":
    app = AccountInfoApp()
    app.mainloop()