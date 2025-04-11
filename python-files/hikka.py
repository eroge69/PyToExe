import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import socket
import ipaddress
import threading
import queue
from PIL import Image, ImageTk
import requests
from io import BytesIO
import os
import subprocess
import re
import winreg
import ctypes
import sys

class HikvisionScanner:
    def __init__(self, root):
        self.root = root
        self.root.title("Hikvision Camera Scanner")
        self.root.geometry("1000x700")
        
        # Установка иконки (замените путь на свой)
        try:
            self.root.iconbitmap(default=self.resource_path('icon.ico'))
        except:
            pass
        
        # Специфичные порты Hikvision
        self.hikvision_ports = [80, 8000, 554, 443, 8200]
        
        # Очередь для потокобезопасного обмена данными
        self.queue = queue.Queue()
        
        # Создание элементов GUI
        self.create_widgets()
        
        # Проверка обновлений очереди
        self.root.after(100, self.process_queue)
        
        # Проверка прав администратора
        self.check_admin()
    
    def resource_path(self, relative_path):
        """ Получает абсолютный путь к ресурсу """
        try:
            base_path = sys._MEIPASS
        except Exception:
            base_path = os.path.abspath(".")
        return os.path.join(base_path, relative_path)
    
    def check_admin(self):
        """ Проверяет, запущено ли приложение с правами администратора """
        try:
            is_admin = ctypes.windll.shell32.IsUserAnAdmin()
            if not is_admin:
                self.queue.put(('warning', "Для некоторых функций требуются права администратора"))
        except:
            pass
    
    def create_widgets(self):
        # Главный фрейм
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Фрейм ввода
        input_frame = ttk.LabelFrame(main_frame, text="Параметры сканирования", padding="10")
        input_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Ввод диапазона сети
        ttk.Label(input_frame, text="Диапазон сети:").grid(row=0, column=0, sticky=tk.W)
        self.range_entry = ttk.Entry(input_frame, width=20)
        self.range_entry.grid(row=0, column=1, sticky=tk.W, padx=5)
        self.range_entry.insert(0, "192.168.1.0/24")
        
        # Кнопка выбора из истории
        ttk.Button(input_frame, text="История", command=self.show_history).grid(row=0, column=2, padx=5)
        
        # Поле для логина/пароля
        ttk.Label(input_frame, text="Логин:").grid(row=1, column=0, sticky=tk.W)
        self.login_entry = ttk.Entry(input_frame, width=15)
        self.login_entry.grid(row=1, column=1, sticky=tk.W, padx=5)
        self.login_entry.insert(0, "admin")
        
        ttk.Label(input_frame, text="Пароль:").grid(row=1, column=2, sticky=tk.W)
        self.password_entry = ttk.Entry(input_frame, width=15, show="*")
        self.password_entry.grid(row=1, column=3, sticky=tk.W, padx=5)
        
        # Кнопки сканирования
        self.scan_button = ttk.Button(input_frame, text="Сканировать сеть", command=self.start_scan)
        self.scan_button.grid(row=0, column=4, padx=10)
        
        self.stop_button = ttk.Button(input_frame, text="Остановить", command=self.stop_scan, state=tk.DISABLED)
        self.stop_button.grid(row=0, column=5, padx=10)
        
        self.advanced_scan_button = ttk.Button(input_frame, text="Расширенное сканирование", command=self.start_advanced_scan)
        self.advanced_scan_button.grid(row=1, column=4, padx=10)
        
        # Прогресс-бар
        self.progress = ttk.Progressbar(main_frame, orient=tk.HORIZONTAL, mode='determinate')
        self.progress.pack(fill=tk.X, pady=(0, 10))
        
        # Фрейм результатов
        results_frame = ttk.LabelFrame(main_frame, text="Результаты сканирования", padding="10")
        results_frame.pack(fill=tk.BOTH, expand=True)
        
        # Таблица результатов
        self.tree = ttk.Treeview(results_frame, columns=('IP', 'Порт', 'Модель', 'Версия ПО', 'Статус', 'Доп. информация'), show='headings')
        self.tree.heading('IP', text='IP-адрес')
        self.tree.heading('Порт', text='Порт')
        self.tree.heading('Модель', text='Модель')
        self.tree.heading('Версия ПО', text='Версия ПО')
        self.tree.heading('Статус', text='Статус')
        self.tree.heading('Доп. информация', text='Доп. информация')
        
        self.tree.column('IP', width=120)
        self.tree.column('Порт', width=60)
        self.tree.column('Модель', width=150)
        self.tree.column('Версия ПО', width=100)
        self.tree.column('Статус', width=100)
        self.tree.column('Доп. информация', width=300)
        
        self.tree.pack(fill=tk.BOTH, expand=True, side=tk.LEFT)
        
        # Полоса прокрутки
        scrollbar = ttk.Scrollbar(results_frame, orient=tk.VERTICAL, command=self.tree.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        # Контекстное меню
        self.context_menu = tk.Menu(self.root, tearoff=0)
        self.context_menu.add_command(label="Открыть в браузере", command=self.open_in_browser)
        self.context_menu.add_command(label="Скопировать IP", command=self.copy_ip)
        self.context_menu.add_command(label="Проверить RTSP поток", command=self.check_rtsp)
        self.context_menu.add_command(label="Экспорт в CSV", command=self.export_to_csv)
        self.tree.bind("<Button-3>", self.show_context_menu)
        
        # Фрейм управления камерой
        control_frame = ttk.LabelFrame(main_frame, text="Управление камерой", padding="10")
        control_frame.pack(fill=tk.X, pady=(10, 0))
        
        # Элементы управления
        ttk.Button(control_frame, text="Получить снимок", command=self.get_snapshot).pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="Перезагрузить камеру", command=self.reboot_camera).pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="Сбросить настройки", command=self.reset_camera).pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="Обновить прошивку", command=self.update_firmware).pack(side=tk.LEFT, padx=5)
        
        # Фрейм предпросмотра
        preview_frame = ttk.LabelFrame(main_frame, text="Предпросмотр", padding="10")
        preview_frame.pack(fill=tk.BOTH, expand=True)
        
        self.preview_label = ttk.Label(preview_frame, text="Выберите камеру для предпросмотра")
        self.preview_label.pack(fill=tk.BOTH, expand=True)
        
        # Привязка выбора в таблице
        self.tree.bind('<<TreeviewSelect>>', self.show_preview)
        
        # Переменные управления сканированием
        self.scan_active = False
        self.scan_thread = None
    
    def show_history(self):
        """ Показывает историю сканирований """
        try:
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\HikvisionScanner") as key:
                history = []
                try:
                    i = 0
                    while True:
                        name, value, _ = winreg.EnumValue(key, i)
                        if name.startswith('scan_'):
                            history.append(value)
                        i += 1
                except WindowsError:
                    pass
                
                if history:
                    menu = tk.Menu(self.root, tearoff=0)
                    for item in history:
                        menu.add_command(label=item, command=lambda x=item: self.range_entry.delete(0, tk.END) or self.range_entry.insert(0, x))
                    menu.tk_popup(*self.root.winfo_pointerxy())
                else:
                    messagebox.showinfo("История", "История сканирований пуста")
        except WindowsError:
            messagebox.showinfo("История", "История сканирований пуста")
    
    def save_to_history(self, network_range):
        """ Сохраняет диапазон в историю """
        try:
            with winreg.CreateKey(winreg.HKEY_CURRENT_USER, r"Software\HikvisionScanner") as key:
                # Получаем количество существующих записей
                try:
                    count = 0
                    while True:
                        winreg.EnumValue(key, count)
                        count += 1
                except WindowsError:
                    pass
                
                # Сохраняем новую запись
                winreg.SetValueEx(key, f"scan_{count}", 0, winreg.REG_SZ, network_range)
        except:
            pass
    
    def start_scan(self):
        if self.scan_active:
            return
            
        # Получаем диапазон сети
        try:
            network = ipaddress.ip_network(self.range_entry.get().strip(), strict=False)
            self.save_to_history(self.range_entry.get().strip())
        except ValueError:
            messagebox.showerror("Ошибка", "Неверный диапазон сети")
            return
        
        # Очищаем предыдущие результаты
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Обновляем UI
        self.scan_button.config(state=tk.DISABLED)
        self.advanced_scan_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.progress['value'] = 0
        self.progress['maximum'] = len(list(network.hosts())) * len(self.hikvision_ports)
        
        # Запускаем сканирование в отдельном потоке
        self.scan_active = True
        self.scan_thread = threading.Thread(
            target=self.scan_network,
            args=(network, self.hikvision_ports, False),
            daemon=True
        )
        self.scan_thread.start()
    
    def start_advanced_scan(self):
        if self.scan_active:
            return
            
        # Получаем диапазон сети
        try:
            network = ipaddress.ip_network(self.range_entry.get().strip(), strict=False)
            self.save_to_history(self.range_entry.get().strip())
        except ValueError:
            messagebox.showerror("Ошибка", "Неверный диапазон сети")
            return
        
        # Очищаем предыдущие результаты
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Обновляем UI
        self.scan_button.config(state=tk.DISABLED)
        self.advanced_scan_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.progress['value'] = 0
        self.progress['maximum'] = len(list(network.hosts())) * (len(self.hikvision_ports) + 10)  # +10 для дополнительных проверок
        
        # Запускаем сканирование в отдельном потоке
        self.scan_active = True
        self.scan_thread = threading.Thread(
            target=self.scan_network,
            args=(network, self.hikvision_ports, True),
            daemon=True
        )
        self.scan_thread.start()
    
    def stop_scan(self):
        self.scan_active = False
        if self.scan_thread and self.scan_thread.is_alive():
            self.scan_thread.join(timeout=1)
        self.scan_button.config(state=tk.NORMAL)
        self.advanced_scan_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
    
    def scan_network(self, network, ports, advanced=False):
        total_hosts = len(list(network.hosts()))
        scanned_hosts = 0
        
        for ip in network.hosts():
            if not self.scan_active:
                break
                
            ip_str = str(ip)
            
            for port in ports:
                if not self.scan_active:
                    break
                
                try:
                    # Пытаемся подключиться к порту
                    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                        s.settimeout(1)
                        result = s.connect_ex((ip_str, port))
                        
                        if result == 0:
                            # Порт открыт, пытаемся идентифицировать камеру
                            model, version, status, info = self.identify_hikvision(ip_str, port)
                            if model or advanced:
                                self.queue.put(('add', (ip_str, port, model, version, status, info)))
                except Exception as e:
                    pass
                
                # Обновляем прогресс
                self.queue.put(('progress', 1))
            
            if advanced and self.scan_active:
                # Дополнительные проверки для расширенного сканирования
                self.queue.put(('status', f"Расширенное сканирование {ip_str}..."))
                
                # Проверка ONVIF
                self.check_onvif(ip_str)
                
                # Проверка RTSP
                self.check_rtsp_port(ip_str)
                
                # Проверка SADP
                self.check_sadp(ip_str)
                
                # Обновляем прогресс
                self.queue.put(('progress', 10))
            
            scanned_hosts += 1
            progress_percent = (scanned_hosts / total_hosts) * 100
            self.queue.put(('status', f"Просканировано {scanned_hosts}/{total_hosts} устройств ({progress_percent:.1f}%)"))
        
        self.queue.put(('done', None))
    
    def identify_hikvision(self, ip, port):
        try:
            # Проверка веб-интерфейса Hikvision
            if port in [80, 443, 8000]:
                url = f"http://{ip}:{port}"
                if port == 443:
                    url = f"https://{ip}:{port}"
                
                try:
                    # Попытка получить базовую информацию без авторизации
                    response = requests.get(f"{url}/ISAPI/System/deviceInfo", timeout=2)
                    if response.status_code == 401:
                        # Требуется авторизация - пробуем стандартные учетные данные
                        login = self.login_entry.get()
                        password = self.password_entry.get()
                        
                        try:
                            response = requests.get(
                                f"{url}/ISAPI/System/deviceInfo",
                                auth=(login, password),
                                timeout=2
                            )
                            if response.status_code == 200:
                                # Парсим XML ответ
                                device_info = response.text
                                model = self.extract_from_xml(device_info, 'model')
                                firmware = self.extract_from_xml(device_info, 'firmwareVersion')
                                
                                # Проверка статуса
                                status_response = requests.get(
                                    f"{url}/ISAPI/System/status",
                                    auth=(login, password),
                                    timeout=2
                                )
                                status = "Online"
                                if status_response.status_code == 200:
                                    status_info = status_response.text
                                    if 'abnormal' in status_info.lower():
                                        status = "Abnormal"
                                
                                return model, firmware, status, "Hikvision Device (Authenticated)"
                        except:
                            pass
                        
                        return "Hikvision (Auth Required)", "Unknown", "Locked", "Requires authentication"
                    
                    elif response.status_code == 200:
                        # Устройство ответило без авторизации (опасно!)
                        device_info = response.text
                        model = self.extract_from_xml(device_info, 'model')
                        firmware = self.extract_from_xml(device_info, 'firmwareVersion')
                        return model, firmware, "Vulnerable!", "No authentication required!"
                    
                except requests.exceptions.RequestException:
                    pass
                
                # Проверка старого веб-интерфейса
                try:
                    response = requests.get(f"{url}/doc/page/login.asp", timeout=2)
                    if response.status_code == 200 and 'hikvision' in response.text.lower():
                        return "Hikvision Web", "Unknown", "Web Interface", "Legacy web interface detected"
                except:
                    pass
            
            # Проверка RTSP потока
            if port == 554:
                try:
                    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    s.settimeout(2)
                    s.connect((ip, port))
                    banner = s.recv(1024).decode('ascii', errors='ignore')
                    s.close()
                    
                    if 'Hikvision' in banner or 'RTSP' in banner:
                        return "Hikvision RTSP", "Unknown", "Streaming", f"RTSP service: {banner[:50]}..."
                except:
                    pass
            
            # Проверка сервиса SADP (Hikvision Discovery Protocol)
            if port == 8000:
                try:
                    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    s.settimeout(2)
                    s.connect((ip, port))
                    banner = s.recv(1024).decode('ascii', errors='ignore')
                    s.close()
                    
                    if 'Hikvision' in banner or 'SADP' in banner:
                        return "Hikvision SADP", "Unknown", "Discovery", "Hikvision device discovery service"
                except:
                    pass
            
        except Exception as e:
            return None, None, None, str(e)
        
        return None, None, None, None
    
    def extract_from_xml(self, xml, tag):
        """ Извлекает значение из XML по тегу """
        match = re.search(f'<{tag}>(.*?)</{tag}>', xml)
        return match.group(1) if match else "Unknown"
    
    def check_onvif(self, ip):
        """ Проверяет ONVIF сервис """
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(1)
                result = s.connect_ex((ip, 8000))
                if result == 0:
                    s.send(b'GET /onvif/device_service HTTP/1.0\r\n\r\n')
                    data = s.recv(1024).decode('ascii', errors='ignore')
                    if 'ONVIF' in data or 'onvif' in data.lower():
                        self.queue.put(('add', (ip, 8000, "Hikvision ONVIF", "Unknown", "ONVIF", "ONVIF service detected")))
        except:
            pass
    
    def check_rtsp_port(self, ip):
        """ Проверяет альтернативные RTSP порты """
        for port in [554, 8554, 10554]:
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.settimeout(1)
                    result = s.connect_ex((ip, port))
                    if result == 0:
                        s.send(b'OPTIONS * RTSP/1.0\r\n\r\n')
                        data = s.recv(1024).decode('ascii', errors='ignore')
                        if 'RTSP' in data:
                            self.queue.put(('add', (ip, port, "RTSP Service", "Unknown", "Streaming", f"RTSP on port {port}")))
                            break
            except:
                continue
    
    def check_sadp(self, ip):
        """ Проверяет сервис SADP (Hikvision Discovery Protocol) """
        try:
            # SADP использует UDP порт 37020
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
                s.settimeout(1)
                s.sendto(b'\x00\x00\x00\x00', (ip, 37020))
                data, _ = s.recvfrom(1024)
                if len(data) > 4 and data[4:8] == b'HIKV':
                    # Это устройство Hikvision, отвечающее на SADP
                    mac = ':'.join(f'{b:02x}' for b in data[40:46])
                    self.queue.put(('add', (ip, 37020, "Hikvision SADP", "Unknown", "Discovered", f"MAC: {mac}")))
        except:
            pass
    
    def process_queue(self):
        try:
            while True:
                item = self.queue.get_nowait()
                if item[0] == 'add':
                    self.tree.insert('', tk.END, values=item[1])
                elif item[0] == 'progress':
                    self.progress.step(item[1])
                elif item[0] == 'status':
                    self.root.title(f"Hikvision Scanner - {item[1]}")
                elif item[0] == 'done':
                    self.scan_active = False
                    self.scan_button.config(state=tk.NORMAL)
                    self.advanced_scan_button.config(state=tk.NORMAL)
                    self.stop_button.config(state=tk.DISABLED)
                    self.root.title("Hikvision Scanner - Сканирование завершено")
                elif item[0] == 'warning':
                    messagebox.showwarning("Предупреждение", item[1])
        except queue.Empty:
            pass
        
        self.root.after(100, self.process_queue)
    
    def show_context_menu(self, event):
        """ Показывает контекстное меню для выбранного устройства """
        item = self.tree.identify_row(event.y)
        if item:
            self.tree.selection_set(item)
            self.context_menu.tk_popup(event.x_root, event.y_root)
    
    def open_in_browser(self):
        """ Открывает веб-интерфейс камеры в браузере """
        selected = self.tree.focus()
        if not selected:
            return
        
        item = self.tree.item(selected)
        ip, port, _, _, _, _ = item['values']
        
        if port in [80, 443, 8000]:
            url = f"http://{ip}:{port}"
            if port == 443:
                url = f"https://{ip}:{port}"
            
            try:
                os.startfile(url)
            except:
                messagebox.showerror("Ошибка", "Не удалось открыть в браузере")
    
    def copy_ip(self):
        """ Копирует IP-адрес в буфер обмена """
        selected = self.tree.focus()
        if not selected:
            return
        
        item = self.tree.item(selected)
        ip = item['values'][0]
        
        self.root.clipboard_clear()
        self.root.clipboard_append(ip)
        messagebox.showinfo("Скопировано", f"IP-адрес {ip} скопирован в буфер обмена")
    
    def check_rtsp(self):
        """ Проверяет RTSP поток """
        selected = self.tree.focus()
        if not selected:
            return
        
        item = self.tree.item(selected)
        ip, port, model, _, _, _ = item['values']
        
        # Стандартные пути RTSP для Hikvision
        rtsp_paths = [
            "/Streaming/Channels/101",
            "/Streaming/Channels/1",
            "/live.sdp",
            "/cam/realmonitor?channel=1&subtype=0"
        ]
        
        login = self.login_entry.get()
        password = self.password_entry.get()
        
        for path in rtsp_paths:
            rtsp_url = f"rtsp://{login}:{password}@{ip}:{port}{path}"
            
            # Проверяем с помощью FFprobe (должен быть установлен)
            try:
                result = subprocess.run(
                    ['ffprobe', '-v', 'error', '-select_streams', 'v:0', 
                     '-show_entries', 'stream=codec_name', '-of', 
                     'default=nokey=1:noprint_wrappers=1', rtsp_url],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    timeout=5
                )
                
                if result.returncode == 0 and b'h264' in result.stdout.lower():
                    messagebox.showinfo("RTSP поток", f"Рабочий RTSP поток найден:\n{rtsp_url}")
                    return
            except:
                continue
        
        messagebox.showinfo("RTSP поток", "Не удалось найти рабочий RTSP поток")
    
    def export_to_csv(self):
        """ Экспортирует результаты в CSV файл """
        file_path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV Files", "*.csv"), ("All Files", "*.*")]
        )
        
        if not file_path:
            return
        
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write("IP,Port,Model,Firmware,Status,Info\n")
                for item in self.tree.get_children():
                    values = self.tree.item(item)['values']
                    f.write(','.join(str(v) for v in values) + '\n')
            
            messagebox.showinfo("Экспорт", f"Данные успешно экспортированы в {file_path}")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось экспортировать данные: {str(e)}")
    
    def show_preview(self, event):
        selected = self.tree.focus()
        if not selected:
            return
        
        item = self.tree.item(selected)
        ip, port, model, _, _, _ = item['values']
        
        if port in [80, 443, 8000]:
            # Попробуем получить снимок с камеры
            login = self.login_entry.get()
            password = self.password_entry.get()
            
            # Стандартные пути для снимков Hikvision
            snapshot_paths = [
                "/ISAPI/Streaming/channels/101/picture",
                "/Streaming/channels/1/picture",
                "/cgi-bin/snapshot.cgi",
                "/jpg/image.jpg",
                "/tmpfs/auto.jpg"
            ]
            
            for path in snapshot_paths:
                url = f"http://{ip}:{port}{path}"
                if port == 443:
                    url = f"https://{ip}:{port}{path}"
                
                try:
                    response = requests.get(
                        url,
                        auth=(login, password),
                        timeout=2,
                        stream=True
                    )
                    
                    if response.status_code == 200:
                        img_data = response.content
                        img = Image.open(BytesIO(img_data))
                        img.thumbnail((600, 400))
                        photo = ImageTk.PhotoImage(img)
                        
                        self.preview_label.config(image=photo)
                        self.preview_label.image = photo
                        return
                except:
                    continue
            
            self.preview_label.config(image='', text=f"Не удалось получить снимок с {model}")
            self.preview_label.image = None
        else:
            self.preview_label.config(image='', text=f"Предпросмотр не поддерживается для порта {port}")
            self.preview_label.image = None
    
    def get_snapshot(self):
        """ Получает снимок с выбранной камеры """
        self.show_preview(None)
    
    def reboot_camera(self):
        """ Перезагружает выбранную камеру """
        selected = self.tree.focus()
        if not selected:
            return
        
        item = self.tree.item(selected)
        ip, port, model, _, _, _ = item['values']
        
        if port not in [80, 443, 8000]:
            messagebox.showerror("Ошибка", "Перезагрузка поддерживается только через веб-интерфейс")
            return
        
        if messagebox.askyesno("Подтверждение", f"Вы уверены, что хотите перезагрузить {model} ({ip})?"):
            login = self.login_entry.get()
            password = self.password_entry.get()
            
            try:
                url = f"http://{ip}:{port}/ISAPI/System/reboot"
                if port == 443:
                    url = f"https://{ip}:{port}/ISAPI/System/reboot"
                
                response = requests.put(
                    url,
                    auth=(login, password),
                    data='<reboot><mode>normal</mode></reboot>',
                    headers={'Content-Type': 'application/xml'},
                    timeout=5
                )
                
                if response.status_code == 200:
                    messagebox.showinfo("Успех", "Камера перезагружается")
                else:
                    messagebox.showerror("Ошибка", f"Не удалось перезагрузить камеру: {response.status_code}")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось перезагрузить камеру: {str(e)}")
    
    def reset_camera(self):
        """ Сбрасывает настройки камеры """
        selected = self.tree.focus()
        if not selected:
            return
        
        item = self.tree.item(selected)
        ip, port, model, _, _, _ = item['values']
        
        if port not in [80, 443, 8000]:
            messagebox.showerror("Ошибка", "Сброс поддерживается только через веб-интерфейс")
            return
        
        if messagebox.askyesno("Подтверждение", 
                             f"Вы уверены, что хотите сбросить настройки {model} ({ip}) к заводским?\nЭто действие нельзя отменить!"):
            login = self.login_entry.get()
            password = self.password_entry.get()
            
            try:
                url = f"http://{ip}:{port}/ISAPI/System/factoryReset"
                if port == 443:
                    url = f"https://{ip}:{port}/ISAPI/System/factoryReset"
                
                response = requests.put(
                    url,
                    auth=(login, password),
                    data='<factoryReset><mode>basic</mode></factoryReset>',
                    headers={'Content-Type': 'application/xml'},
                    timeout=5
                )
                
                if response.status_code == 200:
                    messagebox.showinfo("Успех", "Настройки камеры сброшены к заводским")
                else:
                    messagebox.showerror("Ошибка", f"Не удалось сбросить настройки: {response.status_code}")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось сбросить настройки: {str(e)}")
    
    def update_firmware(self):
        """ Обновляет прошивку камеры """
        selected = self.tree.focus()
        if not selected:
            return
        
        item = self.tree.item(selected)
        ip, port, model, version, _, _ = item['values']
        
        if port not in [80, 443, 8000]:
            messagebox.showerror("Ошибка", "Обновление поддерживается только через веб-интерфейс")
            return
        
        file_path = filedialog.askopenfilename(
            title="Выберите файл прошивки",
            filetypes=[("Digest Files", "*.dig"), ("All Files", "*.*")]
        )
        
        if not file_path:
            return
        
        if messagebox.askyesno("Подтверждение", 
                             f"Вы уверены, что хотите обновить прошивку {model} ({ip})?\nТекущая версия: {version}\n\nЭто действие может сделать камеру неработоспособной!"):
            login = self.login_entry.get()
            password = self.password_entry.get()
            
            try:
                url = f"http://{ip}:{port}/ISAPI/System/updateFirmware"
                if port == 443:
                    url = f"https://{ip}:{port}/ISAPI/System/updateFirmware"
                
                with open(file_path, 'rb') as f:
                    response = requests.put(
                        url,
                        auth=(login, password),
                        data=f,
                        headers={'Content-Type': 'application/octet-stream'},
                        timeout=30
                    )
                
                if response.status_code == 200:
                    messagebox.showinfo("Успех", "Прошивка успешно загружена. Камера перезагружается.")
                else:
                    messagebox.showerror("Ошибка", f"Не удалось обновить прошивку: {response.status_code}")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось обновить прошивку: {str(e)}")

if __name__ == "__main__":
    root = tk.Tk()
    
    # Установка темы Windows
    try:
        from ctypes import windll
        windll.shcore.SetProcessDpiAwareness(1)
    except:
        pass
    
    app = HikvisionScanner(root)
    root.mainloop()