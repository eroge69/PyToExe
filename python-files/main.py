
import tkinter as tk
from tkinter import messagebox

def check_password():
    if entry.get() == "wxero":
        root.destroy()
        open_dashboard()
    else:
        messagebox.showerror("خطأ", "كلمة المرور غير صحيحة")

def open_dashboard():
    dash = tk.Tk()
    dash.title("Insta Followers Booster")
    dash.geometry("500x400")
    dash.configure(bg="black")
    
    tk.Label(dash, text="لوحة التحكم", font=("Arial", 20), fg="lime", bg="black").pack(pady=20)
    tk.Button(dash, text="إنشاء حساب", width=25, height=2).pack(pady=5)
    tk.Button(dash, text="إنشاء عدد حسابات", width=25, height=2).pack(pady=5)
    tk.Button(dash, text="إرسال متابعين", width=25, height=2).pack(pady=5)
    tk.Button(dash, text="عرض الحسابات", width=25, height=2).pack(pady=5)
    tk.Button(dash, text="خروج", width=25, height=2, command=dash.quit).pack(pady=20)
    tk.Label(dash, text="Instagram: @wx.ero | المطور: تواصل مع", fg="pink", bg="black").pack(side="bottom", pady=10)
    
    dash.mainloop()

root = tk.Tk()
root.title("wxeroGPT Login")
root.geometry("300x150")
root.configure(bg="black")

tk.Label(root, text="أدخل كلمة المرور", fg="white", bg="black").pack(pady=10)
entry = tk.Entry(root, show="*", width=30)
entry.pack()
tk.Button(root, text="دخول", command=check_password).pack(pady=10)

root.mainloop()
