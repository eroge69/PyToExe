import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import subprocess
import sys
import hashlib
import random
import time
from datetime import datetime, timezone, timedelta
import ntplib
import pytz
import urllib3
import json
import ctypes
import threading
from queue import Queue
from contextlib import suppress
import re

ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 0)

def install_package(package):
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])

required_packages = ["requests", "ntplib", "pytz", "urllib3"]
for package in required_packages:
    try:
        __import__(package)
    except ImportError:
        install_package(package)

class ClockLabel(ttk.Label):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.ntp_offset = self.sync_with_ntp()
        self.update_clock()
    
    def sync_with_ntp(self):
        client = ntplib.NTPClient()
        for server in ntp_servers:
            try:
                response = client.request(server, version=3, timeout=2)
                ntp_time = datetime.fromtimestamp(response.tx_time, timezone.utc)
                local_time = datetime.now(timezone.utc)
                return ntp_time - local_time
            except Exception:
                continue
        return timedelta(0)

    def update_clock(self):
        try:
            adjusted_time = datetime.now(timezone.utc) + self.ntp_offset
            beijing_time = adjusted_time.astimezone(pytz.timezone('Asia/Shanghai'))
        except Exception:
            beijing_time = datetime.now(pytz.timezone('Asia/Shanghai'))
            
        self.config(text=beijing_time.strftime("Пекинское время: %H:%M:%S"), 
                   style='Clock.TLabel')
        self.after(1000, self.update_clock)

class AnimatedProgressbar(ttk.Progressbar):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.pulse_direction = 1
        self.pulse_value = 0
        
    def pulse(self):
        if not self.cget('value') == 100:
            self.pulse_value += self.pulse_direction * 5
            if self.pulse_value >= 50 or self.pulse_value <= 0:
                self.pulse_direction *= -1
            self.configure(value=self.pulse_value)
            self.after(100, self.pulse)

class GradientFrame(tk.Canvas):
    def __init__(self, parent, color1="#000000", color2="#1a1a1a", **kwargs):
        super().__init__(parent, **kwargs)
        self.color1 = color1
        self.color2 = color2
        self.bind("<Configure>", self.draw_gradient)
        
    def draw_gradient(self, event=None):
        self.delete("gradient")
        width = self.winfo_width()
        height = self.winfo_height()
        
        for y in range(height):
            ratio = y / height
            r = int(self.color1[1:3], 16) * (1 - ratio) + int(self.color2[1:3], 16) * ratio
            g = int(self.color1[3:5], 16) * (1 - ratio) + int(self.color2[3:5], 16) * ratio
            b = int(self.color1[5:7], 16) * (1 - ratio) + int(self.color2[5:7], 16) * ratio
            color = f"#{int(r):02x}{int(g):02x}{int(b):02x}"
            self.create_line(0, y, width, y, tags=("gradient",), fill=color)
        self.lower("gradient")

class AnimatedButton(ttk.Button):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.default_style = 'TButton'
        self.configure(style=self.default_style)
        self.bind("<Enter>", self.on_enter)
        self.bind("<Leave>", self.on_leave)
        self.animation_id = None
        self.is_animating = False

    def on_enter(self, e):
        if not self.is_animating:
            self.configure(style='Hover.TButton')
            self.start_animation()

    def on_leave(self, e):
        if self.animation_id:
            self.after_cancel(self.animation_id)
            self.animation_id = None
        self.is_animating = False
        self.configure(style=self.default_style)

    def start_animation(self):
        self.is_animating = True
        self.flash_animation()

    def flash_animation(self, count=0):
        if self.is_animating and count < 3:
            current_style = self.cget("style")
            new_style = 'Hover.TButton' if current_style == self.default_style else self.default_style
            self.configure(style=new_style)
            self.animation_id = self.after(100, lambda: self.flash_animation(count+1))
        else:
            self.is_animating = False

