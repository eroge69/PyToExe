# Simple Calculator App

import tkinter as tk
from tkinter import messagebox

def calculate():
    try:
        num1 = float(entry1.get())
        num2 = float(entry2.get())
        operation = operation_var.get()
        
        if operation == '+':
            result = num1 + num2
        elif operation == '-':
            result = num1 - num2
        elif operation == '*':
            result = num1 * num2
        elif operation == '/':
            if num2 == 0:
                messagebox.showerror("Error", "Cannot divide by zero!")
                return
            result = num1 / num2
            
        result_label.config(text=f"Result: {result}")
    except ValueError:
        messagebox.showerror("Error", "Please enter valid numbers!")

# Create main window
window = tk.Tk()
window.title("Simple Calculator")
window.geometry("300x200")

# Create input fields
tk.Label(window, text="First Number:").pack()
entry1 = tk.Entry(window)
entry1.pack()

tk.Label(window, text="Second Number:").pack()
entry2 = tk.Entry(window)
entry2.pack()

# Create operation selection
operation_var = tk.StringVar(value='+')
tk.Label(window, text="Operation:").pack()
operations_frame = tk.Frame(window)
operations_frame.pack()

tk.Radiobutton(operations_frame, text="+", variable=operation_var, value='+').pack(side=tk.LEFT)
tk.Radiobutton(operations_frame, text="-", variable=operation_var, value='-').pack(side=tk.LEFT)
tk.Radiobutton(operations_frame, text="*", variable=operation_var, value='*').pack(side=tk.LEFT)
tk.Radiobutton(operations_frame, text="/", variable=operation_var, value='/').pack(side=tk.LEFT)

# Create calculate button
calculate_button = tk.Button(window, text="Calculate", command=calculate)
calculate_button.pack(pady=10)

# Create result label
result_label = tk.Label(window, text="Result: ")
result_label.pack()

# Start the application
window.mainloop()