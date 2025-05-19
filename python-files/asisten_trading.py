import requests
import pandas as pd
import time
from ta.volatility import BollingerBands
from ta.trend import PSARIndicator, IchimokuIndicator
from ta.momentum import StochRSIIndicator

# Daftar aset yang ingin dianalisis
ASSETS = ['btc_idr', 'eth_idr', 'bnb_idr', 'sol_idr', 'ada_idr']  # bisa ditambah

def get_ohlcv(pair, limit=100):
    url = f'https://indodax.com/api/{pair}_chart?resolution=300&limit={limit}'
    try:
        response = requests.get(url).json()
        candles = response['c']
        df = pd.DataFrame(candles, columns=['time', 'open', 'high', 'low', 'close', 'volume'])
        df['close'] = df['close'].astype(float)
        df['high'] = df['high'].astype(float)
        df['low'] = df['low'].astype(float)
        df['time'] = pd.to_datetime(df['time'], unit='s')
        return df
    except:
        return None

def analyze_signals(df):
    signal_beli = 0
    signal_jual = 0
    keterangan = []

    # Bollinger Bands
    bb = BollingerBands(close=df['close'], window=20, window_dev=2)
    df['bb_upper'] = bb.bollinger_hband()
    df['bb_lower'] = bb.bollinger_lband()
    if df['close'].iloc[-1] < df['bb_lower'].iloc[-1]:
        signal_beli += 1
        keterangan.append("BB: BELI")
    elif df['close'].iloc[-1] > df['bb_upper'].iloc[-1]:
        signal_jual += 1
        keterangan.append("BB: JUAL")

    # Parabolic SAR
    psar = PSARIndicator(high=df['high'], low=df['low'], close=df['close'])
    df['psar'] = psar.psar()
    if df['close'].iloc[-1] > df['psar'].iloc[-1]:
        signal_beli += 1
        keterangan.append("PSAR: BELI")
    else:
        signal_jual += 1
        keterangan.append("PSAR: JUAL")

    # Ichimoku
    ichi = IchimokuIndicator(high=df['high'], low=df['low'])
    df['tenkan'] = ichi.ichimoku_conversion_line()
    df['kijun'] = ichi.ichimoku_base_line()
    if df['tenkan'].iloc[-1] > df['kijun'].iloc[-1]:
        signal_beli += 1
        keterangan.append("Ichimoku: BELI")
    else:
        signal_jual += 1
        keterangan.append("Ichimoku: JUAL")

    # Stochastic RSI
    stoch = StochRSIIndicator(close=df['close'])
    df['stoch_k'] = stoch.stochrsi_k()
    df['stoch_d'] = stoch.stochrsi_d()
    if df['stoch_k'].iloc[-1] < 20 and df['stoch_d'].iloc[-1] < 20:
        signal_beli += 1
        keterangan.append("Stoch RSI: BELI")
    elif df['stoch_k'].iloc[-1] > 80 and df['stoch_d'].iloc[-1] > 80:
        signal_jual += 1
        keterangan.append("Stoch RSI: JUAL")
    else:
        keterangan.append("Stoch RSI: Netral")

    # Final Decision
    if signal_beli >= 3:
        return "📈 BELI", keterangan
    elif signal_jual >= 3:
        return "📉 JUAL", keterangan
    else:
        return None, keterangan

def main():
    print("=== ASISTEN TRADING INDIKATOR MULTI ASET ===\n")
    while True:
        print(f"⏱️ Mengecek sinyal... {time.strftime('%Y-%m-%d %H:%M:%S')}")
        for asset in ASSETS:
            df = get_ohlcv(asset)
            if df is None or len(df) < 50:
                print(f"⚠️ Gagal mengambil data: {asset}")
                continue

            signal, info = analyze_signals(df)
            if signal:
                print(f"\n✅ {asset.upper()} - {signal}")
                for i in info:
                    print(f"   - {i}")
        print("\nTunggu 5 menit...\n")
        time.sleep(300)  # tiap 5 menit

if __name__ == "__main__":
    main()
