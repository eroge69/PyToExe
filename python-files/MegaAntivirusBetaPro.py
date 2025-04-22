import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import hashlib
import os
from threading import Thread
from datetime import datetime

class AntivirusApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Python Antivirus Pro")
        self.root.geometry("1000x700")
        self.root.resizable(True, True)
        
        # Стилизация
        self.style = ttk.Style()
        self.style.theme_use('clam')
        self.configure_styles()
        
        # База сигнатур вирусов (MD5 хеши)
        self.malware_db = {
            "d41d8cd98f00b204e9800998ecf8427e": "Empty File Virus",
            "5d41402abc4b2a76b9719d911017c592": "Hello World Trojan",
            "098f6bcd4621d373cade4e832627b4f6": "Test Malware",
            "7d793037a0760186574b0282f2f435e7": "Dangerous Script",
            "b026324c6904b2a9cb4b88d6d61c81d1": "Fake System File"
        }
        
        # Переменные состояния
        self.scanning = False
        self.stop_requested = False
        self.total_files = 0
        self.scanned_files = 0
        self.threats_found = 0
        
        # Создание интерфейса
        self.create_widgets()
        
        # Центрирование окна
        self.center_window()

    def configure_styles(self):
        """Настройка стилей для интерфейса"""
        self.style.configure('TFrame', background='#f0f0f0')
        self.style.configure('TButton', font=('Arial', 10), padding=6)
        self.style.configure('Title.TLabel', 
                           font=('Arial', 16, 'bold'), 
                           background='#f0f0f0',
                           foreground='#2c3e50')
        self.style.configure('Status.TLabel',
                           font=('Arial', 10),
                           background='#f0f0f0',
                           foreground='#2c3e50')
        self.style.map('Action.TButton',
                      foreground=[('active', 'white'), ('!disabled', 'white')],
                      background=[('active', '#3498db'), ('!disabled', '#2980b9')])
        self.style.map('Stop.TButton',
                      foreground=[('active', 'white'), ('!disabled', 'white')],
                      background=[('active', '#e74c3c'), ('!disabled', '#c0392b')])
        self.style.configure('Treeview', 
                           font=('Arial', 10),
                           rowheight=25)
        self.style.configure('Treeview.Heading', 
                           font=('Arial', 10, 'bold'))
        self.style.configure('Green.Horizontal.TProgressbar',
                           troughcolor='#f0f0f0',
                           background='#2ecc71',
                           lightcolor='#2ecc71',
                           darkcolor='#27ae60')
        self.style.configure('Red.Horizontal.TProgressbar',
                           troughcolor='#f0f0f0',
                           background='#e74c3c',
                           lightcolor='#e74c3c',
                           darkcolor='#c0392b')

    def center_window(self):
        """Центрирование окна на экране"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')

    def create_widgets(self):
        """Создание всех элементов интерфейса"""
        # Главный фрейм
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Заголовок
        title_frame = ttk.Frame(main_frame)
        title_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(title_frame, 
                 text="Python Antivirus Pro", 
                 style='Title.TLabel').pack(side=tk.LEFT)
        
        # Панель управления
        control_frame = ttk.Frame(main_frame)
        control_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.select_file_btn = ttk.Button(control_frame, 
                                        text="Выбрать файл",
                                        style='Action.TButton',
                                        command=self.select_file)
        self.select_file_btn.pack(side=tk.LEFT, padx=5)
        
        self.select_folder_btn = ttk.Button(control_frame, 
                                          text="Выбрать папку",
                                          style='Action.TButton',
                                          command=self.select_directory)
        self.select_folder_btn.pack(side=tk.LEFT, padx=5)
        
        self.scan_btn = ttk.Button(control_frame, 
                                  text="Начать сканирование",
                                  style='Action.TButton',
                                  command=self.start_scan,
                                  state=tk.DISABLED)
        self.scan_btn.pack(side=tk.LEFT, padx=5)
        
        self.stop_btn = ttk.Button(control_frame, 
                                 text="Остановить",
                                 style='Stop.TButton',
                                 command=self.stop_scan,
                                 state=tk.DISABLED)
        self.stop_btn.pack(side=tk.LEFT, padx=5)
        
        # Поле пути
        path_frame = ttk.Frame(main_frame)
        path_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(path_frame, 
                 text="Путь для сканирования:",
                 style='Status.TLabel').pack(side=tk.LEFT)
        
        self.path_var = tk.StringVar()
        self.path_entry = ttk.Entry(path_frame, 
                                  textvariable=self.path_var,
                                  font=('Arial', 10),
                                  state='readonly')
        self.path_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        # Статистика сканирования
        stats_frame = ttk.Frame(main_frame)
        stats_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.status_var = tk.StringVar()
        self.status_var.set("Готов к сканированию")
        ttk.Label(stats_frame, 
                 textvariable=self.status_var,
                 style='Status.TLabel').pack(side=tk.LEFT)
        
        self.threats_var = tk.StringVar()
        self.threats_var.set("Угроз обнаружено: 0")
        ttk.Label(stats_frame, 
                 textvariable=self.threats_var,
                 style='Status.TLabel').pack(side=tk.RIGHT)
        
        # Прогресс-бар
        self.progress = ttk.Progressbar(main_frame, 
                                      orient=tk.HORIZONTAL,
                                      length=100,
                                      mode='determinate',
                                      style='Green.Horizontal.TProgressbar')
        self.progress.pack(fill=tk.X, pady=(0, 10))
        
        # Таблица результатов
        results_frame = ttk.Frame(main_frame)
        results_frame.pack(fill=tk.BOTH, expand=True)
        
        self.tree = ttk.Treeview(results_frame, 
                                columns=('file', 'status', 'hash', 'time'),
                                show='headings',
                                selectmode='extended')
        
        self.tree.heading('file', text='Файл')
        self.tree.heading('status', text='Статус')
        self.tree.heading('hash', text='MD5 хеш')
        self.tree.heading('time', text='Время проверки')
        
        self.tree.column('file', width=400, anchor=tk.W)
        self.tree.column('status', width=150, anchor=tk.W)
        self.tree.column('hash', width=200, anchor=tk.W)
        self.tree.column('time', width=150, anchor=tk.W)
        
        scroll_y = ttk.Scrollbar(results_frame, orient=tk.VERTICAL, command=self.tree.yview)
        scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.configure(yscrollcommand=scroll_y.set)
        
        scroll_x = ttk.Scrollbar(results_frame, orient=tk.HORIZONTAL, command=self.tree.xview)
        scroll_x.pack(side=tk.BOTTOM, fill=tk.X)
        self.tree.configure(xscrollcommand=scroll_x.set)
        
        self.tree.pack(fill=tk.BOTH, expand=True)
        
        # Контекстное меню
        self.context_menu = tk.Menu(self.root, tearoff=0)
        self.context_menu.add_command(label="Показать детали", command=self.show_details)
        self.context_menu.add_command(label="Удалить файл", command=self.delete_file)
        self.context_menu.add_command(label="Добавить в исключения", command=self.add_exception)
        
        self.tree.bind("<Button-3>", self.show_context_menu)
        
        # Статус бар
        self.status_bar = ttk.Frame(main_frame)
        self.status_bar.pack(fill=tk.X, pady=(10, 0))
        
        self.last_update_var = tk.StringVar()
        self.last_update_var.set("Последнее обновление: никогда")
        ttk.Label(self.status_bar, 
                 textvariable=self.last_update_var,
                 style='Status.TLabel').pack(side=tk.LEFT)
        
        self.db_status_var = tk.StringVar()
        self.db_status_var.set("База сигнатур: загружено " + str(len(self.malware_db)) + " записей")
        ttk.Label(self.status_bar, 
                 textvariable=self.db_status_var,
                 style='Status.TLabel').pack(side=tk.RIGHT)

    def select_file(self):
        """Выбор файла для сканирования"""
        file_path = filedialog.askopenfilename()
        if file_path:
            self.path_var.set(file_path)
            self.scan_btn.config(state=tk.NORMAL)
            self.clear_results()

    def select_directory(self):
        """Выбор папки для сканирования"""
        dir_path = filedialog.askdirectory()
        if dir_path:
            self.path_var.set(dir_path)
            self.scan_btn.config(state=tk.NORMAL)
            self.clear_results()

    def clear_results(self):
        """Очистка результатов предыдущего сканирования"""
        for item in self.tree.get_children():
            self.tree.delete(item)
        self.threats_found = 0
        self.threats_var.set(f"Угроз обнаружено: {self.threats_found}")
        self.progress['value'] = 0
        self.status_var.set("Готов к сканированию")

    def start_scan(self):
        """Запуск сканирования"""
        path = self.path_var.get()
        if not path:
            messagebox.showwarning("Ошибка", "Выберите файл или папку для сканирования")
            return
        
        self.scanning = True
        self.stop_requested = False
        self.total_files = 0
        self.scanned_files = 0
        self.threats_found = 0
        
        self.select_file_btn.config(state=tk.DISABLED)
        self.select_folder_btn.config(state=tk.DISABLED)
        self.scan_btn.config(state=tk.DISABLED)
        self.stop_btn.config(state=tk.NORMAL)
        
        self.status_var.set("Подготовка к сканированию...")
        self.progress['style'] = 'Green.Horizontal.TProgressbar'
        
        # Запуск сканирования в отдельном потоке
        scan_thread = Thread(target=self.perform_scan, args=(path,))
        scan_thread.start()

    def stop_scan(self):
        """Остановка сканирования"""
        self.stop_requested = True
        self.status_var.set("Остановка сканирования...")

    def perform_scan(self, path):
        """Выполнение сканирования"""
        try:
            if os.path.isfile(path):
                self.total_files = 1
                self.scan_file(path)
            else:
                self.total_files = self.count_files(path)
                if self.total_files == 0:
                    self.root.after(0, lambda: messagebox.showinfo(
                        "Информация", 
                        "В папке нет файлов для сканирования"))
                    return
                
                for root, _, files in os.walk(path):
                    for file in files:
                        if self.stop_requested:
                            break
                        
                        file_path = os.path.join(root, file)
                        self.scan_file(file_path)
                        self.scanned_files += 1
                        
                        # Обновление прогресса
                        progress = (self.scanned_files / self.total_files) * 100
                        self.root.after(0, lambda: self.update_progress(
                            progress, 
                            f"Сканирование... {self.scanned_files}/{self.total_files} файлов"))
            
            if not self.stop_requested:
                self.root.after(0, lambda: self.status_var.set(
                    f"Сканирование завершено. Найдено угроз: {self.threats_found}"))
                self.root.after(0, lambda: messagebox.showinfo(
                    "Готово", 
                    f"Сканирование завершено\nПроверено файлов: {self.scanned_files}\nНайдено угроз: {self.threats_found}"))
        
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror(
                "Ошибка", 
                f"Ошибка при сканировании: {str(e)}"))
        
        finally:
            self.scanning = False
            self.root.after(0, self.enable_controls)

    def count_files(self, path):
        """Подсчет количества файлов в папке"""
        count = 0
        for _, _, files in os.walk(path):
            count += len(files)
        return count

    def scan_file(self, file_path):
        """Проверка одного файла"""
        try:
            md5_hash = self.calculate_md5(file_path)
            current_time = datetime.now().strftime("%H:%M:%S")
            
            if md5_hash in self.malware_db:
                status = "ВРЕДОНОСНЫЙ"
                virus_name = self.malware_db[md5_hash]
                self.threats_found += 1
                self.root.after(0, lambda: self.add_result(
                    file_path, f"{status} ({virus_name})", md5_hash, current_time, True))
            else:
                status = "Безопасный"
                self.root.after(0, lambda: self.add_result(
                    file_path, status, md5_hash, current_time, False))
        
        except PermissionError:
            self.root.after(0, lambda: self.add_result(
                file_path, "ОШИБКА: Нет доступа", "", datetime.now().strftime("%H:%M:%S"), False))
        
        except Exception as e:
            self.root.after(0, lambda: self.add_result(
                file_path, f"ОШИБКА: {str(e)}", "", datetime.now().strftime("%H:%M:%S"), False))

    def calculate_md5(self, file_path):
        """Вычисление MD5 хеша файла"""
        hash_md5 = hashlib.md5()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()

    def add_result(self, file_path, status, md5_hash, time, is_threat):
        """Добавление результата в таблицу"""
        item = self.tree.insert("", tk.END, values=(file_path, status, md5_hash, time))
        
        if "ВРЕДОНОСНЫЙ" in status:
            self.tree.tag_configure('threat', background='#ffdddd')
            self.tree.item(item, tags=('threat',))
            self.progress['style'] = 'Red.Horizontal.TProgressbar'
        elif "ОШИБКА" in status:
            self.tree.tag_configure('error', background='#fff3cd')
            self.tree.item(item, tags=('error',))
        
        self.threats_var.set(f"Угроз обнаружено: {self.threats_found}")
        self.tree.see(item)

    def update_progress(self, value, status):
        """Обновление прогресса и статуса"""
        self.progress['value'] = value
        self.status_var.set(status)

    def enable_controls(self):
        """Включение элементов управления после сканирования"""
        self.select_file_btn.config(state=tk.NORMAL)
        self.select_folder_btn.config(state=tk.NORMAL)
        self.scan_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)

    def show_context_menu(self, event):
        """Показать контекстное меню"""
        item = self.tree.identify_row(event.y)
        if item:
            self.tree.selection_set(item)
            self.context_menu.post(event.x_root, event.y_root)

    def show_details(self):
        """Показать детали выбранного файла"""
        selected = self.tree.selection()
        if selected:
            item = self.tree.item(selected[0])
            details = f"Файл: {item['values'][0]}\nСтатус: {item['values'][1]}\nMD5: {item['values'][2]}"
            messagebox.showinfo("Детали файла", details)

    def delete_file(self):
        """Удалить выбранный файл"""
        selected = self.tree.selection()
        if selected:
            item = self.tree.item(selected[0])
            file_path = item['values'][0]
            
            if messagebox.askyesno("Подтверждение", f"Вы уверены, что хотите удалить файл?\n{file_path}"):
                try:
                    os.remove(file_path)
                    self.tree.delete(selected[0])
                    messagebox.showinfo("Успех", "Файл успешно удален")
                except Exception as e:
                    messagebox.showerror("Ошибка", f"Не удалось удалить файл: {str(e)}")

    def add_exception(self):
        """Добавить файл в исключения"""
        selected = self.tree.selection()
        if selected:
            item = self.tree.item(selected[0])
            md5_hash = item['values'][2]
            
            if md5_hash and md5_hash in self.malware_db:
                del self.malware_db[md5_hash]
                self.db_status_var.set(f"База сигнатур: загружено {len(self.malware_db)} записей")
                messagebox.showinfo("Успех", "Файл добавлен в исключения")
            else:
                messagebox.showinfo("Информация", "Нельзя добавить безопасный файл в исключения")

if __name__ == "__main__":
    root = tk.Tk()
    app = AntivirusApp(root)
    root.mainloop()