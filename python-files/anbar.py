Python 3.13.3 (tags/v3.13.3:6280bb5, Apr  8 2025, 14:47:33) [MSC v.1943 64 bit (AMD64)] on win32
Enter "help" below or click "Help" above for more information.
import tkinter as tk
from tkinter import messagebox
import sqlite3
import datetime

# Verilənlər bazası yarat
conn = sqlite3.connect("anbar.db")
c = conn.cursor()
c.execute("""
    CREATE TABLE IF NOT EXISTS anbar (
        tarix TEXT,
        mehsul TEXT,
        evvelki_qaliq INTEGER,
        medaxil INTEGER,
        satildi INTEGER,
        son_qaliq INTEGER
    )
""")
conn.commit()

# Məntiqi funksiyalar
def hesabla_qaliq():
    try:
        evvelki = int(entry_evvelki.get())
        medaxil = int(entry_medaxil.get())
        satildi = int(entry_satildi.get())
        qaliq = evvelki + medaxil - satildi
        label_netic.set(f"Sabah üçün qalıq: {qaliq}")
        return qaliq
    except ValueError:
        messagebox.showerror("Xəta", "Zəhmət olmasa bütün xanaları düzgün doldurun")
        return None

def yadda_saxla():
    tarix = datetime.date.today().isoformat()
    mehsul = entry_mehsul.get()
    try:
        evvelki = int(entry_evvelki.get())
        medaxil = int(entry_medaxil.get())
        satildi = int(entry_satildi.get())
        son_qaliq = hesabla_qaliq()

        if son_qaliq is not None:
            c.execute("INSERT INTO anbar VALUES (?, ?, ?, ?, ?, ?)",
                      (tarix, mehsul, evvelki, medaxil, satildi, son_qaliq))
            conn.commit()
            messagebox.showinfo("Uğurlu", "Məlumat yadda saxlanıldı")
    except ValueError:
...         messagebox.showerror("Xəta", "Bütün xanalar doldurulmalıdır")
... 
... # GUI yarat
... root = tk.Tk()
... root.title("Anbar Hesabat Sistemi")
... 
... # Xanalar
... label_mehsul = tk.Label(root, text="Məhsul adı:")
... label_mehsul.grid(row=0, column=0)
... entry_mehsul = tk.Entry(root)
... entry_mehsul.grid(row=0, column=1)
... 
... label_evvelki = tk.Label(root, text="Əvvəlki qalıq:")
... label_evvelki.grid(row=1, column=0)
... entry_evvelki = tk.Entry(root)
... entry_evvelki.grid(row=1, column=1)
... 
... label_medaxil = tk.Label(root, text="Mədaxil:")
... label_medaxil.grid(row=2, column=0)
... entry_medaxil = tk.Entry(root)
... entry_medaxil.grid(row=2, column=1)
... 
... label_satildi = tk.Label(root, text="Satıldı:")
... label_satildi.grid(row=3, column=0)
... entry_satildi = tk.Entry(root)
... entry_satildi.grid(row=3, column=1)
... 
... btn_hesabla = tk.Button(root, text="Qalıq Hesabla", command=hesabla_qaliq)
... btn_hesabla.grid(row=4, column=0, columnspan=2, pady=5)
... 
... label_netic = tk.StringVar()
... label_netic.set("Sabah üçün qalıq: -")
... label_result = tk.Label(root, textvariable=label_netic)
... label_result.grid(row=5, column=0, columnspan=2)
... 
... btn_yadda = tk.Button(root, text="Yadda saxla", command=yadda_saxla)
... btn_yadda.grid(row=6, column=0, columnspan=2, pady=10)
... 
... root.mainloop()