class ModernUnlockApp:
    def __init__(self, root):
        self.root = root
        self.root.title("ARU_FHL: v070525")
        self.root.geometry("700x700")
        self.root.resizable(False, False)
        
        self.token_var = tk.StringVar()
        self.status_var = tk.StringVar(value="Готов к работе")
        self.progress_var = tk.DoubleVar(value=0)
        
        self.scriptversion = "XiaoMi Community Request"
        self.active_threads = 0
        self.total_threads = 0
        self.thread_progress = {}
        self.offsets = []
        self.queue = Queue()
        self.thread_workers = {}
        self.thread_lock = threading.Lock()
        self.stop_event = threading.Event()
        self.status_check_timer = None
        
        self.progress_bars = []
        self.status_labels = []
        self.offset_labels = []
        
        self.setup_styles()
        self.create_ui()
        self.check_queue()

    def setup_styles(self):
        self.style = ttk.Style()
        self.style.theme_use('clam')
        self.style.configure('.', background='#111111', foreground='#eeeeee',
                           bordercolor='#444444', darkcolor='#222222',
                           lightcolor='#444444', troughcolor='#333333',
                           fieldbackground='#333333', insertcolor='#ffffff',
                           font=('Segoe UI', 10))
        self.style.configure('TButton', background='#222222', foreground='#eeeeee',
                           bordercolor='#444444', relief='flat', padding=6)
        self.style.configure('Hover.TButton', background='#333333',
                           foreground='#f39c12', bordercolor='#666666', relief='flat')
        self.style.map('TButton', background=[('active', '#333333'), ('disabled', '#222222')],
                     foreground=[('active', '#f39c12'), ('disabled', '#666666')],
                     relief=[('pressed', 'sunken'), ('!pressed', 'flat')])
        self.style.map('Hover.TButton', background=[('active', '#444444'), ('!active', '#333333')],
                     foreground=[('active', '#ffaa00'), ('!active', '#f39c12')])
        self.style.configure('TEntry', foreground='#ffffff', fieldbackground='#333333',
                          bordercolor='#444444', lightcolor='#444444', darkcolor='#444444')
        self.style.configure("orange.Horizontal.TProgressbar", background='#f39c12',
                           troughcolor='#111111', bordercolor='#111111',
                           lightcolor='#f39c12', darkcolor='#e67e22')
        self.style.configure("Red.TLabel", foreground="#e74c3c")
        self.style.configure("Green.TLabel", foreground="#2ecc71")
        self.style.configure("Yellow.TLabel", foreground="#f1c40f")
        self.style.configure("Orange.TLabel", foreground="#f39c12")
        self.style.configure("Clock.TLabel", foreground="#FF8C00",
                          bordercolor='#444444', font=('Segoe UI', 9))
        self.style.configure('StatusBar.TLabel', foreground='#FF8C00',
                          bordercolor='#444444', font=('Segoe UI', 9))

    def create_ui(self):
        self.canvas = GradientFrame(self.root, color1="#000000", color2="#1a1a1a")
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        main_frame = ttk.Frame(self.canvas)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        header_frame = ttk.Frame(main_frame)
        header_frame.pack(fill=tk.X, pady=(0, 15))
        
        title_frame = ttk.Frame(header_frame)
        title_frame.pack(side=tk.LEFT, anchor=tk.W)
        ttk.Label(title_frame, text="ARU_FHL", font=('Segoe UI', 18, 'bold'), 
                style='Orange.TLabel').pack(side=tk.TOP, anchor=tk.W)
        ttk.Label(title_frame, text=self.scriptversion, style='Yellow.TLabel').pack(side=tk.TOP, anchor=tk.W, pady=(0,5))
        
        right_header_frame = ttk.Frame(header_frame)
        right_header_frame.pack(side=tk.RIGHT, anchor=tk.NE)
        
        ClockLabel(right_header_frame).pack(side=tk.TOP, anchor=tk.E)
    
        self.status_bar = ttk.Label(right_header_frame, textvariable=self.status_var, 
                style='StatusBar.TLabel', anchor=tk.W, width=24)
        self.status_bar.pack(side=tk.TOP, pady=(5,0), anchor=tk.E)
        
        input_frame = ttk.Frame(main_frame)
        input_frame.pack(fill=tk.X, pady=(0, 15))
        
        token_frame = ttk.Frame(input_frame)
        token_frame.pack(fill=tk.X, pady=(0, 10))
        ttk.Label(token_frame, text="Токен:").pack(side=tk.LEFT, padx=(0, 10))
        self.token_entry = ttk.Entry(token_frame, textvariable=self.token_var, width=40)
        self.token_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        self.context_menu = tk.Menu(self.root, tearoff=0)
        self.context_menu.add_command(label="Копировать", command=self.copy_to_clipboard)
        self.context_menu.add_command(label="Вставить", command=self.paste_from_clipboard)
        self.context_menu.add_command(label="Вырезать", command=self.cut_to_clipboard)
        self.token_entry.bind("<Button-3>", self.show_context_menu)
        
        offset_frame = ttk.Frame(input_frame)
        offset_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.offset_entries = []
        for i in range(4):
            lbl = ttk.Label(offset_frame, text=f"Смещение {i+1}:")
            lbl.pack(side=tk.LEFT, padx=(0, 2))
            entry = ttk.Entry(offset_frame, width=12, validate="key")
            entry['validatecommand'] = (entry.register(self.validate_number), '%P')
            entry.pack(side=tk.LEFT, padx=(0, 5))
            self.offset_entries.append(entry)
        
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(0, 15))
        
        buttons = [
            ("Статус", self.check_account_status),
            ("Старт", self.start_process),
            ("Стоп", self.stop_process),
            ("Очистить", self.clear_log),
            ("Расчёт смещения", self.launch_ping_tool)
        ]
        
        for text, command in buttons:
            btn = AnimatedButton(button_frame, text=text, command=command)
            btn.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=5)
        
        status_frame = ttk.LabelFrame(main_frame, text="Статус аккаунта", padding=10)
        status_frame.pack(fill=tk.X, pady=(0, 10))
        self.account_status = tk.Text(status_frame, height=2, bg='#111111', fg='#eeeeee',
                                    insertbackground='white', font=('Consolas', 9),
                                    wrap=tk.WORD, state='disabled')
        self.account_status.pack(fill=tk.X, expand=True)
        
        progress_frame = ttk.LabelFrame(main_frame, text="Прогресс выполнения", padding=10)
        progress_frame.pack(fill=tk.X, pady=(0, 10))
        self.main_progress = AnimatedProgressbar(progress_frame, orient="horizontal", 
                                              length=100, mode="determinate",
                                              variable=self.progress_var,
                                              style="orange.Horizontal.TProgressbar")
        self.main_progress.pack(fill=tk.X, expand=True)
        self.main_progress.pulse()
        
        self.thread_status_frame = ttk.Frame(main_frame)
        self.thread_status_frame.pack(fill=tk.X, pady=(0, 10))
        
        log_frame = ttk.LabelFrame(main_frame, text="Лог программы", padding=10)
        log_frame.pack(fill=tk.BOTH, expand=True)
        self.log_area = scrolledtext.ScrolledText(log_frame, wrap=tk.WORD, 
                                                bg='#111111', fg='#eeeeee',
                                                insertbackground='white',
                                                font=('Consolas', 9),
                                                state='disabled')
        self.log_area.pack(fill=tk.BOTH, expand=True)
        
        for color in ['green', 'yellow', 'red', 'blue', 'orange']:
            self.log_area.tag_config(color, foreground=color)
            self.account_status.tag_config(color, foreground=color)

    def show_context_menu(self, event):
        try:
            self.context_menu.tk_popup(event.x_root, event.y_root)
        finally:
            self.context_menu.grab_release()

    def copy_to_clipboard(self):
        self.root.clipboard_clear()
        self.root.clipboard_append(self.token_entry.selection_get())

    def paste_from_clipboard(self):
        self.token_entry.insert(tk.INSERT, self.root.clipboard_get())

    def cut_to_clipboard(self):
        self.copy_to_clipboard()
        self.token_entry.delete(tk.SEL_FIRST, tk.SEL_LAST)

    def validate_number(self, value):
        return value == "" or value.replace(".", "", 1).isdigit()

    def check_queue(self):
        while not self.queue.empty():
            task = self.queue.get()
            if task['type'] == 'log':
                self.log_message(task['message'], task['color'])
            elif task['type'] == 'status':
                self.show_account_status(task['message'], task['color'])
            elif task['type'] == 'progress':
                self.update_progress(task['thread_id'], task['value'])
            elif task['type'] == 'trigger' and task['action'] == 'check_status':
                self.check_account_status()
        self.root.after(100, self.check_queue)

    def update_progress(self, thread_id, value):
        with self.thread_lock:
            self.thread_progress[thread_id] = value
        self.update_thread_visuals()

    def update_thread_visuals(self):
        if len(self.progress_bars) != self.total_threads:
            self.recreate_progress_bars()
        
        for i, (_, progress) in enumerate(self.thread_progress.items()):
            if i < len(self.progress_bars):
                self.progress_bars[i]['value'] = progress
                self.status_labels[i].config(text="🟢" if progress < 100 else "✅")
        
        total = sum(self.thread_progress.values()) / self.total_threads
        self.progress_var.set(total)
        self.root.update_idletasks()

    def recreate_progress_bars(self):
        for widget in self.thread_status_frame.winfo_children():
            widget.destroy()
        
        self.progress_bars.clear()
        self.status_labels.clear()
        self.offset_labels.clear()

        for i in range(self.total_threads):
            frame = ttk.Frame(self.thread_status_frame)
            frame.pack(fill=tk.X, pady=2, expand=True)

            lbl = ttk.Label(frame, text=f"Поток {i+1}:")
            lbl.pack(side=tk.LEFT, padx=(0, 5))

            pb = ttk.Progressbar(
                frame, 
                orient="horizontal",
                length=150,
                mode="determinate",
                style="orange.Horizontal.TProgressbar"
            )
            pb.pack(side=tk.LEFT, expand=True, fill=tk.X)
            self.progress_bars.append(pb)

            offset_lbl = ttk.Label(frame, text=f"{self.offsets[i]} мс")
            offset_lbl.pack(side=tk.LEFT, padx=5)
            self.offset_labels.append(offset_lbl)

            status_lbl = ttk.Label(frame, text="🟢", width=3)
            status_lbl.pack(side=tk.RIGHT)
            self.status_labels.append(status_lbl)

            stop_btn = AnimatedButton(
                frame, 
                text="Стоп", 
                command=lambda tid=i: self.stop_thread(tid)
            )
            stop_btn.pack(side=tk.RIGHT, padx=5)

    def log_message(self, message, color=None):
        self.log_area.config(state='normal')
        self.log_area.insert(tk.END, message + "\n", color or 'white')
        self.log_area.see(tk.END)
        self.log_area.config(state='disabled')

    def show_account_status(self, message, color=None):
        self.account_status.config(state='normal')
        self.account_status.delete(1.0, tk.END)
        self.account_status.insert(tk.END, message + "\n", color or 'white')
        self.account_status.config(state='disabled')

    def clear_log(self):
        self.log_area.config(state='normal')
        self.log_area.delete(1.0, tk.END)
        self.log_area.config(state='disabled')

    def check_account_status(self):
        token = self.token_var.get()
        if not token:
            messagebox.showerror("Ошибка", "Введите токен!")
            return
            
        self.queue.put({'type': 'status', 'message': "Проверка статуса...", 'color': 'yellow'})
        
        def check_status_thread():
            device_id = self.generate_device_id()
            session = HTTP11Session()
            url = "https://sgp-api.buy.mi.com/bbs/api/global/user/bl-switch/state"
            headers = {"Cookie": f"new_bbs_serviceToken={token};versionCode=500415;versionName=5.4.15;deviceId={device_id};"}
            
            response = session.make_request('GET', url, headers=headers)
            if response is None:
                self.queue.put({'type': 'status', 'message': "Ошибка соединения", 'color': 'red'})
                return

            response_data = json.loads(response.data.decode('utf-8', errors='ignore'))
            response.release_conn()

            if response_data.get("code") == 100004:
                self.queue.put({'type': 'status', 'message': "Неверный токен", 'color': 'red'})
                return

            data = response_data.get("data", {})
            status_message, color, _ = self.parse_status_data(data)
            self.queue.put({'type': 'status', 'message': status_message, 'color': color})

        threading.Thread(target=check_status_thread, daemon=True).start()

    def parse_status_data(self, data):
        is_pass = data.get("is_pass")
        button_state = data.get("button_state")
        deadline_format = data.get("deadline_format", "Не указано")
        need_stop = False

        if is_pass == 4:
            if button_state == 1:
                return ("✓ Готов к подаче заявки", 'green', False)
            elif button_state == 2:
                need_stop = True
                return (f"⌛ Блокировка до {deadline_format}", 'red', True)
            elif button_state == 3:
                need_stop = True
                return ("🆕 Аккаунт создан <30 дней", 'red', True)
        elif is_pass == 1:
            need_stop = True
            return (f"✅ Одобрено до {deadline_format}", 'green', True)
        return ("❌ Неизвестный статус", 'red', False)

    def start_process(self):
        with self.thread_lock:
            if any(w.is_alive() for w in self.thread_workers.values()):
                return
            
        token = self.token_var.get()
        if not token:
            messagebox.showerror("Ошибка", "Введите токен!")
            return
            
        try:
            self.offsets = []
            for entry in self.offset_entries:
                value = entry.get().strip()
                if value:
                    self.offsets.append(float(value))
            
            if not self.offsets:
                raise ValueError("Не указано ни одного смещения")
                
            if len(self.offsets) > 4:
                raise ValueError("Максимум 4 смещения")

            with self.thread_lock:
                self.thread_workers = {}
                self.status_var.set("Работает...")
                self.progress_var.set(0)
                self.total_threads = len(self.offsets)
                self.active_threads = self.total_threads
                self.thread_progress = {i: 0 for i in range(self.total_threads)}
                self.stop_event.clear()
                self.recreate_progress_bars()

            for i, offset in enumerate(self.offsets):
                worker = ThreadWorker(
                    parent=self,
                    token=token,
                    offset=offset,
                    thread_id=i,
                    stop_event=self.stop_event
                )
                self.thread_workers[i] = worker
                worker.start()

        except ValueError as e:
            messagebox.showerror("Ошибка", str(e))
            self.offset_entries[0].focus_set()

    def stop_process(self):
        self.stop_event.set()
        with self.thread_lock:
            for worker in self.thread_workers.values():
                worker.safe_stop()
            self.thread_workers.clear()
            
        self.status_var.set("Остановлено")
        self.active_threads = 0
        self.progress_var.set(0)
        self.thread_progress = {}
        self.root.after(0, self.update_thread_visuals)

    def stop_thread(self, thread_id):
        with suppress(KeyError):
            worker = self.thread_workers[thread_id]
            worker.safe_stop()
            del self.thread_workers[thread_id]
        self.queue.put({'type': 'progress', 'thread_id': thread_id, 'value': 100})
        self.root.after(0, self.update_thread_visuals)

    def generate_device_id(self):
        return hashlib.sha1(f"{random.random()}-{time.time()}".encode()).hexdigest().upper()

    def on_closing(self):
        self.stop_process()
        if self.status_check_timer and self.status_check_timer.is_alive():
            self.status_check_timer.cancel()
        self.root.destroy()

    def launch_ping_tool(self):
        PingToolWindow(self.root)

