import tkinter as tk
from tkinter import messagebox
import math

def hitung_titik_embun(T, RH):
    a = 17.62
    b = 243.12
    gamma = (a * T) / (b + T) + math.log(RH / 100.0)
    Td = (b * gamma) / (a - gamma)
    return Td

def on_hitung():
    try:
        T = float(entry_suhu.get())
        RH = float(entry_rh.get())
        if RH <= 0 or RH > 100:
            raise ValueError("RH harus antara 0–100")
        Td = hitung_titik_embun(T, RH)
        label_hasil.config(text=f"Titik Embun: {Td:.2f} °C")
    except ValueError as e:
        messagebox.showerror("Input Error", f"Masukan tidak valid:\n{e}")

# Setup GUI
root = tk.Tk()
root.title("Kalkulator Titik Embun")

tk.Label(root, text="Suhu (°C):").grid(row=0, column=0, padx=10, pady=5, sticky="e")
entry_suhu = tk.Entry(root)
entry_suhu.grid(row=0, column=1, padx=10, pady=5)

tk.Label(root, text="Kelembapan Relatif (%):").grid(row=1, column=0, padx=10, pady=5, sticky="e")
entry_rh = tk.Entry(root)
entry_rh.grid(row=1, column=1, padx=10, pady=5)

tk.Button(root, text="Hitung Titik Embun", command=on_hitung).grid(row=2, column=0, columnspan=2, pady=10)

label_hasil = tk.Label(root, text="Titik Embun: - °C", font=("Arial", 12, "bold"))
label_hasil.grid(row=3, column=0, columnspan=2, pady=10)

root.mainloop()
