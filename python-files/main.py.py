import os
import tkinter as tk
from tkinter import messagebox
import pandas as pd
from openpyxl import Workbook
from openpyxl.styles import Font

# بارگذاری داده‌ها
city_price_df = pd.read_excel("شهر و قیمت.xlsx")
route_type_df = pd.read_excel("مسیر و نوع.xlsx")

# تابع محاسبه و ذخیره
def calculate():
    city = entry_city.get()
    num_customers = entry_customers.get()
    input_date = entry_date.get()

    if not city or not num_customers or not input_date:
        messagebox.showerror("خطا", "لطفاً تمام فیلدها را پر کنید.")
        return

    try:
        num_customers = int(num_customers)

        city_row = city_price_df[city_price_df["آخرین"] == city]
        if city_row.empty:
            messagebox.showerror("خطا", f"شهر '{city}' پیدا نشد.")
            return

        base_price = city_row["قیمت"].values[0]
        route_row = route_type_df[route_type_df["شرح فارسي"].str.contains(city)]
        route_type = route_row["قیمت"].values[0] if not route_row.empty else 1

        price_with_difficulty = base_price * 1.5 if route_type == 2 else base_price
        total_price = price_with_difficulty + (num_customers * 5_000_000)

        # پوشه روی دسکتاپ
        desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
        folder_path = os.path.join(desktop_path, "هزینه ی ارسال بار")
        os.makedirs(folder_path, exist_ok=True)

        filename = f"{city}_{input_date.replace('/', '-')}.xlsx"
        file_path = os.path.join(folder_path, filename)

        wb = Workbook()
        ws = wb.active
        ws.title = "نتیجه محاسبه"
        ws.append(["شهر", "تاریخ", "قیمت پایه", "نوع مسیر", "تعداد مشتری", "قیمت نهایی"])

        for cell in ws["1:1"]:
            cell.font = Font(bold=True)

        ws.append([
            city,
            input_date,
            int(base_price),
            "سخت" if route_type == 2 else "ساده",
            num_customers,
            int(total_price)
        ])

        wb.save(file_path)

        lbl_result.config(
            text=f"✅ فایل در دسکتاپ ذخیره شد:\n{filename}",
            fg="green"
        )
        lbl_price.config(
            text=f"{int(total_price):,} ریال",
            fg="blue",
            font=("B Nazanin", 20, "bold")
        )

    except Exception as e:
        messagebox.showerror("خطا", str(e))


# رابط گرافیکی
root = tk.Tk()
root.title("محاسبه هزینه ارسال بار")
root.geometry("400x350")
root.resizable(False, False)

tk.Label(root, text="نام شهر:").pack()
entry_city = tk.Entry(root)
entry_city.pack()

tk.Label(root, text="تعداد مشتری:").pack()
entry_customers = tk.Entry(root)
entry_customers.pack()

tk.Label(root, text="تاریخ محاسبه (مثلاً 1403/02/15):").pack()
entry_date = tk.Entry(root)
entry_date.pack()

tk.Button(root, text="محاسبه و ذخیره در دسکتاپ", command=calculate).pack(pady=10)

lbl_result = tk.Label(root, text="")
lbl_result.pack()

lbl_price = tk.Label(root, text="")
lbl_price.pack()

root.mainloop()