class ThreadWorker(threading.Thread):
    def __init__(self, parent, token, offset, thread_id, stop_event):
        super().__init__(daemon=True)
        self.parent = parent
        self.token = token
        self.offset = offset
        self.thread_id = thread_id
        self.stop_event = stop_event
        self.running = threading.Event()
        self.running.set()
        self.lock = threading.Lock()
        self.session = HTTP11Session()

    def safe_stop(self):
        with self.lock:
            self.running.clear()
            self.session.close()

    def run(self):
        try:
            self.parent.queue.put({
                'type': 'log',
                'message': f"\n--- Запуск для смещения {self.offset} мс ---",
                'color': 'blue'
            })

            if not self.check_unlock_status():
                return

            start_beijing_time = self.get_initial_beijing_time()
            if start_beijing_time is None:
                return

            start_timestamp = time.time()
            self.wait_until_target_time(start_beijing_time, start_timestamp)
            self.send_unlock_requests(start_beijing_time, start_timestamp)

        except Exception as e:
            self.parent.queue.put({
                'type': 'log',
                'message': f"[{self.offset} мс] Ошибка: {str(e)}",
                'color': 'red'
            })
        finally:
            with self.parent.thread_lock:
                self.parent.active_threads -= 1
                if self.parent.active_threads == 0:
                    self.parent.status_var.set("Завершено")
                    self.parent.status_check_timer = threading.Timer(1.0, 
                        lambda: self.parent.queue.put({'type': 'trigger', 'action': 'check_status'}))
                    self.parent.status_check_timer.start()

    def check_unlock_status(self):
        url = "https://sgp-api.buy.mi.com/bbs/api/global/user/bl-switch/state"
        headers = {
            "Cookie": f"new_bbs_serviceToken={self.token};"
                     f"versionCode=500415;versionName=5.4.15;"
                     f"deviceId={self.parent.generate_device_id()};"
        }
        
        response = self.session.make_request('GET', url, headers=headers)
        if response is None:
            self.parent.queue.put({
                'type': 'log',
                'message': f"[{self.offset} мс] Ошибка проверки статуса",
                'color': 'red'
            })
            return False

        response_data = json.loads(response.data.decode('utf-8', errors='ignore'))
        response.release_conn()

        if response_data.get("code") == 100004:
            self.parent.queue.put({
                'type': 'log',
                'message': f"[{self.offset} мс] Неверный токен",
                'color': 'red'
            })
            return False

        data = response_data.get("data", {})
        status_message, color, need_stop = self.parent.parse_status_data(data)
        
        self.parent.queue.put({
            'type': 'log',
            'message': f"[{self.offset} мс] Статус: {status_message}",
            'color': color
        })
        
        if need_stop:
            self.parent.queue.put({
                'type': 'progress',
                'thread_id': self.thread_id,
                'value': 100
            })
            self.parent.root.after(0, self.parent.update_thread_visuals)
            return False
            
        return True if color in ['green', 'yellow'] else False

    def get_initial_beijing_time(self):
        client = ntplib.NTPClient()
        beijing_tz = pytz.timezone('Asia/Shanghai')
        
        for server in ntp_servers:
            try:
                response = client.request(server, version=3)
                ntp_time = datetime.fromtimestamp(response.tx_time, timezone.utc)
                beijing_time = ntp_time.astimezone(beijing_tz)
                self.parent.queue.put({
                    'type': 'log',
                    'message': f"[{self.offset} мс] Точное время: {beijing_time.strftime('%H:%M:%S.%f')}",
                    'color': 'blue'
                })
                return beijing_time
            except Exception:
                continue
        self.parent.queue.put({
            'type': 'log',
            'message': f"[{self.offset} мс] Ошибка синхронизации времени",
            'color': 'red'
        })
        return None

    def wait_until_target_time(self, start_beijing_time, start_timestamp):
        next_day = start_beijing_time + timedelta(days=1)
        target_time = next_day.replace(
            hour=0, minute=0, second=0, microsecond=0
        ) - timedelta(milliseconds=self.offset)
        
        self.parent.queue.put({
            'type': 'log',
            'message': f"[{self.offset} мс] Начало в: {target_time.strftime('%H:%M:%S.%f')}",
            'color': 'yellow'
        })

        while self.running.is_set() and not self.stop_event.is_set():
            current_time = start_beijing_time + timedelta(seconds=time.time() - start_timestamp)
            delta = (target_time - current_time).total_seconds()
            
            if delta <= 0:
                break
            
            sleep_time = min(0.05, delta)
            time.sleep(sleep_time)

        self.parent.queue.put({
            'type': 'log',
            'message': f"[{self.offset} мс] Начало отправки запросов",
            'color': 'green'
        })

    def send_unlock_requests(self, start_beijing_time, start_timestamp):
        url = "https://sgp-api.buy.mi.com/bbs/api/global/apply/bl-auth"
        headers = {
            "Cookie": f"new_bbs_serviceToken={self.token};"
                     f"versionCode=500415;versionName=5.4.15;"
                     f"deviceId={self.parent.generate_device_id()};"
        }

        while self.running.is_set() and not self.stop_event.is_set():
            try:
                if not self.running.is_set():
                    break

                request_time = start_beijing_time + timedelta(seconds=time.time() - start_timestamp)
                self.parent.queue.put({
                    'type': 'log',
                    'message': f"[{self.offset} мс] Отправка запроса в {request_time.strftime('%H:%M:%S.%f')}",
                    'color': None
                })
                
                response = self.session.make_request('POST', url, headers=headers)
                
                if not response:
                    continue

                response_time = start_beijing_time + timedelta(seconds=time.time() - start_timestamp)
                self.parent.queue.put({
                    'type': 'log',
                    'message': f"[{self.offset} мс] Ответ получен в {response_time.strftime('%H:%M:%S.%f')}",
                    'color': None
                })

                response_data = json.loads(response.data.decode('utf-8', errors='ignore'))
                response.release_conn()
                self.process_response(response_data)

                with self.parent.thread_lock:
                    current = self.parent.thread_progress.get(self.thread_id, 0)
                    new_progress = min(current + 2.5, 100)
                    self.parent.thread_progress[self.thread_id] = new_progress
                    self.parent.queue.put({
                        'type': 'progress',
                        'thread_id': self.thread_id,
                        'value': new_progress
                    })

                time.sleep(0.2)

            except Exception as e:
                self.parent.queue.put({
                    'type': 'log',
                    'message': f"[{self.offset} мс] Ошибка: {str(e)}",
                    'color': 'red'
                })

    def process_response(self, response_data):
        code = response_data.get("code")
        data = response_data.get("data", {})
        
        if code == 0:
            apply_result = data.get("apply_result")
            if apply_result == 1:
                self.parent.queue.put({
                    'type': 'log',
                    'message': f"[{self.offset} мс] ЗАЯВКА ОДОБРЕНА! ПОТОК ОСТАНОВЛЕН",
                    'color': 'green'
                })
                self.safe_stop()
                return

            elif apply_result in (3, 4):
                deadline = data.get("deadline_format", "неизвестно")
                self.parent.queue.put({
                    'type': 'log',
                    'message': f"[{self.offset} мс] Лимит до {deadline}",
                    'color': 'red'
                })
                self.safe_stop()
        elif code == 100001:
            self.parent.queue.put({
                'type': 'log',
                'message': f"[{self.offset} мс] Ошибка запроса",
                'color': 'red'
            })
        elif code == 100003:
            self.parent.queue.put({
                'type': 'log',
                'message': f"[{self.offset} мс] Возможно успех!",
                'color': 'green'
            })
        else:
            self.parent.queue.put({
                'type': 'log',
                'message': f"[{self.offset} мс] Неизвестный ответ: {json.dumps(response_data)}",
                'color': 'yellow'
            })

