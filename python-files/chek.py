import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
import pandas as pd
import jdatetime
import arabic_reshaper
from bidi.algorithm import get_display
from collections import defaultdict

def fix_persian_text(text):
    reshaped_text = arabic_reshaper.reshape(text)
    return get_display(reshaped_text)

def get_days_in_month(year, month):
    for day in range(31, 27, -1):
        try:
            jdatetime.date(year, month, day)
            return day
        except:
            continue
    return 0

def parse_valid_jdate(date_str):
    try:
        parts = str(date_str).strip().split('/')
        if len(parts) == 3:
            y, m, d = map(int, parts)
            return jdatetime.date(y, m, d)
    except:
        return None

def categorize_account(account_number):
    if isinstance(account_number, str):
        if "رسمي" in account_number or "رسمی" in account_number:
            return "رسمی"
        elif "غير رسمي" in account_number or "غیر رسمی" in account_number:
            return "غیررسمی"
    return "نامشخص"

# نگاشت روزهای هفته به فارسی
weekday_map = {
    'Saturday': 'شنبه',
    'Sunday': 'یکشنبه',
    'Monday': 'دوشنبه',
    'Tuesday': 'سه‌شنبه',
    'Wednesday': 'چهارشنبه',
    'Thursday': 'پنجشنبه',
    'Friday': 'جمعه',
}

def analyze(file_path, output_widget):
    try:
        df = pd.read_excel(file_path)

        required_columns = ["تفصيلي", "طرف مقابل", "شماره", "مبلغ", "تاريخ سررسيد", "تاريخ وصول", "وضعيت", "حساب بانكي"]
        if not all(col in df.columns for col in required_columns):
            output_widget.insert(tk.END, "ستون‌های موردنیاز در فایل وجود ندارند." + "\n")
            return

        output = []

        dates = df["تاريخ سررسيد"].dropna().astype(str).map(parse_valid_jdate).dropna()
        dates = sorted(dates)
        dates_by_month = defaultdict(set)
        for d in dates:
            key = (d.year, d.month)
            dates_by_month[key].add(d.day)

        output.append("📆 روزهای بدون چک در هر ماه:")
        for (year, month), days_with_cheques in sorted(dates_by_month.items()):
            days_in_month = get_days_in_month(year, month)
            all_days = set(range(1, days_in_month + 1))
            missing_days = sorted(all_days - days_with_cheques)

            output.append("")
            output.append(f"ماه {month} / سال {year} — روزهای بدون چک:")
            for d in missing_days:
                try:
                    jd = jdatetime.date(year, month, d)
                    weekday_en = jd.strftime('%A')
                    weekday_fa = weekday_map.get(weekday_en, weekday_en)
                    date_str = f"{jd.year}/{jd.month:02}/{jd.day:02}"
                    output.append(f"{date_str} - {weekday_fa}")
                except:
                    continue

        df['تاريخ سررسيد_parsed'] = df["تاريخ سررسيد"].astype(str).map(parse_valid_jdate)
        df = df.dropna(subset=["تاريخ سررسيد_parsed"])
        df['ماه'] = df['تاريخ سررسيد_parsed'].map(lambda d: f"{d.year}/{d.month:02}")
        monthly_sums = df.groupby("ماه")["مبلغ"].sum()

        output.append("")
        output.append("💰 جمع مبالغ چک‌ها در هر ماه:")
        for month, total in monthly_sums.items():
            output.append(f"{month}: {int(total):,} ریال")

        df['نوع حساب'] = df['حساب بانكي'].map(categorize_account)
        total_official = df[df['نوع حساب'] == 'رسمی']["مبلغ"].sum()
        total_unofficial = df[df['نوع حساب'] == 'غیررسمی']["مبلغ"].sum()

        output.append("")
        output.append("🏦 تفکیک هزینه‌های رسمی و غیررسمی:")
        output.append(f"رسمی: {int(total_official):,} ریال")
        output.append(f"غیررسمی: {int(total_unofficial):,} ریال")

        output_widget.delete("1.0", tk.END)
        for line in output:
            output_widget.insert(tk.END, line + "\n")

    except Exception as e:
        messagebox.showerror("خطا", f"خطا در خواندن فایل:\n{str(e)}")

def select_file():
    file_path = filedialog.askopenfilename(filetypes=[("Excel files", "*.xlsx *.xls")])
    if file_path:
        analyze(file_path, output_text)

root = tk.Tk()
root.title("نرم‌افزار تحلیل چک‌ها")
root.geometry("850x650")
root.configure(bg="#f9f9f9")

label = tk.Label(root, text="لطفاً فایل اکسل را انتخاب کنید:", font=("B Nazanin", 16), bg="#f9f9f9")
label.pack(pady=10)

button = tk.Button(root, text="انتخاب فایل", font=("B Nazanin", 14), command=select_file,
                   bg="#007acc", fg="white", padx=15, pady=5)
button.pack()

output_text = scrolledtext.ScrolledText(root, font=("B Nazanin", 14), wrap=tk.WORD, width=95, height=30)
output_text.pack(pady=10)

root.mainloop()


