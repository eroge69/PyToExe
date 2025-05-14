import tkinter as tk
from tkinter import messagebox

def calculate_slope():
    try:
        h1 = float(entry_height1.get())
        h2 = float(entry_height2.get())
        length = float(entry_length.get())

        if length == 0:
            messagebox.showerror("Error", "Length cannot be zero.")
            return

        slope_percent = ((h1 - h2) / length) * 100
        slope_percent_rounded = round(slope_percent, 2)

        if slope_percent == 0:
            slope_ratio = "Flat (no slope)"
        else:
            slope_ratio = f"1 in {round(100 / abs(slope_percent), 2)}"

        label_result.config(
            text=f"Slope: {slope_percent_rounded}%\nRatio: {slope_ratio}"
        )

    except ValueError:
        messagebox.showerror("Input Error", "Please enter valid numbers.")


# GUI setup
root = tk.Tk()
root.title("Slope Calculator")

tk.Label(root, text="Height 1:").grid(row=0, column=0, padx=10, pady=5, sticky="e")
tk.Label(root, text="Height 2:").grid(row=1, column=0, padx=10, pady=5, sticky="e")
tk.Label(root, text="Length:").grid(row=2, column=0, padx=10, pady=5, sticky="e")

entry_height1 = tk.Entry(root)
entry_height2 = tk.Entry(root)
entry_length = tk.Entry(root)

entry_height1.grid(row=0, column=1, padx=10, pady=5)
entry_height2.grid(row=1, column=1, padx=10, pady=5)
entry_length.grid(row=2, column=1, padx=10, pady=5)

tk.Button(root, text="Calculate Slope", command=calculate_slope).grid(
    row=3, column=0, columnspan=2, pady=10
)

label_result = tk.Label(root, text="", font=("Arial", 12), fg="blue")
label_result.grid(row=4, column=0, columnspan=2, pady=10)

root.mainloop()