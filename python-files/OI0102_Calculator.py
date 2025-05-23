# -*- coding: utf-8 -*-
"""
Created on Thu May 22 14:46:43 2025

@author: davis
"""

import tkinter as tk
from tkinter import ttk
from datetime import datetime

def calculate():
    try:
        start = float(start_entry.get())
        end = float(end_entry.get())
        X = ((start-end)**2)**(1/2)
        mode = mode_var.get()

        if mode == "TB1 [SECTOR 1]":
            test_time = (X / 6.5) * 60
            weld_time = test_time + 2  # seconds
        elif mode == "TB2/3 [SECTOR 1]":
            test_time = (X / 6.0) * 60
            weld_time = test_time + 3  # seconds
        elif mode == "Overhead Balance [SECTOR 3]":
            test_time = ((X - 0.73) / 6.5) * 60
            weld_time = ((X - 0.58) / 6.5) * 60
        elif mode == "Horizontal/Flat Balance [SECTOR 3]":
            test_time = ((X - 0.46) / 6.5) * 60
            weld_time = ((X - 0.27) / 6.5) * 60
        elif mode == "Shelf [SECTOR 2]":
            test_time = ((X - 0.58) / 6.5) * 60
            weld_time = ((X - 0.23) / 6.5) * 60
        else:
            result_label.config(text="Invalid mode selected.")
            return

        timestamp = datetime.now().strftime("%m-%d-%Y %H:%M:%S")
        result_text = (
            f"[{timestamp}]\n"
            f"Mode: {mode}\n"
            f"Start: {start}, End: {end}\n"
            f"Total Distance (X): {X:.2f}\n"
            f"Test Time: {test_time:.2f} seconds\n"
            f"Weld Time: {weld_time:.2f} seconds\n"
            f"{'-'*40}\n"
        )

        result_label.config(text=result_text)
        history_text.insert(tk.END, result_text)
        history_text.see(tk.END)

    except ValueError:
        result_label.config(text="Please enter valid numbers.")

def clear_history():
    history_text.delete(1.0, tk.END)

# GUI setup
root = tk.Tk()
root.title("Weld Time Calculator - OI0102")

font_large = ("Helvetica", 14)

tk.Label(root, text="Start Point:", font=font_large).grid(row=0, column=0, sticky='e')
start_entry = tk.Entry(root, font=font_large)
start_entry.grid(row=0, column=1)

tk.Label(root, text="End Point:", font=font_large).grid(row=1, column=0, sticky='e')
end_entry = tk.Entry(root, font=font_large)
end_entry.grid(row=1, column=1)

tk.Label(root, text="Mode:", font=font_large).grid(row=2, column=0, sticky='e')
mode_var = tk.StringVar()
mode_dropdown = ttk.Combobox(root, textvariable=mode_var, values=[
    "TB1 [SECTOR 1]", "TB2/3 [SECTOR 1]", "Overhead Balance [SECTOR 3]", "Horizontal/Flat Balance [SECTOR 3]", "Shelf [SECTOR 2]"
], font=font_large)
mode_dropdown.grid(row=2, column=1)
mode_dropdown.current(0)

tk.Button(root, text="Calculate", command=calculate, font=font_large).grid(row=3, column=0, pady=10)
tk.Button(root, text="Clear History", command=clear_history, font=font_large).grid(row=3, column=1, pady=10)

result_label = tk.Label(root, text="", justify="left", fg="blue", font=font_large)
result_label.grid(row=4, column=0, columnspan=2)

tk.Label(root, text="Calculation History:", font=font_large).grid(row=5, column=0, columnspan=2)

history_text = tk.Text(root, height=10, width=60, font=font_large)
history_text.grid(row=6, column=0, columnspan=2)

root.mainloop()
