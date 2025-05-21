
import tkinter as tk
from tkinter import messagebox
from tkinter import filedialog
from fpdf import FPDF
import qrcode
from PIL import Image
import os

class LabelGeneratorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Etiketten-Generator")
        self.root.geometry("600x400")
        self.root.grid_columnconfigure(1, weight=1)

        # GUI Elemente
        tk.Label(root, text="Artikelbezeichnung:").grid(row=0, column=0, sticky='w')
        self.entry_name = tk.Entry(root)
        self.entry_name.grid(row=0, column=1, sticky='ew', padx=5, pady=5)

        tk.Label(root, text="Stückzahl:").grid(row=1, column=0, sticky='w')
        self.entry_qty = tk.Entry(root)
        self.entry_qty.grid(row=1, column=1, sticky='w', padx=5, pady=5)

        tk.Label(root, text="Technische Details:").grid(row=2, column=0, sticky='nw')
        self.text_details = tk.Text(root, height=4)
        self.text_details.grid(row=2, column=1, sticky='nsew', padx=5, pady=5)

        tk.Label(root, text="Cloud-Link:").grid(row=3, column=0, sticky='w')
        self.entry_link = tk.Entry(root)
        self.entry_link.grid(row=3, column=1, sticky='ew', padx=5, pady=5)

        tk.Label(root, text="Weitere Informationen:").grid(row=4, column=0, sticky='nw')
        self.text_additional = tk.Text(root, height=3)
        self.text_additional.grid(row=4, column=1, sticky='nsew', padx=5, pady=5)

        self.btn_generate = tk.Button(root, text="Etikett erstellen", command=self.generate_label)
        self.btn_generate.grid(row=5, column=0, columnspan=2, pady=10)

        root.grid_rowconfigure(2, weight=1)
        root.grid_rowconfigure(4, weight=1)

    def generate_label(self):
        name = self.entry_name.get()
        qty = self.entry_qty.get()
        details = self.text_details.get("1.0", tk.END).strip()
        link = self.entry_link.get()
        additional = self.text_additional.get("1.0", tk.END).strip()

        if not all([name, qty, link]):
            messagebox.showerror("Fehler", "Bitte alle Pflichtfelder ausfüllen.")
            return

        # QR-Code generieren
        qr = qrcode.make(link)
        qr_path = "temp_qr.png"
        qr.save(qr_path)

        # PDF erstellen (70x50 mm -> ca. 198x141 pt)
        pdf = FPDF(unit="mm", format=(70, 50))
        pdf.add_page()
        pdf.set_font("Arial", size=10)

        pdf.cell(50, 10, f"Artikel: {name}", ln=True)
        pdf.cell(50, 7, f"Stückzahl: {qty}", ln=True)
        pdf.multi_cell(50, 5, f"Details: {details}")
        pdf.multi_cell(50, 5, f"Weitere Infos: {additional}")

        pdf.image(qr_path, x=50, y=5, w=15, h=15)

        save_path = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF-Dateien", "*.pdf")])
        if save_path:
            pdf.output(save_path)
            messagebox.showinfo("Erfolg", f"Etikett gespeichert unter:
{save_path}")

        os.remove(qr_path)


if __name__ == "__main__":
    root = tk.Tk()
    app = LabelGeneratorApp(root)
    root.mainloop()
