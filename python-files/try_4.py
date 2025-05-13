import re
import pandas as pd
from PyPDF2 import PdfReader
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import os
from PIL import Image, ImageTk


class RollCollegeExtractor:
    def __init__(self, root):
        self.root = root
        self.root.title("Nursing College Roll Extractor")
        self.root.geometry("600x500")
        self.root.resizable(False, False)
        self.root.configure(bg="#f0f8ff")

        # Set window icon
        try:
            self.root.iconbitmap('icon.ico')
        except:
            pass

        # Configure styles
        self.style = ttk.Style()
        self.style.configure('TFrame', background="#f0f8ff")
        self.style.configure('TLabel', background="#f0f8ff", font=('Arial', 11))
        self.style.configure('TButton', font=('Arial', 11), padding=8)
        self.style.map('TButton',
                       foreground=[('active', 'black'), ('!active', 'black')],
                       background=[('active', '#c1e1ff'), ('!active', '#add8e6')])

        # Main container frame for centering everything
        self.main_container = ttk.Frame(root)
        self.main_container.pack(expand=True, fill='both', padx=20, pady=10)

        # Header with full-width logo
        self.header_frame = ttk.Frame(self.main_container)
        self.header_frame.pack(fill='x', pady=(0, 20))

        # Logo canvas (full width)
        self.logo_canvas = tk.Canvas(self.header_frame, height=120, bg='#2a5c8a',
                                     highlightthickness=0)
        self.logo_canvas.pack(fill='x')

        # Add logo (centered)
        try:
            img = Image.open("logo.png")
            img = img.resize((400, 100), Image.LANCZOS)
            self.logo_img = ImageTk.PhotoImage(img)
            self.logo_canvas.create_image(300, 60, image=self.logo_img)
            self.logo_canvas.create_text(300, 110,
                                         text="Nursing College Roll Number Extractor",
                                         fill="white", font=('Arial', 14, 'bold'))
        except:
            self.logo_canvas.create_text(300, 60,
                                         text="Nursing College Roll Extractor",
                                         fill="white", font=('Arial', 18, 'bold'))

        # Centered content frame
        self.content_frame = ttk.Frame(self.main_container)
        self.content_frame.pack(expand=True)

        # PDF selection (centered)
        pdf_frame = ttk.Frame(self.content_frame)
        pdf_frame.pack(pady=10)

        ttk.Label(pdf_frame, text="Select PDF File:").pack()

        self.pdf_entry = ttk.Entry(pdf_frame, width=50)
        self.pdf_entry.pack(pady=5)

        ttk.Button(pdf_frame, text="Browse PDF",
                   command=self.browse_pdf).pack(pady=5)

        # Output folder selection (centered)
        folder_frame = ttk.Frame(self.content_frame)
        folder_frame.pack(pady=10)

        ttk.Label(folder_frame, text="Select Output Folder:").pack()

        self.folder_entry = ttk.Entry(folder_frame, width=50)
        self.folder_entry.pack(pady=5)

        ttk.Button(folder_frame, text="Browse Folder",
                   command=self.browse_folder).pack(pady=5)

        # Process button (centered)
        ttk.Button(self.content_frame, text="EXTRACT ROLL NUMBERS",
                   command=self.process_pdf, style='TButton').pack(pady=20)

        # Status bar (bottom)
        self.status_var = tk.StringVar()
        self.status_var.set("Ready to process nursing college PDFs")
        self.status_bar = ttk.Label(root, textvariable=self.status_var,
                                    relief='sunken', anchor='center',
                                    font=('Arial', 10), background='#e0e0e0')
        self.status_bar.pack(fill='x', side='bottom', ipady=5)

    def browse_pdf(self):
        filepath = filedialog.askopenfilename(filetypes=[("PDF files", "*.pdf")])
        if filepath:
            self.pdf_entry.delete(0, tk.END)
            self.pdf_entry.insert(0, filepath)
            self.status_var.set(f"Selected: {os.path.basename(filepath)}")

    def browse_folder(self):
        folderpath = filedialog.askdirectory()
        if folderpath:
            self.folder_entry.delete(0, tk.END)
            self.folder_entry.insert(0, folderpath)
            self.status_var.set(f"Output will be saved to: {folderpath}")

    def process_pdf(self):
        pdf_path = self.pdf_entry.get()
        output_folder = self.folder_entry.get()

        if not pdf_path:
            messagebox.showerror("Error", "Please select a PDF file first!")
            return

        if not output_folder:
            messagebox.showerror("Error", "Please select an output folder!")
            return

        try:
            self.status_var.set("Processing PDF... Please wait")
            self.root.update()

            output_file = self.extract_and_save(pdf_path, output_folder)

            messagebox.showinfo("Success", f"Excel file created:\n{output_file}")
            self.status_var.set(f"Completed: {os.path.basename(output_file)}")

        except Exception as e:
            messagebox.showerror("Error", f"Processing failed:\n{str(e)}")
            self.status_var.set("Error occurred during processing")

    def extract_and_save(self, pdf_path, output_folder):
        reader = PdfReader(pdf_path)
        text = "\n".join(page.extract_text() for page in reader.pages)
        text = re.sub(r'\s+', ' ', text)
        college_sections = re.split(r'(?=\d{3}:\s+Nursing)', text)

        roll_college_list = []

        for section in college_sections:
            college_match = re.match(r'(\d{3}:\s+Nursing.+?\(\d+\))', section)
            if not college_match:
                continue
            college_name = college_match.group(1).strip()
            rolls = re.findall(r'\b(\d{7})\(\w+\)', section)
            for roll in rolls:
                roll_college_list.append((roll, college_name))

        df = pd.DataFrame(roll_college_list, columns=['Roll Number', 'College Name'])
        output_filename = os.path.basename(pdf_path).replace(".pdf", "_Roll_College.xlsx")
        output_path = os.path.join(output_folder, output_filename)
        df.to_excel(output_path, index=False)
        return output_path


if __name__ == "__main__":
    root = tk.Tk()
    app = RollCollegeExtractor(root)
    root.mainloop()