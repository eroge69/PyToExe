import time
import winsound
import tkinter as tk
from tkinter import messagebox

def start_timer():
    try:
        timer_duration = int(entry.get())
    except ValueError:
        messagebox.showerror("Ошибка", "Пожалуйста, введите целое число секунд.")
        return

    root.withdraw()  # Скрываем главное окно

    time.sleep(timer_duration)
    winsound.PlaySound("SystemExclamation", winsound.SND_ALIAS) # Проигрываем системный звук

    root.deiconify() # Показываем окно уведомления
    root.lift() # Поднимаем окно на передний план
    root.focus_force() # Фокусируем окно

    messagebox.showinfo("Таймер", "ПИЗДУЙ ВОДИТЬ ПАДАЛЬ!") # Показываем уведомление

root = tk.Tk()
root.title("ТАЙМЕР для ВОДИЛ")
root.geometry("300x150")

label = tk.Label(root, text="Введите время в секундах:")
label.pack(pady=10)

entry = tk.Entry(root)
entry.pack(pady=5)

button = tk.Button(root, text="Запустить таймер", command=start_timer)
button.pack(pady=10)

root.mainloop()
