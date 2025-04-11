import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, filedialog
import socket
import requests
from threading import Thread
from queue import Queue
from PIL import Image, ImageTk
import io
import json
import os
from datetime import datetime

class CameraScannerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Advanced Camera Scanner (Port 8000)")
        self.root.geometry("1000x750")
        
        # Очередь для межпоточного взаимодействия
        self.queue = Queue()
        
        # Результаты сканирования
        self.scan_results = []
        
        # Создание интерфейса
        self.create_widgets()
        
        # Проверка очереди сообщений
        self.check_queue()
        
        # Загрузка конфигурации
        self.load_config()
    
    def create_widgets(self):
        # Основные фреймы
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Фрейм для ввода IP-адресов
        input_frame = ttk.LabelFrame(main_frame, text="Ввод IP-адресов", padding="10")
        input_frame.pack(fill=tk.X, pady=5)
        
        self.ip_entry = ttk.Entry(input_frame, width=40)
        self.ip_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        self.ip_entry.insert(0, "192.168.1.1-192.168.1.255")  # Пример по умолчанию
        
        scan_btn = ttk.Button(input_frame, text="Сканировать", command=self.start_scan)
        scan_btn.pack(side=tk.LEFT, padx=5)
        
        save_btn = ttk.Button(input_frame, text="Сохранить результаты", command=self.save_results)
        save_btn.pack(side=tk.LEFT, padx=5)
        
        # Фрейм для настроек
        settings_frame = ttk.LabelFrame(main_frame, text="Настройки", padding="10")
        settings_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(settings_frame, text="Таймаут (сек):").pack(side=tk.LEFT)
        self.timeout_var = tk.StringVar(value="2")
        ttk.Entry(settings_frame, textvariable=self.timeout_var, width=5).pack(side=tk.LEFT, padx=5)
        
        ttk.Label(settings_frame, text="Потоки:").pack(side=tk.LEFT, padx=(10, 0))
        self.threads_var = tk.StringVar(value="10")
        ttk.Entry(settings_frame, textvariable=self.threads_var, width=5).pack(side=tk.LEFT)
        
        self.auto_vuln_check = tk.BooleanVar(value=True)
        ttk.Checkbutton(settings_frame, text="Автопроверка уязвимостей", variable=self.auto_vuln_check).pack(side=tk.LEFT, padx=10)
        
        # Фрейм для результатов
        result_frame = ttk.LabelFrame(main_frame, text="Результаты сканирования", padding="10")
        result_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        columns = ("IP", "Status", "Model", "Credentials", "Vulnerabilities")
        self.tree = ttk.Treeview(result_frame, columns=columns, show="headings")
        
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=120, stretch=True)
        
        self.tree.column("IP", width=120)
        self.tree.column("Vulnerabilities", width=200)
        
        scrollbar = ttk.Scrollbar(result_frame, orient="vertical", command=self.tree.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.pack(fill=tk.BOTH, expand=True)
        
        # Контекстное меню для дерева
        self.tree_menu = tk.Menu(self.root, tearoff=0)
        self.tree_menu.add_command(label="Проверить уязвимости", command=self.check_vulnerabilities)
        self.tree_menu.add_command(label="Получить скриншот", command=self.get_screenshot)
        self.tree_menu.add_command(label="Копировать IP", command=self.copy_ip)
        self.tree.bind("<Button-3>", self.show_tree_menu)
        
        # Фрейм для логов
        log_frame = ttk.LabelFrame(main_frame, text="Лог", padding="10")
        log_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        self.log_area = scrolledtext.ScrolledText(log_frame, wrap=tk.WORD, width=80, height=10)
        self.log_area.pack(fill=tk.BOTH, expand=True)
        
        # Окно для просмотра скриншотов
        self.screenshot_window = None
    
    def load_config(self):
        # Загрузка стандартных учетных данных из файла
        try:
            with open("credentials.json", "r") as f:
                self.credentials = json.load(f)
            self.log("Загружены стандартные учетные данные")
        except:
            self.credentials = [
                {"username": "admin", "password": "admin"},
                {"username": "admin", "password": "12345"},
                {"username": "admin", "password": "123456"},
                {"username": "admin", "password": "password"},
                {"username": "root", "password": "root"},
                {"username": "root", "password": "12345"},
                {"username": "user", "password": "user"},
            ]
            self.log("Используются стандартные учетные данные по умолчанию")
    
    def show_tree_menu(self, event):
        item = self.tree.identify_row(event.y)
        if item:
            self.tree.selection_set(item)
            self.tree_menu.post(event.x_root, event.y_root)
    
    def start_scan(self):
        ip_range = self.ip_entry.get()
        if not ip_range:
            messagebox.showerror("Ошибка", "Введите диапазон IP-адресов")
            return
        
        # Очистка предыдущих результатов
        for item in self.tree.get_children():
            self.tree.delete(item)
        self.scan_results = []
        
        # Получение настроек
        try:
            timeout = float(self.timeout_var.get())
            max_threads = int(self.threads_var.get())
        except ValueError:
            messagebox.showerror("Ошибка", "Некорректные значения таймаута или количества потоков")
            return
        
        # Запуск сканирования в отдельных потоках
        self.log(f"Начало сканирования с {max_threads} потоками и таймаутом {timeout} сек...")
        
        # Генерация списка IP-адресов
        ips = self.generate_ip_list(ip_range)
        
        # Создание и запуск потоков
        self.threads = []
        self.ip_queue = Queue()
        
        for ip in ips:
            self.ip_queue.put(ip)
        
        for _ in range(min(max_threads, len(ips))):
            t = Thread(target=self.scan_worker, args=(timeout,), daemon=True)
            t.start()
            self.threads.append(t)
    
    def generate_ip_list(self, ip_range):
        ips = []
        
        if "-" in ip_range:
            start_ip, end_ip = ip_range.split("-")
            start = list(map(int, start_ip.split(".")))
            end = list(map(int, end_ip.split(".")))
            
            for a in range(start[0], end[0]+1):
                for b in range(start[1], end[1]+1):
                    for c in range(start[2], end[2]+1):
                        for d in range(start[3], end[3]+1):
                            ips.append(f"{a}.{b}.{c}.{d}")
        else:
            ips = [ip_range]
        
        return ips
    
    def scan_worker(self, timeout):
        while not self.ip_queue.empty():
            ip = self.ip_queue.get()
            
            try:
                if self.is_camera_online(ip, 8000, timeout):
                    self.queue.put(("add_ip", ip))
                    
                    # Проверка учетных данных
                    creds = self.check_default_credentials(ip, timeout)
                    
                    # Определение модели камеры
                    model = self.detect_camera_model(ip, timeout, creds)
                    
                    # Проверка уязвимостей (если включено)
                    vulns = []
                    if self.auto_vuln_check.get():
                        vulns = self.check_all_vulnerabilities(ip, timeout, creds)
                    
                    # Сохранение результатов
                    result = {
                        "ip": ip,
                        "status": "Online",
                        "model": model,
                        "credentials": creds,
                        "vulnerabilities": vulns,
                        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    }
                    self.scan_results.append(result)
                    
                    self.queue.put(("update_result", ip, model, creds, vulns))
                else:
                    self.queue.put(("log", f"{ip} - не отвечает"))
            except Exception as e:
                self.queue.put(("log", f"Ошибка при сканировании {ip}: {str(e)}"))
            
            self.ip_queue.task_done()
    
    def is_camera_online(self, ip, port, timeout):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(timeout)
                result = s.connect_ex((ip, port))
                return result == 0
        except:
            return False
    
    def check_default_credentials(self, ip, timeout):
        for cred in self.credentials:
            username = cred["username"]
            password = cred["password"]
            
            if self.try_login(ip, username, password, timeout):
                return f"{username}:{password}"
        
        return "Не найдены"
    
    def try_login(self, ip, username, password, timeout):
        try:
            # Попробуем несколько популярных конечных точек
            endpoints = [
                "/",
                "/liveview.shtml",
                "/cgi-bin/main.cgi",
                "/ISAPI/System/deviceInfo"
            ]
            
            for endpoint in endpoints:
                url = f"http://{ip}:8000{endpoint}"
                try:
                    response = requests.get(url, auth=(username, password), timeout=timeout)
                    if response.status_code == 200:
                        return True
                except:
                    continue
        except:
            pass
        
        return False
    
    def detect_camera_model(self, ip, timeout, credentials):
        if credentials == "Не найдены":
            return "Неизвестно (нет доступа)"
        
        try:
            username, password = credentials.split(":")
            
            # Попробуем получить информацию о устройстве
            urls = [
                f"http://{ip}:8000/ISAPI/System/deviceInfo",
                f"http://{ip}:8000/cgi-bin/magicBox.cgi?action=getSystemInfo",
                f"http://{ip}:8000/cgi-bin/global.cgi?action=getInfo"
            ]
            
            for url in urls:
                try:
                    response = requests.get(url, auth=(username, password), timeout=timeout)
                    if response.status_code == 200:
                        # Попробуем найти модель в ответе
                        content = response.text.lower()
                        if "hikvision" in content:
                            return "Hikvision"
                        elif "dahua" in content:
                            return "Dahua"
                        elif "axis" in content:
                            return "Axis"
                        
                        # Парсинг XML (для Hikvision)
                        if "<model>" in content:
                            start = content.find("<model>") + len("<model>")
                            end = content.find("</model>")
                            if start != -1 and end != -1:
                                return content[start:end].strip().capitalize()
                except:
                    continue
            
            return "Неизвестно (модель не определена)"
        except:
            return "Неизвестно (ошибка определения)"
    
    def check_all_vulnerabilities(self, ip, timeout, credentials):
        vulns = []
        
        # 1. Проверка на открытый RTSP-порт
        if self.is_camera_online(ip, 554, timeout):
            vulns.append("Открытый RTSP-порт (554)")
        
        # 2. Проверка на уязвимость CVE-2021-36260 (Hikvision)
        if self.check_cve_2021_36260(ip, timeout):
            vulns.append("CVE-2021-36260 (Hikvision RCE)")
        
        # 3. Проверка на уязвимость CVE-2017-7921 (Hikvision)
        if self.check_cve_2017_7921(ip, timeout, credentials):
            vulns.append("CVE-2017-7921 (Hikvision auth bypass)")
        
        return ", ".join(vulns) if vulns else "Не найдены"
    
    def check_cve_2021_36260(self, ip, timeout):
        try:
            url = f"http://{ip}:8000/ISAPI/System/deviceInfo"
            response = requests.put(url, data="<xml>test</xml>", timeout=timeout)
            return response.status_code == 500 and "Hikvision" in response.text
        except:
            return False
    
    def check_cve_2017_7921(self, ip, timeout, credentials):
        if credentials != "Не найдены":
            return False
            
        try:
            url = f"http://{ip}:8000/ISAPI/Security/userCheck"
            response = requests.get(url, timeout=timeout)
            return response.status_code == 200 and "anonymous" in response.text.lower()
        except:
            return False
    
    def check_vulnerabilities(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Предупреждение", "Выберите камеру из списка")
            return
        
        ip = self.tree.item(selected[0])["values"][0]
        credentials = self.tree.item(selected[0])["values"][3]
        
        Thread(target=self._check_vulnerabilities, args=(ip, credentials), daemon=True).start()
    
    def _check_vulnerabilities(self, ip, credentials):
        self.queue.put(("log", f"Проверка уязвимостей для {ip}..."))
        
        timeout = float(self.timeout_var.get())
        vulns = self.check_all_vulnerabilities(ip, timeout, credentials)
        
        self.queue.put(("update_vulnerabilities", ip, vulns))
        self.queue.put(("log", f"Результаты проверки уязвимостей для {ip}: {vulns}"))
    
    def get_screenshot(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Предупреждение", "Выберите камеру из списка")
            return
        
        ip = self.tree.item(selected[0])["values"][0]
        credentials = self.tree.item(selected[0])["values"][3]
        
        if credentials == "Не найдены":
            messagebox.showwarning("Предупреждение", "Не удалось найти учетные данные для этой камеры")
            return
        
        username, password = credentials.split(":")
        Thread(target=self._get_screenshot, args=(ip, username, password), daemon=True).start()
    
    def _get_screenshot(self, ip, username, password):
        try:
            timeout = float(self.timeout_var.get())
            
            # Попробуем несколько популярных конечных точек для скриншотов
            endpoints = [
                f"http://{ip}:8000/ISAPI/Streaming/channels/101/picture",  # Hikvision
                f"http://{ip}:8000/cgi-bin/snapshot.cgi",  # Dahua
                f"http://{ip}:8000/axis-cgi/jpg/image.cgi"  # Axis
            ]
            
            for url in endpoints:
                try:
                    response = requests.get(url, auth=(username, password), timeout=timeout)
                    if response.status_code == 200 and 'image' in response.headers.get('Content-Type', ''):
                        img = Image.open(io.BytesIO(response.content))
                        self.queue.put(("show_screenshot", ip, img))
                        return
                except:
                    continue
            
            self.queue.put(("log", f"Не удалось получить скриншот с {ip}"))
        except Exception as e:
            self.queue.put(("log", f"Ошибка при получении скриншота: {str(e)}"))
    
    def show_screenshot(self, ip, img):
        if self.screenshot_window is None or not tk.Toplevel.winfo_exists(self.screenshot_window):
            self.screenshot_window = tk.Toplevel(self.root)
            self.screenshot_window.title(f"Скриншот с {ip}")
            self.screenshot_window.geometry("800x600")
            
            self.screenshot_label = ttk.Label(self.screenshot_window)
            self.screenshot_label.pack(fill=tk.BOTH, expand=True)
            
            save_btn = ttk.Button(self.screenshot_window, text="Сохранить", 
                                 command=lambda: self.save_screenshot(ip, img))
            save_btn.pack(pady=5)
        
        # Масштабирование изображения под окно
        width, height = 800, 550
        img.thumbnail((width, height))
        photo = ImageTk.PhotoImage(img)
        
        self.screenshot_label.configure(image=photo)
        self.screenshot_label.image = photo
    
    def save_screenshot(self, ip, img):
        filename = f"screenshot_{ip}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
        filepath = filedialog.asksaveasfilename(
            initialfile=filename,
            defaultextension=".jpg",
            filetypes=[("JPEG Image", "*.jpg"), ("All Files", "*.*")]
        )
        
        if filepath:
            try:
                img.save(filepath)
                self.log(f"Скриншот сохранен как {filepath}")
            except Exception as e:
                self.log(f"Ошибка при сохранении скриншота: {str(e)}")
    
    def save_results(self):
        if not self.scan_results:
            messagebox.showwarning("Предупреждение", "Нет результатов для сохранения")
            return
        
        filename = f"scan_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        filepath = filedialog.asksaveasfilename(
            initialfile=filename,
            defaultextension=".json",
            filetypes=[("JSON Files", "*.json"), ("All Files", "*.*")]
        )
        
        if filepath:
            try:
                with open(filepath, "w") as f:
                    json.dump(self.scan_results, f, indent=4)
                self.log(f"Результаты сохранены в {filepath}")
            except Exception as e:
                self.log(f"Ошибка при сохранении результатов: {str(e)}")
    
    def copy_ip(self):
        selected = self.tree.selection()
        if selected:
            ip = self.tree.item(selected[0])["values"][0]
            self.root.clipboard_clear()
            self.root.clipboard_append(ip)
            self.log(f"IP-адрес {ip} скопирован в буфер обмена")
    
    def log(self, message):
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_area.insert(tk.END, f"[{timestamp}] {message}\n")
        self.log_area.see(tk.END)
    
    def check_queue(self):
        while not self.queue.empty():
            task = self.queue.get()
            
            if task[0] == "add_ip":
                self.tree.insert("", tk.END, values=(task[1], "Online", "Проверка...", "Проверка...", "Проверка..."))
            
            elif task[0] == "update_result":
                for item in self.tree.get_children():
                    if self.tree.item(item)["values"][0] == task[1]:
                        values = list(self.tree.item(item)["values"])
                        values[2] = task[2]  # Model
                        values[3] = task[3]  # Credentials
                        values[4] = task[4]  # Vulnerabilities
                        self.tree.item(item, values=values)
                        break
            
            elif task[0] == "update_vulnerabilities":
                for item in self.tree.get_children():
                    if self.tree.item(item)["values"][0] == task[1]:
                        values = list(self.tree.item(item)["values"])
                        values[4] = task[2]  # Vulnerabilities
                        self.tree.item(item, values=values)
                        
                        # Обновим также в scan_results
                        for result in self.scan_results:
                            if result["ip"] == task[1]:
                                result["vulnerabilities"] = task[2]
                                break
                        break
            
            elif task[0] == "log":
                self.log(task[1])
            
            elif task[0] == "show_screenshot":
                self.show_screenshot(task[1], task[2])
        
        self.root.after(100, self.check_queue)

if __name__ == "__main__":
    root = tk.Tk()
    app = CameraScannerApp(root)
    root.mainloop()