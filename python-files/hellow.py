import tkinter as tk

# Створення головного вікна
window = tk.Tk()
window.title("Hello App")

# Додавання тексту
label = tk.Label(window, text="Hello, World!", font=("Arial", 24))
label.pack(padx=20, pady=20)

# Запуск головного циклу
window.mainloop()
