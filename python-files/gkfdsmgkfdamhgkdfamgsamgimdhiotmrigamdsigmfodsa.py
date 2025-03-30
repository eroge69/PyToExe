import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, timedelta
import pandas as pd
import pyperclip
import time
import random
from tkinter import font as tkfont
import hashlib

# Ключи для доступа
VALID_KEYS = {
    hashlib.md5("Polkin".encode()).hexdigest(): True,
    hashlib.md5("Sidor".encode()).hexdigest(): True,
    hashlib.md5("Tatarin".encode()).hexdigest(): True,
    hashlib.md5("Sadkovsky".encode()).hexdigest(): True,
    hashlib.md5("Maslikhin".encode()).hexdigest(): True,
    hashlib.md5("1337".encode()).hexdigest(): True,
    hashlib.md5("Abdullin".encode()).hexdigest(): True
}

class AppManager:
    def __init__(self):
        self.current_window = None
        self.start_auth()
    
    def start_auth(self):
        if self.current_window:
            self.current_window.destroy()
        self.current_window = KeyAuthWindow(self.start_splash)
    
    def start_splash(self):
        if self.current_window:
            self.current_window.destroy()
        self.current_window = SplashScreen(self.start_main_app)
    
    def start_main_app(self):
        if self.current_window:
            self.current_window.destroy()
        self.current_window = DiaryGenerator()

class KeyAuthWindow:
    def __init__(self, callback):
        self.root = tk.Tk()
        self.callback = callback
        self.root.title("Авторизация Генератор Дневников 3.0V")
        self.root.geometry("400x200")
        self.root.resizable(False, False)
        self.center_window()
        
        self.bg_color = "#2c3e50"
        self.fg_color = "white"
        self.accent_color = "#3498db"
        
        self.main_frame = tk.Frame(self.root, bg=self.bg_color)
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        self.title_label = tk.Label(self.main_frame, 
                                  text="Введите ключ доступа",                                 
                                  font=("Arial", 16, "bold"), 
                                  bg=self.bg_color, fg=self.fg_color)
        self.title_label.pack(pady=(20, 10))
        
        self.key_entry = ttk.Entry(self.main_frame, width=30, font=("Arial", 12), show="*")
        self.key_entry.pack(pady=10)
        self.key_entry.focus()
        
        self.auth_btn = ttk.Button(self.main_frame, text="Войти", command=self.check_key)
        self.auth_btn.pack(pady=10)
        
        self.status_label = tk.Label(self.main_frame, text="", font=("Arial", 10), bg=self.bg_color, fg="#e74c3c")
        self.status_label.pack()
        
        self.root.bind('<Return>', lambda event: self.check_key())
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        self.root.mainloop()
    
    def center_window(self):
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f"{width}x{height}+{x}+{y}")
    
    def check_key(self):
        entered_key = self.key_entry.get()
        hashed_key = hashlib.md5(entered_key.encode()).hexdigest()
        
        if hashed_key in VALID_KEYS:
            self.root.destroy()
            self.callback()
        else:
            self.status_label.config(text="Неверный ключ доступа!")
            self.key_entry.delete(0, tk.END)
            self.shake_window()
    
    def shake_window(self):
        x = self.root.winfo_x()
        y = self.root.winfo_y()
        for i in range(0, 3):
            for dx, dy in [(10,0), (-10,0), (10,0), (-10,0)]:
                self.root.geometry(f"+{x+dx}+{y+dy}")
                self.root.update()
                time.sleep(0.02)
        self.root.geometry(f"+{x}+{y}")
    
    def on_close(self):
        self.root.destroy()
        exit()

