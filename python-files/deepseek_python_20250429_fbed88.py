import pandas as pd
import numpy as np
from collections import Counter
from tkinter import *
from tkinter import ttk, filedialog, messagebox
from keras.models import Sequential
from keras.layers import LSTM, Dense, Dropout
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import os
from tqdm import tqdm

class LotteryPredictorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Lottery Numbers Predictor v1.0")
        self.root.geometry("900x700")
        self.root.resizable(True, True)
        
        # Variables
        self.file_path = StringVar()
        self.results_text = StringVar(value="Результаты появятся здесь...")
        self.progress = DoubleVar()
        self.model_trained = False
        self.model = None
        self.data = None
        self.freq = None
        
        # Create UI
        self.create_widgets()
        
    def create_widgets(self):
        # File Selection Frame
        file_frame = LabelFrame(self.root, text="Выбор файла с данными", padx=5, pady=5)
        file_frame.pack(fill="x", padx=10, pady=5)
        
        Entry(file_frame, textvariable=self.file_path, width=70).pack(side=LEFT, padx=5)
        Button(file_frame, text="Обзор...", command=self.browse_file).pack(side=LEFT, padx=5)
        
        # Analysis Frame
        analysis_frame = LabelFrame(self.root, text="Анализ данных", padx=5, pady=5)
        analysis_frame.pack(fill="x", padx=10, pady=5)
        
        Button(analysis_frame, text="Анализировать данные", command=self.analyze_data).pack(side=LEFT, padx=5)
        Button(analysis_frame, text="Показать график частот", command=self.show_frequency_chart).pack(side=LEFT, padx=5)
        
        # Model Frame
        model_frame = LabelFrame(self.root, text="Модель прогнозирования", padx=5, pady=5)
        model_frame.pack(fill="x", padx=10, pady=5)
        
        Button(model_frame, text="Обучить модель LSTM", command=self.train_model).pack(side=LEFT, padx=5)
        Button(model_frame, text="Предсказать числа", command=self.predict_numbers).pack(side=LEFT, padx=5)
        
        # Progress Bar
        progress_frame = Frame(self.root)
        progress_frame.pack(fill="x", padx=10, pady=5)
        
        Label(progress_frame, text="Прогресс:").pack(side=LEFT)
        ttk.Progressbar(progress_frame, variable=self.progress, maximum=100).pack(side=LEFT, fill="x", expand=True, padx=5)
        
        # Results Frame
        results_frame = LabelFrame(self.root, text="Результаты", padx=5, pady=5)
        results_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        self.results_textbox = Text(results_frame, wrap=WORD)
        self.results_textbox.pack(fill="both", expand=True, padx=5, pady=5)
        
        scrollbar = Scrollbar(self.results_textbox)
        scrollbar.pack(side=RIGHT, fill=Y)
        self.results_textbox.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.results_textbox.yview)
        
        # Status Bar
        self.status_bar = Label(self.root, text="Готов к работе", bd=1, relief=SUNKEN, anchor=W)
        self.status_bar.pack(side=BOTTOM, fill=X)
    
    def browse_file(self):
        filename = filedialog.askopenfilename(
            title="Выберите файл с историческими данными",
            filetypes=(("CSV files", "*.csv"), ("All files", "*.*"))
        )
        if filename:
            self.file_path.set(filename)
            self.update_status(f"Выбран файл: {filename}")
    
    def analyze_data(self):
        if not self.file_path.get():
            messagebox.showerror("Ошибка", "Сначала выберите файл с данными")
            return
            
        try:
            self.update_status("Анализ данных...")
            self.progress.set(10)
            
            # Load data
            self.data = pd.read_csv(self.file_path.get(), header=None)
            numbers = self.data.iloc[:, 3:11].values.flatten()
            
            # Frequency analysis
            self.freq = Counter(numbers)
            total = sum(self.freq.values())
            freq_percent = {k: v/total*100 for k, v in self.freq.items()}
            
            # Show results
            result = "=== Анализ частотности чисел ===\n"
            for num, count in sorted(self.freq.items()):
                result += f"Число {num}: {count} раз ({freq_percent[num]:.1f}%)\n"
            
            top_10 = self.freq.most_common(10)
            result += "\nТоп-10 самых частых чисел:\n"
            for num, count in top_10:
                result += f"{num} ({count} раз)\n"
            
            self.results_textbox.delete(1.0, END)
            self.results_textbox.insert(END, result)
            self.progress.set(100)
            self.update_status("Анализ завершен")
            
        except Exception as e:
            self.update_status("Ошибка анализа данных")
            messagebox.showerror("Ошибка", f"Не удалось проанализировать данные:\n{str(e)}")
    
    def show_frequency_chart(self):
        if not self.freq:
            messagebox.showerror("Ошибка", "Сначала выполните анализ данных")
            return
            
        # Create chart
        nums = sorted(self.freq.keys())
        counts = [self.freq[num] for num in nums]
        
        fig, ax = plt.subplots(figsize=(10, 5))
        ax.bar(nums, counts)
        ax.set_title('Частота выпадения чисел')
        ax.set_xlabel('Число')
        ax.set_ylabel('Количество выпадений')
        ax.grid(True)
        
        # Show in new window
        chart_window = Toplevel(self.root)
        chart_window.title("График частотности чисел")
        
        canvas = FigureCanvasTkAgg(fig, master=chart_window)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=BOTH, expand=True)
    
    def train_model(self):
        if not self.data:
            messagebox.showerror("Ошибка", "Сначала загрузите и проанализируйте данные")
            return
            
        try:
            self.update_status("Обучение модели LSTM...")
            self.progress.set(0)
            
            # Prepare data
            X = self.data.iloc[:, 3:11].values / 20.0  # Normalize
            seq_length = 10
            
            X_seq, y_seq = [], []
            for i in tqdm(range(len(X) - seq_length), desc="Подготовка данных"):
                X_seq.append(X[i:i+seq_length])
                y_seq.append(X[i+seq_length])
                self.progress.set(i / (len(X) - seq_length) * 50)
            
            X_seq, y_seq = np.array(X_seq), np.array(y_seq)
            
            # Build model
            self.model = Sequential([
                LSTM(128, return_sequences=True, input_shape=(seq_length, 8)),
                Dropout(0.2),
                LSTM(64),
                Dense(8, activation='sigmoid')
            ])
            
            self.model.compile(optimizer='adam', loss='mse')
            
            # Train model
            history = self.model.fit(
                X_seq, y_seq, 
                epochs=50, 
                batch_size=32, 
                verbose=0,
                callbacks=[TqdmCallback(verbose=1)]
            )
            
            self.progress.set(100)
            self.model_trained = True
            self.update_status("Модель обучена успешно")
            self.results_textbox.insert(END, "\n\n=== Модель LSTM обучена ===\n")
            
        except Exception as e:
            self.update_status("Ошибка обучения модели")
            messagebox.showerror("Ошибка", f"Не удалось обучить модель:\n{str(e)}")
    
    def predict_numbers(self):
        if not self.model_trained or not self.freq:
            messagebox.showerror("Ошибка", "Сначала обучите модель и проанализируйте данные")
            return
            
        try:
            self.update_status("Генерация предсказаний...")
            self.progress.set(0)
            
            # 1. Get top frequent numbers
            top_10 = [num for num, _ in self.freq.most_common(10)]
            
            # 2. Monte Carlo prediction
            def monte_carlo_prediction(freq, n=8, trials=1000):
                nums, counts = zip(*freq.items())
                probs = np.array(counts) / sum(counts)
                best_combo = None
                max_score = -1

                for _ in range(trials):
                    combo = np.random.choice(nums, size=n, p=probs, replace=False)
                    score = sum(freq[num] for num in combo)
                    if score > max_score:
                        max_score = score
                        best_combo = combo
                    self.progress.set(_ / trials * 30)

                return sorted(best_combo)

            mc_pred = monte_carlo_prediction(self.freq)
            
            # 3. LSTM prediction
            X = self.data.iloc[:, 3:11].values / 20.0
            seq_length = 10
            last_seq = X[-seq_length:].reshape(1, seq_length, 8)
            lstm_pred = (self.model.predict(last_seq).flatten() * 20).astype(int)
            lstm_pred = np.clip(lstm_pred, 1, 20)  # Ensure numbers are between 1-20
            
            # 4. Find cold numbers (not appeared in last 50 draws)
            last_50 = self.data.tail(50).iloc[:, 3:11].values.flatten()
            cold_numbers = [num for num in range(1, 21) if num not in last_50]
            
            # 5. Hybrid prediction
            hybrid_set = set(mc_pred) | set(lstm_pred) | set(top_10)
            if cold_numbers:
                hybrid_set.update(cold_numbers[:2])  # Add 2 coldest numbers
            
            # Rank by frequency
            hybrid_ranked = sorted(hybrid_set, key=lambda x: -self.freq[x])[:8]
            
            # Show results
            result = "\n=== Результаты предсказания ===\n"
            result += f"Топ-10 частых чисел: {top_10}\n"
            result += f"Монте-Карло: {mc_pred}\n"
            result += f"LSTM: {sorted(lstm_pred)}\n"
            if cold_numbers:
                result += f"Холодные числа: {cold_numbers[:5]} (выбраны {cold_numbers[:2]})\n"
            result += f"\nГИБРИДНОЕ ПРЕДСКАЗАНИЕ: {hybrid_ranked}\n"
            
            self.results_textbox.insert(END, result)
            self.progress.set(100)
            self.update_status("Предсказание завершено")
            
        except Exception as e:
            self.update_status("Ошибка предсказания")
            messagebox.showerror("Ошибка", f"Не удалось сгенерировать предсказание:\n{str(e)}")
    
    def update_status(self, message):
        self.status_bar.config(text=message)
        self.root.update_idletasks()

class TqdmCallback:
    def __init__(self, verbose=1):
        self.verbose = verbose
        
    def on_epoch_end(self, epoch, logs=None):
        if self.verbose:
            print(f"Epoch {epoch+1}, Loss: {logs['loss']:.4f}")

if __name__ == "__main__":
    root = Tk()
    app = LotteryPredictorApp(root)
    root.mainloop()