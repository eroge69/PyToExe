# Comandante → Molent Pocket klik dönüşüm masaüstü arayüzü (Tkinter)

import tkinter as tk
from tkinter import messagebox

def comandante_to_molent(comandante_clicks):
    comandante_micron = comandante_clicks * 30
    molent_map = {
        6: 350,
        8: 450,
        12: 550,
        14: 650,
        16: 750,
        20: 1150,
        24: 1350,
        30: 1650,
    }
    closest_molent = min(molent_map.items(), key=lambda x: abs(x[1] - comandante_micron))
    return comandante_micron, closest_molent[0], closest_molent[1]

def hesapla():
    try:
        klik = int(entry.get())
        micron, molent_klik, molent_micron = comandante_to_molent(klik)
        sonuc_label.config(
            text=f"\nComandante: {klik} klik ≈ {micron} µm\nMolent öneri: {molent_klik} klik ≈ {molent_micron} µm"
        )
    except ValueError:
        messagebox.showerror("Hata", "Lütfen geçerli bir sayı girin.")

# Arayüz kurulum
pencere = tk.Tk()
pencere.title("Comandante → Molent Dönüştürücü")
pencere.geometry("400x250")
pencere.resizable(False, False)

etiket = tk.Label(pencere, text="Comandante klik sayısını girin:", font=("Arial", 12))
etiket.pack(pady=10)

entry = tk.Entry(pencere, font=("Arial", 14), justify='center')
entry.pack(pady=5)

buton = tk.Button(pencere, text="Dönüştür", command=hesapla, font=("Arial", 12))
buton.pack(pady=10)

sonuc_label = tk.Label(pencere, text="", font=("Arial", 12))
sonuc_label.pack(pady=10)

pencere.mainloop()
