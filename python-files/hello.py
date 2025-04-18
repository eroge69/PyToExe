import tkinter as tk
from tkinter import messagebox

class MyApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Приветствие")
        self.root.geometry("400x300")  # Устанавливаем размер окна

        self.label = tk.Label(root, text="Привет всем!", font=("Arial", 14))
        self.label.pack(pady=20)

        self.button_who = tk.Button(root, text="Ты кто?", command=self.ask_who, font=("Arial", 12))
        self.button_who.pack(pady=10)

        self.button_hello = tk.Button(root, text="Привет", command=self.ask_name, font=("Arial", 12))
        self.button_hello.pack(pady=10)

        self.name = ""
        self.locked = False  # Флаг для блокировки закрытия окна

        # Переопределяем поведение закрытия окна
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def ask_who(self):
        messagebox.showinfo("Информация", "Я ваш виртуальный помощник!")

    def ask_name(self):
        if self.name:
            self.label.config(text=f"Привет, {self.name}! Как дела?")
            self.button_who.pack_forget()
            self.button_hello.pack_forget()

            self.button_normal = tk.Button(root, text="Нормально", command=self.say_great, font=("Arial", 12))
            self.button_normal.pack(pady=10)

            self.button_great = tk.Button(root, text="Круто", command=self.say_great, font=("Arial", 12))
            self.button_great.pack(pady=10)
        else:
            self.label.config(text="О дараво, как зовут?")
            self.button_who.pack_forget()
            self.button_hello.pack_forget()

            self.name_entry = tk.Entry(root, font=("Arial", 12))
            self.name_entry.pack(pady=10)

            self.submit_button = tk.Button(root, text="Отправить", command=self.submit_name, font=("Arial", 12))
            self.submit_button.pack(pady=10)

    def submit_name(self):
        self.name = self.name_entry.get()
        self.label.config(text=f"Привет, {self.name}!")
        self.name_entry.pack_forget()
        self.submit_button.pack_forget()

        self.button_who.pack(pady=10)
        self.button_hello.pack(pady=10)

    def say_great(self):
        self.label.config(text="Ха, сейчас исправим!", fg="red")
        self.button_normal.pack_forget()
        self.button_great.pack_forget()

        self.button_hello.config(text="Что ты сделал?", command=self.what_did_you_do)
        self.button_hello.pack(pady=10)

        self.locked = True  # Блокируем закрытие окна

    def what_did_you_do(self):
        self.label.config(text="Попробуй меня закрыть хаахахах", fg="red")
        self.button_hello.pack_forget()

        self.button_foo = tk.Button(root, text="Ты чо баран?", command=self.you_are_an_idiot, font=("Arial", 12))
        self.button_foo.pack(pady=10)

    def you_are_an_idiot(self):
        self.label.config(text="Нет, а ты да!!!!", fg="red")
        self.button_foo.pack_forget()

    def on_closing(self):
        # Переопределяем поведение закрытия окна
        if self.locked:
            pass  # Не закрываем окно, если оно заблокировано
        else:
            self.root.destroy()  # Закрываем окно, если оно не заблокировано

if __name__ == "__main__":
    root = tk.Tk()
    app = MyApp(root)
    root.mainloop()
