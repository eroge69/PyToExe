import tkinter as tk
from tkinter import messagebox

def show_message():
    messagebox.showinfo("Сообщение", "Привет, Мир!")

root = tk.Tk()
root.title("Мое приложение")

test_button = tk.Button(root, text="Тест", command=show_message)
exit_button = tk.Button(root, text="Выход", command=root.destroy)

test_button.pack(pady=10)
exit_button.pack(pady=5)

root.mainloop()