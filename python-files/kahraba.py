
import tkinter as tk
from tkinter import messagebox

def حساب_الاستهلاك():
    try:
        قراءة_سابقة = float(entry_قراءة_سابقة.get())
        قراءة_حالياً = float(entry_قراءة_حالية.get())
        تعرفة = float(entry_تعرفة.get())

        if قراءة_حالياً < قراءة_سابقة:
            messagebox.showerror("خطأ", "القراءة الحالية يجب أن تكون أكبر من السابقة.")
            return

        استهلاك = قراءة_حالياً - قراءة_سابقة
        تكلفة = استهلاك * تعرفة

        label_النتيجة.config(text=f"الاستهلاك: {استهلاك:.2f} kWh\nالتكلفة: {تكلفة:.2f} درهم")
    except ValueError:
        messagebox.showerror("خطأ", "يرجى إدخال أرقام صحيحة.")

# إنشاء الواجهة
window = tk.Tk()
window.title("حساب استهلاك الكهرباء")
window.geometry("300x300")
window.resizable(False, False)

tk.Label(window, text="القراءة السابقة:").pack()
entry_قراءة_سابقة = tk.Entry(window)
entry_قراءة_سابقة.pack()

tk.Label(window, text="القراءة الحالية:").pack()
entry_قراءة_حالية = tk.Entry(window)
entry_قراءة_حالية.pack()

tk.Label(window, text="تعرفة الكهرباء (درهم/ك.و.س):").pack()
entry_تعرفة = tk.Entry(window)
entry_تعرفة.pack()

tk.Button(window, text="احسب", command=حساب_الاستهلاك).pack(pady=10)

label_النتيجة = tk.Label(window, text="")
label_النتيجة.pack()

window.mainloop()
