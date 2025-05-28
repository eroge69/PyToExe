import os
import sys
import imaplib
import email
import logging
from email.header import decode_header
from email.utils import parsedate_to_datetime
import tkinter as tk
from tkinter import ttk, scrolledtext, filedialog, messagebox
import threading
import queue

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename=resource_path('email_processor.log')
)

class GUILogHandler(logging.Handler):
    def __init__(self, queue):
        super().__init__()
        self.queue = queue
    
    def emit(self, record):
        msg = self.format(record)
        self.queue.put(msg)

def decode_mime_header(header):
    if not header:
        return ""
    
    decoded_parts = []
    for part, encoding in decode_header(header):
        if isinstance(part, bytes):
            encoding = encoding if encoding is not None else 'utf-8'
            for enc in [encoding, 'utf-8', 'cp1251', 'koi8-r', 'windows-1252']:
                try:
                    decoded_part = part.decode(enc)
                    decoded_parts.append(decoded_part)
                    break
                except (UnicodeDecodeError, LookupError):
                    continue
            else:
                decoded_parts.append(part.decode('utf-8', errors='replace'))
        else:
            decoded_parts.append(str(part))
    
    return ' '.join(decoded_parts).strip()

def clean_filename(filename):
    replace_chars = ['/', '\\', ':', '*', '?', '"', '<', '>', '|']
    filename = ''.join([c if c not in replace_chars else '_' for c in filename])
    return filename.strip()[:250]

def load_counter():
    try:
        with open(resource_path('counter.txt'), 'r') as f:
            return int(f.read().strip())
    except (FileNotFoundError, ValueError):
        return 985

def save_counter(counter):
    try:
        with open(resource_path('counter.txt'), 'w') as f:
            f.write(str(counter))
    except Exception as e:
        logging.error(f"Ошибка сохранения счетчика: {str(e)}")
        raise

def process_attachment(part, folder_path):
    filename = part.get_filename()
    if not filename:
        return None
    
    filename = decode_mime_header(filename)
    filename = clean_filename(filename)
    
    base, ext = os.path.splitext(filename)
    counter = 1
    while os.path.exists(os.path.join(folder_path, filename)):
        filename = f"{base}_{counter}{ext}"
        counter += 1
    
    filepath = os.path.join(folder_path, filename)
    try:
        with open(filepath, 'wb') as f:
            f.write(part.get_payload(decode=True))
        return filename
    except Exception as e:
        logging.error(f"Ошибка сохранения файла {filename}: {str(e)}")
        return None

class EmailClientGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Обработчик писем K-H25")
        self.geometry("1200x800")
        
        self.message_queue = queue.Queue()
        self.mail = None
        self.emails_list = []
        self.current_counter = load_counter()
        self.is_processing = False
        
        self.create_widgets()
        self.setup_logging()
        self.after(100, self.process_messages)
    
    def setup_logging(self):
        self.log_handler = GUILogHandler(self.message_queue)
        self.log_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
        root_logger = logging.getLogger()
        root_logger.addHandler(self.log_handler)
    
    def create_widgets(self):
        main_frame = ttk.Frame(self)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        settings_frame = ttk.LabelFrame(main_frame, text="Настройки подключения")
        settings_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(settings_frame, text="Почта:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=2)
        self.email_entry = ttk.Entry(settings_frame, width=40)
        self.email_entry.grid(row=0, column=1, sticky=tk.EW, padx=5, pady=2)
        
        ttk.Label(settings_frame, text="Пароль:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=2)
        self.password_entry = ttk.Entry(settings_frame, show='*', width=40)
        self.password_entry.grid(row=1, column=1, sticky=tk.EW, padx=5, pady=2)
        
        ttk.Label(settings_frame, text="IMAP сервер:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=2)
        self.server_entry = ttk.Entry(settings_frame, width=40)
        self.server_entry.grid(row=2, column=1, sticky=tk.EW, padx=5, pady=2)
        
        ttk.Label(settings_frame, text="Путь сохранения:").grid(row=3, column=0, sticky=tk.W, padx=5, pady=2)
        self.path_entry = ttk.Entry(settings_frame, width=40)
        self.path_entry.grid(row=3, column=1, sticky=tk.EW, padx=5, pady=2)
        ttk.Button(settings_frame, text="Обзор", command=self.browse_folder).grid(row=3, column=2, padx=5)
        
        ttk.Label(settings_frame, text="Индекс K-H25:").grid(row=4, column=0, sticky=tk.W, padx=5, pady=2)
        self.index_entry = ttk.Entry(settings_frame, width=40)
        self.index_entry.grid(row=4, column=1, sticky=tk.EW, padx=5, pady=2)
        
        settings_frame.columnconfigure(1, weight=1)
        
        control_frame = ttk.Frame(main_frame)
        control_frame.pack(fill=tk.X, pady=5)
        
        self.btn_fetch = ttk.Button(control_frame, text="Загрузить письма", command=self.start_fetch_emails)
        self.btn_fetch.pack(side=tk.LEFT, padx=5)
        
        self.btn_process = ttk.Button(control_frame, text="Обработать выбранные", command=self.start_process_emails)
        self.btn_process.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(control_frame, text="Обновить счетчик", command=self.update_counter_label).pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="Выход", command=self.destroy).pack(side=tk.RIGHT, padx=5)
        
        self.progress_frame = ttk.Frame(main_frame)
        self.progress_frame.pack(fill=tk.X, pady=5)
        
        self.progress_label = ttk.Label(self.progress_frame, text="Прогресс:")
        self.progress_label.pack(side=tk.LEFT, padx=5)
        
        self.progress = ttk.Progressbar(
            self.progress_frame,
            orient=tk.HORIZONTAL,
            length=300,
            mode='determinate'
        )
        self.progress.pack(side=tk.LEFT, expand=True, fill=tk.X)
        
        self.progress_value = ttk.Label(self.progress_frame, text="0%")
        self.progress_value.pack(side=tk.LEFT, padx=5)
        
        self.progress_frame.pack_forget()
        
        self.tree = ttk.Treeview(
            main_frame,
            columns=("Num", "From", "Subject", "Date"),
            show='headings',
            selectmode='extended'
        )
        
        self.tree.heading("Num", text="№", anchor=tk.W)
        self.tree.heading("From", text="Отправитель", anchor=tk.W)
        self.tree.heading("Subject", text="Тема", anchor=tk.W)
        self.tree.heading("Date", text="Дата", anchor=tk.W)
        
        self.tree.column("Num", width=50, anchor=tk.W)
        self.tree.column("From", width=250, anchor=tk.W)
        self.tree.column("Subject", width=400, anchor=tk.W)
        self.tree.column("Date", width=100, anchor=tk.W)
        
        self.tree.pack(fill=tk.BOTH, expand=True, pady=5)
        
        log_frame = ttk.Frame(main_frame)
        log_frame.pack(fill=tk.BOTH, expand=True)
        
        self.log_text = scrolledtext.ScrolledText(log_frame, state='disabled')
        self.log_text.pack(fill=tk.BOTH, expand=True)
        
        self.status_var = tk.StringVar()
        status_bar = ttk.Label(self, textvariable=self.status_var, relief=tk.SUNKEN)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        self.counter_var = tk.StringVar()
        self.update_counter_label()
        counter_label = ttk.Label(self, textvariable=self.counter_var)
        counter_label.pack(side=tk.BOTTOM, anchor=tk.W, padx=10)
    
    def update_counter_label(self):
        self.counter_var.set(f"Текущий порядковый номер: {self.current_counter}")
    
    def browse_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.path_entry.delete(0, tk.END)
            self.path_entry.insert(0, folder)
    
    def log_message(self, message):
        self.log_text.configure(state='normal')
        self.log_text.insert(tk.END, message + '\n')
        self.log_text.configure(state='disabled')
        self.log_text.see(tk.END)
        self.status_var.set(message)
    
    def process_messages(self):
        while not self.message_queue.empty():
            try:
                msg = self.message_queue.get_nowait()
                
                if msg.startswith("PROGRESS:"):
                    parts = msg.split(":")
                    current, total = parts[1].split("/")
                    percent = (int(current)/int(total)) * 100
                    self.progress['value'] = int(current)
                    self.progress_value['text'] = f"{percent:.1f}%"
                elif msg == "COMPLETE":
                    self.progress_frame.pack_forget()
                    self.toggle_buttons('normal')
                    self.is_processing = False
                    self.update_counter_label()
                    messagebox.showinfo("Успех", "Обработка писем завершена!")
                elif msg.startswith("ERROR:"):
                    error_msg = msg.split(":", 1)[1]
                    self.progress_frame.pack_forget()
                    self.toggle_buttons('normal')
                    self.is_processing = False
                    messagebox.showerror("Ошибка", error_msg)
                else:
                    self.log_message(msg)
                
            except queue.Empty:
                break
        self.after(100, self.process_messages)
    
    def toggle_buttons(self, state):
        self.btn_fetch['state'] = state
        self.btn_process['state'] = state
    
    def start_fetch_emails(self):
        if not self.validate_connection_params():
            return
        threading.Thread(target=self.fetch_emails, daemon=True).start()
    
    def validate_connection_params(self):
        params = [
            self.email_entry.get(),
            self.password_entry.get(),
            self.server_entry.get(),
            self.path_entry.get(),
            self.index_entry.get()
        ]
        if not all(params):
            messagebox.showerror("Ошибка", "Все поля должны быть заполнены!")
            return False
        return True
    
    def fetch_emails(self):
        try:
            self.mail = imaplib.IMAP4_SSL(self.server_entry.get())
            self.mail.login(self.email_entry.get(), self.password_entry.get())
            self.mail.select('inbox')
            
            status, messages = self.mail.search(None, 'UNSEEN')
            if status != 'OK' or not messages[0]:
                self.message_queue.put("Нет новых непрочитанных писем.")
                return
            
            self.emails_list = []
            message_ids = messages[0].split()
            
            for idx, msg_id in enumerate(message_ids, 1):
                status, msg_data = self.mail.fetch(msg_id, '(BODY.PEEK[HEADER])')
                if status != 'OK':
                    continue
                
                msg = email.message_from_bytes(msg_data[0][1])
                subject = decode_mime_header(msg.get('Subject', 'Без темы'))
                from_ = decode_mime_header(msg.get('From', 'Неизвестный отправитель'))
                date_str = msg.get('Date', '')
                
                try:
                    parsed_date = parsedate_to_datetime(date_str)
                    date_formatted = parsed_date.strftime('%d.%m.%Y')
                except:
                    date_formatted = "Неизвестная дата"
                
                self.emails_list.append({
                    'id': msg_id,
                    'num': idx,
                    'subject': subject,
                    'from': from_,
                    'date': date_formatted
                })
            
            self.tree.delete(*self.tree.get_children())
            for email_info in self.emails_list:
                self.tree.insert('', 'end', values=(
                    email_info['num'],
                    email_info['from'],
                    email_info['subject'],
                    email_info['date']
                ))
            
            self.message_queue.put(f"Найдено {len(self.emails_list)} непрочитанных писем.")
        except Exception as e:
            self.message_queue.put(f"Ошибка: {str(e)}")
            logging.error(str(e))
    
    def start_process_emails(self):
        if self.is_processing:
            messagebox.showwarning("Предупреждение", "Обработка уже выполняется!")
            return
        
        selected_items = self.tree.selection()
        if not selected_items:
            messagebox.showwarning("Предупреждение", "Выберите письма для обработки.")
            return
        
        indices = [self.tree.index(item) for item in selected_items]
        selected_emails = [self.emails_list[i] for i in indices]
        
        self.progress['maximum'] = len(selected_emails)
        self.progress['value'] = 0
        self.progress_frame.pack()
        self.progress_value['text'] = "0%"
        self.toggle_buttons('disabled')
        self.is_processing = True
        
        threading.Thread(
            target=self.process_emails,
            args=(selected_emails,),
            daemon=True
        ).start()
    
    def process_emails(self, selected_emails):
        try:
            total = len(selected_emails)
            for i, email_info in enumerate(selected_emails, 1):
                msg_id = email_info['id']
                
                self.message_queue.put(f"PROGRESS:{i}/{total}")
                
                status, msg_data = self.mail.fetch(msg_id, '(RFC822)')
                if status != 'OK':
                    self.message_queue.put(f"Ошибка получения письма {msg_id}")
                    continue
                
                msg = email.message_from_bytes(msg_data[0][1])
                subject = decode_mime_header(msg.get('Subject', 'Без темы'))
                date_str = msg.get('Date', '')
                
                try:
                    parsed_date = parsedate_to_datetime(date_str)
                    date_formatted = parsed_date.strftime('%d.%m.%Y')
                except:
                    date_formatted = "Неизвестная дата"
                
                folder_name = f"{self.current_counter}{self.index_entry.get()} от {date_formatted} {clean_filename(subject)}"
                folder_path = os.path.join(self.path_entry.get(), folder_name)
                os.makedirs(folder_path, exist_ok=True)
                self.message_queue.put(f"Создана папка: {folder_path}")
                
                attachments = []
                for part in msg.walk():
                    if part.get_content_disposition() == 'attachment':
                        filename = process_attachment(part, folder_path)
                        if filename:
                            attachments.append(filename)
                
                self.message_queue.put(f"Сохранено вложений: {len(attachments)}")
                self.mail.store(msg_id, '+FLAGS', '\\Seen')
                
                self.current_counter += 1
                save_counter(self.current_counter)
                self.message_queue.put(f"Номер обновлен: {self.current_counter}")
            
            self.message_queue.put("COMPLETE")
        except Exception as e:
            self.message_queue.put(f"ERROR:{str(e)}")
            logging.exception("Ошибка обработки письма")
    
    def destroy(self):
        if self.mail:
            try:
                self.mail.close()
                self.mail.logout()
            except:
                pass
        super().destroy()

if __name__ == "__main__":
    if not os.path.exists(resource_path('counter.txt')):
        with open(resource_path('counter.txt'), 'w') as f:
            f.write('985')
    
    app = EmailClientGUI()
    app.mainloop()