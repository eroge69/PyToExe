
import tkinter as tk
import pyperclip

# Values list
values = []

def add_value(val):
    values.append(str(val))
    update_display()

def update_display():
    display.config(state='normal')
    display.delete(1.0, tk.END)
    display.insert(tk.END, ' '.join(values))
    display.config(state='disabled')

def copy_to_clipboard():
    pyperclip.copy(' '.join(values))

def clear_values():
    values.clear()
    update_display()

# Window setup
root = tk.Tk()
root.title("Floating Notepad")
root.attributes('-topmost', True)
root.geometry("300x250")
root.resizable(False, False)

# Buttons
btn_values = [10, 50, 80, 5, 15, 100]
for i, val in enumerate(btn_values):
    btn = tk.Button(root, text=str(val), width=6, command=lambda v=val: add_value(v))
    btn.grid(row=0, column=i, padx=2, pady=10)

# Text display
display = tk.Text(root, height=5, width=35, wrap="word", state='disabled')
display.grid(row=1, column=0, columnspan=6, padx=10, pady=5)

# Control buttons
copy_btn = tk.Button(root, text="Copy", command=copy_to_clipboard, bg='lightgreen')
copy_btn.grid(row=2, column=1, pady=10)

clear_btn = tk.Button(root, text="Clear", command=clear_values, bg='lightcoral')
clear_btn.grid(row=2, column=4, pady=10)

root.mainloop()
