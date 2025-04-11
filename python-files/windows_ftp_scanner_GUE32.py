import ftplib
import socket
import threading
import ipaddress
from tkinter import *
from tkinter import ttk, messagebox, filedialog
from queue import Queue

class AdvancedFTPScanner:
    def __init__(self, master):
        self.master = master
        master.title("Advanced FTP Scanner v4.0")
        master.geometry("900x700")
        
        # Очередь для потока сканирования
        self.scan_queue = Queue()
        
        # Настройки
        self.scanning = False
        self.thread_count = 20
        self.timeout = 5
        self.credentials = [("anonymous", ""), ("admin", "admin"), ("ftp", "ftp")]
        
        # Создание интерфейса
        self.create_widgets()
        self.status("Готов к работе")

    def create_widgets(self):
        # Главный контейнер
        main_frame = ttk.Frame(self.master, padding=10)
        main_frame.pack(fill=BOTH, expand=True)
        
        # Вкладки
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill=BOTH, expand=True)
        
        # Вкладка одиночного сканирования
        self.create_single_scan_tab()
        
        # Вкладка диапазона IP
        self.create_range_scan_tab()
        
        # Вкладка списка IP
        self.create_list_scan_tab()
        
        # Результаты
        self.create_results_section(main_frame)
        
        # Статус бар
        self.status_bar = ttk.Label(self.master, relief=SUNKEN, anchor=W)
        self.status_bar.pack(fill=X, side=BOTTOM)

    def create_single_scan_tab(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Одиночное сканирование")
        
        ttk.Label(tab, text="Цель (IP/домен):").grid(row=0, column=0, sticky=W, pady=5)
        self.single_target = ttk.Entry(tab, width=25)
        self.single_target.grid(row=0, column=1, padx=5, pady=5)
        self.single_target.insert(0, "127.0.0.1")
        
        ttk.Label(tab, text="Порт:").grid(row=0, column=2, sticky=W, pady=5)
        self.single_port = ttk.Entry(tab, width=8)
        self.single_port.grid(row=0, column=3, pady=5)
        self.single_port.insert(0, "21")
        
        ttk.Button(tab, text="Сканировать", 
                  command=lambda: self.start_scan([self.single_target.get()], 
                                                int(self.single_port.get()))).grid(row=1, column=0, columnspan=4, pady=10)

    def create_range_scan_tab(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Диапазон IP")
        
        ttk.Label(tab, text="Начальный IP:").grid(row=0, column=0, sticky=W, pady=5)
        self.start_ip = ttk.Entry(tab, width=15)
        self.start_ip.grid(row=0, column=1, padx=5, pady=5)
        self.start_ip.insert(0, "192.168.1.1")
        
        ttk.Label(tab, text="Конечный IP:").grid(row=0, column=2, sticky=W, pady=5)
        self.end_ip = ttk.Entry(tab, width=15)
        self.end_ip.grid(row=0, column=3, pady=5)
        self.end_ip.insert(0, "192.168.1.10")
        
        ttk.Label(tab, text="Порт:").grid(row=1, column=0, sticky=W, pady=5)
        self.range_port = ttk.Entry(tab, width=8)
        self.range_port.grid(row=1, column=1, pady=5)
        self.range_port.insert(0, "21")
        
        ttk.Label(tab, text="Потоков:").grid(row=1, column=2, sticky=W, pady=5)
        self.thread_count_entry = ttk.Entry(tab, width=8)
        self.thread_count_entry.grid(row=1, column=3, pady=5)
        self.thread_count_entry.insert(0, str(self.thread_count))
        
        ttk.Button(tab, text="Сканировать диапазон", 
                  command=self.start_range_scan).grid(row=2, column=0, columnspan=4, pady=10)

    def create_list_scan_tab(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Список IP")
        
        self.ip_list = Text(tab, height=10, width=40)
        self.ip_list.grid(row=0, column=0, columnspan=2, padx=5, pady=5)
        self.ip_list.insert(END, "192.168.1.1\n192.168.1.2\n192.168.1.3")
        
        ttk.Label(tab, text="Порт:").grid(row=1, column=0, sticky=W, pady=5)
        self.list_port = ttk.Entry(tab, width=8)
        self.list_port.grid(row=1, column=1, pady=5, sticky=W)
        self.list_port.insert(0, "21")
        
        btn_frame = ttk.Frame(tab)
        btn_frame.grid(row=2, column=0, columnspan=2, pady=10)
        
        ttk.Button(btn_frame, text="Загрузить из файла", 
                  command=self.load_ip_list).pack(side=LEFT, padx=5)
        ttk.Button(btn_frame, text="Сканировать список", 
                  command=self.start_list_scan).pack(side=LEFT, padx=5)

    def create_results_section(self, parent):
        result_frame = ttk.LabelFrame(parent, text="Результаты", padding=10)
        result_frame.pack(fill=BOTH, expand=True)
        
        # Таблица результатов
        self.result_tree = ttk.Treeview(result_frame, columns=("IP", "Port", "Status", "Anonymous", "Credentials", "Files"), show="headings")
        
        # Настройка колонок
        columns = [
            ("IP", 120),
            ("Port", 60),
            ("Status", 100),
            ("Anonymous", 100),
            ("Credentials", 150),
            ("Files", 250)
        ]
        
        for col, width in columns:
            self.result_tree.heading(col, text=col)
            self.result_tree.column(col, width=width)
        
        scrollbar = ttk.Scrollbar(result_frame, orient=VERTICAL, command=self.result_tree.yview)
        self.result_tree.configure(yscrollcommand=scrollbar.set)
        
        scrollbar.pack(side=RIGHT, fill=Y)
        self.result_tree.pack(fill=BOTH, expand=True)
        
        # Прогресс-бар
        self.progress = ttk.Progressbar(result_frame, orient=HORIZONTAL, mode='determinate')
        self.progress.pack(fill=X, pady=5)
        
        # Кнопки управления
        btn_frame = ttk.Frame(parent)
        btn_frame.pack(fill=X, pady=5)
        
        ttk.Button(btn_frame, text="Очистить результаты", 
                  command=self.clear_results).pack(side=LEFT, padx=5)
        ttk.Button(btn_frame, text="Экспорт в CSV", 
                  command=self.export_results).pack(side=LEFT, padx=5)
        
        # Чекбоксы
        options_frame = ttk.Frame(parent)
        options_frame.pack(fill=X, pady=5)
        
        self.anon_var = IntVar(value=1)
        ttk.Checkbutton(options_frame, text="Проверять анонимный вход", 
                       variable=self.anon_var).pack(side=LEFT, padx=10)
        
        self.brute_var = IntVar(value=0)
        ttk.Checkbutton(options_frame, text="Пробовать стандартные учетные данные", 
                       variable=self.brute_var).pack(side=LEFT, padx=10)
        
        self.files_var = IntVar(value=0)
        ttk.Checkbutton(options_frame, text="Получать список файлов", 
                       variable=self.files_var).pack(side=LEFT, padx=10)

    def status(self, message):
        self.status_bar.config(text=message)
        self.master.update_idletasks()
    
    def clear_results(self):
        self.result_tree.delete(*self.result_tree.get_children())
        self.status("Результаты очищены")
    
    def load_ip_list(self):
        filepath = filedialog.askopenfilename(filetypes=[("Text files", "*.txt"), ("All files", "*.*")])
        if filepath:
            try:
                with open(filepath, 'r') as f:
                    self.ip_list.delete(1.0, END)
                    self.ip_list.insert(END, f.read())
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось загрузить файл: {str(e)}")
    
    def start_range_scan(self):
        try:
            start_ip = self.start_ip.get()
            end_ip = self.end_ip.get()
            port = int(self.range_port.get())
            self.thread_count = int(self.thread_count_entry.get())
            
            # Генерация списка IP
            start = ipaddress.IPv4Address(start_ip)
            end = ipaddress.IPv4Address(end_ip)
            
            targets = []
            current = start
            while current <= end:
                targets.append(str(current))
                current += 1
            
            self.start_scan(targets, port)
            
        except Exception as e:
            messagebox.showerror("Ошибка", f"Некорректный диапазон IP: {str(e)}")
    
    def start_list_scan(self):
        targets = self.ip_list.get(1.0, END).strip().split('\n')
        targets = [ip.strip() for ip in targets if ip.strip()]
        port = int(self.list_port.get())
        self.start_scan(targets, port)
    
    def start_scan(self, targets, port):
        if self.scanning:
            return
            
        if not targets:
            messagebox.showwarning("Ошибка", "Нет целей для сканирования")
            return
        
        self.scanning = True
        self.clear_results()
        self.progress['maximum'] = len(targets)
        self.progress['value'] = 0
        self.status(f"Сканирование {len(targets)} целей...")
        
        # Добавляем задачи в очередь
        for target in targets:
            self.scan_queue.put((target, port))
        
        # Запускаем потоки сканирования
        for _ in range(min(self.thread_count, len(targets))):
            thread = threading.Thread(target=self.scan_worker, daemon=True)
            thread.start()
    
    def scan_worker(self):
        while not self.scan_queue.empty() and self.scanning:
            target, port = self.scan_queue.get()
            
            try:
                result = self.scan_ftp(target, port)
                self.master.after(0, self.add_result, result)
            except Exception as e:
                self.master.after(0, self.add_result, {
                    'ip': target,
                    'port': port,
                    'status': f"Ошибка: {str(e)}",
                    'anonymous': "N/A",
                    'credentials': "N/A",
                    'files': "N/A"
                })
            
            self.master.after(0, self.update_progress)
            self.scan_queue.task_done()
        
        if self.scan_queue.empty():
            self.master.after(0, self.scan_complete)
    
    def scan_ftp(self, target, port):
        result = {
            'ip': target,
            'port': port,
            'status': "Неизвестно",
            'anonymous': "Нет",
            'credentials': "Нет",
            'files': "Нет"
        }
        
        try:
            # Проверка доступности порта
            with socket.create_connection((target, port), timeout=self.timeout):
                result['status'] = "Порт открыт"
                
                ftp = ftplib.FTP(timeout=self.timeout)
                ftp.connect(target, port)
                
                # Проверка анонимного входа
                if self.anon_var.get():
                    try:
                        ftp.login()
                        result['anonymous'] = "Да"
                        
                        # Получение списка файлов
                        if self.files_var.get():
                            try:
                                files = []
                                ftp.dir(files.append)
                                result['files'] = "\n".join(files[:5]) + ("..." if len(files) > 5 else "")
                            except:
                                result['files'] = "Ошибка чтения"
                        
                        ftp.quit()
                        return result
                    except ftplib.error_perm:
                        result['anonymous'] = "Нет"
                
                # Brute-force
                if self.brute_var.get():
                    for login, password in self.credentials:
                        try:
                            ftp = ftplib.FTP(timeout=self.timeout)
                            ftp.connect(target, port)
                            ftp.login(login, password)
                            result['credentials'] = f"{login}/{password}"
                            
                            # Получение списка файлов
                            if self.files_var.get():
                                try:
                                    files = []
                                    ftp.dir(files.append)
                                    result['files'] = "\n".join(files[:5]) + ("..." if len(files) > 5 else "")
                                except:
                                    result['files'] = "Ошибка чтения"
                            
                            ftp.quit()
                            break
                        except ftplib.error_perm:
                            continue
                        except:
                            break
                
                ftp.quit()
                return result
                
        except socket.timeout:
            result['status'] = "Таймаут"
        except ConnectionRefusedError:
            result['status'] = "Отклонено"
        except Exception as e:
            result['status'] = f"Ошибка: {str(e)}"
        
        return result
    
    def add_result(self, result):
        self.result_tree.insert("", "end", values=(
            result['ip'],
            result['port'],
            result['status'],
            result['anonymous'],
            result['credentials'],
            result['files']
        ))
    
    def update_progress(self):
        self.progress['value'] += 1
        self.status(f"Прогресс: {self.progress['value']}/{self.progress['maximum']}")
    
    def scan_complete(self):
        self.scanning = False
        self.status(f"Сканирование завершено. Проверено {self.progress['value']} целей.")
    
    def export_results(self):
        filepath = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            title="Сохранить результаты"
        )
        
        if not filepath:
            return
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                # Заголовки
                headers = ["IP", "Port", "Status", "Anonymous", "Credentials", "Files"]
                f.write(";".join(headers) + "\n")
                
                # Данные
                for item in self.result_tree.get_children():
                    values = self.result_tree.item(item, 'values')
                    f.write(";".join(str(v) for v in values) + "\n")
            
            messagebox.showinfo("Успешно", f"Результаты сохранены в {filepath}")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить файл: {str(e)}")

if __name__ == "__main__":
    root = Tk()
    try:
        app = AdvancedFTPScanner(root)
        root.mainloop()
    except Exception as e:
        print(f"Ошибка: {str(e)}")
        input("Нажмите Enter для выхода...")