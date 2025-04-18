import tkinter as tk
from tkinter import messagebox
from datetime import datetime
import webbrowser

# النافذة الرئيسية
root = tk.Tk()
root.title("SHAKER EQ")
root.geometry("500x670")
root.configure(bg='#F5F5F5')  # خلفية بيضاء ناعمة

# المتغيرات
total_amount_var = tk.DoubleVar()
item_name_var = tk.StringVar()
item_price_var = tk.DoubleVar()
customer_name_var = tk.StringVar()
purchased_total = 0.0
items_list = []

# دالة لإضافة منتج
def add_item():
    global purchased_total
    try:
        name = item_name_var.get()
        price = item_price_var.get()
        if name and price > 0:
            purchased_total += price
            items_list.append(f"{name} - {price:.2f} شيكل")
            result_label.config(text=f"المجموع الحالي: {purchased_total:.2f} شيكل", fg="#2E7D32")
            item_name_entry.delete(0, tk.END)
            item_price_entry.delete(0, tk.END)
        else:
            result_label.config(text="يرجى إدخال اسم المنتج وسعره الصحيح!", fg="red")
    except:
        result_label.config(text="يرجى إدخال بيانات صحيحة!", fg="red")

# عرض الفاتورة
def show_invoice():
    if not items_list:
        messagebox.showinfo("الفاتورة", "لا توجد منتجات.")
    else:
        now = datetime.now()
        formatted_datetime = now.strftime("%A, %d %B %Y - %I:%M %p")

        invoice_window = tk.Toplevel(root)
        invoice_window.title("فاتورة الشراء")
        invoice_window.geometry("400x470")
        invoice_window.configure(bg='white')

        tk.Label(invoice_window, text="🛒", font=('Arial', 24), bg='white').pack()
        tk.Label(invoice_window, text="SHAKER EQ", font=('Arial', 16, 'bold'), bg='white', fg='#1B5E20').pack()
        tk.Label(invoice_window, text=formatted_datetime, font=('Arial', 10), bg='white', fg='gray').pack(pady=5)

        tk.Label(invoice_window, text=f"الزبون: {customer_name_var.get()}", font=('Arial', 12), bg='white').pack(pady=5)

        invoice_frame = tk.Frame(invoice_window, bg='white')
        invoice_frame.pack(pady=10)

        for item in items_list:
            tk.Label(invoice_frame, text=item, font=('Arial', 11), bg='white').pack(anchor='w')

        tk.Label(invoice_window, text=f"\nالمجموع: {purchased_total:.2f} شيكل", font=('Arial', 13, 'bold'), fg='green', bg='white').pack()

# إعادة التصفير
def reset_all():
    global purchased_total, items_list
    purchased_total = 0.0
    items_list = []
    total_amount_var.set(0.0)
    item_name_var.set("")
    item_price_var.set(0.0)
    customer_name_var.set("")
    result_label.config(text="تمت إعادة التصفير.", fg="black")

# حساب المبلغ المتبقي
def calculate_remaining():
    try:
        total = total_amount_var.get()
        remaining = total - purchased_total
        result_label.config(text=f"المبلغ المُتبقي لإرجاعه: {remaining:.2f} شيكل", fg="#2E7D32")
    except:
        result_label.config(text="تأكد من صحة المبلغ الكلي!", fg="red")

# فتح الإيميل
def open_email():
    webbrowser.open("mailto:shakerasadthaher@gmail.com")

# عرض معلومات عن التطبيق
def show_about():
    about_window = tk.Toplevel(root)
    about_window.title("عن التطبيق")
    about_window.geometry("480x350")
    about_window.configure(bg="white")

    tk.Label(about_window, text="🛒 SHAKER EQ", font=("Arial", 18, "bold"), fg="#1B5E20", bg="white").pack(pady=10)

    description = (
        "هذا التطبيق تم تطويره بواسطة شاكر ظاهر.\n\n"
        "يهدف التطبيق إلى تسهيل عمليات الحساب داخل المحلات التجارية "
        "وتقديم تجربة احترافية وسريعة في إدارة الفواتير والمبالغ المدفوعة.\n\n"
        "يوفر التطبيق إمكانية حساب المبالغ المتبقية، توليد فواتير منظمة، "
        "وتتبع المشتريات مع عرض التاريخ والوقت بدقة.\n\n"
        "في حال واجهتكم أي مشاكل أثناء الاستخدام أو لديكم استفسارات، "
        "يرجى التواصل عبر البريد التالي:\n\n"
        "📧 shakerasadthaher@gmail.com"
    )

    tk.Label(about_window, text=description, font=("Arial", 11), fg="black", bg="white", justify="right", wraplength=450).pack(padx=20, pady=10)

# أزرار جاهزة
def styled_button(text, command, color="#388E3C"):
    return tk.Button(root, text=text, command=command, bg=color, fg='white', font=('Arial', 12, 'bold'), width=30)

# واجهة المستخدم
tk.Label(root, text="🛒", bg='#F5F5F5', font=('Arial', 28)).pack(pady=5)
tk.Label(root, text="SHAKER EQ", bg='#F5F5F5', fg='#1B5E20', font=('Arial', 18, 'bold')).pack()

tk.Label(root, text="اسم الزبون:", bg='#F5F5F5', fg='black', font=('Arial', 12)).pack()
tk.Entry(root, textvariable=customer_name_var, font=('Arial', 12)).pack(pady=5)

tk.Label(root, text="المبلغ الكلي الذي دفعه الزبون:", bg='#F5F5F5', fg='black', font=('Arial', 12)).pack()
tk.Entry(root, textvariable=total_amount_var, font=('Arial', 12)).pack(pady=5)

tk.Label(root, text="اسم المنتج:", bg='#F5F5F5', fg='black', font=('Arial', 12)).pack()
item_name_entry = tk.Entry(root, textvariable=item_name_var, font=('Arial', 12))
item_name_entry.pack(pady=5)

tk.Label(root, text="سعر المنتج:", bg='#F5F5F5', fg='black', font=('Arial', 12)).pack()
item_price_entry = tk.Entry(root, textvariable=item_price_var, font=('Arial', 12))
item_price_entry.pack(pady=5)

# الأزرار
styled_button("➕ أضف المنتج", add_item).pack(pady=7)
styled_button("💰 احسب المبلغ المُتبقي", calculate_remaining).pack(pady=7)
styled_button("🧾 طلب فاتورة", show_invoice).pack(pady=7)
styled_button("🔁 إعادة التصفير", reset_all, color="#D32F2F").pack(pady=7)
styled_button("📧 الدعم الفني", open_email, color="#1976D2").pack(pady=7)
styled_button("ℹ️ معلومات عن التطبيق", show_about, color="#455A64").pack(pady=7)

# النتائج
result_label = tk.Label(root, text="", bg='#F5F5F5', fg='black', font=('Arial', 14))
result_label.pack(pady=10)

# تشغيل التطبيق
root.mainloop()
