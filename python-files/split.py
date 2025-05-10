import fitz  # PyMuPDF
import tkinter as tk
from tkinter import filedialog, messagebox
import os

def split_pdf(filepath):
    try:
        doc = fitz.open(filepath)
        if len(doc) != 1:
            messagebox.showerror("Errore", "Il PDF deve avere una sola pagina.")
            return

        page = doc[0]
        rect = page.rect

        upper = fitz.Rect(rect.x0, rect.y0, rect.x1, rect.y1 / 2)
        lower = fitz.Rect(rect.x0, rect.y1 / 2, rect.x1, rect.y1)

        new_doc = fitz.open()
        for part in [upper, lower]:
            new_page = new_doc.new_page(width=part.width, height=part.height)
            new_page.show_pdf_page(new_page.rect, doc, 0, clip=part)

        output_path = os.path.splitext(filepath)[0] + "_split.pdf"
        new_doc.save(output_path)
        messagebox.showinfo("Fatto", f"PDF diviso in 2 pagine.\nSalvato come:\n{output_path}")
    except Exception as e:
        messagebox.showerror("Errore", str(e))

def choose_file():
    filepath = filedialog.askopenfilename(
        title="Scegli un PDF",
        filetypes=[("PDF files", "*.pdf")]
    )
    if filepath:
        split_pdf(filepath)

# GUI setup
root = tk.Tk()
root.title("Dividi PDF in 2 Pagine")
root.geometry("300x150")

label = tk.Label(root, text="Seleziona un PDF a 1 pagina da dividere")
label.pack(pady=10)

button = tk.Button(root, text="Scegli PDF", command=choose_file)
button.pack(pady=20)

root.mainloop()
