import tkinter as tk
from tkinter import messagebox
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta

def calculate_rsi(data, window=14):
    delta = data['Close'].diff()
    gain = delta.clip(lower=0).rolling(window=window).mean()
    loss = -delta.clip(upper=0).rolling(window=window).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

def calculate_stoch_rsi(rsi, window=14):
    min_rsi = rsi.rolling(window=window).min()
    max_rsi = rsi.rolling(window=window).max()
    return (rsi - min_rsi) / (max_rsi - min_rsi)

def check_signal(mode="long"):
    try:
        symbol_input = entry.get().strip().upper()
        symbol = symbol_input + "-USD"

        end_date = datetime.now()
        start_date = end_date - timedelta(days=100)
        df = yf.download(symbol, start=start_date, end=end_date, interval="4h")

        if df.empty or len(df) < 20:
            messagebox.showwarning("❗️داده یافت نشد", f"برای نماد {symbol} داده‌ای دریافت نشد یا کافی نیست.")
            return

        df['RSI'] = calculate_rsi(df)
        df['StochRSI'] = calculate_stoch_rsi(df['RSI'])

        if df['RSI'].isnull().all() or df['StochRSI'].isnull().all():
            messagebox.showerror("خطا", "محاسبه اندیکاتورها ناموفق بود.")
            return

        latest_rsi = df['RSI'].iloc[-1]
        latest_stochrsi = df['StochRSI'].iloc[-1]

        if mode == "long":
            if latest_rsi < 30 and latest_stochrsi < 0.2:
                messagebox.showinfo("📈 سیگنال خرید", f"{symbol}\nسیگنال خرید صادر شده!")
            else:
                messagebox.showinfo("⛔️ بدون سیگنال خرید", f"{symbol}\nدر حال حاضر سیگنال خرید نداریم.")

        elif mode == "short":
            if latest_rsi > 70 and latest_stochrsi > 0.8:
                messagebox.showinfo("📉 سیگنال فروش", f"{symbol}\nسیگنال فروش (شورت) صادر شده!")
            else:
                messagebox.showinfo("⛔️ بدون سیگنال فروش", f"{symbol}\nدر حال حاضر سیگنال فروش نداریم.")

    except Exception as e:
        messagebox.showerror("خطا", f"خطا در پردازش داده:\n{str(e)}")

# رابط گرافیکی
root = tk.Tk()
root.title("📊 تحلیل رمزارز - RSI + Stoch RSI")
root.geometry("330x200")

tk.Label(root, text="نماد رمزارز (مثل: ADA, BTC, ETH)", font=("tahoma", 11)).pack(pady=10)
entry = tk.Entry(root, font=("tahoma", 12))
entry.pack()

btn_frame = tk.Frame(root)
btn_frame.pack(pady=20)

tk.Button(btn_frame, text="تحلیل لانگ", command=lambda: check_signal("long"), width=14).grid(row=0, column=0, padx=6)
tk.Button(btn_frame, text="تحلیل شورت", command=lambda: check_signal("short"), width=14).grid(row=0, column=1, padx=6)

root.mainloop()
