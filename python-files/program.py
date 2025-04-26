import tkinter as tk
from tkinter import messagebox
import sqlite3
import pandas as pd
from datetime import datetime

# إعداد قاعدة البيانات
conn = sqlite3.connect('expenses.db')
cursor = conn.cursor()

# التأكد من إضافة العمود name إذا لم يكن موجود
cursor.execute('''PRAGMA foreign_keys=OFF;''')  # إيقاف القيود المؤقتًا

# التحقق من وجود العمود 'name' قبل إضافته
cursor.execute("PRAGMA table_info(records);")
columns = [column[1] for column in cursor.fetchall()]
if 'name' not in columns:
    cursor.execute('''ALTER TABLE records ADD COLUMN name TEXT;''')  # إضافة العمود name
conn.commit()

# وظيفة لتقسيم المبلغ وحفظه
def save_record():
    try:
        name = entry_name.get()
        amount = float(entry_amount.get())
        rent = amount * 0.50
        labor = amount * 0.45
        profit = amount * 0.05
        date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        cursor.execute("INSERT INTO records (name, amount, rent, labor, profit, date) VALUES (?, ?, ?, ?, ?, ?)",
                       (name, amount, rent, labor, profit, date))
        conn.commit()

        # تصدير السجل مباشرة إلى Excel بعد حفظه
        export_to_excel()

        messagebox.showinfo("تم", f"تم تقسيم المبلغ بنجاح!\nإيجار: {rent}\nعمال: {labor}\nأرباح: {profit}")
        load_records()

    except ValueError:
        messagebox.showerror("خطأ", "يرجى إدخال قيمة صحيحة للمبلغ.")

# وظيفة لتحميل السجلات
def load_records():
    cursor.execute("SELECT * FROM records")
    rows = cursor.fetchall()
    text_output.delete(1.0, tk.END)
    for row in rows:
        text_output.insert(tk.END, f"{row[5]} - {row[1]} | المبلغ: {row[2]} | إيجار: {row[3]} | عمال: {row[4]} | أرباح: {row[5]}\n")

# وظيفة لتصدير السجلات إلى Excel تلقائيًا بعد إضافة كل عملية جديدة
def export_to_excel():
    try:
        cursor.execute("SELECT * FROM records")
        rows = cursor.fetchall()
        df = pd.DataFrame(rows, columns=["ID", "Name", "Amount", "Rent", "Labor", "Profit", "Date"])
        df.to_excel("expenses_records.xlsx", index=False)
        print("تم تصدير السجلات إلى ملف Excel بنجاح!")
    except Exception as e:
        messagebox.showerror("خطأ", f"حدث خطأ أثناء التصدير: {e}")

# إعداد واجهة المستخدم
root = tk.Tk()
root.title("برنامج تقسيم المصاريف")
root.geometry("500x400")
root.config(bg="gray")

# الحقول والأزرار
label_name = tk.Label(root, text="أدخل الاسم:", bg="gray", fg="white")
label_name.pack(pady=10)
entry_name = tk.Entry(root)
entry_name.pack(pady=5)

label_amount = tk.Label(root, text="أدخل المبلغ:", bg="gray", fg="white")
label_amount.pack(pady=10)
entry_amount = tk.Entry(root)
entry_amount.pack(pady=5)

button_save = tk.Button(root, text="حفظ التقسيم", command=save_record)
button_save.pack(pady=10)

text_output = tk.Text(root, width=50, height=10, wrap=tk.WORD)
text_output.pack(pady=10)

# تحميل السجلات عند فتح البرنامج
load_records()

root.mainloop()

# إغلاق الاتصال بقاعدة البيانات عند إغلاق البرنامج
conn.close()
