
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image
import os

class TifToJpegConverter(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("TIF to JPEG Converter")
        self.geometry("400x250")
        self.configure(bg="#f0f0f0")
        self.files = []
        self.create_widgets()

    def create_widgets(self):
        self.label = tk.Label(self, text="Выбери .tif/.tiff файлы для конвертации", bg="#f0f0f0", font=("Arial", 12))
        self.label.pack(pady=20)

        self.select_btn = tk.Button(self, text="Выбрать файлы", command=self.select_files, width=25)
        self.select_btn.pack(pady=5)

        self.convert_btn = tk.Button(self, text="Начать конвертацию", command=self.convert_files, width=25)
        self.convert_btn.pack(pady=10)

        self.status = tk.Label(self, text="", bg="#f0f0f0", fg="green")
        self.status.pack(pady=10)

    def select_files(self):
        files = filedialog.askopenfilenames(filetypes=[("TIF files", "*.tif *.tiff")])
        self.files = list(files)
        self.status.config(text=f"Выбрано файлов: {len(self.files)}")

    def convert_files(self):
        if not self.files:
            messagebox.showwarning("Нет файлов", "Пожалуйста, выбери .tif/.tiff файлы")
            return

        output_dir = filedialog.askdirectory(title="Выбери папку для JPEG файлов")
        if not output_dir:
            return

        converted = 0
        for file_path in self.files:
            try:
                img = Image.open(file_path)
                rgb_img = img.convert("RGB")
                base_name = os.path.splitext(os.path.basename(file_path))[0]
                output_path = os.path.join(output_dir, base_name + ".jpg")
                rgb_img.save(output_path, "JPEG")
                converted += 1
            except Exception as e:
                print(f"Ошибка при конвертации {file_path}: {e}")

        self.status.config(text=f"Сконвертировано файлов: {converted}")
        messagebox.showinfo("Готово", f"Успешно сконвертировано: {converted} файлов!")

if __name__ == "__main__":
    app = TifToJpegConverter()
    app.mainloop()
