import MetaTrader5 as mt5
import pandas as pd
import numpy as np
import matplotlib
#matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
from scipy.stats import zscore
from scipy.signal import hilbert
import seaborn as sns
import mplfinance as mpf
from dtaidistance import dtw  # using fast DTW version
from joblib import Parallel, delayed  # for parallel processing
import time
import datetime

# برای بوق زدن در ویندوز می‌توانید خطوط زیر را در صورت نیاز از حالت توضیح خارج کنید:
# import winsound
# def beep(): winsound.Beep(1000, 500)  # فرکانس 1000 هرتز، مدت 500 میلی‌ثانیه

# بوق زدن برای سیستم‌های چندسکویی (به عنوان جایگزین، تنها صدای بوق چاپ می‌شود)
def beep():
    print('\a')


class PatternAnalyzer:
    def __init__(self, symbol, window_size=10, num_similar=5, pip_size=1):
        self.symbol = symbol
        self.window_size = window_size          # تعداد کندل‌های الگوی مادر
        self.num_similar = num_similar
        self.pip_size = pip_size                # اندازه پیت (pip) برای تبدیل اختلافات به واحد پیت
        self.indicators_config = {
            'CCI': {'period': 20},
            'DominantCycle': {'period': 20},
            'AmpEnv': {'period': 20, 'ratio': 0.05},
            'BB': {'period': 20, 'std_dev': 2},
            'ROC': {'period': 12},
            'Stochastic': {'k_period': 14, 'd_period': 3},
            'ZL_MACD': {'fast': 12, 'slow': 26, 'signal': 9},
            'ATR': {'period': 14},
            'RSI': {'period': 14},
            'ADX': {'period': 14}  # اضافه شدن اندیکاتور ADX
        }
    
    def connect_mt5(self):
        if not mt5.initialize():
            raise ConnectionError("Failed to connect to MetaTrader 5!")
        print("Connected to MetaTrader 5 successfully.")
    
    def get_historical_data(self, timeframe, num_bars=99000):
        """
        دریافت داده‌ها از MT5 و حذف کندل جاری (باز نشده) بر اساس تایم‌فریم.
        """
        rates = mt5.copy_rates_from_pos(self.symbol, timeframe, 0, num_bars)
        df = pd.DataFrame(rates)
        df['time'] = pd.to_datetime(df['time'], unit='s')
        df.set_index('time', inplace=True)
        df.sort_index(inplace=True)

        # نگاشت تایم‌فریم به ثانیه
        tf_to_seconds = {
            mt5.TIMEFRAME_M1: 60,
            mt5.TIMEFRAME_M5: 300,
            mt5.TIMEFRAME_M15: 900,
            mt5.TIMEFRAME_M30: 1800,
            mt5.TIMEFRAME_H1: 3600,
            mt5.TIMEFRAME_H4: 14400,
            mt5.TIMEFRAME_D1: 86400,
            mt5.TIMEFRAME_W1: 604800,
            mt5.TIMEFRAME_MN1: 2592000
        }
        period_seconds = tf_to_seconds.get(timeframe, None)
        if period_seconds is not None and not df.empty:
            current_time = pd.Timestamp.now(tz=df.index[-1].tz)
            last_open = df.index[-1]
            if current_time < last_open + pd.Timedelta(seconds=period_seconds):
                df = df.iloc[:-1]
        return df
    
    def _calculate_emas(self, df):
        periods = [3, 6, 9, 12, 48]
        for p in periods:
            df[f'EMA_{p}'] = df['close'].ewm(span=p, adjust=False).mean()
        return df
    
    def _normalize_window(self, window):
        base = window.iloc[0]['close']
        cols = ['close'] + [f'EMA_{p}' for p in [3, 6, 9, 12, 48]]
        norm_df = window[cols].copy()
        return (norm_df / base - 1) * 100

    def _extract_core_features(self, window):
        norm = self._normalize_window(window)
        close_vals = norm['close'].to_numpy()
        ema_diffs = np.column_stack([norm[f'EMA_{p}'].to_numpy() - close_vals for p in [3,6,9,12,48]])
        base_features = np.concatenate([close_vals, ema_diffs.flatten()])
        
        periods = np.array([3,6,9,12,48])
        last_emas_norm = np.array([norm[f'EMA_{p}'].iloc[-1] for p in periods])
        order_sorted = periods[np.argsort(-last_emas_norm)]
        ema_vals = np.array([window[f'EMA_{p}'].iloc[-1] for p in periods])
        ordered_ema_vals = ema_vals[np.argsort(-last_emas_norm)]
        distances = np.abs(np.diff(ordered_ema_vals)) / self.pip_size
        extra_features = np.concatenate([order_sorted.astype(np.float64), distances])
        
        return np.concatenate([base_features, extra_features])
    
    def _find_similar_mother_patterns(self, mother_df):
        latest_window = mother_df.iloc[-self.window_size:]
        self.latest_mother_features = self._extract_core_features(latest_window)
        
        indices = range(len(mother_df) - self.window_size - 20)
        historical = Parallel(n_jobs=-1)(
            delayed(self._extract_core_features)(mother_df.iloc[i : i+self.window_size])
            for i in indices
        )
        historical = list(zip(historical, indices))
        
        def compute_distance(feat, idx):
            return dtw.distance_fast(self.latest_mother_features.astype(np.float64),
                                      feat.astype(np.float64)), idx
        
        results = Parallel(n_jobs=-1)(
            delayed(compute_distance)(feat, idx) for feat, idx in historical
        )
        
        self.mother_similar_indices = sorted(results, key=lambda x: x[0])[:self.num_similar*2]
        return self.mother_similar_indices
    
    def _calculate_advanced_indicators(self, window):
        df = window.copy()
        high, low, close = df.high, df.low, df.close
        tp = (high + low + close) / 3
        cci_period = self.indicators_config['CCI']['period']
        cci = (tp - tp.rolling(cci_period).mean()) / (0.015 * tp.rolling(cci_period).std())
        diff = close.diff().fillna(0)
        cycle = np.arctan(diff.rolling(5).mean()) * 180/np.pi
        amp_env_period = self.indicators_config['AmpEnv']['period']
        amp_env_ratio = self.indicators_config['AmpEnv']['ratio']
        ma = close.rolling(amp_env_period).mean()
        amp_env_upper = ma * (1 + amp_env_ratio)
        amp_env_lower = ma * (1 - amp_env_ratio)
        bb_period = self.indicators_config['BB']['period']
        bb_std = self.indicators_config['BB']['std_dev']
        bb_middle = close.rolling(bb_period).mean()
        bb_std_dev = close.rolling(bb_period).std()
        bb_upper = bb_middle + (bb_std * bb_std_dev)
        bb_lower = bb_middle - (bb_std * bb_std_dev)
        roc_period = self.indicators_config['ROC']['period']
        roc = (close / close.shift(roc_period) - 1) * 100
        stoch_k = self.indicators_config['Stochastic']['k_period']
        stoch_d = self.indicators_config['Stochastic']['d_period']
        lowest_low = low.rolling(stoch_k).min()
        highest_high = high.rolling(stoch_k).max()
        stoch_K = ((close - lowest_low) / (highest_high - lowest_low)) * 100
        stoch_D = stoch_K.rolling(stoch_d).mean()
        macd_fast = self.indicators_config['ZL_MACD']['fast']
        macd_slow = self.indicators_config['ZL_MACD']['slow']
        macd_signal = self.indicators_config['ZL_MACD']['signal']
        ema_fast = close.ewm(span=macd_fast).mean()
        ema_slow = close.ewm(span=macd_slow).mean()
        zl_fast = 2 * ema_fast - ema_fast.ewm(span=macd_fast).mean()
        zl_slow = 2 * ema_slow - ema_slow.ewm(span=macd_slow).mean()
        macd_line = zl_fast - zl_slow
        signal_line = macd_line.ewm(span=macd_signal).mean()
        atr_period = self.indicators_config['ATR']['period']
        tr = np.maximum(high - low,
                      np.maximum(np.abs(high - close.shift()),
                               np.abs(low - close.shift())))
        atr = tr.rolling(atr_period).mean()
        rsi_period = self.indicators_config['RSI']['period']
        delta = close.diff()
        gain = delta.where(delta > 0, 0)
        loss = -delta.where(delta < 0, 0)
        avg_gain = gain.ewm(alpha=1/rsi_period, adjust=False).mean()
        avg_loss = loss.ewm(alpha=1/rsi_period, adjust=False).mean()
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        
        # محاسبه ADX
        adx_period = self.indicators_config['ADX']['period']
        up_move = high.diff()
        down_move = low.diff().abs()
        plus_dm = np.where((up_move > down_move) & (up_move > 0), up_move, 0.0)
        minus_dm = np.where((down_move > up_move) & (down_move > 0), down_move, 0.0)
        plus_di = 100 * (pd.Series(plus_dm).ewm(alpha=1/adx_period, min_periods=adx_period).mean() / atr)
        minus_di = 100 * (pd.Series(minus_dm).ewm(alpha=1/adx_period, min_periods=adx_period).mean() / atr)
        dx = 100 * np.abs(plus_di - minus_di) / (plus_di + minus_di)
        adx = pd.Series(dx).ewm(alpha=1/adx_period, min_periods=adx_period).mean()
        
        df_indicators = pd.DataFrame({
            'CCI': cci,
            'DominantCycle': cycle,
            'AmpEnv_Upper': amp_env_upper,
            'AmpEnv_Lower': amp_env_lower,
            'BB_Upper': bb_upper,
            'BB_Middle': bb_middle,
            'BB_Lower': bb_lower,
            'ROC': roc,
            'Stoch_K': stoch_K,
            'Stoch_D': stoch_D,
            'MACD': macd_line,
            'Signal': signal_line,
            'ATR': atr,
            'RSI': rsi,
            'ADX': adx
        })
        return df_indicators
    
    def _match_indicators(self, main_indicators, compare_indicators):
        scores = []
        for col in main_indicators.columns:
            try:
                main_col = main_indicators[col].dropna()
                compare_col = compare_indicators[col].dropna()
                main_col += np.random.normal(0, 1e-10, len(main_col))
                compare_col += np.random.normal(0, 1e-10, len(compare_col))
                if len(main_col) < 5 or len(compare_col) < 5:
                    continue
                min_len = min(len(main_col), len(compare_col))
                corr = np.corrcoef(main_col[-min_len:], compare_col[-min_len:])[0, 1]
                scores.append(corr if not np.isnan(corr) else 0)
            except Exception as e:
                print(f"خطا در پردازش {col}: {str(e)}")
                continue
        return np.mean(scores) if scores else 0
    
    def analyze_dual_pattern(self):
        self.connect_mt5()
        
        mother_timeframe = mt5.TIMEFRAME_H1
        mother_df = self.get_historical_data(mother_timeframe)
        mother_df = self._calculate_emas(mother_df)
        
        gen_timeframe = mt5.TIMEFRAME_M5
        gen_df = self.get_historical_data(gen_timeframe)
        gen_df = self._calculate_emas(gen_df)
        
        sample_mother_window = mother_df.iloc[-self.window_size:]
        sample_mother_indicators = self._calculate_advanced_indicators(sample_mother_window)
        
        latest_mother_start = sample_mother_window.index[0]
        latest_mother_end = sample_mother_window.index[-1]
        sample_gen_window = gen_df[(gen_df.index >= latest_mother_start) & (gen_df.index <= latest_mother_end)]
        sample_gen_indicators = self._calculate_advanced_indicators(sample_gen_window)
        
        mother_similar_indices = self._find_similar_mother_patterns(mother_df)
        
        def compute_match(idx):
            try:
                mother_window = mother_df.iloc[idx: idx+self.window_size]
                hist_mother_indicators = self._calculate_advanced_indicators(mother_window)
                mother_similarity = self._match_indicators(sample_mother_indicators, hist_mother_indicators)
                start_time = mother_window.index[0]
                end_time = mother_window.index[-1]
                hist_gen_window = gen_df[(gen_df.index >= start_time) & (gen_df.index <= end_time)]
                if len(hist_gen_window) < 5:
                    return None
                hist_gen_indicators = self._calculate_advanced_indicators(hist_gen_window)
                gen_similarity = self._match_indicators(sample_gen_indicators, hist_gen_indicators)
                if mother_similarity > 0.45 and gen_similarity > 0.45:
                    return ((mother_similarity + gen_similarity) / 2, idx)
                else:
                    return None
            except Exception as e:
                print(f"خطا در تحلیل الگوی ترکیبی در اندیس {idx}: {str(e)}")
                return None
        
        candidate_indices = [idx for (_, idx) in mother_similar_indices]
        final_matches = Parallel(n_jobs=-1)(
            delayed(compute_match)(idx) for idx in candidate_indices
        )
        final_matches = [res for res in final_matches if res is not None]
        self.final_results = sorted(final_matches, key=lambda x: -x[0])[:self.num_similar]
        print(f"تعداد {len(self.final_results)} الگوی مشابه ترکیبی (مادر و جنین) یافت شد.")
    
    # تابع جدید visualize_dual که تنها کندل‌های آینده را بدون خطوط عمودی رسم می‌کند
    def visualize_dual(self):
        sns.set_style("whitegrid")
        plt.rcParams.update({'font.size': 12})
        figures = []
        
        # دریافت داده‌های جنین با تایم‌فریم M5
        gen_timeframe = mt5.TIMEFRAME_M5
        gen_df = self.get_historical_data(gen_timeframe)
        gen_df = self._calculate_emas(gen_df)
        
        # تعداد کندل‌های آینده که می‌خواهیم نمایش دهیم (مثلاً 40 کندل)
        future_candles = 40  
        time_per_candle = pd.Timedelta(minutes=5)
        
        # دریافت داده‌های مادر برای گرفتن زمان پایان الگوی تشخیص داده شده
        mother_timeframe = mt5.TIMEFRAME_H1
        mother_df = self.get_historical_data(mother_timeframe)
        mother_df = self._calculate_emas(mother_df)
        
        for i, (score, m_idx) in enumerate(self.final_results):
            mother_window = mother_df.iloc[m_idx: m_idx+self.window_size]
            # زمان پایان الگوی مادر
            end_time = mother_window.index[-1]
            
            # انتخاب داده‌های جنین از پایان الگو به اندازه future_candles
            future_start = end_time
            future_end = future_start + future_candles * time_per_candle
            gen_future_window = gen_df[(gen_df.index >= future_start) & (gen_df.index <= future_end)]
            
            title_gen = f'Future Candles After Pattern {i+1} (Score: {score:.2f}) ' + self.symbol
            fig_gen, ax_gen = mpf.plot(
                gen_future_window,
                type='candle',
                style='charles',
                title=title_gen,
                returnfig=True
            )
            figures.append(fig_gen)
        
        plt.show()
        for fig in figures:
            plt.close(fig)


