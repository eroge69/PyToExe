import tkinter as tk

# ایجاد پنجره اصلی
window = tk.Tk()
window.title("Hello World")
window.geometry("300x200")

# ایجاد برچسب با متن "Hello World"
label = tk.Label(window, text="Hello World!", font=("Arial", 24))
label.pack(expand=True)

# اجرای حلقه اصلی برنامه
window.mainloop()