class SplashScreen:
    def __init__(self, callback):
        self.root = tk.Tk()
        self.callback = callback
        self.root.title("Загрузка...")
        self.root.geometry("400x300")
        self.root.overrideredirect(True)
        self.center_window()
        
        self.bg_color = "#2c3e50"
        self.fg_color = "white"
        self.accent_color = "#3498db"
        
        self.main_frame = tk.Frame(self.root, bg=self.bg_color)
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        self.logo_label = tk.Label(self.main_frame, text="⚕", font=("Arial", 60), 
                                 bg=self.bg_color, fg=self.accent_color)
        self.logo_label.pack(pady=(30, 10))
        
        self.title_label = tk.Label(self.main_frame, 
                                  text="Медицинский Генератор Дневников\nV 3.0", 
                                  font=("Arial", 16, "bold"), 
                                  bg=self.bg_color, fg=self.fg_color)
        self.title_label.pack(pady=(0, 20))
        
        self.progress = ttk.Progressbar(self.main_frame, orient=tk.HORIZONTAL, 
                                      length=250, mode='determinate')
        self.progress.pack(pady=10)
        
        self.status_label = tk.Label(self.main_frame, text="Загрузка данных...", 
                                   font=("Arial", 10), bg=self.bg_color, fg=self.fg_color)
        self.status_label.pack()
        
        self.author_label = tk.Label(self.main_frame, 
                                   text="by Svyatoslav and Vladimir", 
                                   font=("Arial", 8), 
                                   bg=self.bg_color, fg="#bdc3c7")
        self.author_label.pack(side=tk.BOTTOM, pady=10)
        
        self.root.after(100, self.animate_progress)
        self.root.mainloop()
    
    def center_window(self):
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f"{width}x{height}+{x}+{y}")
    
    def animate_progress(self):
        for i in range(101):
            self.progress['value'] = i
            self.status_label.config(text=f"Загрузка... {i}%")
            self.root.update()
            time.sleep(0.03)
        
        self.root.after(500, self.close_splash)
    
    def close_splash(self):
        self.root.destroy()
        self.callback()

