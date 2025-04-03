import cv2
import os
import tkinter as tk
from tkinter import filedialog, messagebox, StringVar, ttk
import numpy as np
from PIL import ImageTk, Image
from tifffile import imread, imwrite


class ImageMergerApp:
    def __init__(self, root):
        imge = Image.open("croco.ico")
        icon = ImageTk.PhotoImage(imge)

        # Установка иконки
        root.iconphoto(False, icon)
        self.root = root
        self.root.title("Crocodilini Imaginili")
        self.images = []
        self.cut_image_path = None
        self.selected_tiff = None
        self.output_directory = StringVar()

        self.main_frame = tk.Frame(root)
        self.main_frame.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        self.create_image_selection_widgets()
        self.create_calculator_widgets()
        self.create_conversion_widgets()

        self.main_frame.columnconfigure(0, weight=3)
        self.main_frame.columnconfigure(1, weight=1)
        self.main_frame.columnconfigure(2, weight=1)

    def create_image_selection_widgets(self):
        frame = tk.Frame(self.main_frame)
        frame.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")

        dir_frame = tk.Frame(frame)
        dir_frame.pack(pady=5, fill=tk.X)
        tk.Label(dir_frame, text="Папка для сохранения:").pack(side=tk.LEFT, padx=5)
        tk.Entry(dir_frame, textvariable=self.output_directory, width=30).pack(side=tk.LEFT, fill=tk.X, expand=True,
                                                                               padx=5)
        tk.Button(dir_frame, text="Обзор", command=self.browse_directory).pack(side=tk.LEFT, padx=5)

        ttk.Separator(frame, orient='horizontal').pack(pady=10, fill=tk.X)
        tk.Button(frame, text="Выбрать изображения для объединения", command=self.select_images).pack(pady=5, fill=tk.X)
        tk.Button(frame, text="Объединить изображения(если более 60к пикселей высоты формат TIFF", command=self.merge_images).pack(pady=5, fill=tk.X)

        ttk.Separator(frame, orient='horizontal').pack(pady=10, fill=tk.X)
        tk.Button(frame, text="Выбрать изображение для нарезки", command=self.select_cut_image).pack(pady=5, fill=tk.X)

        self.cut_method = StringVar(value="height")
        tk.Radiobutton(frame, text="Нарезка по высоте", variable=self.cut_method, value="height",
                       command=self.update_cut_label).pack(pady=5, anchor=tk.W)
        tk.Radiobutton(frame, text="Нарезка на количество", variable=self.cut_method, value="pieces",
                       command=self.update_cut_label).pack(pady=5, anchor=tk.W)

        self.cut_label = tk.Label(frame, text="Введите высоту фрагмента (пиксели):")
        self.cut_label.pack(pady=5, fill=tk.X)
        self.cut_height_entry = tk.Entry(frame)
        self.cut_height_entry.pack(pady=5, fill=tk.X)

        tk.Label(frame, text="Имя файлов для сохранения:").pack(pady=5, fill=tk.X)
        self.save_name_entry = tk.Entry(frame)
        self.save_name_entry.pack(pady=5, fill=tk.X)

        tk.Label(frame, text="Формат сохранения:").pack(pady=5, fill=tk.X)
        self.save_format = StringVar(value="JPEG")
        tk.OptionMenu(frame, self.save_format, "JPEG", "PNG", "JPG", "TIFF").pack(pady=5, fill=tk.X)
        tk.Button(frame, text="Нарезать изображение", command=self.cut_image).pack(pady=5, fill=tk.X)

    def create_calculator_widgets(self):
        frame = tk.Frame(self.main_frame)
        frame.grid(row=0, column=1, padx=5, pady=5, sticky="nsew")

        tk.Label(frame, text="Калькулятор").pack(pady=5)
        self.calculator_entry = tk.Entry(frame)
        self.calculator_entry.pack(pady=5, fill=tk.X)

        btn_frame = tk.Frame(frame)
        btn_frame.pack(pady=10)

        buttons = [
            ('7', 0, 0), ('8', 0, 1), ('9', 0, 2), ('+', 0, 3),
            ('4', 1, 0), ('5', 1, 1), ('6', 1, 2), ('-', 1, 3),
            ('1', 2, 0), ('2', 2, 1), ('3', 2, 2), ('*', 2, 3),
            ('0', 3, 0), ('.', 3, 1), ('=', 3, 2), ('/', 3, 3)
        ]

        for (text, row, col) in buttons:
            cmd = lambda x=text: self.calculator_entry.insert(tk.END, x) if x != '=' else self.calculate_result()
            tk.Button(btn_frame, text=text, width=3, command=cmd).grid(row=row, column=col, padx=2, pady=2)

        self.result_label = tk.Label(frame, text="")
        self.result_label.pack(pady=5)

    def create_conversion_widgets(self):
        frame = tk.Frame(self.main_frame)
        frame.grid(row=0, column=2, padx=5, pady=5, sticky="nsew")

        tk.Label(frame, text="Конвертация TIFF").pack(pady=5)
        ttk.Separator(frame).pack(fill=tk.X, pady=5)

        tk.Button(frame, text="Выбрать TIFF файл", command=self.select_tiff_file).pack(pady=5, fill=tk.X)

        self.target_format = StringVar(value="PNG")
        tk.OptionMenu(frame, self.target_format, "PNG").pack(pady=5, fill=tk.X)

        tk.Button(frame, text="Конвертировать", command=self.convert_tiff).pack(pady=5, fill=tk.X)
        self.conversion_status = tk.Label(frame, text="")
        self.conversion_status.pack(pady=5)

    def browse_directory(self):
        directory = filedialog.askdirectory()
        if directory:
            self.output_directory.set(directory)

    def select_images(self):
        file_paths = filedialog.askopenfilenames(filetypes=[("Image files", "*.*")])
        self.images = list(file_paths)
        if self.images:
            messagebox.showinfo("Выбор изображений", f"Выбрано {len(self.images)} изображений.")

    def select_cut_image(self):
        file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.*")])
        if file_path:
            self.cut_image_path = file_path

    def read_image_unicode(self, image_path):
        try:
            return cv2.imdecode(np.fromfile(image_path, dtype=np.uint8), cv2.IMREAD_COLOR)
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка при чтении изображения: {e}")
            return None

    def merge_images(self):
        if not self.images or not self.output_directory.get():
            messagebox.showwarning("Ошибка", "Проверьте ввод данных")
            return

        save_name = self.save_name_entry.get() or "merged_image"
        save_format = self.save_format.get().lower()
        images = []
        max_width = 0
        total_height = 0

        for img_path in self.images:
            img = self.read_image_unicode(img_path)
            if img is not None:
                images.append(img)
                max_width = max(max_width, img.shape[1])
                total_height += img.shape[0]

        try:
            merged_image = np.zeros((total_height, max_width, 3), dtype=np.uint8)
            current_height = 0
            for img in images:
                h, w = img.shape[:2]
                merged_image[current_height:current_height + h, :w] = img
                current_height += h
                del img

            output_path = os.path.join(self.output_directory.get(), f"{save_name}.{save_format}")
            if save_format in ['tif', 'tiff']:
                imwrite(output_path, merged_image, bigtiff=True)
            else:
                cv2.imwrite(output_path, merged_image)

            messagebox.showinfo("Успех", f"Изображения объединены: {output_path}")

        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка объединения: {str(e)}")

    def cut_image(self):
        if not self.cut_image_path or not self.output_directory.get():
            messagebox.showwarning("Ошибка", "Проверьте ввод данных")
            return

        try:
            img = self.read_image_unicode(self.cut_image_path)
            height = img.shape[0]
            width = img.shape[1]

            if self.cut_method.get() == "pieces":
                num_pieces = int(self.cut_height_entry.get())
                actual_cut_height = height // num_pieces
            else:
                actual_cut_height = int(self.cut_height_entry.get())
                num_pieces = (height + actual_cut_height - 1) // actual_cut_height

            save_name = self.save_name_entry.get() or "fragment"
            save_format = self.save_format.get().lower()

            for i in range(num_pieces):
                start = i * actual_cut_height
                end = min(start + actual_cut_height, height)
                piece = img[start:end, 0:width]
                output_path = os.path.join(self.output_directory.get(), f"{save_name}_{i + 1}.{save_format}")
                cv2.imwrite(output_path, piece)

            messagebox.showinfo("Успех", f"Нарезано {num_pieces} фрагментов")

        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка нарезки: {str(e)}")

    def update_cut_label(self):
        if self.cut_method.get() == "pieces":
            self.cut_label.config(text="Введите количество фрагментов:")
        else:
            self.cut_label.config(text="Введите высоту фрагмента (пиксели):")
        self.cut_height_entry.delete(0, tk.END)

    def calculate_result(self):
        try:
            result = eval(self.calculator_entry.get())
            self.result_label.config(text=f"Результат: {result}")
        except:
            messagebox.showwarning("Ошибка", "Некорректное выражение")

    def select_tiff_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("TIFF files", "*.tif;*.tiff")])
        if file_path:
            self.selected_tiff = file_path
            self.conversion_status.config(text=f"Выбран файл: {os.path.basename(file_path)}")

    def convert_tiff(self):
        if not self.selected_tiff or not self.output_directory.get():
            messagebox.showwarning("Ошибка", "Проверьте ввод данных")
            return

        try:
            img = imread(self.selected_tiff)
            base_name = os.path.splitext(os.path.basename(self.selected_tiff))[0]
            target_format = self.target_format.get().lower()
            output_path = os.path.join(self.output_directory.get(), f"{base_name}_converted.{target_format}")

            save_params = []
            if target_format in ['jpg', 'jpeg']:
                save_params = [cv2.IMWRITE_JPEG_QUALITY, 90]
            elif target_format == 'webp':
                save_params = [cv2.IMWRITE_WEBP_QUALITY, 90]

            cv2.imwrite(output_path, img, save_params)
            messagebox.showinfo("Успех", f"Файл конвертирован: {output_path}")

        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка конвертации: {str(e)}")



if __name__ == "__main__":
    root = tk.Tk()
    root.geometry("1200x800")
    app = ImageMergerApp(root)
    root.mainloop()
