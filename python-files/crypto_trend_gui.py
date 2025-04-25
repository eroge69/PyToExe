
import tkinter as tk
from tkinter import ttk
import requests
import threading
import time
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import pandas as pd
import numpy as np

def fetch_ohlcv():
    url = "https://www.okx.com/api/v5/market/candles?instId=XRP-USDT&bar=1m&limit=100"
    response = requests.get(url)
    data = response.json()
    ohlcv = data['data']
    df = pd.DataFrame(ohlcv, columns=["timestamp", "open", "high", "low", "close", "volume", "volccy"])
    df = df.iloc[::-1].reset_index(drop=True)
    df['close'] = df['close'].astype(float)
    return df

def calculate_indicators(df):
    df['MA20'] = df['close'].rolling(window=20).mean()
    df['RSI'] = compute_rsi(df['close'], 14)
    df['MACD'], df['Signal'] = compute_macd(df['close'])
    return df

def compute_rsi(series, period):
    delta = series.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

def compute_macd(series):
    exp1 = series.ewm(span=12, adjust=False).mean()
    exp2 = series.ewm(span=26, adjust=False).mean()
    macd = exp1 - exp2
    signal = macd.ewm(span=9, adjust=False).mean()
    return macd, signal

def detect_trend(df):
    if df['close'].iloc[-1] > df['MA20'].iloc[-1] and df['RSI'].iloc[-1] > 50 and df['MACD'].iloc[-1] > df['Signal'].iloc[-1]:
        return "UPTREND"
    elif df['close'].iloc[-1] < df['MA20'].iloc[-1] and df['RSI'].iloc[-1] < 50 and df['MACD'].iloc[-1] < df['Signal'].iloc[-1]:
        return "DOWNTREND"
    else:
        return "SIDEWAYS"

class TrendApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Crypto Trend Detector - XRP/USDT")

        self.label = ttk.Label(root, text="Fetching data...", font=("Arial", 16))
        self.label.pack(pady=10)

        self.figure, self.ax = plt.subplots(figsize=(6, 3), dpi=100)
        self.canvas = FigureCanvasTkAgg(self.figure, master=root)
        self.canvas.get_tk_widget().pack()

        self.update_data()

    def update_data(self):
        df = fetch_ohlcv()
        df = calculate_indicators(df)
        trend = detect_trend(df)

        self.label.config(text=f"Current Trend: {trend}", foreground=("green" if trend=="UPTREND" else "red" if trend=="DOWNTREND" else "orange"))

        self.ax.clear()
        self.ax.plot(df['close'], label='Close Price')
        self.ax.plot(df['MA20'], label='MA20')
        self.ax.set_title("XRP/USDT Price Chart")
        self.ax.legend()
        self.canvas.draw()

        self.root.after(60000, self.update_data)  # update every 60 seconds

if __name__ == '__main__':
    root = tk.Tk()
    app = TrendApp(root)
    root.mainloop()