class HTTP11Session:
    def __init__(self):
        self.http = urllib3.PoolManager(
            maxsize=4,
            retries=urllib3.Retry(2),
            timeout=urllib3.Timeout(connect=1.5, read=3.0),
            block=True
        )
        self.active = True

    def make_request(self, method, url, headers=None):
        if not self.active:
            return None
        try:
            return self.http.request(
                method,
                url,
                headers=headers,
                body=b'{"is_retry":true}' if method == 'POST' else None,
                preload_content=False
            )
        except Exception:
            return None

    def close(self):
        self.active = False
        self.http.clear()

ntp_servers = [
    "ntp0.ntp-servers.net", "ntp1.ntp-servers.net",
    "ntp2.ntp-servers.net", "ntp3.ntp-servers.net",
    "ntp4.ntp-servers.net", "ntp5.ntp-servers.net"
]

class PingToolWindow:
    def __init__(self, parent):
        self.parent = parent
        self.window = tk.Toplevel(parent)
        self.window.title("ARU_FHL: Shift Calc")
        self.window.geometry("500x400")
        self.window.resizable(False, False)
        
        self.stop_event = threading.Event()
        self.gui_queue = Queue()
        self.results = []
        self.duration = 0
        self.target_time = None
        
        self.setup_styles()
        self.setup_ui()
        self.update_gui()
        self.start_time_thread()

    def setup_styles(self):
        self.style = ttk.Style(self.window)
        self.style.theme_use('clam')
        self.style.configure('.', background='#111111', foreground='#eeeeee',
                           bordercolor='#444444', darkcolor='#222222',
                           lightcolor='#444444', troughcolor='#333333',
                           fieldbackground='#333333', insertcolor='#ffffff',
                           font=('Segoe UI', 10))
        self.style.configure("orange.Horizontal.TProgressbar", 
                            background='#f39c12',
                            troughcolor='#111111',
                            bordercolor='#111111',
                            lightcolor='#f39c12',
                            darkcolor='#e67e22')
        self.style.configure('Clock.TLabel', foreground="#FF8C00",
                          font=('Segoe UI', 9))

    def setup_ui(self):
        self.canvas = GradientFrame(self.window, color1="#000000", color2="#1a1a1a")
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        main_frame = ttk.Frame(self.canvas)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        time_frame = ttk.Frame(main_frame)
        time_frame.pack(fill=tk.X, pady=10)
        self.time_label = ttk.Label(time_frame, 
                                  text="Пекинское время: Загрузка...",
                                  style='Clock.TLabel')
        self.time_label.pack(side=tk.TOP)
        
        self.countdown_label = ttk.Label(time_frame,
                                       text="До запуска: --:--:--",
                                       style='Clock.TLabel')
        self.countdown_label.pack(side=tk.TOP)
        
        control_frame = ttk.Frame(main_frame)
        control_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(control_frame, text="Время (ЧЧ:ММ):").pack(side=tk.LEFT)
        self.hour_entry = ttk.Entry(control_frame, width=3)
        self.hour_entry.pack(side=tk.LEFT, padx=2)
        ttk.Label(control_frame, text=":").pack(side=tk.LEFT)
        self.minute_entry = ttk.Entry(control_frame, width=3)
        self.minute_entry.pack(side=tk.LEFT, padx=2)
        
        ttk.Label(control_frame, text="Длит. (сек):").pack(side=tk.LEFT, padx=(10, 2))
        self.duration_entry = ttk.Entry(control_frame, width=5)
        self.duration_entry.pack(side=tk.LEFT)
        
        self.start_btn = AnimatedButton(control_frame, 
                                      text="Старт", 
                                      command=self.start_countdown)
        self.start_btn.pack(side=tk.LEFT, padx=5)
        
        AnimatedButton(control_frame, 
                     text="Стоп", 
                     command=self.stop_ping).pack(side=tk.LEFT, padx=5)
        
        self.progress_frame = ttk.LabelFrame(main_frame, 
                                           text="Прогресс выполнения",
                                           padding=10)
        self.progress_frame.pack(fill=tk.X, pady=10)
        
        result_frame = ttk.LabelFrame(main_frame, 
                                    text="Результаты", 
                                    padding=10)
        result_frame.pack(fill=tk.BOTH, expand=True)
        
        self.result_text = scrolledtext.ScrolledText(result_frame,
                                                   wrap=tk.WORD,
                                                   bg='#111111',
                                                   fg='#eeeeee',
                                                   state='disabled')
        self.result_text.pack(fill=tk.BOTH, expand=True)
        
        self.result_text.tag_config('success', foreground='green')
        self.result_text.tag_config('error', foreground='red')
        self.result_text.tag_config('info', foreground='yellow')
        
        validate_hour = (self.window.register(self.validate_hour), '%P')
        validate_minute = (self.window.register(self.validate_minute), '%P')
        self.hour_entry.config(validate="key", validatecommand=validate_hour)
        self.minute_entry.config(validate="key", validatecommand=validate_minute)

    def validate_hour(self, value):
        if value == "": return True
        return value.isdigit() and 0 <= int(value) <= 23

    def validate_minute(self, value):
        if value == "": return True
        return value.isdigit() and 0 <= int(value) <= 59

    def get_beijing_time(self):
        client = ntplib.NTPClient()
        for server in ntp_servers:
            try:
                response = client.request(server, version=3, timeout=2)
                ntp_time = datetime.fromtimestamp(response.tx_time, timezone.utc)
                beijing_time = ntp_time.astimezone(pytz.timezone('Asia/Shanghai'))
                return beijing_time
            except Exception:
                continue
        return datetime.now(pytz.timezone('Asia/Shanghai'))

    def start_countdown(self):
        try:
            target_hour = int(self.hour_entry.get() or 0)
            target_minute = int(self.minute_entry.get() or 0)
            if not (0 <= target_hour <=23 and 0 <= target_minute <=59):
                raise ValueError
        except:
            messagebox.showerror("Ошибка", "Некорректное время")
            return

        beijing_time = self.get_beijing_time()
        target_time = beijing_time.replace(
            hour=target_hour, 
            minute=target_minute, 
            second=0, 
            microsecond=0
        )
        if target_time <= beijing_time:
            target_time += timedelta(days=1)
        
        self.target_time = target_time
        self.stop_event.clear()
        self.gui_queue.put(('log', f"Расчет будет произведен в {target_time.strftime('%H:%M:%S')} (по Пекину). Ожидайте...", 'info'))
        threading.Thread(target=self.countdown_thread, daemon=True).start()

    def countdown_thread(self):
        while not self.stop_event.is_set():
            current_time = self.get_beijing_time()
            remaining = self.target_time - current_time
            if remaining.total_seconds() <= 0:
                self.gui_queue.put(('log', "Начинаем вычисление приблизительного времени смещения...", 'info'))
                self.start_ping()
                break
            
            hours, remainder = divmod(int(remaining.total_seconds()), 3600)
            minutes, seconds = divmod(remainder, 60)
            countdown_str = f"Начало через: {hours:02}:{minutes:02}:{seconds:02}"
            self.gui_queue.put(('update_countdown', countdown_str))
            time.sleep(1)

    def start_ping(self):
        try:
            self.duration = int(self.duration_entry.get())
            if not 1 <= self.duration <= 300:
                raise ValueError
        except:
            messagebox.showerror("Ошибка", "Введите число от 1 до 300")
            return

        self.results = []
        self.clear_results()
        
        ips = ["161.117.95.164", '161.117.96.161']
        for ip in ips:
            threading.Thread(target=self.ping_thread, args=(ip,), daemon=True).start()

    def ping_thread(self, ip):
        try:
            if sys.platform.startswith('win'):
                command = ['ping', '-n', str(self.duration), '-w', '2000', ip]
            else:
                command = ['ping', '-w', str(self.duration), '-c', str(self.duration), ip]

            process = subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
                universal_newlines=True,
                encoding='cp866' if sys.platform.startswith('win') else 'utf-8',
                errors='replace'
            )

            times = []
            start_time = time.time()
            end_time = start_time + self.duration + 5

            self.gui_queue.put(('add_progress', ip))
            
            while time.time() < end_time and not self.stop_event.is_set():
                line = process.stdout.readline()
                if not line:
                    break
                
                match = re.search(
                    r'(время[=<]|time[=<]|время\s*=\s*)(\d+\.?\d*)\s*м?s?', 
                    line, 
                    re.IGNORECASE
                )
                if match:
                    try:
                        t = float(match.group(2))
                        times.append(t)
                    except:
                        pass
                
                elapsed = time.time() - start_time
                progress = min(int((elapsed / self.duration) * 100), 100)
                self.gui_queue.put(('update_progress', (ip, progress)))

            if process.poll() is None:
                process.kill()

            if self.stop_event.is_set():
                return

            if not times:
                self.gui_queue.put(('log', f"{ip} - Нет ответа", 'error'))
                return

            min_ping = round(min(times), 2)
            avg = round(sum(times) / len(times), 2)
            max_ping = round(max(times), 2)
            self.results.append((min_ping, avg, max_ping))
            
            if len(self.results) == 2:
                total_min = sum(r[0] for r in self.results)
                total_avg = sum(r[1] for r in self.results)
                total_max = sum(r[2] for r in self.results)
                final_score = (total_avg + total_max)/2*1.5
                self.gui_queue.put(('log', f"Рекомендуемое смещение: {final_score:.2f} мс", 'info'))

        except Exception as e:
            self.gui_queue.put(('log', f"Ошибка: {str(e)}", 'error'))

    def stop_ping(self):
        self.stop_event.set()
        self.gui_queue.put(('log', "Тестирование остановлено", 'error'))

    def clear_results(self):
        self.result_text.config(state='normal')
        self.result_text.delete(1.0, tk.END)
        self.result_text.config(state='disabled')
        for widget in self.progress_frame.winfo_children():
            widget.destroy()

    def start_time_thread(self):
        def time_updater():
            while not self.stop_event.is_set():
                beijing_time = self.get_beijing_time()
                time_str = beijing_time.strftime("Пекинское время: %H:%M:%S")
                self.gui_queue.put(('update_time', time_str))
                time.sleep(1)
        
        threading.Thread(target=time_updater, daemon=True).start()

    def update_gui(self):
        while not self.gui_queue.empty():
            task_type, *args = self.gui_queue.get()
            
            if task_type == 'update_time':
                self.time_label.config(text=args[0])
            elif task_type == 'update_countdown':
                self.countdown_label.config(text=args[0])
            elif task_type == 'add_progress':
                ip = args[0]
                frame = ttk.Frame(self.progress_frame)
                frame.pack(fill=tk.X, pady=5)
                ttk.Label(frame, text=f"{ip}:").pack(side=tk.LEFT)
                pb = ttk.Progressbar(frame, orient='horizontal', length=200,
                                   style="orange.Horizontal.TProgressbar")
                pb.pack(side=tk.LEFT, padx=5)
                frame.percent = ttk.Label(frame, text="0%")
                frame.percent.pack(side=tk.LEFT)
                frame.pb = pb
            elif task_type == 'update_progress':
                ip, progress = args[0]
                for child in self.progress_frame.winfo_children():
                    if ip in child.winfo_children()[0].cget('text'):
                        child.pb['value'] = progress
                        child.percent.config(text=f"{progress}%")
            elif task_type == 'log':
                msg, tag = args
                self.result_text.config(state='normal')
                self.result_text.insert(tk.END, msg + "\n", tag)
                self.result_text.see(tk.END)
                self.result_text.config(state='disabled')
        
        self.window.after(100, self.update_gui)

    def __del__(self):
        self.stop_event.set()

if __name__ == "__main__":
    root = tk.Tk()
    app = ModernUnlockApp(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    
    root.option_add('*tearOff', False)
    root.tk.call('tk', 'scaling', 1.5)
    root.bind_all('<<ThreadUpdate>>', lambda e: root.update_idletasks())
    
    root.mainloop()