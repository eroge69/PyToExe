import tkinter as tk
from tkinter import ttk

# Создание главного окна
root = tk.Tk()
root.title("Мое первое приложение")
root.geometry("400x300")  # Ширина x Высота

# Метка (Label)
label = ttk.Label(root, text="Привет, Tkinter!")
label.pack(pady=10)  # pady - отступ сверху и снизу

# Поле ввода (Entry)
entry = ttk.Entry(root)
entry.pack(pady=10)

# Кнопка (Button)
def on_click():
    text = entry.get()
    label.config(text=f"Вы ввели: {text}")

button = ttk.Button(root, text="Нажми меня", command=on_click)
button.pack(pady=10)

# Запуск главного цикла
root.mainloop()