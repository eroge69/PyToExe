import pandas as pd
import tkinter as tk
from tkinter import messagebox
import os
from PIL import Image, ImageTk









def calculate_volumes():
    try:
        A = float(entry_A.get())
        B = float(entry_B.get())
        C = float(entry_C.get())
        h1 = float(entry_h1.get())
        h2 = float(entry_h2.get())

        V1 = A * B * C / 2
        V2 = 3.14 / 6 * (h1**3 + h2**3) + 3.14 / 8 * A * B * (h2 + h1)

        data = {
            'A (см)': [A], 'B (см)': [B], 'C (см)': [C], 'h1 (см)': [h1], 'h2 (см)': [h2], 'V1': [V1], 'V2': [V2]
        }
        df = pd.DataFrame(data)

        try:
            filepath = os.path.join("output", "volumes.xlsx")
            if not os.path.exists("output"):
                os.makedirs("output")

            try:
                existing_df = pd.read_excel(filepath)
                df = pd.concat([existing_df, df], ignore_index=True)

            except FileNotFoundError:
                pass

            df.to_excel(filepath, index=False)
            messagebox.showinfo("Успех", f"Результаты сохранены в {filepath}\nV1 = {V1}\nV2 = {V2}")

        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка при сохранении в Excel: {e}")

    except ValueError:
        messagebox.showerror("Ошибка", "Введите числовые значения.")



root = tk.Tk()
root.title("Калькулятор объемов")


img = Image.open("c:/Users/lazukin_v/Desktop/ваня/овая папка/hh.jpg")

img.show()


labels = ["A (см):", "B (см):", "C (см):", "h1 (см):", "h2 (+-):"]








entries = []
for i, label_text in enumerate(labels):
    tk.Label(root, text=label_text).grid(row=i, column=0)
    entry = tk.Entry(root)
    entry.grid(row=i, column=1)
    entries.append(entry)

entry_A, entry_B, entry_C, entry_h1, entry_h2 = entries

tk.Button(root, text="Вычислить", command=calculate_volumes).grid(row=len(labels), column=0, columnspan=2)

root.mainloop()

