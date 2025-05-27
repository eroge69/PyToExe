import tkinter as tk
from tkinter import filedialog, messagebox
import subprocess
import os

class DiffPDFApp:
    def __init__(self, master):
        self.master = master
        master.title("Comparar PDFs - diff-pdf")
        master.geometry("400x250")

        self.label = tk.Label(master, text="Selecciona dos archivos PDF para comparar")
        self.label.pack(pady=10)

        self.file1_button = tk.Button(master, text="Seleccionar primer PDF", command=self.load_file1)
        self.file1_button.pack(pady=5)

        self.file2_button = tk.Button(master, text="Seleccionar segundo PDF", command=self.load_file2)
        self.file2_button.pack(pady=5)

        self.compare_button = tk.Button(master, text="Comparar", command=self.compare_pdfs, state=tk.DISABLED)
        self.compare_button.pack(pady=20)

        self.file1 = None
        self.file2 = None

    def load_file1(self):
        self.file1 = filedialog.askopenfilename(filetypes=[("PDF files", "*.pdf")])
        if self.file1:
            self.file1_button.config(text=os.path.basename(self.file1))
        self.check_ready()

    def load_file2(self):
        self.file2 = filedialog.askopenfilename(filetypes=[("PDF files", "*.pdf")])
        if self.file2:
            self.file2_button.config(text=os.path.basename(self.file2))
        self.check_ready()

    def check_ready(self):
        if self.file1 and self.file2:
            self.compare_button.config(state=tk.NORMAL)

    def compare_pdfs(self):
        output_file = "diff.pdf"
        try:
            subprocess.run(["diff-pdf", f"--output-diff={output_file}", self.file1, self.file2], check=True)
            messagebox.showinfo("Éxito", f"Diferencias generadas en {output_file}")
        except subprocess.CalledProcessError:
            messagebox.showerror("Error", "Error al ejecutar diff-pdf.")
        except FileNotFoundError:
            messagebox.showerror("Error", "No se encontró el ejecutable diff-pdf. Asegúrate de que esté en el PATH.")

# Ejecutar interfaz
if __name__ == "__main__":
    root = tk.Tk()
    app = DiffPDFApp(root)
    root.mainloop()
