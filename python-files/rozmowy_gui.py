import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
from datetime import datetime
import os
import csv
import pandas as pd

PLIK = "rozmowy.csv"

class AplikacjaRozmowy:
    def __init__(self, root):
        self.root = root
        self.root.title("Rejestrator rozmów - Netland Computers")
        self.root.geometry("500x600")
        self.root.configure(bg="#f0f0f0")

        self.logo_img = Image.open("logo-netland.png")
        self.logo_img = self.logo_img.resize((300, 90), Image.LANCZOS)
        self.logo = ImageTk.PhotoImage(self.logo_img)
        self.logo_label = tk.Label(root, image=self.logo, bg="#f0f0f0")
        self.logo_label.pack(pady=(10, 5))

        self.typ_label = tk.Label(root, text="Typ klienta:", font=("Arial", 12), bg="#f0f0f0")
        self.typ_label.pack()
        self.typ_combobox = ttk.Combobox(root, values=["Prywatny", "Drukarkowy", "Outsourcingowy"], state="readonly")
        self.typ_combobox.pack(pady=5)
        self.typ_combobox.current(0)

        self.czas_label = tk.Label(root, text="Czas rozmowy (min):", font=("Arial", 12), bg="#f0f0f0")
        self.czas_label.pack()
        self.czas_entry = tk.Entry(root)
        self.czas_entry.pack(pady=5)

        self.zapisz_btn = tk.Button(root, text="Zapisz rozmowę", command=self.zapisz_rozmowe, bg="#007acc", fg="white", font=("Arial", 12), width=20)
        self.zapisz_btn.pack(pady=10)

        self.raport_btn = tk.Button(root, text="Generuj raport", command=self.generuj_raport, bg="#4CAF50", fg="white", font=("Arial", 12), width=20)
        self.raport_btn.pack(pady=5)

        self.wyjscie_btn = tk.Button(root, text="Zamknij", command=root.quit, bg="#888", fg="white", font=("Arial", 11), width=20)
        self.wyjscie_btn.pack(pady=15)

    def zapisz_rozmowe(self):
        typ = self.typ_combobox.get()
        czas = self.czas_entry.get()

        if not czas.isdigit():
            messagebox.showerror("Błąd", "Czas rozmowy musi być liczbą całkowitą.")
            return

        data = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(PLIK, "a", encoding="utf-8", newline="") as f:
            writer = csv.writer(f)
            writer.writerow([data, typ, czas])

        messagebox.showinfo("Zapisano", "Rozmowa została zapisana.")
        self.czas_entry.delete(0, tk.END)

    def generuj_raport(self):
        if not os.path.exists(PLIK):
            messagebox.showerror("Błąd", "Brak danych do raportu.")
            return

        df = pd.read_csv(PLIK, names=["Data", "Typ", "Czas"])
        df["Czas"] = pd.to_numeric(df["Czas"], errors="coerce")
        df = df.dropna()
        raport = df.groupby("Typ")["Czas"].sum().reset_index()

        raport_str = "\n".join([f"{row['Typ']}: {int(row['Czas'])} minut" for _, row in raport.iterrows()])
        messagebox.showinfo("Raport", f"Łączny czas rozmów:\n\n{raport_str}")

if __name__ == "__main__":
    root = tk.Tk()
    app = AplikacjaRozmowy(root)
    root.mainloop()