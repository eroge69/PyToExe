import pandas as pd
from tkinter import Tk, filedialog, messagebox
import os

def txt_to_excel(txt_file_path, excel_file_path):
    try:
        # قراءة ملف TXT
        with open(txt_file_path, 'r', encoding='utf-8') as file:
            lines = file.readlines()
        
        # افتراض أن البيانات مفصولة بمسافات أو Tabs
        data = [line.strip().split() for line in lines if line.strip()]

        # إنشاء DataFrame
        df = pd.DataFrame(data)

        # كتابة إلى Excel مع التنسيق
        with pd.ExcelWriter(excel_file_path, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, header=False)

        messagebox.showinfo("نجاح", f"تم تحويل الملف إلى Excel بنجاح:\n{excel_file_path}")

    except Exception as e:
        messagebox.showerror("خطأ", f"حدث خطأ أثناء التحويل:\n{str(e)}")

def select_txt_file():
    root = Tk()
    root.withdraw()
    txt_path = filedialog.askopenfilename(title="اختر ملف TXT", filetypes=[("Text Files", "*.txt")])
    if txt_path:
        # اقتراح اسم ملف Excel
        excel_path = os.path.splitext(txt_path)[0] + ".xlsx"
        txt_to_excel(txt_path, excel_path)

if __name__ == "__main__":
    select_txt_file()
