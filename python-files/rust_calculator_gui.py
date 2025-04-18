import tkinter as tk

class RustCalculator(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Rust Calculator")
        self.geometry("500x600")
        self.configure(bg="gray")

        self.label = tk.Label(self, text="Bir item seç:", bg="gray", fg="white", font=("Arial", 14))
        self.label.pack(pady=10)

        # Dropdown menü
        self.combo = tk.StringVar()
        self.combo.set("Roket")  # Default item
        self.dropdown = tk.OptionMenu(self, self.combo, "Roket", "C4", "Satchel", "PM", "HV Roket")
        self.dropdown.config(bg="darkgray", fg="white")
        self.dropdown.pack(pady=10)

        # Miktar inputu
        self.amount_input = tk.Entry(self, bg="darkgray", fg="white", font=("Arial", 12))
        self.amount_input.insert(0, "1")
        self.amount_input.pack(pady=10)

        # Hesapla butonu
        self.calc_btn = tk.Button(self, text="Hesapla", command=self.calculate, bg="orange", fg="white", font=("Arial", 14))
        self.calc_btn.pack(pady=10)

        # Sonuç alanı
        self.result = tk.Text(self, height=10, width=50, bg="darkgray", fg="white", font=("Arial", 12))
        self.result.pack(pady=10)

        # Loading label (Hesaplanıyor yazısı)
        self.loading_label = tk.Label(self, text="", bg="gray", fg="white", font=("Arial", 14))
        self.loading_label.pack(pady=10)

    def calculate(self):
        # Loading efekti başlatılıyor
        self.loading_label.config(text="Hesaplanıyor...")
        self.update()

        # Girdi ve item seçimi
        item = self.combo.get().lower()
        try:
            amount = int(self.amount_input.get())
        except:
            self.result.delete(1.0, tk.END)
            self.result.insert(tk.END, "Lütfen geçerli bir sayı gir.")
            self.loading_label.config(text="")
            return

        # Hesaplama işlemi
        output = f"{item.upper()} - {amount} adet:\n\n"

        if item == "roket":
            output += f"Kömür: {1950 * amount}\nSülfür: {1400 * amount}\nMetal Parça: {100 * amount}\nYakıt: {30 * amount}\nBoru: {2 * amount}"
        elif item == "c4":
            output += f"Kömür: {3000 * amount}\nSülfür: {2200 * amount}\nMetal Parça: {200 * amount}\nYakıt: {60 * amount}\nTech Trash: {2 * amount}"
        elif item == "satchel":
            output += f"Kömür: {720 * amount}\nSülfür: {480 * amount}\nMetal Parça: {80 * amount}\nKumaş: {10 * amount}\nHalat: {1 * amount}"
        elif item == "pm":
            output += f"Kömür: {(600 / 10) * amount}\nSülfür: {(500 / 10) * amount}\nMetal Parça: {(100 / 10) * amount}"
        elif item == "hv":
            output += f"Kömür: {300 * amount}\nSülfür: {200 * amount}"
        else:
            output += "Bilinmeyen item."

        # Sonuçları ekle
        self.result.delete(1.0, tk.END)
        self.result.insert(tk.END, output)
        self.loading_label.config(text="")

if __name__ == "__main__":
    app = RustCalculator()
    app.mainloop()
