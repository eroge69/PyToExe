
import tkinter as tk
from datetime import datetime, timedelta
import jdatetime

def calculate_future_date():
    try:
        days = int(entry.get())
        today = datetime.today()
        future = today + timedelta(days=days)
        
        # تبدیل تاریخ میلادی به شمسی
        future_jalali = jdatetime.date.fromgregorian(date=future)
        
        result_label.config(
            text=f"{days} روز بعد: {future.strftime('%Y-%m-%d')} (میلادی)\n"
                 f"{future_jalali.strftime('%Y/%m/%d')} (شمسی)"
        )
    except ValueError:
        result_label.config(text="لطفاً یک عدد معتبر وارد کنید.")

# ساخت رابط گرافیکی
root = tk.Tk()
root.title("محاسبه تاریخ آینده (شمسی/میلادی)")
root.geometry("350x180")

tk.Label(root, text="تعداد روز بعد از امروز را وارد کنید:").pack(pady=5)

entry = tk.Entry(root)
entry.pack()

tk.Button(root, text="محاسبه", command=calculate_future_date).pack(pady=10)

result_label = tk.Label(root, text="", justify="center")
result_label.pack()

root.mainloop()
