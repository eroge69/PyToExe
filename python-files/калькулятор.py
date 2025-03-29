import tkinter as tk
from tkinter import ttk


class Calculator:
    def __init__(self, master):
        self.master = master
        master.title("Калькулятор")

        # Создаем поле для вывода
        self.display = tk.Entry(master, width=20, font=("Arial", 20))
        self.display.grid(row=0, column=0, columnspan=4)

        # Создаем кнопки
        buttons = [
            '7', '8', '9', '/',
            '4', '5', '6', '*',
            '1', '2', '3', '-',
            '0', '.', '=', '+'
        ]

        # Размещаем кнопки в сетке
        self.buttons = []
        row = 1
        col = 0
        for i in range(len(buttons)):
            text = buttons[i]

            # Создаем кнопку
            button = tk.Button(master, text=text, padx=20, pady=20,
                               font=("Arial", 16), command=lambda txt=text: self.click(txt))

            # Добавляем в список для дальнейшего использования
            self.buttons.append(button)

            # Размещаем в сетке
            button.grid(row=row, column=col)

            col += 1
            if col > 3:
                col = 0
                row += 1

        # Кнопка очистки
        clear_button = tk.Button(master, text="C", padx=20, pady=20,
                                 font=("Arial", 16), command=self.clear)
        clear_button.grid(row=5, column=0, columnspan=2)

        # Кнопка удаления
        delete_button = tk.Button(master, text="←", padx=20, pady=20,
                                  font=("Arial", 16), command=self.delete)
        delete_button.grid(row=5, column=2, columnspan=2)

    def click(self, key):
        if key == '=':
            try:
                result = eval(self.display.get())
                self.display.delete(0, tk.END)
                self.display.insert(0, str(result))
            except:
                self.display.delete(0, tk.END)
                self.display.insert(0, "Ошибка")
        elif key == 'C':
            self.clear()
        elif key == '←':
            self.delete()
        else:
            self.display.insert(tk.END, key)

    def clear(self):
        self.display.delete(0, tk.END)

    def delete(self):
        current = self.display.get()
        self.display.delete(0, tk.END)
        self.display.insert(0, current[:-1])


# Создаем окно
root = tk.Tk()
Calculator(root)
root.mainloop()