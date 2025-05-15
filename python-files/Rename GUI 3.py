import os
import re
import traceback
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
from pdf2image import convert_from_path
import cv2
import pytesseract
from PIL import Image, ImageEnhance, ImageFilter

# Set tesseract path
pytesseract.pytesseract.tesseract_cmd = r"C:\Users\SaniruK\AppData\Local\Programs\Tesseract-OCR\tesseract.exe"

# Supported file types
SUPPORTED_EXTENSIONS = ('.pdf', '.jpg', '.jpeg', '.png')

class InvoiceRenamerApp(tk.Tk):
    def __init__(self):
        super().__init__()
        # Transparent-style overlay watermark
        watermark = tk.Label(self, text="Saniru Rashen", font=("Arial", 30, "bold"),
                             fg="#e0e0e0", bg="#f5f5f5")
        watermark.place(relx=0.5, rely=0.5, anchor="center")
        watermark.lower()  # Push it behind other widgets

        self.title("Invoice Renamer (Fixed OCR)")
        self.geometry("850x720")
        self.configure(bg="#f5f5f5")

        self.folder_path = tk.StringVar()
        self.crop_start_x = tk.DoubleVar(value=0.7)        # Default 70%
        self.crop_top_percentage = tk.DoubleVar(value=25.0)  # Default 25%

        # Folder selection
        tk.Label(self, text="Select Folder with Invoices:", bg="#f5f5f5", font=("Arial", 14)).pack(pady=10)
        tk.Entry(self, textvariable=self.folder_path, width=60, font=("Arial", 12)).pack(pady=5)
        tk.Button(self, text="Browse", command=self.browse_folder, font=("Arial", 12)).pack(pady=5)

        # Zoom settings
        tk.Label(self, text="Right Side Start (e.g., 0.7 = 70% from left):", bg="#f5f5f5", font=("Arial", 12)).pack(pady=5)
        tk.Entry(self, textvariable=self.crop_start_x, width=10, font=("Arial", 12)).pack(pady=5)

        tk.Label(self, text="Top Height to Scan (e.g., 25 for 25%):", bg="#f5f5f5", font=("Arial", 12)).pack(pady=5)
        tk.Entry(self, textvariable=self.crop_top_percentage, width=10, font=("Arial", 12)).pack(pady=5)

        # Button to apply recommended settings
        tk.Button(self, text="Apply Recommended Settings (0.8, 15%)", command=self.apply_recommended_settings, font=("Arial", 12), bg="#2196F3", fg="white").pack(pady=10)

        # Start button
        tk.Button(self, text="Start Renaming", command=self.start_renaming, font=("Arial", 12, 'bold'), bg="#4CAF50", fg="white").pack(pady=10)

        # Log output
        self.log_box = scrolledtext.ScrolledText(self, width=100, height=20, font=("Consolas", 10))
        self.log_box.pack(pady=10)

    def browse_folder(self):
        folder_selected = filedialog.askdirectory()
        if folder_selected:
            self.folder_path.set(folder_selected)

    def log(self, message):
        self.log_box.insert(tk.END, message + "\n")
        self.log_box.see(tk.END)
        self.update()

    def apply_recommended_settings(self):
        self.crop_start_x.set(0.8)
        self.crop_top_percentage.set(15.0)
        self.log("Applied recommended settings: Right Start 0.8, Top Height 15%")

    def start_renaming(self):
        try:
            folder = self.folder_path.get()
            if not folder:
                messagebox.showwarning("Warning", "Please select a folder first.")
                return

            files = [f for f in os.listdir(folder) if f.lower().endswith(SUPPORTED_EXTENSIONS)]
            if not files:
                messagebox.showinfo("Info", "No supported files found in the selected folder.")
                return

            for file_name in files:
                try:
                    full_path = os.path.join(folder, file_name)
                    new_name = self.process_file(full_path)

                    if new_name:
                        new_path = os.path.join(folder, new_name)
                        os.rename(full_path, new_path)
                        self.log(f"Renamed: {file_name} → {new_name}")
                    else:
                        not_found_name = f"not_found_{file_name}"
                        not_found_path = os.path.join(folder, not_found_name)
                        os.rename(full_path, not_found_path)
                        self.log(f"No invoice number found. Renamed to: {not_found_name}")

                except Exception as file_err:
                    self.log(f"Error processing {file_name}: {str(file_err)}")

            messagebox.showinfo("Done", "Renaming completed.")

        except Exception as e:
            error_message = traceback.format_exc()
            messagebox.showerror("Error", error_message)

    def process_file(self, file_path):
        filename, ext = os.path.splitext(file_path)
        image = None

        if ext.lower() == '.pdf':
            images = convert_from_path(file_path, first_page=1, last_page=1, dpi=300)
            if images:
                image = images[0]
        else:
            image = Image.open(file_path)

        if image is None:
            return None

        # Crop only a portion of top right
        width, height = image.size
        start_x = int(width * self.crop_start_x.get())
        crop_height = int(height * (self.crop_top_percentage.get() / 100))
        crop_area = (start_x, 0, width, crop_height)
        cropped_image = image.crop(crop_area)

        # Preprocessing
        processed_image = cropped_image.convert('L')
        processed_image = processed_image.filter(ImageFilter.MedianFilter())
        enhancer = ImageEnhance.Contrast(processed_image)
        processed_image = enhancer.enhance(3.0)  # Increased contrast more aggressively

        # Enlarge image to help OCR (2x zoom)
        width_enlarge, height_enlarge = processed_image.size
        enlarged_image = processed_image.resize((width_enlarge * 2, height_enlarge * 2))

        temp_image_path = filename + "_temp.jpg"
        enlarged_image.save(temp_image_path)

        invoice_number = self.read_first_number_ocr(temp_image_path)

        os.remove(temp_image_path)

        if invoice_number:
            return f"{invoice_number}{ext.lower()}"

        return None

    def read_first_number_ocr(self, image_path):
        try:
            img = Image.open(image_path)
            # Stronger config for OCR focusing on digits only
            custom_config = r'--oem 3 --psm 6 -c tessedit_char_whitelist=0123456789'
            text = pytesseract.image_to_string(img, config=custom_config)

            matches = re.findall(r"\b0\d{7}\b", text)
            if matches:
                return matches[0]  # Take the first match found

            return None
        except Exception:
            return None

if __name__ == "__main__":
    app = InvoiceRenamerApp()
    app.mainloop()
