# passport_photo_maker.py

import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk
from reportlab.pdfgen import canvas

class PassportPhotoApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Passport Photo Maker")
        self.image = None
        self.cropped = None

        self.upload_button = tk.Button(root, text="Upload Photo", command=self.upload_photo)
        self.upload_button.pack()

        self.canvas = tk.Canvas(root, width=300, height=300)
        self.canvas.pack()

        self.crop_button = tk.Button(root, text="Crop and Generate", command=self.crop_image, state=tk.DISABLED)
        self.crop_button.pack()

        self.save_img_button = tk.Button(root, text="Save as JPEG", command=self.save_image, state=tk.DISABLED)
        self.save_img_button.pack()

        self.save_pdf_button = tk.Button(root, text="Save as PDF", command=self.save_pdf, state=tk.DISABLED)
        self.save_pdf_button.pack()

    def upload_photo(self):
        file_path = filedialog.askopenfilename()
        if file_path:
            self.image = Image.open(file_path)
            self.display_image(self.image)
            self.crop_button.config(state=tk.NORMAL)

    def display_image(self, img):
        img.thumbnail((300, 300))
        self.tk_image = ImageTk.PhotoImage(img)
        self.canvas.create_image(150, 150, image=self.tk_image)

    def crop_image(self):
        if self.image:
            width, height = self.image.size
            target_ratio = 35 / 45
            new_height = height
            new_width = int(height * target_ratio)
            left = (width - new_width) // 2
            top = 0
            right = left + new_width
            bottom = new_height
            self.cropped = self.image.crop((left, top, right, bottom)).resize((150, 200))
            self.create_sheet()
            self.save_img_button.config(state=tk.NORMAL)
            self.save_pdf_button.config(state=tk.NORMAL)

    def create_sheet(self):
        self.sheet = Image.new("RGB", (4 * 150 + 12, 2 * 200 + 4), "white")
        for i in range(2):
            for j in range(4):
                self.sheet.paste(self.cropped, (j * 150 + j * 4, i * 200 + i * 4))
        self.display_image(self.sheet)

    def save_image(self):
        path = filedialog.asksaveasfilename(defaultextension=".jpg", filetypes=[("JPEG", "*.jpg")])
        if path:
            self.sheet.save(path, "JPEG")

    def save_pdf(self):
        path = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF", "*.pdf")])
        if path:
            c = canvas.Canvas(path, pagesize=(self.sheet.width, self.sheet.height))
            self.sheet.save("temp_image.jpg")
            c.drawImage("temp_image.jpg", 0, 0, width=self.sheet.width, height=self.sheet.height)
            c.save()

if __name__ == "__main__":
    root = tk.Tk()
    app = PassportPhotoApp(root)
    root.mainloop()
