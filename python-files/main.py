import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, filedialog
import pyotp
import json
import os
import time
import threading
from datetime import datetime
import pyperclip
from PIL import Image, ImageTk, ImageFilter, ImageDraw
import io
import sys
import pystray
from pystray import MenuItem as item
import winreg
from cryptography.fernet import Fernet
import base64
from hashlib import sha256

class TwoFactorAuthApp:
    def __init__(self, root):
        self.root = root
        self.root.title("2FA Authenticator")
        self.root.geometry("320x600")
        self.root.resizable(False, False)
        
        # Инициализация шифрования
        self.encryption_key = self._get_encryption_key()
        self.cipher = Fernet(self.encryption_key)
        
        # Настройки трея
        self.tray_icon = None
        self.create_tray_icon()
        
        # Проверяем аргументы командной строки для скрытого запуска
        if '--hidden' in sys.argv:
            self.root.withdraw()
        
        # Настройки приложения
        self.settings = {
            "blur_codes": False,
            "blur_intensity": 5,
            "theme": "light",
            "start_minimized": False,
            "start_with_system": False
        }
        self.settings_file = "2fa_settings.enc"
        
        # Хранение аккаунтов
        self.accounts = {}
        self.account_frames = {}
        self.config_file = "2fa_accounts.enc"
        
        # Перетаскивание плашек
        self.drag_data = {"item": None, "y": 0}
        
        # Загрузка настроек и аккаунтов
        self.load_settings()
        self.apply_theme()
        
        # Создание интерфейса
        self.create_widgets()
        
        # Запуск потока обновления кодов
        self.running = True
        self.update_thread = threading.Thread(target=self.update_codes, daemon=True)
        self.update_thread.start()
        
        self.load_accounts()
        self.check_autostart()
        
        # Обработчики событий
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.root.bind("<Unmap>", self.on_minimize)

    def _get_encryption_key(self):
        """Генерация или загрузка ключа шифрования"""
        key_file = "2fa_key.key"
        if os.path.exists(key_file):
            try:
                with open(key_file, "rb") as f:
                    return f.read()
            except:
                pass
        
        # Генерируем новый ключ
        key = Fernet.generate_key()
        try:
            with open(key_file, "wb") as f:
                f.write(key)
        except:
            pass
        return key
    
    def encrypt_data(self, data):
        """Шифрование данных"""
        json_data = json.dumps(data).encode()
        return self.cipher.encrypt(json_data)
    
    def decrypt_data(self, encrypted_data):
        """Дешифрование данных"""
        try:
            json_data = self.cipher.decrypt(encrypted_data)
            return json.loads(json_data.decode())
        except:
            return None

    def create_tray_icon(self):
        """Создание иконки в системном трее"""
        image = Image.new('RGB', (64, 64), color='white')
        draw = ImageDraw.Draw(image)
        draw.text((10, 10), "2FA", fill='black')
        
        menu = (
            item('Показать', self.show_app),
            item('Скрыть', self.hide_app),
            item('Выход', self.exit_app)
        )
        
        self.tray_icon = pystray.Icon("2FA Authenticator", image, "2FA Authenticator", menu)
    
    def run_tray_icon(self):
        """Запуск иконки в трее"""
        self.tray_icon.run()
    
    def show_app(self, icon=None, item=None):
        """Показать окно приложения"""
        self.root.after(0, self.root.deiconify)
    
    def hide_app(self, icon=None, item=None):
        """Скрыть окно в трей"""
        self.root.withdraw()
    
    def exit_app(self, icon=None, item=None):
        """Выход из приложения"""
        self.running = False
        if self.update_thread.is_alive():
            self.update_thread.join()
        self.save_accounts()
        self.save_settings()
        self.tray_icon.stop()
        self.root.destroy()
    
    def on_minimize(self, event):
        """Обработчик минимизации окна"""
        if event.widget == self.root:
            self.hide_app()

    def check_autostart(self):
        """Проверка настроек автозагрузки"""
        if self.settings["start_with_system"]:
            self.set_autostart(True)
    
    def set_autostart(self, enable):
        """Настройка автозагрузки для Windows"""
        key = winreg.HKEY_CURRENT_USER
        key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
        
        try:
            with winreg.OpenKey(key, key_path, 0, winreg.KEY_ALL_ACCESS) as registry_key:
                if enable:
                    winreg.SetValueEx(
                        registry_key, 
                        "2FA Authenticator", 
                        0, 
                        winreg.REG_SZ, 
                        f'"{sys.executable}" "{os.path.abspath(__file__)}" --hidden'
                    )
                else:
                    try:
                        winreg.DeleteValue(registry_key, "2FA Authenticator")
                    except WindowsError:
                        pass
        except Exception as e:
            print(f"Ошибка настройки автозагрузки: {e}")

    def load_settings(self):
        """Загрузка зашифрованных настроек"""
        if os.path.exists(self.settings_file):
            try:
                with open(self.settings_file, "rb") as f:
                    encrypted_data = f.read()
                    decrypted_data = self.decrypt_data(encrypted_data)
                    if decrypted_data:
                        self.settings.update(decrypted_data)
            except Exception as e:
                print(f"Ошибка загрузки настроек: {e}")
    
    def save_settings(self):
        """Сохранение зашифрованных настроек"""
        try:
            encrypted_data = self.encrypt_data(self.settings)
            with open(self.settings_file, "wb") as f:
                f.write(encrypted_data)
        except Exception as e:
            print(f"Ошибка сохранения настроек: {e}")
    
    def apply_theme(self):
        """Применение выбранной темы"""
        if self.settings["theme"] == "dark":
            self.bg_color = "#2d2d2d"
            self.card_bg = "#3d3d3d"
            self.card_border = "#4a4a4a"
            self.text_color = "#ffffff"
            self.timer_color = "#4a6baf"
        else:
            self.bg_color = "#f5f5f5"
            self.card_bg = "#ffffff"
            self.card_border = "#e0e0e0"
            self.text_color = "#000000"
            self.timer_color = "#4a6baf"
        
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        # Настройка стилей
        self.style.configure('.', background=self.bg_color)
        self.style.configure('TFrame', background=self.bg_color)
        self.style.configure('TLabel', background=self.bg_color, foreground=self.text_color)
        self.style.configure('TButton', background=self.bg_color)
        self.style.configure('Header.TLabel', font=('Helvetica', 16, 'bold'), 
                           foreground=self.text_color)
        self.style.configure('AccountFrame.TFrame', 
                           background=self.card_bg,
                           borderwidth=1,
                           relief='solid',
                           bordercolor=self.card_border)

    def load_accounts(self):
        """Загрузка зашифрованных аккаунтов"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, "rb") as f:
                    encrypted_data = f.read()
                    decrypted_data = self.decrypt_data(encrypted_data)
                    if decrypted_data:
                        for name, secret in decrypted_data.items():
                            self.accounts[name] = pyotp.TOTP(secret)
                        self.update_account_list()
                        self.status_bar.config(text=f"Загружено {len(self.accounts)} аккаунтов")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось загрузить аккаунты: {str(e)}")
    
    def save_accounts(self):
        """Сохранение зашифрованных аккаунтов"""
        try:
            data = {name: totp.secret for name, totp in self.accounts.items()}
            encrypted_data = self.encrypt_data(data)
            with open(self.config_file, "wb") as f:
                f.write(encrypted_data)
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить аккаунты: {str(e)}")

    def create_widgets(self):
        """Создание элементов интерфейса"""
        # Заголовок
        header_frame = ttk.Frame(self.root)
        header_frame.pack(pady=10, fill='x', padx=10)
        
        ttk.Label(header_frame, text="2FA Authenticator", style='Header.TLabel').pack(side='left')
        
        # Кнопка настроек
        settings_btn = ttk.Button(header_frame, text="⚙", width=2, 
                                command=self.show_settings)
        settings_btn.pack(side='right', padx=5)
        
        # Панель кнопок
        button_frame = ttk.Frame(self.root)
        button_frame.pack(pady=10, fill='x', padx=10)
        
        ttk.Button(button_frame, text="Добавить", command=self.add_account).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Импорт", command=self.import_accounts).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Экспорт", command=self.export_accounts).pack(side='left', padx=5)
        
        # Контейнер для аккаунтов с прокруткой
        self.container = ttk.Frame(self.root)
        self.container.pack(fill='both', expand=True, padx=10, pady=5)
        
        self.canvas = tk.Canvas(self.container, bg=self.bg_color, highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(self.container, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = ttk.Frame(self.canvas)
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(
                scrollregion=self.canvas.bbox("all")
            )
        )
        
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor='nw')
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        
        # Прокрутка колесиком мыши
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)
        
        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")
        
        # Строка состояния
        self.status_bar = ttk.Label(self.root, text="Готов", relief='sunken', anchor='w')
        self.status_bar.pack(fill='x', ipady=2)
    
    def _on_mousewheel(self, event):
        """Обработчик прокрутки колесика мыши"""
        self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")
    
    def update_account_list(self):
        """Обновление списка аккаунтов"""
        # Очистка существующих элементов
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
        
        self.account_frames = {}
        
        for account_name in self.accounts.keys():
            # Основной фрейм с обводкой
            frame = ttk.Frame(
                self.scrollable_frame, 
                style='AccountFrame.TFrame',
                padding=(15, 10)
            )
            frame.pack(fill='x', pady=5, ipadx=5, ipady=5)
            
            # Дополнительная обводка сверху
            border_frame = ttk.Frame(frame, height=1, style='AccountFrame.TFrame')
            border_frame.pack(fill='x', pady=(0, 5))
            
            # Основное содержимое плашки
            content_frame = ttk.Frame(frame)
            content_frame.pack(fill='x', expand=True)
            
            # Название аккаунта
            name_label = ttk.Label(
                content_frame, 
                text=account_name, 
                font=('Helvetica', 11, 'bold'),
                anchor='w',
                foreground=self.text_color
            )
            name_label.pack(side='left', fill='x', expand=True)
            
            # Код 2FA
            totp = self.accounts[account_name]
            current_code = totp.now()
            formatted_code = f"{current_code[:3]} {current_code[3:]}"
            
            self.code_label = ttk.Label(
                content_frame, 
                text=formatted_code,
                font=('Courier', 16, 'bold'),
                foreground=self.timer_color,
                anchor='e'
            )
            self.code_label.pack(side='right')
            
            # Размытие кода, если включено
            if self.settings["blur_codes"]:
                self.apply_blur(self.code_label)
            
            # Таймер
            timer_canvas = tk.Canvas(frame, width=250, height=4, bg=self.card_bg, highlightthickness=0)
            timer_canvas.pack(fill='x', pady=(5, 0))
            
            remaining_seconds = totp.interval - datetime.now().timestamp() % totp.interval
            progress_width = 400 * (remaining_seconds / totp.interval)
            
            if remaining_seconds < 10:
                color = '#f44336'
            elif remaining_seconds < 20:
                color = '#FFC107'
            else:
                color = '#4CAF50'
            
            timer_bar = timer_canvas.create_rectangle(0, 0, progress_width, 4, fill=color, outline='')
            
            # Сохраняем ссылки для обновления
            self.account_frames[account_name] = {
                'frame': frame,
                'code_label': self.code_label,
                'timer_canvas': timer_canvas,
                'timer_bar': timer_bar,
                'blurred': False
            }
            
            # Обработчики кликов
            frame.bind("<Button-1>", lambda e, name=account_name: self.copy_code(name))
            name_label.bind("<Button-1>", lambda e, name=account_name: self.copy_code(name))
            self.code_label.bind("<Button-1>", lambda e, name=account_name: self.copy_code(name))
            
            # Контекстное меню (ПКМ)
            frame.bind("<Button-3>", lambda e, name=account_name: self.show_context_menu(e, name))
    
    def apply_blur(self, label):
        """Применение размытия к коду"""
        if not self.settings["blur_codes"]:
            return
            
        text = label.cget("text")
        if not text:
            return
            
        # Создаем изображение с текстом
        img = Image.new('RGB', (100, 30), color=self.card_bg)
        draw = ImageDraw.Draw(img)
        draw.text((10, 10), text, fill='black')
        
        # Применяем размытие
        img = img.filter(ImageFilter.GaussianBlur(self.settings["blur_intensity"]))
        
        # Конвертируем в PhotoImage
        photo = ImageTk.PhotoImage(img)
        
        # Обновляем label
        label.config(image=photo, text='', compound='center')
        label.image = photo
        label.blurred = True
    
    def drag_start(self, event, item):
        """Начало перетаскивания"""
        self.drag_data["item"] = item
        self.drag_data["y"] = event.y
    
    def drag_stop(self, event):
        """Конец перетаскивания"""
        self.drag_data["item"] = None
        self.drag_data["y"] = 0
    
    def drag_motion(self, event):
        """Перетаскивание плашки"""
        if not self.drag_data["item"]:
            return
            
        dy = event.y - self.drag_data["y"]
        self.drag_data["item"].place(y=self.drag_data["item"].winfo_y() + dy)
        self.drag_data["y"] = event.y
    
    def show_context_menu(self, event, account_name):
        """Контекстное меню для аккаунта"""
        menu = tk.Menu(self.root, tearoff=0)
        menu.add_command(label=f"Копировать код {account_name}", 
                       command=lambda: self.copy_code(account_name))
        menu.add_separator()
        menu.add_command(label=f"Удалить {account_name}", 
                       command=lambda: self.remove_account(account_name))
        menu.tk_popup(event.x_root, event.y_root)
    
    def copy_code(self, account_name):
        """Копирование кода в буфер обмена"""
        totp = self.accounts[account_name]
        current_code = totp.now()
        pyperclip.copy(current_code)
        self.status_bar.config(text=f"Скопирован код для {account_name}")
        
        # Анимация подсветки
        frame = self.account_frames[account_name]['frame']
        original_bg = frame.cget('style')
        frame.configure(style='TFrame')
        frame.after(100, lambda: frame.configure(style=original_bg))
    
    def update_account_cards(self):
        """Обновление всех карточек аккаунтов"""
        for account_name, widgets in self.account_frames.items():
            totp = self.accounts[account_name]
            current_code = totp.now()
            formatted_code = f"{current_code[:3]} {current_code[3:]}"
            
            if self.settings["blur_codes"]:
                if not widgets.get('blurred', False):
                    widgets['code_label'].config(text=formatted_code)
                    self.apply_blur(widgets['code_label'])
                    widgets['blurred'] = True
            else:
                widgets['code_label'].config(text=formatted_code, image='')
                widgets['blurred'] = False
            
            remaining_seconds = totp.interval - datetime.now().timestamp() % totp.interval
            progress_width = 400 * (remaining_seconds / totp.interval)
            
            if remaining_seconds < 10:
                color = '#f44336'
            elif remaining_seconds < 20:
                color = '#FFC107'
            else:
                color = '#4CAF50'
            
            widgets['timer_canvas'].coords(widgets['timer_bar'], 0, 0, progress_width, 4)
            widgets['timer_canvas'].itemconfig(widgets['timer_bar'], fill=color)
    
    def update_codes(self):
        """Поток для периодического обновления кодов"""
        while self.running:
            self.update_account_cards()
            time.sleep(1)

    def show_settings(self):
        """Окно настроек"""
        settings_window = tk.Toplevel(self.root)
        settings_window.title("Настройки")
        settings_window.geometry("350x400")
        settings_window.resizable(False, False)
        
        # Настройки размытия
        blur_frame = ttk.Frame(settings_window)
        blur_frame.pack(fill='x', padx=15, pady=10)
        
        self.blur_var = tk.BooleanVar(value=self.settings["blur_codes"])
        blur_cb = ttk.Checkbutton(
            blur_frame, 
            text="Размывать коды", 
            variable=self.blur_var,
            command=self.toggle_blur
        )
        blur_cb.pack(anchor='w')
        
        # Интенсивность размытия
        intensity_frame = ttk.Frame(settings_window)
        intensity_frame.pack(fill='x', padx=15, pady=5)
        
        ttk.Label(intensity_frame, text="Интенсивность:").pack(side='left')
        self.intensity_scale = ttk.Scale(
            intensity_frame, 
            from_=1, 
            to=10, 
            value=self.settings["blur_intensity"],
            command=self.update_blur_intensity
        )
        self.intensity_scale.pack(side='left', padx=10, expand=True, fill='x')
        
        # Настройки темы
        theme_frame = ttk.Frame(settings_window)
        theme_frame.pack(fill='x', padx=15, pady=10)
        
        ttk.Label(theme_frame, text="Тема:").pack(anchor='w')
        
        self.theme_var = tk.StringVar(value=self.settings["theme"])
        ttk.Radiobutton(
            theme_frame, 
            text="Светлая", 
            variable=self.theme_var, 
            value="light",
            command=self.change_theme
        ).pack(anchor='w')
        
        ttk.Radiobutton(
            theme_frame, 
            text="Темная", 
            variable=self.theme_var, 
            value="dark",
            command=self.change_theme
        ).pack(anchor='w')
        
        # Автозагрузка
        autostart_frame = ttk.Frame(settings_window)
        autostart_frame.pack(fill='x', padx=15, pady=10)
        
        self.autostart_var = tk.BooleanVar(value=self.settings["start_with_system"])
        autostart_cb = ttk.Checkbutton(
            autostart_frame, 
            text="Запускать при старте системы", 
            variable=self.autostart_var,
            command=self.toggle_autostart
        )
        autostart_cb.pack(anchor='w')
        
        # Кнопки
        btn_frame = ttk.Frame(settings_window)
        btn_frame.pack(fill='x', padx=15, pady=10)
        
        ttk.Button(
            btn_frame, 
            text="Закрыть", 
            command=settings_window.destroy
        ).pack(fill='x')
    
    def toggle_blur(self):
        """Переключение размытия кодов"""
        self.settings["blur_codes"] = self.blur_var.get()
        self.save_settings()
        self.update_account_cards()
    
    def update_blur_intensity(self, value):
        """Обновление интенсивности размытия"""
        self.settings["blur_intensity"] = int(float(value))
        self.save_settings()
        if self.settings["blur_codes"]:
            self.update_account_cards()
    
    def change_theme(self):
        """Смена темы"""
        self.settings["theme"] = self.theme_var.get()
        self.save_settings()
        self.apply_theme()
        self.update_account_list()
    
    def toggle_autostart(self):
        """Переключение автозагрузки"""
        self.settings["start_with_system"] = self.autostart_var.get()
        self.set_autostart(self.settings["start_with_system"])
        self.save_settings()

    def add_account(self):
        """Добавление нового аккаунта"""
        account_name = simpledialog.askstring("Добавить аккаунт", "Введите имя аккаунта (например, Google):")
        if not account_name:
            return
            
        secret_key = simpledialog.askstring("Добавить аккаунт", "Введите секретный ключ (оставьте пустым для генерации):")
        if secret_key is None:
            return
            
        if not secret_key:
            secret_key = pyotp.random_base32()
            messagebox.showinfo("Новый ключ", 
                             f"Сгенерирован новый ключ для {account_name}:\n\n{secret_key}\n\n"
                             "Сохраните его в надежном месте!", parent=self.root)
        
        self.accounts[account_name] = pyotp.TOTP(secret_key)
        self.update_account_list()
        self.save_accounts()
        self.status_bar.config(text=f"Добавлен аккаунт: {account_name}")
    
    def import_accounts(self):
        """Импорт аккаунтов из файла"""
        file_path = filedialog.askopenfilename(
            title="Выберите файл для импорта",
            filetypes=[("JSON файлы", "*.json"), ("Все файлы", "*.*")]
        )
        
        if file_path:
            try:
                with open(file_path, 'r') as f:
                    data = json.load(f)
                    
                if isinstance(data, dict):
                    for name, secret in data.items():
                        self.accounts[name] = pyotp.TOTP(secret)
                    
                    self.update_account_list()
                    self.save_accounts()
                    self.status_bar.config(text=f"Импортировано {len(data)} аккаунтов")
                    messagebox.showinfo("Успех", f"Импортировано {len(data)} аккаунтов", parent=self.root)
                else:
                    messagebox.showerror("Ошибка", "Неверный формат файла", parent=self.root)
            except Exception as e:
                messagebox.showerror("Ошибка", f"Ошибка импорта: {str(e)}", parent=self.root)
    
    def export_accounts(self):
        """Экспорт аккаунтов в файл"""
        if not self.accounts:
            messagebox.showwarning("Предупреждение", "Нет аккаунтов для экспорта", parent=self.root)
            return
            
        file_path = filedialog.asksaveasfilename(
            title="Сохранить файл экспорта",
            defaultextension=".json",
            filetypes=[("JSON файлы", "*.json"), ("Все файлы", "*.*")]
        )
        
        if file_path:
            try:
                data = {name: totp.secret for name, totp in self.accounts.items()}
                with open(file_path, 'w') as f:
                    json.dump(data, f, indent=2)
                
                self.status_bar.config(text=f"Экспортировано {len(data)} аккаунтов")
                messagebox.showinfo("Успех", f"Экспортировано {len(data)} аккаунтов", parent=self.root)
            except Exception as e:
                messagebox.showerror("Ошибка", f"Ошибка экспорта: {str(e)}", parent=self.root)
    
    def remove_account(self, account_name):
        """Удаление аккаунта"""
        if messagebox.askyesno("Подтверждение", f"Удалить аккаунт '{account_name}'?", parent=self.root):
            del self.accounts[account_name]
            self.update_account_list()
            self.save_accounts()
            self.status_bar.config(text=f"Удален аккаунт: {account_name}")
    
    def on_closing(self):
        """Обработчик закрытия приложения"""
        self.running = False
        if self.update_thread.is_alive():
            self.update_thread.join()
        self.save_accounts()
        self.save_settings()
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = TwoFactorAuthApp(root)
    
    # Запуск иконки в трее в отдельном потоке
    threading.Thread(target=app.run_tray_icon, daemon=True).start()
    
    root.mainloop()