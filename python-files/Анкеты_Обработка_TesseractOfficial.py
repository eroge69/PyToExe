
import os
import pytesseract
from pdf2image import convert_from_path
import cv2
import numpy as np
import pandas as pd
import tkinter as tk
from tkinter import messagebox
import traceback

# Пути
pdf_folder = r'C:\Users\Производство\Desktop\Anket\Анкеты'
tesseract_path = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
poppler_path = r'C:\Users\Производство\Desktop\Anket\Popler\poppler-24.08.0\Library\bin'
output_excel = os.path.join(os.path.dirname(pdf_folder), 'анализ-анкет.xlsx')

# Установка пути к Tesseract
pytesseract.pytesseract.tesseract_cmd = tesseract_path

# Установка переменной окружения для tessdata
os.environ["TESSDATA_PREFIX"] = os.path.join(os.path.dirname(tesseract_path), "tessdata")

def process_surveys():
    data = []

    try:
        for filename in os.listdir(pdf_folder):
            if filename.lower().endswith('.pdf'):
                file_path = os.path.join(pdf_folder, filename)
                pages = convert_from_path(file_path, dpi=300, poppler_path=poppler_path)

                for page in pages:
                    img = np.array(page)
                    h, w = img.shape[:2]
                    crop = img[0:h, int(w * 0.75):w]

                    gray = cv2.cvtColor(crop, cv2.COLOR_BGR2GRAY)
                    _, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY_INV)

                    text = pytesseract.image_to_string(thresh, config='--psm 6 digits')
                    digits = [int(s) for s in text.split() if s.isdigit()]
                    while len(digits) < 11:
                        digits.append(None)

                    data.append(digits[:11])

        columns = [f'Вопрос {i+1}' for i in range(11)]
        df = pd.DataFrame(data, columns=columns)
        df.to_excel(output_excel, index=False, engine='openpyxl')

        messagebox.showinfo("Готово", f"Обработка завершена!\nФайл сохранён как:\n{output_excel}")
    except Exception as e:
        messagebox.showerror("Ошибка", f"Произошла ошибка:\n{traceback.format_exc()}")

# Интерфейс
root = tk.Tk()
root.title("Обработка анкет")
root.geometry("400x200")

label = tk.Label(root, text="Нажмите кнопку для обработки анкет в PDF", font=("Arial", 12))
label.pack(pady=30)

button = tk.Button(root, text="Запустить обработку", font=("Arial", 12, "bold"), command=process_surveys)
button.pack(pady=10)

root.mainloop()
