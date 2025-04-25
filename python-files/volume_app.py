import tkinter as tk
from tkinter import messagebox

def interpolate_volume(sounding_input, table):
    table = sorted(table)
    for i in range(len(table) - 1):
        x0, y0 = table[i]
        x1, y1 = table[i + 1]
        if x0 <= sounding_input <= x1:
            return y0 + ((y1 - y0) / (x1 - x0)) * (sounding_input - x0)
    return None

volume_table = [
    (0, 0.0), (100, 3483.26), (200, 3482.48), (300, 3482.74), (400, 3482.93),
    (500, 3482.41), (600, 3482.74), (700, 3481.92), (800, 3483.12), (900, 3482.57),
    (1000, 3483.53), (1100, 3483.22), (1200, 3483.95), (1300, 3481.32), (1400, 3483.48),
    (1500, 3459.25), (1600, 3460.91), (1700, 3463.88), (1800, 345.25), (1900, 59.93),
    (2000, 60.32), (2100, 56.67), (2200, 57.05), (2300, 57.42), (2400, 57.79),
    (2500, 58.16), (2600, 58.53), (2700, 58.91), (2800, 59.28), (2900, 59.65),
    (3000, 60.02), (3100, 60.39), (3200, 56.42), (3300, 56.77), (3400, 57.11),
    (3500, 57.46), (3600, 57.81), (3700, 58.15), (3800, 58.50), (3900, 58.84), (4000, 455.282)
]

def calculate():
    user_input = entry.get()
    try:
        sounding_input = float(user_input)
        if sounding_input < volume_table[0][0] or sounding_input > volume_table[-1][0]:
            result_var.set("Out of range.")
        else:
            volume = interpolate_volume(sounding_input, volume_table)
            if volume is None:
                result_var.set("Value not in interpolation range.")
            else:
                result_var.set(f"Volume: {volume:.2f} m³")
    except ValueError:
        messagebox.showerror("Invalid input", "Please enter a valid number.")

# GUI Setup
root = tk.Tk()
root.title("Volume Interpolation")
root.geometry("300x150")

frame = tk.Frame(root, padx=10, pady=10)
frame.pack(fill="both", expand=True)

label = tk.Label(frame, text="Enter sounding value (mm):")
label.pack()

entry = tk.Entry(frame)
entry.pack()

button = tk.Button(frame, text="Calculate Volume", command=calculate)
button.pack(pady=5)

result_var = tk.StringVar()
result_label = tk.Label(frame, textvariable=result_var, fg="blue")
result_label.pack()

root.mainloop()
