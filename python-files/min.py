Python 3.13.2 (tags/v3.13.2:4f8bb39, Feb  4 2025, 15:23:48) [MSC v.1942 64 bit (AMD64)] on win32
Type "help", "copyright", "credits" or "license()" for more information.
>>> import tkinter as tk
>>> from tkinter import ttk
>>> root = tk.Tk()
>>> root.title("Calculator")
''
>>> display = ttk.Entry(root, font=("Helvetica", 24))
>>> display.grid(row=0, column=0, columnspan=4)
>>> def button_click(value):
...     current = display.get()
...     display.delete(0, tk.END)
...     display.insert(0, current + value)
... 
...     
>>> buttons = [
...     ('7', 1, 0), ('8', 1, 1), ('9', 1, 2), ('/', 1, 3),
...     ('4', 2, 0), ('5', 2, 1), ('6', 2, 2), ('*', 2, 3),
...     ('1', 3, 0), ('2', 3, 1), ('3', 3, 2), ('-', 3, 3),
...     ('0', 4, 0), ('.', 4, 1), ('=', 4, 2), ('+', 4, 3)
... ]
>>> for (text, row, col) in buttons:
...     button = ttk.Button(root, text=text, command=lambda t=text: button_click(t))
...     button.grid(row=row, column=col, padx=10, pady=10)
... 
...     
