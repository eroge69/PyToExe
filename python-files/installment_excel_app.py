
import tkinter as tk
from tkinter import messagebox
import pandas as pd
from datetime import datetime

EXCEL_FILE = "data.xlsx"

def add_installment():
    name = entry_name.get()
    try:
        total = float(entry_total.get())
        paid = float(entry_paid.get())
        date = entry_date.get()
    except:
        messagebox.showerror("خطأ", "يرجى إدخال مبلغ صحيح")
        return

    remaining = total - paid
    status = "مدفوع" if remaining <= 0 else "غير مدفوع"

    new_row = pd.DataFrame([[name, total, paid, remaining, date, status]],
                           columns=["اسم الزبون", "المبلغ الكلي", "الدفعة", "المبلغ المتبقي", "تاريخ الدفع", "الحالة"])

    try:
        df = pd.read_excel(EXCEL_FILE, sheet_name="الأقساط")
        df = pd.concat([df, new_row], ignore_index=True)
    except:
        df = new_row

    with pd.ExcelWriter(EXCEL_FILE, engine="openpyxl", mode="a", if_sheet_exists="replace") as writer:
        df.to_excel(writer, sheet_name="الأقساط", index=False)

    messagebox.showinfo("تم", "تمت إضافة القسط بنجاح")
    entry_name.delete(0, tk.END)
    entry_total.delete(0, tk.END)
    entry_paid.delete(0, tk.END)
    entry_date.delete(0, tk.END)

app = tk.Tk()
app.title("نظام التقسيط - مكتبة هوبي")
app.geometry("400x450")
app.configure(bg="#f9f6f0")

tk.Label(app, text="اسم الزبون").pack()
entry_name = tk.Entry(app)
entry_name.pack()

tk.Label(app, text="المبلغ الكلي").pack()
entry_total = tk.Entry(app)
entry_total.pack()

tk.Label(app, text="الدفعة").pack()
entry_paid = tk.Entry(app)
entry_paid.pack()

tk.Label(app, text="تاريخ الدفع").pack()
entry_date = tk.Entry(app)
entry_date.pack()

tk.Button(app, text="إضافة القسط", command=add_installment, bg="#1f4f4f", fg="white").pack(pady=20)

app.mainloop()
