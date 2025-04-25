import fitz  # PyMuPDF
import pandas as pd
import tkinter as tk
from tkinter import filedialog, messagebox
from datetime import datetime

# تحويل درجة الحرارة من فهرنهايت إلى سيلزيوس
def fahrenheit_to_celsius(f):
    return round((f - 32) * 5 / 9, 1)

# دالة استخراج البيانات من PDF
def extract_data_from_pdf(pdf_path):
    data = []
    doc = fitz.open(pdf_path)

    for page in doc:
        text = page.get_text()

        if "Air System Sizing Summary for system" in text:
            lines = text.split('\n')
            system_name = ""
            total_coil_load_mbh = ""
            max_block_cfm = ""
            oa_db_wb_f = ""

            for i, line in enumerate(lines):
                if "Air System Name" in line:
                    system_name = line.split('system')[-1].strip()
                if "Central Cooling Coil Sizing Data" in line:
                    for j in range(i+1, i+15):
                        if "Total coil load" in lines[j] and "MBH" in lines[j]:
                            parts = lines[j].split()
                            total_coil_load_mbh = parts[-2]
                        if "Max block CFM" in lines[j]:
                            parts = lines[j].split()
                            max_block_cfm = parts[-2]
                if "OA DB / WB" in line and "/" in line:
                    oa_db_wb_f = line.split()[-3] + ' ' + line.split()[-1]

            if system_name:
                mbh = float(total_coil_load_mbh)
                btu_hr = mbh * 1000
                tons = round(btu_hr / 12000, 2)

                try:
                    oa_db_f, oa_wb_f = map(float, oa_db_wb_f.replace('°F', '').split('/'))
                    oa_db_c = fahrenheit_to_celsius(oa_db_f)
                    oa_wb_c = fahrenheit_to_celsius(oa_wb_f)
                    oa_db_wb_c = f"{oa_db_c} / {oa_wb_c}"
                except:
                    oa_db_wb_c = ""

                data.append({
                    "System Name": system_name,
                    "Total Coil Load (MBH)": mbh,
                    "Total Coil Load (BTU/hr)": btu_hr,
                    "Total Coil Load (Tons)": tons,
                    "Max Block CFM": max_block_cfm,
                    "OA DB/WB (\u00b0F)": oa_db_wb_f,
                    "OA DB/WB (\u00b0C)": oa_db_wb_c
                })

    doc.close()
    return data

# دالة إنشاء واجهة المستخدم
def run_gui():
    def select_file():
        file_path = filedialog.askopenfilename(filetypes=[("PDF Files", "*.pdf")])
        if file_path:
            pdf_path.set(file_path)

    def extract():
        if not pdf_path.get():
            messagebox.showerror("خطأ", "من فضلك اختر ملف PDF أولاً!")
            return

        try:
            data = extract_data_from_pdf(pdf_path.get())
            if not data:
                messagebox.showwarning("تحذير", "لم يتم العثور على بيانات!")
                return

            df = pd.DataFrame(data)
            save_path = filedialog.asksaveasfilename(
                defaultextension=".xlsx",
                filetypes=[("Excel Files", "*.xlsx")],
                initialfile=datetime.now().strftime("%Y-%m-%d")
            )
            if save_path:
                df.to_excel(save_path, index=False)
                messagebox.showinfo("نجاح", f"تم استخراج البيانات وحفظها في:\n{save_path}")
        except Exception as e:
            messagebox.showerror("خطأ", str(e))

    # إنشاء الواجهة
    root = tk.Tk()
    root.title("Halawa EXT")
    root.geometry("400x200")

    pdf_path = tk.StringVar()

    tk.Button(root, text="اختر ملف PDF", command=select_file, height=2, width=20).pack(pady=20)
    tk.Button(root, text="Extract", command=extract, height=2, width=20).pack(pady=10)

    root.mainloop()

if __name__ == "__main__":
    run_gui()
