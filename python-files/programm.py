import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import sqlite3
import json
import csv
import zipfile
import logging
import configparser
import os
import datetime

# --- Модуль Логирования ---
logging.basicConfig(level=logging.INFO,  # можно менять на logging.DEBUG для более детальной информации
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    filename='Logs/utility.log',  # Укажите путь для лог-файла
                    filemode='w')  # 'w' - перезаписывать, 'a' - добавлять

def log_message(message, level=logging.INFO):
    """Функция для логирования сообщений."""
    logging.log(level, message)

# --- Модуль Конфигурации ---
config = configparser.ConfigParser()
config_file = 'Configs/config.cfg' # Укажите путь для файла конфигурации

def load_config():
    """Загружает конфигурацию из файла."""
    try:
        config.read(config_file)
        log_message(f"Конфигурация загружена из {config_file}")
        return config
    except Exception as e:
        log_message(f"Ошибка при загрузке конфигурации: {e}", logging.ERROR)
        messagebox.showerror("Ошибка", f"Ошибка при загрузке конфигурации: {e}")
        return None

def save_config():
    """Сохраняет конфигурацию в файл."""
    try:
        with open(config_file, 'w') as configfile:
            config.write(configfile)
        log_message(f"Конфигурация сохранена в {config_file}")
        messagebox.showinfo("Успех", "Конфигурация успешно сохранена.")

    except Exception as e:
        log_message(f"Ошибка при сохранении конфигурации: {e}", logging.ERROR)
        messagebox.showerror("Ошибка", f"Ошибка при сохранении конфигурации: {e}")


# --- Модуль работы с базой данных ---
def get_db_connection(db_path):
    """Подключается к базе данных SQLite."""
    try:
        conn = sqlite3.connect(db_path)
        log_message(f"Успешное подключение к базе данных: {db_path}")
        return conn
    except sqlite3.Error as e:
        log_message(f"Ошибка подключения к базе данных: {e}", logging.ERROR)
        messagebox.showerror("Ошибка", f"Ошибка подключения к базе данных: {e}")
        return None

def display_data(conn, tree):
    """Отображает данные из базы данных в Treeview."""
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM your_table")  # Замените 'your_table' на имя вашей таблицы
        rows = cursor.fetchall()

        # Очистить Treeview перед заполнением
        for item in tree.get_children():
            tree.delete(item)

        # Вставить заголовки столбцов
        column_names = [description[0] for description in cursor.description]
        tree["columns"] = column_names
        tree.column("#0", width=0, stretch=tk.NO)  # Скрываем пустой столбец
        for col in column_names:
            tree.column(col, anchor=tk.CENTER, width=100)
            tree.heading(col, text=col, anchor=tk.CENTER)

        for row in rows:
            tree.insert("", tk.END, values=row)
        log_message("Данные успешно отображены из базы данных.")

    except sqlite3.Error as e:
        log_message(f"Ошибка при отображении данных: {e}", logging.ERROR)
        messagebox.showerror("Ошибка", f"Ошибка при отображении данных: {e}")


def export_data_json(conn, filename):
    """Экспортирует данные из базы данных в JSON файл."""
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM your_table") # Замените 'your_table' на имя вашей таблицы
        rows = cursor.fetchall()

        column_names = [description[0] for description in cursor.description]
        data = [dict(zip(column_names, row)) for row in rows]

        with open(filename, 'w') as f:
            json.dump(data, f, indent=4)  # indent для читабельности
        log_message(f"Данные успешно экспортированы в JSON файл: {filename}")
        messagebox.showinfo("Успех", f"Данные успешно экспортированы в JSON файл: {filename}")

    except sqlite3.Error as e:
        log_message(f"Ошибка при экспорте в JSON: {e}", logging.ERROR)
        messagebox.showerror("Ошибка", f"Ошибка при экспорте в JSON: {e}")

    except Exception as e:
        log_message(f"Ошибка при записи JSON файла: {e}", logging.ERROR)
        messagebox.showerror("Ошибка", f"Ошибка при записи JSON файла: {e}")