if __name__ == "__main__":
    # لیست نمادهایی که می‌خواهید برای‌شان الگو جستجو شود.
    # در این مثال ابتدا طلا (XAUUSD.n) را آنالیز می‌کنیم؛ اگر نتیجه‌ای نبود،
    # نمادهای بعدی را بررسی می‌کنیم.
    if not mt5.initialize():
        print("initialize() failed, error code =", mt5.last_error())
        quit()
    symbol="XAUUSD.n"
    tick = mt5.symbol_info_tick(symbol)
    server_time = datetime.datetime.fromtimestamp(tick.time)
    
    #print("زمان فعلی سرور:", server_time)
    # تعریف دستی تاریخ انقضا (مثلاً 1 مه 2025 ساعت 00:00:00)
    expiration_date = datetime.datetime(2025, 5, 26, 0, 0, 0)
    print("تاریخ انقضا وارد شده:", expiration_date)
    if server_time > expiration_date:
        print("دستیار ترید منقضی شده است. اجرای برنامه متوقف می‌شود.")
        mt5.shutdown()
        quit()
    else:
        remaining_time = expiration_date - server_time
        print("دستیار ترید فعال است. زمان باقی‌مانده:", remaining_time)

    symbols = ["NDXUSD.n", "DJIUSD.n", "XAUUSD.n","XAGUSD.n" ]
    #symbols = ["US100", "US30", "XAUUSD","XAGUSD" ]
    symbol_index = 0  # شروع از اولین نماد

    while True:
        current_symbol = symbols[symbol_index]
        print(f"Analyzing symbol: {current_symbol}")

        # ایجاد نمونه‌ای از PatternAnalyzer مخصوص نماد جاری
        analyzer = PatternAnalyzer(symbol=current_symbol, window_size=10, num_similar=5)

        try:
            analyzer.connect_mt5()
        except ConnectionError as ce:
            print("Connection error:", ce)
            # در صورت مشکل در اتصال، می‌توانید بخواهید از این نماد رد شوید
            symbol_index = (symbol_index + 1) % len(symbols)
            time.sleep(30)
            continue

        analyzer.analyze_dual_pattern()

        if analyzer.final_results:
            print(f"Found pattern for {current_symbol}!")
            beep()  # بوق در صورت یافتن الگوی جدید
            analyzer.visualize_dual()
            # اگر الگو پیدا شد، ممکن است بخواهید دوباره برای همان نماد ادامه دهید.
            # اگر می‌خواهید بعد از یافتن الگو، به نماد بعدی بروید:
            # symbol_index = (symbol_index + 1) % len(symbols)
            # یا ثابت بمانید.
            time.sleep(300)  # تا پایان کندل M5، به مدت 5 دقیقه انتظار می‌رود.
        else:
            print(f"No pattern found for {current_symbol}, switching to next symbol.")
            # در صورت عدم یافتن الگو، به نماد بعدی می‌رویم.
            symbol_index = (symbol_index + 1) % len(symbols)
            time.sleep(30)  # کمی وقفه‌ی کوتاه قبل از تلاش بعدی.

        mt5.shutdown()  # بستن ارتباط با MT5
