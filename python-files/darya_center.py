import tkinter as tk
from tkinter import ttk, messagebox

def calculate_coins_to_dinar():
    try:
        coins = float(entry_coins.get())
        
        if rate_var.get() == 1:
            rate = 15500
        elif rate_var.get() == 2:
            rate = 16000
        else:
            rate = float(entry_custom_rate.get())
            if rate <= 0:
                raise ValueError
        
        result = (coins / 1000) * rate
        lbl_coins_result.config(text=f"المبلغ بالدينار: {result:,.0f} IQD", foreground='#27ae60')
        
    except ValueError:
        messagebox.showerror("خطأ", "قيم غير صالحة في حقل العملات")
        lbl_coins_result.config(text="حدث خطأ في الحساب", foreground='red')

def calculate_dinar_to_coins():
    try:
        dinar = float(entry_dinar.get())
        
        if rate_var.get() == 1:
            rate = 15500
        elif rate_var.get() == 2:
            rate = 16000
        else:
            rate = float(entry_custom_rate.get())
            if rate <= 0:
                raise ValueError
        
        result = (dinar / rate) * 1000
        lbl_dinar_result.config(text=f"عدد العملات: {result:,.0f} عملة", foreground='#2980b9')
        
    except ValueError:
        messagebox.showerror("خطأ", "قيم غير صالحة في حقل الدينار")
        lbl_dinar_result.config(text="حدث خطأ في الحساب", foreground='red')

def toggle_custom_rate():
    if rate_var.get() == 3:
        entry_custom_rate.config(state='normal')
    else:
        entry_custom_rate.config(state='disabled')

# إنشاء النافذة الرئيسية
root = tk.Tk()
root.title("Darya Center - Advanced Converter")
root.geometry("600x500")

# الإطار الرئيسي
main_frame = ttk.Frame(root, padding=20)
main_frame.pack(expand=True, fill='both')

# عنوان البرنامج
ttk.Label(main_frame, 
         text="محول عملات تيك توك المتقدم",
         font=('Arial', 16, 'bold'),
         foreground='#2c3e50').grid(row=0, column=0, columnspan=3, pady=10)

# قسم تحويل العملات إلى دينار
coins_frame = ttk.LabelFrame(main_frame, text="تحويل العملات إلى دينار")
coins_frame.grid(row=1, column=0, padx=10, pady=5, sticky='nsew')

ttk.Label(coins_frame, text="عدد العملات:").grid(row=0, column=0, padx=5)
entry_coins = ttk.Entry(coins_frame, width=20)
entry_coins.grid(row=0, column=1, padx=5)

btn_coins = ttk.Button(coins_frame, 
                      text="تحويل إلى دينار",
                      command=calculate_coins_to_dinar)
btn_coins.grid(row=0, column=2, padx=5)

lbl_coins_result = ttk.Label(coins_frame, text="", font=('Arial', 10))
lbl_coins_result.grid(row=1, column=0, columnspan=3, pady=5)

# قسم تحويل الدينار إلى عملات
dinar_frame = ttk.LabelFrame(main_frame, text="تحويل الدينار إلى عملات")
dinar_frame.grid(row=2, column=0, padx=10, pady=5, sticky='nsew')

ttk.Label(dinar_frame, text="المبلغ بالدينار:").grid(row=0, column=0, padx=5)
entry_dinar = ttk.Entry(dinar_frame, width=20)
entry_dinar.grid(row=0, column=1, padx=5)

btn_dinar = ttk.Button(dinar_frame, 
                      text="تحويل إلى عملات",
                      command=calculate_dinar_to_coins)
btn_dinar.grid(row=0, column=2, padx=5)

lbl_dinar_result = ttk.Label(dinar_frame, text="", font=('Arial', 10))
lbl_dinar_result.grid(row=1, column=0, columnspan=3, pady=5)

# إعدادات سعر الصرف
rate_frame = ttk.LabelFrame(main_frame, text="إعدادات سعر الصرف")
rate_frame.grid(row=3, column=0, pady=15, sticky='we')

rate_var = tk.IntVar(value=1)

ttk.Radiobutton(rate_frame, 
               text="السعر الأساسي 1: 1000 عملة = 15,500 دينار",
               variable=rate_var,
               value=1,
               command=toggle_custom_rate).pack(anchor='w', padx=10)

ttk.Radiobutton(rate_frame, 
               text="السعر الأساسي 2: 1000 عملة = 16,000 دينار",
               variable=rate_var,
               value=2,
               command=toggle_custom_rate).pack(anchor='w', padx=10)

ttk.Radiobutton(rate_frame, 
               text="سعر مخصص:",
               variable=rate_var,
               value=3,
               command=toggle_custom_rate).pack(anchor='w', padx=10, pady=5)

entry_custom_rate = ttk.Entry(rate_frame, width=15, state='disabled')
entry_custom_rate.pack(side='left', padx=10)
ttk.Label(rate_frame, text="دينار لكل 1000 عملة").pack(side='left')

# تذييل البرنامج
ttk.Label(root, 
         text="الإصدار 3.0 - نظام التحويل الثنائي",
         foreground='gray').pack(side='bottom', pady=5)

root.mainloop()