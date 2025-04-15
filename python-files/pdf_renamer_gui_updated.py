
import tkinter as tk
from tkinter import filedialog, StringVar, Label, Button, Entry, Text, Scrollbar, END, simpledialog
import os
import fitz
import re


class PDFRenamerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("PDF Renamer – OCR faktur")
        self.root.geometry("700x500")

        self.input_path = StringVar()
        self.output_path = StringVar()
        self.month_filter = StringVar()

        # UI
        Label(root, text="Wybierz folder z fakturami (wejściowy):").pack(pady=(10, 0))
        Button(root, text="Wybierz folder wejściowy", command=self.choose_input_folder).pack()
        Label(root, textvariable=self.input_path, fg="blue").pack()

        Label(root, text="Wybierz folder do zapisu (wyjściowy):").pack(pady=(10, 0))
        Button(root, text="Wybierz folder wyjściowy", command=self.choose_output_folder).pack()
        Label(root, textvariable=self.output_path, fg="green").pack()

        Label(root, text="Filtruj tylko faktury z miesiąca (YYYY-MM):").pack(pady=(10, 0))
        Entry(root, textvariable=self.month_filter).pack()

        Button(root, text="START", command=self.start, bg="green", fg="white", height=2, width=20).pack(pady=10)
        Button(root, text="Pokaż tekst faktury", command=self.preview_pdf_text).pack(pady=(0, 10))

        self.log_box = Text(root, height=12, width=80)
        self.log_box.pack(pady=(10, 0))
        Scrollbar(root, command=self.log_box.yview).pack(side=tk.RIGHT, fill=tk.Y)
        self.log_box.config(yscrollcommand=lambda f, l: None)

    def log(self, message):
        self.log_box.insert(END, message + '\n')
        self.log_box.see(END)

    def choose_input_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.input_path.set(folder)

    def choose_output_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.output_path.set(folder)

    def start(self):
        input_dir = self.input_path.get()
        output_dir = self.output_path.get()
        month_filter = self.month_filter.get()

        if not input_dir or not output_dir:
            self.log("❗ Proszę wybrać oba foldery.")
            return

        pdf_files = [f for f in os.listdir(input_dir) if f.lower().endswith('.pdf')]
        total = len(pdf_files)
        processed = 0

        for filename in pdf_files:
            filepath = os.path.join(input_dir, filename)
            try:
                text = self.extract_text_from_pdf(filepath)
                issuer, date = self.extract_invoice_data(text)

                # Filtr miesiąca
                if month_filter and not date.startswith(month_filter):
                    self.log(f"⏩ Pominięto: {filename} – data {date} nie pasuje do filtra {month_filter}")
                    continue

                new_name = f"{issuer}_{date}.pdf".replace(" ", "_")
                new_name = self.ensure_unique_filename(output_dir, new_name)
                new_path = os.path.join(output_dir, new_name)

                with open(filepath, 'rb') as src, open(new_path, 'wb') as dst:
                    dst.write(src.read())

                processed += 1
                self.log(f"✅ {processed}/{total} – Zmieniono nazwę: {filename} -> {new_name}")
            except Exception as e:
                self.log(f"❌ Błąd przy pliku {filename}: {e}")

    def ensure_unique_filename(self, folder, filename):
        base, ext = os.path.splitext(filename)
        counter = 1
        new_filename = filename
        while os.path.exists(os.path.join(folder, new_filename)):
            new_filename = f"{base}_({counter}){ext}"
            counter += 1
        return new_filename

    def extract_text_from_pdf(self, pdf_path):
        text = ""
        with fitz.open(pdf_path) as doc:
            for page in doc:
                text += page.get_text()
        return text

    def extract_invoice_data(self, text):
        issuer_match = re.search(r"(?:FIRMA|WYSTAWCA|SPRZEDAWCA)\s*[:\-]?\s*(.+)", text, re.IGNORECASE)
        date_match = re.search(r"(?:DATA WYSTAWIENIA|DATA)\s*[:\-]?\s*(\d{4}[-/.]\d{2}[-/.]\d{2})", text, re.IGNORECASE)

        issuer = issuer_match.group(1).strip().split('\n')[0] if issuer_match else "Wystawca_Nieznany"
        date = date_match.group(1).strip().replace('/', '-').replace('.', '-') if date_match else "Data_Nieznana"

        issuer = re.sub(r'[^\w\-]', '_', issuer)
        return issuer, date

    def preview_pdf_text(self):
        file_path = filedialog.askopenfilename(filetypes=[("PDF files", "*.pdf")])
        if not file_path:
            return

        try:
            text = self.extract_text_from_pdf(file_path)
            top = tk.Toplevel(self.root)
            top.title("Podgląd tekstu faktury")
            text_widget = Text(top, wrap=tk.WORD, width=100, height=30)
            text_widget.pack(expand=True, fill="both")
            text_widget.insert(END, text)
        except Exception as e:
            self.log(f"❌ Błąd podczas podglądu: {e}")


if __name__ == "__main__":
    root = tk.Tk()
    app = PDFRenamerApp(root)
    root.mainloop()
