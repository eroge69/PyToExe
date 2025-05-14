import openpyxl
import re
from openpyxl.utils import get_column_letter
import tkinter as tk
from tkinter import filedialog, messagebox
import os

def extract_prompts_from_excel(file_path):
    wb = openpyxl.load_workbook(file_path)
    ws = wb.active

    for row in ws.iter_rows(min_row=2, min_col=6, max_col=6):  # Cột F là cột số 6
        cell = row[0]
        text = cell.value
        if not isinstance(text, str):
            continue

        matches = re.findall(r'Prompt \d+:\s*(.*?)(?=\s*Prompt \d+:|$)', text, flags=re.DOTALL)

        row_num = cell.row
        for i, content in enumerate(matches):
            col_idx = 7 + i  # G = 7
            ws.cell(row=row_num, column=col_idx).value = content.strip()

    output_path = os.path.splitext(file_path)[0] + "_output.xlsx"
    wb.save(output_path)
    return output_path

def select_file():
    file_path = filedialog.askopenfilename(filetypes=[("Excel files", "*.xlsx")])
    if file_path:
        try:
            output_file = extract_prompts_from_excel(file_path)
            messagebox.showinfo("Thành công", f"Đã xuất kết quả ra file:\n{output_file}")
        except Exception as e:
            messagebox.showerror("Lỗi", str(e))

# Tạo giao diện đơn giản
app = tk.Tk()
app.title("Trích xuất Prompts từ Excel")
app.geometry("400x200")

label = tk.Label(app, text="Chọn file Excel chứa cột F có Prompts", pady=20)
label.pack()

btn = tk.Button(app, text="Chọn file Excel", command=select_file, padx=10, pady=5)
btn.pack()

app.mainloop()