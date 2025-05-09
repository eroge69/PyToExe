import pandas as pd
from binance.client import Client
import matplotlib.pyplot as plt

# Nepotrebuješ API kľúče na získanie historických dát
client = Client()

symbol = 'BTCUSDT'
interval = Client.KLINE_INTERVAL_1HOUR  # 1h sviečky
lookback = "60 days ago UTC"            # 60 dní späť

# Stiahnutie historických dát
klines = client.get_historical_klines(symbol, interval, lookback)
df = pd.DataFrame(klines, columns=[
    'time', 'open', 'high', 'low', 'close', 'volume',
    'close_time', 'quote_asset_volume', 'number_of_trades',
    'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume', 'ignore'
])
df['close'] = df['close'].astype(float)
df['time'] = pd.to_datetime(df['time'], unit='ms')

# Parametre stratégie
buy_threshold = -0.02    # -2%
sell_threshold = 0.015   # +1.5%
quantity = 0.001         # 0.001 BTC

# Inicializácia premenných
usdt_balance = 1000      # Začiatočný kapitál v USDT
btc_balance = 0
last_trade_price = None
trade_log = []

for i in range(1, len(df)):
    price = df.iloc[i]['close']
    prev_price = df.iloc[i-1]['close']

    # Prvý nákup (ak ešte nemáme BTC)
    if btc_balance == 0 and (price < prev_price * (1 + buy_threshold)):
        btc_balance = usdt_balance / price
        usdt_balance = 0
        last_trade_price = price
        trade_log.append((df.iloc[i]['time'], 'BUY', price, btc_balance, usdt_balance))
    # Predaj (ak máme BTC)
    elif btc_balance > 0 and (price > last_trade_price * (1 + sell_threshold)):
        usdt_balance = btc_balance * price
        btc_balance = 0
        last_trade_price = price
        trade_log.append((df.iloc[i]['time'], 'SELL', price, btc_balance, usdt_balance))

# Ak držíme BTC na konci, prepočítame na USDT
final_balance = usdt_balance + btc_balance * df.iloc[-1]['close']

print(f"Počiatočný kapitál: 1000 USDT")
print(f"Konečný stav: {final_balance:.2f} USDT")
print(f"Počet obchodov: {len(trade_log)}")
for t in trade_log:
    print(f"{t[0]} - {t[1]} za cenu {t[2]}")

# Voliteľne: vykresliť graf
plt.figure(figsize=(12,6))
plt.plot(df['time'], df['close'], label='BTC/USDT')
for t in trade_log:
    color = 'g' if t[1] == 'BUY' else 'r'
    plt.scatter(t[0], t[2], color=color, marker='^' if t[1]=='BUY' else 'v')
plt.title('Backtest stratégie na BTC/USDT')
plt.xlabel('Čas')
plt.ylabel('Cena')
plt.legend()
plt.show()
