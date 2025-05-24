import requests
import pandas as pd
import time
import threading
from ta.trend import EMAIndicator, MACD
from ta.momentum import RSIIndicator
from playsound import playsound
from datetime import datetime
import tkinter as tk
from tkinter import scrolledtext
import concurrent.futures
from sklearn.linear_model import LinearRegression
import numpy as np
import ccxt
from xgboost import XGBClassifier
import datetime

# PARAMETRY
symbols = ['BTC', 'ETH', 'BNB', 'ADA', 'XRP', 'SOL', 'DOT', 'DOGE', 'LTC', 'AVAX', 'SHIB', 'MATIC', 'LINK', 'ALGO']
currency = 'USD'
interwal = '5'  # 5-minutowe świece
sl_pct = 0.0075
tp_pct = 0.025
log_file = 'logi.txt'

# Słownik do przechowywania danych historycznych i modeli
historical_data = {}
models = {}

# Funkcja do logowania
def loguj(tresc):
    with open(log_file, 'a') as f:
        f.write(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | {tresc}\n")

# Pobieranie danych historycznych (dużo świec)
def pobierz_dane(symbol):
    try:
        url = f'https://min-api.cryptocompare.com/data/v2/histominute?fsym={symbol}&tsym={currency}&limit=1000&aggregate={interwal}'
        response = requests.get(url)
        data = response.json()
        if 'Data' in data and 'Data' in data['Data']:
            df = pd.DataFrame(data['Data']['Data'])
            df['time'] = pd.to_datetime(df['time'], unit='s')
            df.set_index('time', inplace=True)
            return df
    except Exception as e:
        print(f"Błąd pobierania danych dla {symbol}: {e}")
    return None

def telegram_powiadomienie(tresc):
    token = '7076890997:AAHDNuuX3e9DOGhxRZ9-T0ylWh7eKjc87lc'  # Twój token
    chat_id = '-4977647861'  # Twój chat_id
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    params = {'chat_id': chat_id, 'text': tresc}
    requests.get(url, params=params)

# Funkcja trenująca model liniowy na danych historycznych (zamknięcia)
def trenuj_model(df):
    lookback = len(df)
    if lookback < 10:
        return None
    X = np.array(range(lookback)).reshape(-1,1)
    y = df['close'].values
    model = LinearRegression()
    model.fit(X,y)
    return model

# Funkcja aktualizująca dane i model dla danego symbolu
def aktualizuj_model(symbol):
    global historical_data, models
    df_new = pobierz_dane(symbol)
    if df_new is None:
        return None, None
    # Jeśli brak danych historycznych, ustaw na nowe
    if symbol not in historical_data:
        historical_data[symbol] = df_new
    else:
        # Dokładamy tylko nowe dane (unikalne indeksy)
        df_old = historical_data[symbol]
        df_combined = pd.concat([df_old, df_new])
        df_combined = df_combined[~df_combined.index.duplicated(keep='last')]
        historical_data[symbol] = df_combined.sort_index()
    # Trenujemy model na aktualnych danych
    model = trenuj_model(historical_data[symbol])
    models[symbol] = model
    return historical_data[symbol], model

# Analiza i generowanie sygnału na podstawie modelu i wskaźników
def analizuj(symbol):
    df = historical_data.get(symbol)
    model = models.get(symbol)
    if df is None or model is None:
        return 'NONE', f"{symbol} | Brak danych/modelu."

    # Obliczenia wskaźników
    df['rsi'] = RSIIndicator(df['close'], 14).rsi()
    df['ema20'] = EMAIndicator(df['close'], 20).ema_indicator()
    df['ema50'] = EMAIndicator(df['close'], 50).ema_indicator()
    macd_indicator = MACD(df['close'])
    df['macd'] = macd_indicator.macd()
    df['macd_signal'] = macd_indicator.macd_signal()
    df['volume_mean'] = df['volumefrom'].rolling(20).mean()
    df['vol_ratio'] = df['volumefrom'] / df['volume_mean']

    df.dropna(inplace=True)
    if len(df) < 20:
        return 'NONE', f"{symbol} | Za mało danych po czyszczeniu."

    ostatnia = df.iloc[-1]
    last_price = ostatnia['close']

    # Prognoza regresyjna (do info, nie do decyzji)
    lookback = len(df)
    pred_price = model.predict(np.array([[lookback]]))[0]
    pred_change = (pred_price - last_price) / last_price
    tp_price = last_price * (1 + tp_pct)
    sl_price = last_price * (1 - sl_pct)

    # Przygotowanie danych do klasyfikacji 3-klasowej
    df['future_close'] = df['close'].shift(-3)
    zmiana = df['future_close'] / df['close'] - 1

    def klasyfikuj(zm):
        if zm > 0.01:
            return 2  # BUY (LONG)
        elif zm < -0.01:
            return 0  # SELL (SHORT)
        else:
            return 1  # HOLD

    df['target'] = zmiana.apply(klasyfikuj)

    features = ['rsi', 'ema20', 'ema50', 'macd', 'vol_ratio']
    X = df[features]
    y = df['target']

    model_XG = XGBClassifier(
        n_estimators=100,
        eval_metric='mlogloss',
        objective='multi:softmax',
        num_class=3,
        base_score=0.5
    )
    model_XG.fit(X, y)

    # Predykcja najnowszego wiersza
    X_pred = ostatnia[features].values.reshape(1, -1)
    pred_klasa = model_XG.predict(X_pred)[0]

    if pred_klasa == 2:  # BUY
        komunikat = f"{symbol} | SYGNAŁ BUY (LONG) | Cena: {last_price:.2f} | TP: {tp_price:.2f} | SL: {sl_price:.2f} | AI_pred_change: {pred_change:.3%}"
        telegram_powiadomienie(komunikat)
        return 'BUY', komunikat

    elif pred_klasa == 0:  # SELL
        komunikat = f"{symbol} | SYGNAŁ SELL (SHORT) | Cena: {last_price:.2f} | TP: {tp_price:.2f} | SL: {sl_price:.2f} | AI_pred_change: {pred_change:.3%}"
        telegram_powiadomienie(komunikat)
        return 'SELL', komunikat

    else:  # HOLD
        komunikat = f"{symbol} | BRAK SYGNAŁU (HOLD) | Cena: {last_price:.2f} | AI_pred_change: {pred_change:.3%}"
        return 'HOLD', komunikat


# Równoległe aktualizowanie modeli i generowanie sygnałów
def run_bot_parallel():
    results = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        futures = {executor.submit(aktualizuj_model, sym): sym for sym in symbols}
        for future in concurrent.futures.as_completed(futures):
            sym = futures[future]
            df, model = future.result()
            if df is not None and model is not None:
                sygnal, komunikat = analizuj(sym)
                results.append((sygnal, komunikat))
            else:
                results.append(('NONE', f"❌ Nie udało się pobrać danych/modelu dla {sym}"))
    return results

# GUI i logika bota
class TradingBotGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Trading Bot Crypto - Uczący się")
        self.root.geometry("750x550")
        self.root.config(bg="#222222")

        self.text_area = scrolledtext.ScrolledText(root, width=80, height=25, bg="#1e1e1e", fg="white", font=("Consolas", 10))
        self.text_area.pack(padx=10, pady=10)

        self.start_button = tk.Button(root, text="Start", command=self.start_bot, bg="#4caf50", fg="white", font=("Arial", 12, "bold"))
        self.start_button.pack(pady=5)

        self.stop_button = tk.Button(root, text="Stop", command=self.stop_bot, bg="#f44336", fg="white", font=("Arial", 12, "bold"))
        self.stop_button.pack(pady=5)
        self.stop_button.config(state=tk.DISABLED)

        self.running = False

    def log(self, text, color="white"):
        self.text_area.configure(state='normal')
        self.text_area.insert(tk.END, text + "\n")
        self.text_area.tag_add(text, "end-1l linestart", "end-1l lineend")
        self.text_area.tag_config(text, foreground=color)
        self.text_area.see(tk.END)
        self.text_area.configure(state='disabled')

    def run_bot(self):
        self.running = True
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        while self.running:
            results = run_bot_parallel()
            for sygnal, komunikat in results:
                if sygnal == 'BUY':
                    self.log(komunikat, color="lime")
                    loguj(komunikat)
                    try:
                        playsound('ping.mp3')
                    except:
                        pass
                elif sygnal == 'SELL':
                    self.log(komunikat, color="red")
                    loguj(komunikat)
                    try:
                        playsound('ping.mp3')
                    except:
                        pass
                else:
                    self.log(komunikat, color="gray")
            time.sleep(5*60)  # 5 minut

    def start_bot(self):
        self.thread = threading.Thread(target=self.run_bot, daemon=True)
        self.thread.start()

    def stop_bot(self):
        self.running = False
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.log("Bot zatrzymany.", color="yellow")

if __name__ == "__main__":
    models = {}
    features_dict = {}
    last_train_time = 0
    root = tk.Tk()
    app = TradingBotGUI(root)
    root.mainloop()
