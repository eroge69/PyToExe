
import os
from tkinter import Tk, filedialog, messagebox
from docx import Document

Tk().withdraw()
folder_path = filedialog.askdirectory(title="پوشه فایل‌های Word را انتخاب کنید")

if not folder_path:
    messagebox.showerror("خطا", "هیچ پوشه‌ای انتخاب نشد.")
    exit()

word_files = [f for f in os.listdir(folder_path) if f.endswith('.docx')]
word_files.sort()

if not word_files:
    messagebox.showinfo("اطلاع", "هیچ فایل Word با پسوند .docx در این پوشه یافت نشد.")
    exit()

merged_doc = Document()

for i, file in enumerate(word_files):
    sub_doc = Document(os.path.join(folder_path, file))
    for element in sub_doc.element.body:
        merged_doc.element.body.append(element)
    if i != len(word_files) - 1:
        merged_doc.add_page_break()

output_path = os.path.join(folder_path, 'merged_document.docx')
merged_doc.save(output_path)

messagebox.showinfo("موفقیت", f"فایل نهایی با نام:\n\n{output_path}\n\nساخته شد.")