class DiaryGenerator:
    def __init__(self):
        self.root = tk.Tk()
        self.setup_main_window()
        self.create_widgets()
        self.setup_styles()
        self.center_window()
        self.root.mainloop()
    
    def center_window(self):
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f"{width}x{height}+{x}+{y}")
    
    def setup_main_window(self):
        self.root.title("ГЕНЕРАТОР МЕДИЦИНСКИХ ДНЕВНИКОВ V 3.0")
        self.root.geometry("1000x800")
        self.root.configure(bg='#f5f7fa')
        
        try:
            self.root.iconbitmap("medical_icon.ico")
        except:
            pass
        
        self.category_colors = {
            'Голова': '#3498db',
            'Нерв': '#9b59b6',
            'Спина': '#1abc9c',
            'После операции': '#e74c3c',
            'Заключительный': '#2ecc71'
        }
    
    def setup_styles(self):
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        self.style.configure('TFrame', background='#f5f7fa')
        self.style.configure('TLabel', background='#f5f7fa', font=('Arial', 10))
        self.style.configure('TButton', font=('Arial', 10), padding=8)
        
        self.style.configure('Generate.TButton', 
                           font=('Arial', 12, 'bold'),
                           foreground='white',
                           background='#27ae60',
                           padding=10,
                           borderwidth=0)
        self.style.map('Generate.TButton',
            foreground=[('pressed', 'white'), ('active', 'white')],
            background=[('pressed', '#219653'), ('active', '#2ecc71')]
        )
        
        for category, color in self.category_colors.items():
            self.style.configure(f'{category}.TButton', 
                               font=('Arial', 11, 'bold'),
                               foreground='white',
                               background=color,
                               padding=10)
    
    def create_widgets(self):
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        self.create_header(main_frame)
        self.create_input_fields(main_frame)
        self.create_category_buttons(main_frame)
        self.create_output_field(main_frame)
        self.create_control_buttons(main_frame)
    
    def create_header(self, parent):
        header_frame = tk.Frame(parent, bg='#3498db', height=100)
        header_frame.pack(fill=tk.X, pady=(0, 20))
        
        title_label = tk.Label(header_frame, 
                             text="ГЕНЕРАТОР МЕДИЦИНСКИХ ДНЕВНИКОВ",
                             font=('Arial', 18, 'bold'), 
                             bg='#3498db', fg='white')
        title_label.pack(pady=15)
        
        self.gen_btn = ttk.Button(header_frame, 
                                text="СГЕНЕРИРОВАТЬ ИСТОРИЮ", 
                                style='Generate.TButton',
                                command=self.generate_random)
        self.gen_btn.pack(side=tk.RIGHT, padx=20, pady=10)
        self.gen_btn.bind("<Enter>", self.move_button)
    
    def move_button(self, event):
        btn = event.widget
        x = random.randint(10, 100)
        y = random.randint(10, 30)
        btn.place(x=x, y=y)
        btn.after(300, lambda: btn.pack(side=tk.RIGHT, padx=20, pady=10))
    
    def generate_random(self):
        categories = list(self.category_colors.keys())
        self.generate_diary(random.choice(categories))
    
    def create_input_fields(self, parent):
        input_frame = ttk.LabelFrame(parent, text="Основные параметры", padding=15)
        input_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(input_frame, text="Лечащий врач:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.doctor_entry = ttk.Entry(input_frame, width=30, font=('Arial', 10))
        self.doctor_entry.grid(row=0, column=1, padx=5, pady=5, sticky=tk.W)
        
        ttk.Label(input_frame, text="Начальник отделения:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.head_entry = ttk.Entry(input_frame, width=30, font=('Arial', 10))
        self.head_entry.grid(row=1, column=1, padx=5, pady=5, sticky=tk.W)
        
        ttk.Label(input_frame, text="Тип начальника:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        self.head_type = ttk.Combobox(input_frame, values=["ВрИО Нач. НХО", "Нач. НХО"], 
                                    width=15, font=('Arial', 10))
        self.head_type.grid(row=2, column=1, sticky=tk.W, padx=5, pady=5)
        self.head_type.set("ВрИО Нач. НХО")
        
        ttk.Label(input_frame, text="Начальная дата:").grid(row=3, column=0, sticky=tk.W, padx=5, pady=5)
        self.date_entry = ttk.Entry(input_frame, width=15, font=('Arial', 10))
        self.date_entry.grid(row=3, column=1, sticky=tk.W, padx=5, pady=5)
        self.date_entry.insert(0, datetime.now().strftime('%d.%m.%Y'))
        
        ttk.Label(input_frame, text="Конечная дата:").grid(row=4, column=0, sticky=tk.W, padx=5, pady=5)
        self.end_date_entry = ttk.Entry(input_frame, width=15, font=('Arial', 10))
        self.end_date_entry.grid(row=4, column=1, sticky=tk.W, padx=5, pady=5)
        self.end_date_entry.insert(0, (datetime.now() + timedelta(days=7)).strftime('%d.%m.%Y'))
        
        ttk.Label(input_frame, text="Периодичность (дней):").grid(row=5, column=0, sticky=tk.W, padx=5, pady=5)
        self.period_entry = ttk.Spinbox(input_frame, from_=1, to=30, width=5, font=('Arial', 10))
        self.period_entry.grid(row=5, column=1, sticky=tk.W, padx=5, pady=5)
        self.period_entry.set(1)
    
    def create_category_buttons(self, parent):
        category_frame = ttk.LabelFrame(parent, text="Категории дневников", padding=15)
        category_frame.pack(fill=tk.BOTH, pady=10, expand=True)
        
        btn_frame = ttk.Frame(category_frame)
        btn_frame.pack(fill=tk.BOTH, expand=True)
        
        categories = list(self.category_colors.keys())
        for i, category in enumerate(categories):
            btn = ttk.Button(btn_frame, 
                           text=category, 
                           style=f'{category}.TButton',
                           command=lambda c=category: self.generate_diary(c))
            btn.grid(row=i//2, column=i%2, padx=10, pady=10, sticky="nsew")
            btn_frame.grid_columnconfigure(i%2, weight=1)
        
        for i in range((len(categories)+1)//2):
            btn_frame.grid_rowconfigure(i, weight=1)
    
    def create_output_field(self, parent):
        output_frame = ttk.LabelFrame(parent, text="Сгенерированный дневник", padding=15)
        output_frame.pack(fill=tk.BOTH, pady=10, expand=True)
        
        self.output_text = tk.Text(output_frame, 
                                 height=15, 
                                 wrap=tk.WORD, 
                                 font=('Arial', 10), 
                                 padx=10, 
                                 pady=10,
                                 bg='white',
                                 fg='#2c3e50',
                                 insertbackground='#3498db',
                                 selectbackground='#3498db',
                                 selectforeground='white')
        self.output_text.pack(fill=tk.BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(output_frame, orient="vertical", command=self.output_text.yview)
        scrollbar.pack(side="right", fill="y")
        self.output_text.configure(yscrollcommand=scrollbar.set)
    
    def create_control_buttons(self, parent):
        control_frame = ttk.Frame(parent)
        control_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(control_frame, 
                 text="Копировать", 
                 command=self.copy_to_clipboard).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(control_frame, 
                 text="Очистить", 
                 command=self.clear_output).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(control_frame, 
                 text="Сгенерировать за период", 
                 command=self.generate_for_period).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(control_frame, 
                 text="Сохранить в Excel", 
                 command=self.save_to_excel).pack(side=tk.RIGHT, padx=5)
    
    def generate_vital_signs(self):
        bp = f"{random.randint(100, 140)}/{random.randint(60, 90)}"
        pulse = random.randint(60, 90)
        rr = random.randint(12, 20)
        return bp, pulse, rr
    
    def generate_diary(self, category):
        try:
            doctor = self.doctor_entry.get().strip()
            head = self.head_entry.get().strip()
            head_type = self.head_type.get().strip()
            date_str = self.date_entry.get().strip()
            period = int(self.period_entry.get())
            
            if not doctor or not head or not date_str:
                messagebox.showerror("Ошибка", "Заполните все обязательные поля", parent=self.root)
                return
            
            date = datetime.strptime(date_str, '%d.%m.%Y')
            date += timedelta(days=period)
            self.date_entry.delete(0, tk.END)
            self.date_entry.insert(0, date.strftime('%d.%m.%Y'))
            
            bp, pulse, rr = self.generate_vital_signs()
            diary = self.get_diary_template(category, doctor, head, head_type, date, bp, pulse, rr)
            
            self.output_text.config(state=tk.NORMAL)
            # Вместо удаления предыдущего текста добавляем разделитель и новую запись
            if self.output_text.get(1.0, tk.END).strip():
                self.output_text.insert(tk.END, "\n\n" + "="*80 + "\n\n")
            self.output_text.insert(tk.END, diary)
            self.output_text.see(tk.END)  # Прокручиваем к новому содержимому
            self.output_text.config(state=tk.NORMAL)
            
        except ValueError as e:
            messagebox.showerror("Ошибка", f"Некорректный формат даты или числа: {e}", parent=self.root)
    
    def generate_for_period(self):
        try:
            doctor = self.doctor_entry.get().strip()
            head = self.head_entry.get().strip()
            head_type = self.head_type.get().strip()
            start_date_str = self.date_entry.get().strip()
            end_date_str = self.end_date_entry.get().strip()
            period = int(self.period_entry.get())
            
            if not doctor or not head or not start_date_str or not end_date_str:
                messagebox.showerror("Ошибка", "Заполните все обязательные поля", parent=self.root)
                return
            
            start_date = datetime.strptime(start_date_str, '%d.%m.%Y')
            end_date = datetime.strptime(end_date_str, '%d.%m.%Y')
            
            if start_date > end_date:
                messagebox.showerror("Ошибка", "Конечная дата должна быть позже начальной", parent=self.root)
                return
            
            current_date = start_date
            diaries = []
            category = self.get_selected_category()
            
            self.output_text.config(state=tk.NORMAL)
            # Добавляем разделитель, если уже есть текст
            if self.output_text.get(1.0, tk.END).strip():
                self.output_text.insert(tk.END, "\n\n" + "="*80 + "\n\n")
            
            while current_date <= end_date:
                bp, pulse, rr = self.generate_vital_signs()
                diary = self.get_diary_template(category, doctor, head, head_type, current_date, bp, pulse, rr)
                diaries.append(diary)
                
                if current_date + timedelta(days=period) <= end_date:
                    diary += "\n\n" + "-"*80 + "\n\n"
                
                current_date += timedelta(days=period)
            
            self.date_entry.delete(0, tk.END)
            self.date_entry.insert(0, current_date.strftime('%d.%m.%Y'))
            
            self.output_text.insert(tk.END, "\n\n".join(diaries))
            self.output_text.see(tk.END)  # Прокручиваем к новому содержимому
            self.output_text.config(state=tk.NORMAL)
            
        except ValueError as e:
            messagebox.showerror("Ошибка", f"Некорректный формат даты или числа: {e}", parent=self.root)
    
    def generate_for_period(self):
        try:
            doctor = self.doctor_entry.get().strip()
            head = self.head_entry.get().strip()
            head_type = self.head_type.get().strip()
            start_date_str = self.date_entry.get().strip()
            end_date_str = self.end_date_entry.get().strip()
            period = int(self.period_entry.get())
            
            if not doctor or not head or not start_date_str or not end_date_str:
                messagebox.showerror("Ошибка", "Заполните все обязательные поля", parent=self.root)
                return
            
            start_date = datetime.strptime(start_date_str, '%d.%m.%Y')
            end_date = datetime.strptime(end_date_str, '%d.%m.%Y')
            
            if start_date > end_date:
                messagebox.showerror("Ошибка", "Конечная дата должна быть позже начальной", parent=self.root)
                return
            
            current_date = start_date
            diaries = []
            category = self.get_selected_category()
            
            self.output_text.config(state=tk.NORMAL)
            self.output_text.delete(1.0, tk.END)
            
            while current_date <= end_date:
                bp, pulse, rr = self.generate_vital_signs()
                diary = self.get_diary_template(category, doctor, head, head_type, current_date, bp, pulse, rr)
                diaries.append(diary)
                
                if current_date + timedelta(days=period) <= end_date:
                    diary += "\n\n" + "-"*80 + "\n\n"
                
                current_date += timedelta(days=period)
            
            self.date_entry.delete(0, tk.END)
            self.date_entry.insert(0, current_date.strftime('%d.%m.%Y'))
            
            self.output_text.insert(tk.END, "\n\n".join(diaries))
            self.output_text.config(state=tk.NORMAL)
            
        except ValueError as e:
            messagebox.showerror("Ошибка", f"Некорректный формат даты или числа: {e}", parent=self.root)
    
    def get_selected_category(self):
        for category in self.category_colors:
            if hasattr(self, f'{category}_btn'):
                if self.__dict__[f'{category}_btn'].state():
                    return category
        return 'Голова'
    
    def get_diary_template(self, category, doctor, head, head_type, date, bp, pulse, rr):
        time_str = "12:20" if category != "Заключительный" else "12:00"
        
        templates = {
            'Голова': (
                f"{date.strftime('%d.%m.%Y')}   {time_str}\n"
                f"Состояние удовлетворительное. Жалобы на головную боль, головокружение.\n"
                f"В легких дыхание везикулярное, хрипов нет. АД={bp} мм.рт.ст. Пульс {pulse} уд/мин. ЧД {rr} в мин.\n"
                f"Живот мягкий, безболезненный. Физ. отправления в норме. Назначена терапия.\n\n"
                f"{' ' * 60}Леч. врач{' ' * 20}{doctor}\n\n"
                f"{' ' * 60}{head_type}{' ' * 15}{head}"
            ),
            'Нерв': (
                f"{date.strftime('%d.%m.%Y')}   {time_str}\n"
                f"Состояние удовлетворительное. Жалобы на онемение конечностей, слабость.\n"
                f"Неврологический статус: сознание ясное, ориентация сохранена.\n"
                f"АД={bp} мм.рт.ст. Пульс {pulse} уд/мин. ЧД {rr} в мин.\n"
                f"Сухожильные рефлексы живые, D=S. Координаторные пробы с интенцией.\n\n"
                f"{' ' * 60}Леч. врач{' ' * 20}{doctor}\n\n"
                f"{' ' * 60}{head_type}{' ' * 15}{head}"
            ),
            'Спина': (
                f"{date.strftime('%d.%m.%Y')}   {time_str}\n"
                f"Состояние удовлетворительное. Жалобы на боли в поясничном отделе.\n"
                f"Пальпация болезненна на уровне L4-L5. Симптом натяжения (+).\n"
                f"АД={bp} мм.рт.ст. Пульс {pulse} уд/мин. ЧД {rr} в мин.\n"
                f"Рекомендовано: ЛФК, физиотерапия, медикаментозная терапия.\n\n"
                f"{' ' * 60}Леч. врач{' ' * 20}{doctor}\n\n"
                f"{' ' * 60}{head_type}{' ' * 15}{head}"
            ),
            'После операции': (
                f"{date.strftime('%d.%m.%Y')}   {time_str}\n"
                f"Состояние удовлетворительное. Послеоперационный период без осложнений.\n"
                f"Рана чистая, сухая. Швы не напряжены. Температура 36.6°C.\n"
                f"АД={bp} мм.рт.ст. Пульс {pulse} уд/мин. ЧД {rr} в мин.\n"
                f"Рекомендована перевязка, продолжение терапии.\n\n"
                f"{' ' * 60}Леч. врач{' ' * 20}{doctor}\n\n"
                f"{' ' * 60}{head_type}{' ' * 15}{head}"
            ),
            'Заключительный': (
                f"{date.strftime('%d.%m.%Y')}   {time_str}\n"
                f"Заключительный осмотр. Состояние удовлетворительное.\n"
                f"Болевой синдром регрессировал. Живот мягкий, безболезненный.\n"
                f"АД={bp} мм.рт.ст. Пульс {pulse} уд/мин. ЧД {rr} в мин.\n"
                f"Курс лечения завершен. Даны рекомендации. Претензий нет.\n\n"
                f"{' ' * 60}Леч. врач{' ' * 20}{doctor}\n\n"
                f"{' ' * 60}{head_type}{' ' * 15}{head}"
            )
        }
        return templates.get(category, "Неизвестная категория")
    
    def copy_to_clipboard(self):
        text = self.output_text.get(1.0, tk.END).strip()
        if text:
            pyperclip.copy(text)
            messagebox.showinfo("Успех", "Текст скопирован в буфер обмена", parent=self.root)
        else:
            messagebox.showwarning("Предупреждение", "Нет текста для копирования", parent=self.root)
    
    def clear_output(self):
        self.output_text.config(state=tk.NORMAL)
        self.output_text.delete(1.0, tk.END)
    
    def save_to_excel(self):
        text = self.output_text.get(1.0, tk.END).strip()
        if not text:
            messagebox.showwarning("Предупреждение", "Нет текста для сохранения", parent=self.root)
            return
        
        try:
            diaries = text.split("\n\n" + "-"*80 + "\n\n")
            
            data = []
            current_date = datetime.strptime(self.date_entry.get().strip(), '%d.%m.%Y')
            period = int(self.period_entry.get())
            
            for i, diary in enumerate(diaries):
                diary_date = current_date - timedelta(days=period * (len(diaries) - i - 1))
                data.append({
                    'Дата': diary_date,
                    'Дневник': diary,
                    'Лечащий врач': self.doctor_entry.get().strip(),
                    'Начальник отделения': self.head_entry.get().strip(),
                    'Тип дневника': self.get_current_category(diary)
                })
            
            df = pd.DataFrame(data)
            
            start_date = data[0]['Дата'].strftime('%Y%m%d')
            end_date = data[-1]['Дата'].strftime('%Y%m%d')
            
            file_path = f"дневники_{start_date}_по_{end_date}.xlsx"
            df.to_excel(file_path, index=False)
            messagebox.showinfo("Успех", f"Файл сохранен как {file_path}", parent=self.root)
            
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить файл: {e}", parent=self.root)
    
    def get_current_category(self, diary_text=""):
        if not diary_text:
            diary_text = self.output_text.get(1.0, tk.END)
        
        for category in self.category_colors:
            if category in diary_text:
                return category
        return "Неизвестная категория"

if __name__ == "__main__":
    app = AppManager()