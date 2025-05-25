import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import sqlite3
from tkcalendar import DateEntry


# ========== Работа с базой данных ==========
class TrainDB:
    def __init__(self, db_name="trains.db"):
        self.conn = sqlite3.connect(db_name)
        self.create_table()

    def create_table(self):
        with self.conn:
            self.conn.execute("""
                CREATE TABLE IF NOT EXISTS trains (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    destination TEXT NOT NULL,
                    train_number TEXT NOT NULL UNIQUE,
                    departure_time TEXT NOT NULL,
                    platskart INT NOT NULL,
                    common INT NOT NULL,
                    kupe INT NOT NULL,
                    sv INT NOT NULL
                )
            """)

    def add_train(self, data):
        try:
            with self.conn:
                self.conn.execute("""
                    INSERT INTO trains 
                    (destination, train_number, departure_time, platskart, common, kupe, sv)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, data)
            return True
        except sqlite3.IntegrityError:
            return False  # Номер поезда уже существует

    def get_all_trains(self):
        return self.conn.execute("SELECT * FROM trains").fetchall()

    def find_by_number(self, number):
        return self.conn.execute("SELECT * FROM trains WHERE train_number=?", (number,)).fetchone()

    def find_by_destination(self, dest):
        return self.conn.execute("SELECT * FROM trains WHERE destination LIKE ?", (f"%{dest}%",)).fetchall()

    def find_after_time(self, time_str):
        return self.conn.execute("SELECT * FROM trains WHERE departure_time > ?", (time_str,)).fetchall()

    def find_by_destination_and_time(self, dest, time_str):
        return self.conn.execute(
            "SELECT * FROM trains WHERE destination LIKE ? AND departure_time > ?",
            (f"%{dest}%", time_str)
        ).fetchall()


# ========== Основное окно приложения ==========
class TrainApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Вокзал - Управление поездами")
        self.root.geometry("950x600")

        self.db = TrainDB()
        self.init_ui()

    def init_ui(self):
        notebook = ttk.Notebook(self.root)

        # Вкладка: Добавление поезда
        tab_add = ttk.Frame(notebook)
        self.setup_add_tab(tab_add)
        notebook.add(tab_add, text="Добавить поезд")

        # Вкладка: Поиск поездов
        tab_search = ttk.Frame(notebook)
        self.setup_search_tab(tab_search)
        notebook.add(tab_search, text="Поиск поездов")

        # Вкладка: Все поезда
        tab_all = ttk.Frame(notebook)
        self.setup_all_trains_tab(tab_all)
        notebook.add(tab_all, text="Все поезда")

        notebook.pack(expand=True, fill="both")

    def setup_add_tab(self, tab):
        fields = ["Пункт назначения", "Номер поезда", "Дата отправления", "Время отправления"]
        self.add_entries = {}

        for i, label in enumerate(fields):
            ttk.Label(tab, text=label).grid(row=i, column=0, sticky="w", padx=10, pady=5)
            if label == "Дата отправления":
                entry = DateEntry(tab, width=20, background='darkblue', foreground='white', date_pattern='yyyy-mm-dd')
            elif label == "Время отправления":
                entry = ttk.Entry(tab)
                entry.insert(0, "HH:MM")
            else:
                entry = ttk.Entry(tab)
            entry.grid(row=i, column=1, padx=10, pady=5)
            self.add_entries[label] = entry

        # Поля для вагонов
        wagon_labels = ["Плацкарт", "Общий", "Купе", "СВ"]
        self.wagon_entries = {}
        for j, w_label in enumerate(wagon_labels):
            ttk.Label(tab, text=w_label).grid(row=j + len(fields), column=0, sticky="w", padx=10, pady=5)
            entry = ttk.Entry(tab)
            entry.insert(0, "0")
            entry.grid(row=j + len(fields), column=1, padx=10, pady=5)
            self.wagon_entries[w_label] = entry

        btn_add = ttk.Button(tab, text="Добавить поезд", command=self.add_train_handler)
        btn_add.grid(row=len(fields) + len(wagon_labels), columnspan=2, pady=10)

    def add_train_handler(self):
        dest = self.add_entries["Пункт назначения"].get().strip()
        num = self.add_entries["Номер поезда"].get().strip()
        date = self.add_entries["Дата отправления"].get()
        time = self.add_entries["Время отправления"].get().strip()
        dep_time = f"{date} {time}"

        try:
            pl = int(self.wagon_entries["Плацкарт"].get())
            cm = int(self.wagon_entries["Общий"].get())
            kp = int(self.wagon_entries["Купе"].get())
            sv = int(self.wagon_entries["СВ"].get())
        except ValueError:
            messagebox.showwarning("Ошибка", "Количество вагонов должно быть числом.")
            return

        if not dest or not num:
            messagebox.showwarning("Ошибка", "Заполните все поля!")
            return

        success = self.db.add_train((dest, num, dep_time, pl, cm, kp, sv))
        if success:
            messagebox.showinfo("Успех", "Поезд успешно добавлен!")
        else:
            messagebox.showwarning("Ошибка", "Поезд с таким номером уже существует.")

    def setup_search_tab(self, tab):
        self.search_type = ttk.Combobox(tab, values=[
            "По номеру",
            "По времени отправления",
            "По направлению",
            "По направлению и времени"
        ])
        self.search_type.current(0)
        self.search_type.grid(row=0, column=0, columnspan=2, sticky="ew", padx=10, pady=5)

        self.number_input = ttk.Entry(tab)
        self.destination_input = ttk.Entry(tab)
        self.datetime_input = DateEntry(tab, date_pattern='yyyy-mm-dd')
        self.time_input = ttk.Entry(tab)
        self.time_input.insert(0, "HH:MM")

        # Размещаем все поля, но скрываем их до нужного момента
        self.number_input.grid(row=1, column=1, padx=10, pady=5)
        self.destination_input.grid(row=2, column=1, padx=10, pady=5)
        self.datetime_input.grid(row=3, column=1, padx=10, pady=5)
        self.time_input.grid(row=4, column=1, padx=10, pady=5)

        # Подписи к полям
        ttk.Label(tab, text="Номер поезда:").grid(row=1, column=0, sticky="w", padx=10)
        ttk.Label(tab, text="Пункт назначения:").grid(row=2, column=0, sticky="w", padx=10)
        ttk.Label(tab, text="Дата отправления:").grid(row=3, column=0, sticky="w", padx=10)
        ttk.Label(tab, text="Время отправления:").grid(row=4, column=0, sticky="w", padx=10)

        # Кнопка поиска и очистки
        self.search_btn = ttk.Button(tab, text="Поиск", command=self.perform_search)
        self.search_btn.grid(row=5, column=0, padx=10, pady=10, sticky="ew")

        clear_btn = ttk.Button(tab, text="Очистить", command=lambda: self.update_table([]))
        clear_btn.grid(row=5, column=1, padx=10, pady=10, sticky="ew")

        # Таблица результатов
        self.result_table = ttk.Treeview(tab, show="headings", selectmode="browse")
        cols = ("ID", "Назначение", "№ поезда", "Отправление", "Плацкарт", "Общий", "Купе", "СВ")
        self.result_table["columns"] = cols
        for col in cols:
            self.result_table.heading(col, text=col)
            self.result_table.column(col, width=100, anchor="center")
        self.result_table.grid(row=6, column=0, columnspan=2, sticky="nsew", padx=10, pady=10)

        tab.grid_rowconfigure(6, weight=1)
        tab.grid_columnconfigure(0, weight=1)

        self.update_table(self.db.get_all_trains())

        # Привязка события изменения типа поиска
        self.search_type.bind("<<ComboboxSelected>>", self.update_search_fields)
        self.update_search_fields()  # Инициализация отображения полей

    def update_search_fields(self, event=None):
        idx = self.search_type.current()

        # Скрываем все поля
        self.number_input.grid_remove()
        self.destination_input.grid_remove()
        self.datetime_input.grid_remove()
        self.time_input.grid_remove()

        # Показываем нужные
        if idx == 0:
            self.number_input.grid(row=1, column=1, padx=10, pady=5)
        elif idx == 1:
            self.datetime_input.grid(row=3, column=1, padx=10, pady=5)
            self.time_input.grid(row=4, column=1, padx=10, pady=5)
        elif idx == 2:
            self.destination_input.grid(row=2, column=1, padx=10, pady=5)
        elif idx == 3:
            self.destination_input.grid(row=2, column=1, padx=10, pady=5)
            self.datetime_input.grid(row=3, column=1, padx=10, pady=5)
            self.time_input.grid(row=4, column=1, padx=10, pady=5)

    def perform_search(self):
        idx = self.search_type.current()
        if idx == 0:
            res = self.db.find_by_number(self.number_input.get())
            self.update_table([res] if res else [])
        elif idx == 1:
            dt = f"{self.datetime_input.get()} {self.time_input.get()}"
            res = self.db.find_after_time(dt)
            self.update_table(res)
        elif idx == 2:
            res = self.db.find_by_destination(self.destination_input.get())
            self.update_table(res)
        elif idx == 3:
            dt = f"{self.datetime_input.get()} {self.time_input.get()}"
            res = self.db.find_by_destination_and_time(self.destination_input.get(), dt)
            self.update_table(res)

    def setup_all_trains_tab(self, tab):
        # Таблица
        self.all_trains_table = ttk.Treeview(tab, show="headings", selectmode="browse")
        cols = ("ID", "Назначение", "№ поезда", "Отправление", "Плацкарт", "Общий", "Купе", "СВ")
        self.all_trains_table["columns"] = cols
        for col in cols:
            self.all_trains_table.heading(col, text=col)
            self.all_trains_table.column(col, width=100, anchor="center")
        self.all_trains_table.pack(fill="both", expand=True, padx=10, pady=10)

        # Кнопка обновления
        refresh_btn = ttk.Button(tab, text="Обновить список", command=self.refresh_all_trains)
        refresh_btn.pack(pady=10)

        # Загрузка данных
        self.refresh_all_trains()

    def refresh_all_trains(self):
        data = self.db.get_all_trains()
        self.all_trains_table.delete(*self.all_trains_table.get_children())
        for row in data:
            self.all_trains_table.insert("", "end", values=row)

    def update_table(self, data):
        self.result_table.delete(*self.result_table.get_children())
        if isinstance(data, dict) or isinstance(data, tuple):
            data = [data]
        for row in data:
            self.result_table.insert("", "end", values=row)


# ========== Запуск приложения ==========
if __name__ == "__main__":
    root = tk.Tk()
    app = TrainApp(root)
    root.mainloop()