def export_data_csv(conn, filename):
    """Экспортирует данные из базы данных в CSV файл."""
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM your_table")  # Замените 'your_table' на имя вашей таблицы
        rows = cursor.fetchall()

        column_names = [description[0] for description in cursor.description]

        with open(filename, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(column_names)
            writer.writerows(rows)
        log_message(f"Данные успешно экспортированы в CSV файл: {filename}")
        messagebox.showinfo("Успех", f"Данные успешно экспортированы в CSV файл: {filename}")

    except sqlite3.Error as e:
        log_message(f"Ошибка при экспорте в CSV: {e}", logging.ERROR)
        messagebox.showerror("Ошибка", f"Ошибка при экспорте в CSV: {e}")

    except Exception as e:
        log_message(f"Ошибка при записи CSV файла: {e}", logging.ERROR)
        messagebox.showerror("Ошибка", f"Ошибка при записи CSV файла: {e}")

def import_data_json(conn, filename):
    """Импортирует данные из JSON файла в базу данных."""
    try:
        with open(filename, 'r') as f:
            data = json.load(f)

        if not data:
            messagebox.showerror("Ошибка", "JSON файл пуст.")
            return

        cursor = conn.cursor()
        # Предполагаем, что первый элемент в data содержит структуру таблицы
        columns = data[0].keys()
        placeholders = ', '.join(['?'] * len(columns))
        column_names = ', '.join(columns)
        table_name = "your_table"  # Замените на имя вашей таблицы

        # Создаем таблицу, если она не существует
        create_table_sql = f"CREATE TABLE IF NOT EXISTS {table_name} ({column_names})" #  нужно добавить типы данных
        cursor.execute(create_table_sql)

        insert_sql = f"INSERT INTO {table_name} ({column_names}) VALUES ({placeholders})"
        for row in data:
            values = [row[col] for col in columns]
            cursor.execute(insert_sql, values)

        conn.commit()
        log_message(f"Данные успешно импортированы из JSON файла: {filename}")
        messagebox.showinfo("Успех", f"Данные успешно импортированы из JSON файл: {filename}")

    except FileNotFoundError:
        log_message(f"Файл не найден: {filename}", logging.ERROR)
        messagebox.showerror("Ошибка", f"Файл не найден: {filename}")

    except json.JSONDecodeError as e:
        log_message(f"Ошибка декодирования JSON: {e}", logging.ERROR)
        messagebox.showerror("Ошибка", f"Ошибка декодирования JSON: {e}")

    except sqlite3.Error as e:
        log_message(f"Ошибка базы данных при импорте из JSON: {e}", logging.ERROR)
        messagebox.showerror("Ошибка", f"Ошибка базы данных при импорте из JSON: {e}")

    except Exception as e:
        log_message(f"Произошла непредвиденная ошибка: {e}", logging.ERROR)
        messagebox.showerror("Ошибка", f"Произошла непредвиденная ошибка: {e}")


def import_data_csv(conn, filename):
    """Импортирует данные из CSV файла в базу данных."""
    try:
        with open(filename, 'r') as csvfile:
            reader = csv.reader(csvfile)
            header = next(reader)  # Получаем заголовки столбцов
            table_name = "your_table" # Замените на имя вашей таблицы

            cursor = conn.cursor()

            # Создаем таблицу, если она не существует (с типами данных TEXT для простоты)
            column_definitions = ', '.join([f'{col} TEXT' for col in header])
            create_table_sql = f"CREATE TABLE IF NOT EXISTS {table_name} ({column_definitions})"
            cursor.execute(create_table_sql)

            # Подготавливаем SQL запрос для вставки данных
            placeholders = ', '.join(['?'] * len(header))
            insert_sql = f"INSERT INTO {table_name} VALUES ({placeholders})"

            # Вставляем данные
            for row in reader:
                cursor.execute(insert_sql, row)

            conn.commit()
            log_message(f"Данные успешно импортированы из CSV файла: {filename}")
            messagebox.showinfo("Успех", f"Данные успешно импортированы из CSV файла: {filename}")

    except FileNotFoundError:
        log_message(f"Файл не найден: {filename}", logging.ERROR)
        messagebox.showerror("Ошибка", f"Файл не найден: {filename}")

    except sqlite3.Error as e:
        log_message(f"Ошибка базы данных при импорте из CSV: {e}", logging.ERROR)
        messagebox.showerror("Ошибка", f"Ошибка базы данных при импорте из CSV: {e}")

    except Exception as e:
        log_message(f"Произошла непредвиденная ошибка: {e}", logging.ERROR)
        messagebox.showerror("Ошибка", f"Произошла непредвиденная ошибка: {e}")


# --- Модуль упаковки системы ---
def package_system(source_dir, output_dir):
    """Упаковывает систему в ZIP архив."""
    try:
        utility_name = config['General']['UtilityName']
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        zip_filename = os.path.join(output_dir, f"{utility_name}_{timestamp}.zip")

        with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, _, files in os.walk(source_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, source_dir)  # Относительный путь внутри архива
                    zipf.write(file_path, arcname)

        log_message(f"Система успешно упакована в архив: {zip_filename}")
        messagebox.showinfo("Успех", f"Система успешно упакована в архив: {zip_filename}")

    except Exception as e:
        log_message(f"Ошибка при упаковке системы: {e}", logging.ERROR)
        messagebox.showerror("Ошибка", f"Ошибка при упаковке системы: {e}")

# --- Графический интерфейс ---
class UtilityGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Утилита обслуживания ИС")

        # Загрузка иконки (если иконка есть, положите ее в Images/utility.ico)
        try:
            self.root.iconbitmap("Images/utility.ico")
        except:
            log_message("Иконка не найдена.", logging.WARNING)


        # Загрузка конфигурации
        self.config = load_config()
        if not self.config:
            self.config = configparser.ConfigParser()
            self.config['General'] = {'UtilityName': 'MyUtility', 'Version': '1.0'}
            self.config['Database'] = {'DatabasePath': ''}
            self.config['System'] = {'SystemPath': ''}
            save_config()  # Сохранить значения по умолчанию
            self.config = load_config()

        self.db_connection = None  # Инициализируем подключение к БД

        # --- Главное меню ---
        self.main_menu = tk.Menu(root)
        root.config(menu=self.main_menu)

        self.file_menu = tk.Menu(self.main_menu, tearoff=0)
        self.file_menu.add_command(label="Выход", command=root.quit)
        self.main_menu.add_cascade(label="Файл", menu=self.file_menu)

        # --- Вкладки ---
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(expand=True, fill=tk.BOTH, padx=10, pady=10)

        self.create_main_tab()
        self.create_data_tab()
        self.create_package_tab()
        self.create_config_tab()


    def create_main_tab(self):
        """Создает вкладку с основной информацией."""
        self.main_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.main_tab, text="Главная")

        #  Имя утилиты и версия
        ttk.Label(self.main_tab, text=f"Наименование утилиты: {self.config['General']['UtilityName']}", font=('Arial', 12)).pack(pady=5)
        ttk.Label(self.main_tab, text=f"Версия: {self.config['General']['Version']}", font=('Arial', 12)).pack(pady=5)

        # Статус базы данных
        self.db_status_label = ttk.Label(self.main_tab, text="Статус базы данных: Не подключена", font=('Arial', 12))
        self.db_status_label.pack(pady=5)

        # Функция обновления статуса БД
        self.update_db_status()

    def update_db_status(self):
        """Обновляет статус подключения к базе данных."""
        db_path = self.config['Database']['DatabasePath']
        if os.path.exists(db_path):
            self.db_connection = get_db_connection(db_path)  # Попытка установить соединение
            if self.db_connection:
                self.db_status_label.config(text="Статус базы данных: Подключена", foreground="green")
                return  # Если подключение успешно, выходим
        self.db_status_label.config(text="Статус базы данных: Не подключена", foreground="red")
        self.db_connection = None #  явно указываем, что соединения нет


    def create_data_tab(self):
        """Создает вкладку для работы с данными."""
        self.data_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.data_tab, text="Данные")

        # Treeview для отображения данных
        self.data_tree = ttk.Treeview(self.data_tab)
        self.data_tree.pack(expand=True, fill=tk.BOTH, padx=10, pady=10)

        # Кнопки для экспорта и импорта данных
        export_json_button = ttk.Button(self.data_tab, text="Экспорт в JSON", command=self.export_to_json)
        export_json_button.pack(side=tk.LEFT, padx=5, pady=5)

        export_csv_button = ttk.Button(self.data_tab, text="Экспорт в CSV", command=self.export_to_csv)
        export_csv_button.pack(side=tk.LEFT, padx=5, pady=5)

        import_json_button = ttk.Button(self.data_tab, text="Импорт из JSON", command=self.import_from_json)
        import_json_button.pack(side=tk.LEFT, padx=5, pady=5)

        import_csv_button = ttk.Button(self.data_tab, text="Импорт из CSV", command=self.import_from_csv)
        import_csv_button.pack(side=tk.LEFT, padx=5, pady=5)

        display_data_button = ttk.Button(self.data_tab, text="Отобразить данные", command=self.display_data_from_db)
        display_data_button.pack(side=tk.LEFT, padx=5, pady=5)


    def display_data_from_db(self):
        """Отображает данные из базы данных."""
        if not self.db_connection:
            messagebox.showerror("Ошибка", "База данных не подключена. Проверьте настройки.")
            return
        display_data(self.db_connection, self.data_tree)


    def export_to_json(self):
        """Экспортирует данные в JSON файл."""
        if not self.db_connection:
            messagebox.showerror("Ошибка", "База данных не подключена. Проверьте настройки.")
            return

        filename = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON files", "*.json")])
        if filename:
            export_data_json(self.db_connection, filename)

    def export_to_csv(self):
        """Экспортирует данные в CSV файл."""
        if not self.db_connection:
            messagebox.showerror("Ошибка", "База данных не подключена. Проверьте настройки.")
            return
        filename = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
        if filename:
            export_data_csv(self.db_connection, filename)

    def import_from_json(self):
         """Импортирует данные из JSON файла."""
         if not self.db_connection:
             messagebox.showerror("Ошибка", "База данных не подключена. Проверьте настройки.")
             return

         filename = filedialog.askopenfilename(defaultextension=".json", filetypes=[("JSON files", "*.json")])
         if filename:
             import_data_json(self.db_connection, filename)
             self.display_data_from_db() # Обновляем отображение данных

    def import_from_csv(self):
        """Импортирует данные из CSV файла."""
        if not self.db_connection:
            messagebox.showerror("Ошибка", "База данных не подключена. Проверьте настройки.")
            return

        filename = filedialog.askopenfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
        if filename:
            import_data_csv(self.db_connection, filename)
            self.display_data_from_db() # Обновляем отображение данных


    def create_package_tab(self):
        """Создает вкладку для упаковки системы."""
        self.package_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.package_tab, text="Упаковка")

        # Кнопка для выбора директории системы
        self.system_path_label = ttk.Label(self.package_tab, text="Путь к системе:")
        self.system_path_label.pack(pady=5)

        self.system_path_value = tk.StringVar(value=self.config['System']['SystemPath'])
        self.system_path_entry = ttk.Entry(self.package_tab, textvariable=self.system_path_value, width=50)
        self.system_path_entry.pack(pady=5)

        self.browse_system_button = ttk.Button(self.package_tab, text="Выбрать директорию", command=self.browse_system_directory)
        self.browse_system_button.pack(pady=5)


        # Кнопка для выбора директории вывода
        self.output_path_label = ttk.Label(self.package_tab, text="Путь для сохранения архива:")
        self.output_path_label.pack(pady=5)

        self.output_path_value = tk.StringVar() #  Можно указать значение по умолчанию
        self.output_path_entry = ttk.Entry(self.package_tab, textvariable=self.output_path_value, width=50)
        self.output_path_entry.pack(pady=5)

        self.browse_output_button = ttk.Button(self.package_tab, text="Выбрать директорию вывода", command=self.browse_output_directory)
        self.browse_output_button.pack(pady=5)


        # Кнопка для запуска упаковки
        self.package_button = ttk.Button(self.package_tab, text="Упаковать систему", command=self.start_packaging)
        self.package_button.pack(pady=10)

    def browse_system_directory(self):
        """Открывает диалоговое окно для выбора директории системы."""
        directory = filedialog.askdirectory()
        if directory:
            self.system_path_value.set(directory)
            self.config['System']['SystemPath'] = directory
            save_config() # Сохраняем в конфиг сразу
            log_message(f"Выбрана директория системы: {directory}")

    def browse_output_directory(self):
        """Открывает диалоговое окно для выбора директории вывода."""
        directory = filedialog.askdirectory()
        if directory:
            self.output_path_value.set(directory)
            log_message(f"Выбрана директория вывода: {directory}")


    def start_packaging(self):
        """Запускает процесс упаковки системы."""
        source_dir = self.system_path_value.get()
        output_dir = self.output_path_value.get()

        if not source_dir or not os.path.isdir(source_dir):
            messagebox.showerror("Ошибка", "Необходимо выбрать корректную директорию системы.")
            return

        if not output_dir or not os.path.isdir(output_dir):
             messagebox.showerror("Ошибка", "Необходимо выбрать корректную директорию вывода.")
             return

        package_system(source_dir, output_dir)


    def create_config_tab(self):
        """Создает вкладку для настройки конфигурации."""
        self.config_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.config_tab, text="Конфигурация")

        #  Имя утилиты
        ttk.Label(self.config_tab, text="Наименование утилиты:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        self.utility_name_value = tk.StringVar(value=self.config['General']['UtilityName'])
        ttk.Entry(self.config_tab, textvariable=self.utility_name_value, width=30).grid(row=0, column=1, padx=5, pady=5, sticky=tk.E)

        # Версия утилиты
        ttk.Label(self.config_tab, text="Версия:").grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        self.version_value = tk.StringVar(value=self.config['General']['Version'])
        ttk.Entry(self.config_tab, textvariable=self.version_value, width=30).grid(row=1, column=1, padx=5, pady=5, sticky=tk.E)

        # Путь к базе данных
        ttk.Label(self.config_tab, text="Путь к базе данных:").grid(row=2, column=0, padx=5, pady=5, sticky=tk.W)
        self.db_path_value = tk.StringVar(value=self.config['Database']['DatabasePath'])
        ttk.Entry(self.config_tab, textvariable=self.db_path_value, width=30).grid(row=2, column=1, padx=5, pady=5, sticky=tk.E)
        ttk.Button(self.config_tab, text="Обзор", command=self.browse_database).grid(row=2, column=2, padx=5, pady=5)

        # Путь к системе
        ttk.Label(self.config_tab, text="Путь к системе:").grid(row=3, column=0, padx=5, pady=5, sticky=tk.W)
        self.system_path_value_config = tk.StringVar(value=self.config['System']['SystemPath'])
        ttk.Entry(self.config_tab, textvariable=self.system_path_value_config, width=30).grid(row=3, column=1, padx=5, pady=5, sticky=tk.E)
        ttk.Button(self.config_tab, text="Обзор", command=self.browse_system_config).grid(row=3, column=2, padx=5, pady=5)

        # Кнопка сохранения конфигурации
        ttk.Button(self.config_tab, text="Сохранить", command=self.save_config_data).grid(row=4, column=0, columnspan=3, padx=5, pady=10)

    def browse_database(self):
        """Открывает диалоговое окно для выбора файла базы данных."""
        filename = filedialog.askopenfilename(defaultextension=".db", filetypes=[("Database files", "*.db")])
        if filename:
            self.db_path_value.set(filename)

    def browse_system_config(self):
        """Открывает диалоговое окно для выбора директории системы (вкладка Config)."""
        directory = filedialog.askdirectory()
        if directory:
            self.system_path_value_config.set(directory)

    def save_config_data(self):
        """Сохраняет данные конфигурации."""
        self.config['General']['UtilityName'] = self.utility_name_value.get()
        self.config['General']['Version'] = self.version_value.get()
        self.config['Database']['DatabasePath'] = self.db_path_value.get()
        self.config['System']['SystemPath'] = self.system_path_value_config.get()

        save_config()
        self.update_db_status() #  Обновляем статус БД
        messagebox.showinfo("Успех", "Конфигурация успешно сохранена.")
        log_message("Конфигурация сохранена через интерфейс.")



# --- Запуск приложения ---
if __name__ == "__main__":
    # Создаем необходимые директории, если их нет
    os.makedirs('Logs', exist_ok=True)
    os.makedirs('Configs', exist_ok=True)
    os.makedirs('Images', exist_ok=True)


    root = tk.Tk()
    gui = UtilityGUI(root)
    root.mainloop()

    # Закрываем соединение с базой данных при выходе
    if gui.db_connection:
        gui.db_connection.close()
        log_message("Соединение с базой данных закрыто.")