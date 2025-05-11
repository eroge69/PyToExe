from img2table.document import Image
from img2table.ocr import TesseractOCR
from tkinter import filedialog, Tk, messagebox
import os

def convert_image_to_excel():
    # Select image
    path = filedialog.askopenfilename(filetypes=[("Image Files", "*.png;*.jpg;*.jpeg")])
    if not path:
        return

    # Set up OCR
    ocr = TesseractOCR(lang="eng")

    # Load image
    image = Image(src=path)

    # Extract tables
    extracted_tables = image.extract_tables(ocr=ocr, implicit_rows=True, borderless_tables=True)

    # Save to Excel
    output_path = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel files", "*.xlsx")])
    if output_path:
        image.to_xlsx(output_path, ocr=ocr)
        messagebox.showinfo("Success", f"Excel saved at:\n{output_path}")

# GUI
root = Tk()
root.title("Image to Excel Converter (Table Preserved)")
root.geometry("400x200")
from tkinter import Button
Button(root, text="Select Image & Convert", font=("Helvetica", 14), command=convert_image_to_excel).pack(pady=60)
root.mainloop()
