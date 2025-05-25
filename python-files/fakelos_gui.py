
import tkinter as tk
from tkinter import messagebox
from fpdf import FPDF
import os
from math import sin, cos

FONT_PATH = "DejaVuSans.ttf"
FONT_NAME = "DejaVu"

class EnvelopeApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Εκτύπωση Φακέλου DL")
        self.root.geometry("400x300")

        tk.Label(root, text="Όνομα Παραλήπτη").pack()
        self.name_entry = tk.Entry(root, width=40)
        self.name_entry.pack()

        tk.Label(root, text="Διεύθυνση Παραλήπτη").pack()
        self.address_entry = tk.Entry(root, width=40)
        self.address_entry.pack()

        tk.Label(root, text="Πόλη & Τ.Κ. Παραλήπτη").pack()
        self.city_entry = tk.Entry(root, width=40)
        self.city_entry.pack()

        tk.Button(root, text="Εκτύπωση", command=self.create_pdf).pack(pady=20)

    def create_pdf(self):
        name = self.name_entry.get()
        address = self.address_entry.get()
        city = self.city_entry.get()

        if not name or not address or not city:
            messagebox.showerror("Σφάλμα", "Συμπλήρωσε όλα τα πεδία")
            return

        class RotatedTextPDF(FPDF):
            def __init__(self):
                super().__init__(orientation='P', unit='mm', format=(110, 220))
                self.add_page()
                self.add_font(FONT_NAME, '', FONT_PATH, uni=True)
                self.set_font(FONT_NAME, size=12)

            def rotate_text(self, x, y, text, angle, font_size=12, width=80, line_height=6):
                self.set_font(FONT_NAME, size=font_size)
                self.set_xy(x, y)
                self._out(f'q')
                self._out(f'1 0 0 1 {x:.2f} {y:.2f} cm')
                rad = angle * 3.14159 / 180
                c = round(cos(rad), 6)
                s = round(sin(rad), 6)
                self._out(f'{c} {s} {-s} {c} 0 0 cm')
                self.multi_cell(width, line_height, text)
                self._out('Q')

        pdf = RotatedTextPDF()
        pdf.rotate_text(100, 20, "Ο.Σ.Μ.Α.Ε.Σ.\nΔημ. Σούτσου 40\n11521 Αθήνα", angle=90, font_size=12)
        pdf.rotate_text(20, 100, f"{name}\n{address}\n{city}", angle=90, font_size=14)

        desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
        output_path = os.path.join(desktop_path, "fakelos.pdf")
        pdf.output(output_path)
        messagebox.showinfo("Ολοκληρώθηκε", f"Ο φάκελος αποθηκεύτηκε:
{output_path}")

if __name__ == "__main__":
    root = tk.Tk()
    app = EnvelopeApp(root)
    root.mainloop()
