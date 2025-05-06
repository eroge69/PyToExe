import customtkinter as ctk
from customtkinter import *
from PIL import Image, ImageTk
import tkinter as tk
from tkinter import filedialog
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from pytorch_forecasting import TemporalFusionTransformer, TimeSeriesDataSet
import pytorch_lightning as pl
from pytorch_lightning.callbacks import EarlyStopping, Callback
import torch
import torch.nn as nn
import torch.nn.functional as F
from torchmetrics import Metric
import traceback
import numpy as np
from datetime import datetime, timedelta
from scipy.signal import savgol_filter
import random
import warnings
from scipy.stats import linregress
from statsmodels.tsa.seasonal import STL
from scipy.optimize import curve_fit
import time

#-----------------------------------------------------------
# Global Variables
#-----------------------------------------------------------
df = None
app = None
MAX_MMR = 2500
MIN_MMR = 0
PREDICTION_LENGTH = 180
TARGET_INCREASE_PCT = 0.15

#-----------------------------------------------------------
# UI Color Scheme
#-----------------------------------------------------------
PRIMARY_COLOR = "#2E3440"
SECONDARY_COLOR = "#3B4252"
ACCENT_COLOR = "#88C0D0"
HIGHLIGHT_COLOR = "#A3BE8C"
WARNING_COLOR = "#EBCB8B"
ERROR_COLOR = "#D08770"
TEXT_COLOR = "#ECEFF4"
BG_COLOR = "#1E1E2E"
OVERLAY_COLOR = "#1A1A1A"

#-----------------------------------------------------------
# Fonts
#-----------------------------------------------------------
TITLE_FONT = ("Segoe UI", 24, "bold")
HEADER_FONT = ("Segoe UI", 14)
BUTTON_FONT = ("Segoe UI", 12)
STATUS_FONT = ("Segoe UI", 10)
TIP_FONT = ("Segoe UI", 11, "italic")
DISCLAIMER_FONT = ("Segoe UI", 9)

#-----------------------------------------------------------
# Tips List
#-----------------------------------------------------------
INSPIRATIONAL_TIPS = [
    "Focus on one skill improvement at a time - mastery comes from focused practice.",
    "Review your replays to identify patterns in both wins and losses.",
    "Consistency beats intensity - regular practice trumps sporadic marathon sessions.",
    "The best players focus on their own improvement, not just their rank.",
    "Every loss is a lesson - analyze what went wrong without frustration.",
    "Quality over quantity - 1 hour of focused practice > 3 hours of distracted play.",
    "Warm up before competitive matches - it makes a difference!",
    "Take breaks between sessions - fresh mind equals better performance.",
    "Find a training partner at a similar skill level to push each other.",
    "Watch professional players in your position to learn new techniques.",
    "Confidence comes from preparation - the more you practice, the less you doubt.",
    "Small daily improvements lead to massive long-term gains.",
    "Focus on the process, not just the outcome - good habits create good results.",
    "Mindset matters - approach each game as an opportunity to learn.",
    "The difference between good and great is often just persistence.",
    "Record your gameplay to spot mistakes you don't notice in real-time.",
    "Master the fundamentals before advanced techniques - they never go out of style.",
    "Play to improve, not just to win - the rank will follow naturally.",
    "Identify your weakest areas and target them specifically.",
    "Stay hydrated and take care of your physical health - it affects performance.",
    "Learn from losses but don't dwell on them - focus on the next opportunity.",
    "Develop a pre-game routine to get in the right mindset.",
    "Communicate effectively with teammates - it's a team game after all.",
    "Vary your training to prevent burnout and plateaus.",
    "Set specific, measurable goals for each session.",
    "Analyze opponent strategies to anticipate their moves.",
    "Practice under pressure to simulate real match conditions.",
    "Stay positive - tilt only makes performance worse.",
    "Take responsibility for losses - there's always something you could have done better.",
    "Celebrate small victories and progress along the way."
]

#-----------------------------------------------------------
# Progress Callback Class
#-----------------------------------------------------------
class ProgressCallback(Callback):
    def __init__(self, progress_bar, progress_label):
        super().__init__()
        self.progress_bar = progress_bar
        self.progress_label = progress_label
    
    def on_train_start(self, trainer, pl_module):
        if app is not None:
            self.progress_bar.set(0)
            self.progress_label.configure(text="Training: 0%")
            app.update()
    
    def on_train_epoch_end(self, trainer, pl_module):
        if self.progress_bar and self.progress_label and app is not None:
            progress = trainer.current_epoch / trainer.max_epochs
            self.progress_bar.set(progress)
            progress_text = f"Training: {int(progress * 100)}%"
            self.progress_label.configure(text=progress_text)
            app.update()
    
    def on_train_end(self, trainer, pl_module):
        if self.progress_bar and self.progress_label and app is not None:
            self.progress_bar.set(1.0)
            self.progress_label.configure(text="Training complete!")
            app.update()

#-----------------------------------------------------------
# Enhanced MSE Loss Class
#-----------------------------------------------------------
class EnhancedMSELoss(Metric):
    def __init__(self):
        super().__init__()
        self.add_state("sum_loss", default=torch.tensor(0.0), dist_reduce_fx="sum")
        self.add_state("count", default=torch.tensor(0.0), dist_reduce_fx="sum")
        
    def update(self, predictions, targets):
        if isinstance(targets, tuple):
            targets = targets[0]
            
        if hasattr(predictions, 'prediction'):
            predictions = predictions.prediction
            
        predictions = predictions.squeeze(-1)
        targets = targets.squeeze(-1)
        
        mse_loss = F.mse_loss(predictions, targets, reduction='sum')
        pred_diff = predictions[1:] - predictions[:-1]
        target_diff = targets[1:] - targets[:-1]
        trend_loss = F.mse_loss(pred_diff, target_diff, reduction='sum')
        pred_fft = torch.fft.fft(predictions - predictions.mean())
        target_fft = torch.fft.fft(targets - targets.mean())
        pattern_loss = F.mse_loss(torch.abs(pred_fft), torch.abs(target_fft), reduction='sum')
        loss = mse_loss + 0.3 * trend_loss + 0.2 * pattern_loss
        self.sum_loss += loss
        self.count += targets.numel()
    
    def compute(self):
        return self.sum_loss / self.count

#-----------------------------------------------------------
# Enhanced TFT Class
#-----------------------------------------------------------
class EnhancedTFT(pl.LightningModule):
    def __init__(self, model: TemporalFusionTransformer):
        super().__init__()
        self.model = model
        self.loss_fn = EnhancedMSELoss()
        self.save_hyperparameters(ignore=['model'])
        self.automatic_optimization = True

    def forward(self, x):
        if isinstance(x, dict):
            expected_features = len(self.model.hparams.x_reals)
            
            if 'encoder_cont' in x:
                encoder_features = x['encoder_cont'].shape[-1]
                if encoder_features < expected_features:
                    padding = torch.zeros(*x['encoder_cont'].shape[:-1], 
                                        expected_features - encoder_features,
                                        device=x['encoder_cont'].device)
                    x['encoder_cont'] = torch.cat([x['encoder_cont'], padding], dim=-1)
                elif encoder_features > expected_features:
                    x['encoder_cont'] = x['encoder_cont'][..., :expected_features]
            
            if 'decoder_cont' in x:
                decoder_features = x['decoder_cont'].shape[-1]
                if decoder_features < expected_features:
                    padding = torch.zeros(*x['decoder_cont'].shape[:-1], 
                                        expected_features - decoder_features,
                                        device=x['decoder_cont'].device)
                    x['decoder_cont'] = torch.cat([x['decoder_cont'], padding], dim=-1)
                elif decoder_features > expected_features:
                    x['decoder_cont'] = x['decoder_cont'][..., :expected_features]
            
            if 'encoder_lengths' not in x:
                x['encoder_lengths'] = torch.tensor([x['encoder_cont'].shape[1]], 
                                                  device=x['encoder_cont'].device)
            if 'decoder_lengths' not in x:
                x['decoder_lengths'] = torch.tensor([x['decoder_cont'].shape[1]], 
                                                  device=x['encoder_cont'].device)
        
        return self.model(x)

    def training_step(self, batch, batch_idx):
        x, y = batch
        output = self.forward(x)
        loss = self.loss_fn(output, y)
        self.log("train_loss", loss, prog_bar=True, sync_dist=True)
        return loss

    def validation_step(self, batch, batch_idx):
        x, y = batch
        output = self.forward(x)
        loss = self.loss_fn(output, y)
        self.log("val_loss", loss, prog_bar=True, sync_dist=True)
        return loss

    def predict_step(self, batch, batch_idx, dataloader_idx=0):
        x, y = batch
        output = self.forward(x)
        return output.prediction if hasattr(output, 'prediction') else output

    def configure_optimizers(self):
        optimizer = torch.optim.AdamW(self.parameters(), lr=0.03, weight_decay=1e-3)
        scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(
            optimizer, patience=3, factor=0.5, verbose=False)
        return {
            'optimizer': optimizer,
            'lr_scheduler': scheduler,
            'monitor': 'val_loss'
        }

#-----------------------------------------------------------
# Loading Overlay Class
#-----------------------------------------------------------
class LoadingOverlay(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.configure(fg_color=OVERLAY_COLOR, corner_radius=0)
        self.place(relx=0, rely=0, relwidth=1, relheight=1)
        self.lift()
        
        self.content_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.content_frame.pack(expand=True, padx=20, pady=20)
        
        self.label = ctk.CTkLabel(
            self.content_frame,
            text="Processing Prediction...",
            font=TITLE_FONT,
            text_color=TEXT_COLOR
        )
        self.label.pack(pady=(0, 20))
        
        self.progress = ctk.CTkProgressBar(
            self.content_frame,
            mode='indeterminate',
            fg_color=PRIMARY_COLOR,
            progress_color=ACCENT_COLOR,
            width=300,
            height=10
        )
        self.progress.pack(pady=(0, 20))
        self.progress.start()
        
        self.tip_label = ctk.CTkLabel(
            self.content_frame,
            text="",
            font=TIP_FONT,
            text_color=TEXT_COLOR,
            wraplength=700,
            justify="center"
        )
        self.tip_label.pack(pady=(20, 0))
        
        self.alpha = 0
        self.current_tip = ""
        self.fade_in()
        self.show_random_tip()
    
    def fade_in(self):
        if not self.winfo_exists():
            return
        self.alpha = min(1.0, self.alpha + 0.05)
        self._set_alpha(self.alpha)
        if self.alpha < 1.0:
            self.after(20, self.fade_in)
    
    def fade_out(self):
        if not self.winfo_exists():
            return
        self.alpha = max(0.0, self.alpha - 0.05)
        self._set_alpha(self.alpha)
        if self.alpha > 0.0:
            self.after(20, self.fade_out)
        else:
            self.progress.stop()
            self.destroy()
    
    def _set_alpha(self, alpha):
        r = int(OVERLAY_COLOR[1:3], 16)
        g = int(OVERLAY_COLOR[3:5], 16)
        b = int(OVERLAY_COLOR[5:7], 16)
        blended_r = int(r * alpha + int(BG_COLOR[1:3], 16) * (1 - alpha))
        blended_g = int(g * alpha + int(BG_COLOR[3:5], 16) * (1 - alpha))
        blended_b = int(b * alpha + int(BG_COLOR[5:7], 16) * (1 - alpha))
        blended_color = f"#{blended_r:02x}{blended_g:02x}{blended_b:02x}"
        self.configure(fg_color=blended_color)
    
    def show_random_tip(self):
        if not self.winfo_exists():
            return
            
        tips = INSPIRATIONAL_TIPS
        if not self.current_tip or self.current_tip not in tips:
            next_tip = random.choice(tips)
        else:
            current_index = tips.index(self.current_tip)
            next_index = (current_index + 1) % len(tips)
            next_tip = tips[next_index]
        
        self.current_tip = next_tip
        self.tip_label.configure(text=next_tip)
        self.after(8000, self.show_random_tip)

#-----------------------------------------------------------
# GUI Creation
#-----------------------------------------------------------
def create_gui():
    global app, progress_bar, progress_label, status_label, viz_frame, viz_canvas, tip_label, main_frame
    
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")
    
    app = ctk.CTk()
    app.geometry("1100x800")
    app.title("PROJECT: Rocket")
    app.configure(fg_color=BG_COLOR)
    
    main_frame = ctk.CTkFrame(app, fg_color=PRIMARY_COLOR)
    main_frame.pack(fill="both", expand=True, padx=10, pady=10)  # Reduced padding here
    
    header_frame = ctk.CTkFrame(main_frame, fg_color=PRIMARY_COLOR)
    header_frame.pack(fill="x", padx=10, pady=(10, 5))  # Reduced padding
    
    title_label = ctk.CTkLabel(
        header_frame,
        text="PROJECT: Rocket",
        font=TITLE_FONT,
        text_color=ACCENT_COLOR
    )
    title_label.pack(pady=(0, 5))  # Reduced padding
    
    subtitle_label = ctk.CTkLabel(
        header_frame,
        text="Predict future MMR trends based on historical data",
        font=HEADER_FONT,
        text_color=TEXT_COLOR
    )
    subtitle_label.pack()
    
    content_frame = ctk.CTkFrame(main_frame, fg_color=PRIMARY_COLOR)
    content_frame.pack(fill="both", expand=True, padx=10, pady=5)  # Reduced padding
    
    control_frame = ctk.CTkFrame(content_frame, fg_color=SECONDARY_COLOR, width=250)
    control_frame.pack(side="left", fill="y", padx=(0, 5), pady=5)  # Reduced padding
    control_frame.pack_propagate(False)
    
    import_frame = ctk.CTkFrame(control_frame, fg_color=SECONDARY_COLOR)
    import_frame.pack(fill="x", padx=5, pady=5)  # Reduced padding
    
    import_header = ctk.CTkLabel(
        import_frame,
        text="DATA IMPORT",
        font=HEADER_FONT,
        text_color=ACCENT_COLOR
    )
    import_header.pack(anchor="w", pady=(0, 5))  # Reduced padding
    
    import_btn = ctk.CTkButton(
        import_frame,
        text="Import CSV File",
        command=import_csv,
        font=BUTTON_FONT,
        fg_color=ACCENT_COLOR,
        hover_color="#81A1C1",
        text_color=PRIMARY_COLOR
    )
    import_btn.pack(fill="x", pady=5)
    
    predict_frame = ctk.CTkFrame(control_frame, fg_color=SECONDARY_COLOR)
    predict_frame.pack(fill="x", padx=5, pady=5)  # Reduced padding
    
    predict_header = ctk.CTkLabel(
        predict_frame,
        text="PREDICTION",
        font=HEADER_FONT,
        text_color=ACCENT_COLOR
    )
    predict_header.pack(anchor="w", pady=(0, 5))  # Reduced padding
    
    predict_btn = ctk.CTkButton(
        predict_frame,
        text="Run Prediction",
        command=pred_button_pressed,
        font=BUTTON_FONT,
        fg_color=HIGHLIGHT_COLOR,
        hover_color="#8FBCBB",
        text_color=PRIMARY_COLOR
    )
    predict_btn.pack(fill="x", pady=5)
    
    status_frame = ctk.CTkFrame(control_frame, fg_color=SECONDARY_COLOR)
    status_frame.pack(fill="both", expand=True, padx=5, pady=5)  # Reduced padding
    
    status_header = ctk.CTkLabel(
        status_frame,
        text="STATUS",
        font=HEADER_FONT,
        text_color=ACCENT_COLOR
    )
    status_header.pack(anchor="w", pady=(0, 5))  # Reduced padding
    
    progress_label = ctk.CTkLabel(
        status_frame,
        text="Ready",
        font=STATUS_FONT,
        text_color=TEXT_COLOR
    )
    progress_label.pack(anchor="w", pady=(0, 5))
    
    progress_bar = ctk.CTkProgressBar(
        status_frame,
        orientation="horizontal",
        mode="determinate",
        fg_color=PRIMARY_COLOR,
        progress_color=ACCENT_COLOR,
        height=8
    )
    progress_bar.set(0)
    progress_bar.pack(fill="x", pady=5)
    
    status_label = ctk.CTkLabel(
        status_frame,
        text="No data loaded",
        font=STATUS_FONT,
        text_color=TEXT_COLOR,
        wraplength=230,
        justify="left"
    )
    status_label.pack(anchor="w", pady=(5, 0), fill="x")
    
    right_frame = ctk.CTkFrame(content_frame, fg_color=SECONDARY_COLOR)
    right_frame.pack(side="right", fill="both", expand=True, pady=5)  # Reduced padding
    
    viz_frame = ctk.CTkFrame(right_frame, fg_color=SECONDARY_COLOR)
    viz_frame.pack(fill="both", expand=True, padx=5, pady=(5, 2))  # Reduced padding
    
    viz_header = ctk.CTkLabel(
        viz_frame,
        text="VISUALIZATION",
        font=HEADER_FONT,
        text_color=ACCENT_COLOR
    )
    viz_header.pack(anchor="w", padx=5, pady=(5, 2))  # Reduced padding
    
    viz_canvas = None
    
    tips_frame = ctk.CTkFrame(right_frame, fg_color=SECONDARY_COLOR, height=80)
    tips_frame.pack(fill="x", padx=5, pady=(2, 5))  # Reduced padding
    
    tips_header = ctk.CTkLabel(
        tips_frame,
        text="TRAINING TIP",
        font=HEADER_FONT,
        text_color=ACCENT_COLOR
    )
    tips_header.pack(anchor="w", padx=5, pady=(2, 0))  # Reduced padding
    
    tip_label = ctk.CTkLabel(
        tips_frame,
        text="",
        font=TIP_FONT,
        text_color=TEXT_COLOR,
        wraplength=750,
        justify="left"
    )
    tip_label.pack(fill="x", padx=5, pady=(0, 2))  # Reduced padding
    
    footer_frame = ctk.CTkFrame(main_frame, fg_color=PRIMARY_COLOR, height=60)
    footer_frame.pack(fill="x", padx=5, pady=(2, 5))  # Reduced padding
    
    disclaimer_label = ctk.CTkLabel(
        footer_frame,
        text="This prediction is an estimate generated by machine learning and should not be taken as a guaranteed outcome. "
             "It is influenced by trends in your performance and assumes similar play continues. "
             "As performance and game dynamics change, prediction accuracy may vary — especially for longer forecast ranges.",
        font=DISCLAIMER_FONT,
        text_color=TEXT_COLOR,
        wraplength=1050,
        justify="left"
    )
    disclaimer_label.pack(side="left", padx=5, pady=2, fill="x", expand=True)  # Reduced padding
    
    quit_btn = ctk.CTkButton(
        footer_frame,
        text="Exit",
        command=quit_button_pressed,
        font=BUTTON_FONT,
        fg_color=ERROR_COLOR,
        hover_color="#BF616A",
        text_color=TEXT_COLOR,
        width=80
    )
    quit_btn.pack(side="right", padx=5)  # Reduced padding
    
    rotate_tips()
    
    return app

#-----------------------------------------------------------
# Helper Functions
#-----------------------------------------------------------
def rotate_tips():
    global tip_label
    if 'tip_label' not in globals():
        return
    
    current_tip = tip_label.cget("text")
    tips = INSPIRATIONAL_TIPS
    
    if not current_tip or current_tip not in tips:
        next_tip = random.choice(tips)
    else:
        current_index = tips.index(current_tip)
        next_index = (current_index + 1) % len(tips)
        next_tip = tips[next_index]
    
    tip_label.configure(text=next_tip)
    app.after(10000, rotate_tips)

def clear_viz_frame():
    global viz_canvas
    if viz_canvas is not None:
        viz_canvas.get_tk_widget().destroy()
        viz_canvas = None

def update_viz_frame(fig):
    global viz_canvas, viz_frame
    clear_viz_frame()
    viz_canvas = FigureCanvasTkAgg(fig, master=viz_frame)
    viz_canvas.draw()
    viz_canvas.get_tk_widget().pack(fill="both", expand=True, padx=5, pady=(0, 5))  # Reduced padding

#-----------------------------------------------------------
# Data Processing Functions
#-----------------------------------------------------------
def import_csv():
    global df, status_label, progress_label, progress_bar
    
    file_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
    if not file_path:
        return
    
    progress_bar.set(0)
    progress_label.configure(text="Processing...")
    status_label.configure(text=f"Loading file: {file_path.split('/')[-1]}", text_color=TEXT_COLOR)
    app.update()
    
    try:
        df = pd.read_csv(file_path)
        status_label.configure(text="CSV loaded successfully!", text_color=HIGHLIGHT_COLOR)
        
        df.columns = df.columns.str.strip()
        if len(df.columns) == 2:
            df.columns = ["ds", "y"]
        
        if 'ds' not in df.columns or 'y' not in df.columns:
            status_label.configure(
                text="Error: CSV needs 'ds' (date) and 'y' (value) columns",
                text_color=ERROR_COLOR
            )
            df = None
            return

        df['ds'] = pd.to_datetime(df['ds'], errors='coerce')
        if df['ds'].isna().sum() > 0:
            df = df.dropna(subset=['ds'])
            status_label.configure(
                text="Warning: Fixed invalid dates in the dataset",
                text_color=WARNING_COLOR
            )
            
        progress_label.configure(text="Ready")
        progress_bar.set(1.0)
            
    except Exception as e:
        status_label.configure(
            text=f"Error loading CSV: {str(e)}",
            text_color=ERROR_COLOR
        )
        progress_label.configure(text="Error")
        progress_bar.set(0)
        df = None

def extract_date_features(data):
    data['month'] = data['ds'].dt.month
    data['day'] = data['ds'].dt.day
    data['day_of_week'] = data['ds'].dt.dayofweek
    data['day_of_year'] = data['ds'].dt.dayofyear
    data['week_of_year'] = data['ds'].dt.isocalendar().week.astype(int)
    data['quarter'] = data['ds'].dt.quarter
    data['is_weekend'] = data['ds'].dt.dayofweek.isin([5,6]).astype(int)
    data['is_month_start'] = data['ds'].dt.is_month_start.astype(int)
    data['is_month_end'] = data['ds'].dt.is_month_end.astype(int)
    return data

def decompose_timeseries(data):
    try:
        stl = STL(data['y'].values, period=7, robust=True)
        res = stl.fit()
        
        return {
            'trend': res.trend,
            'seasonal': res.seasonal,
            'residual': res.resid,
            'trend_strength': max(0, min(1, 1 - (np.var(res.resid) / np.var(res.trend + res.resid)))),
            'seasonal_strength': max(0, min(1, 1 - (np.var(res.resid) / np.var(res.seasonal + res.resid))))
        }
    except:
        trend = savgol_filter(data['y'].values, window_length=min(31, len(data)), polyorder=2)
        seasonal = data.groupby(data['ds'].dt.dayofweek)['y'].mean().values
        seasonal = np.tile(seasonal, len(data) // 7 + 1)[:len(data)]
        residual = data['y'].values - trend - seasonal
        
        return {
            'trend': trend,
            'seasonal': seasonal,
            'residual': residual,
            'trend_strength': 0.7,
            'seasonal_strength': 0.5
        }

def analyze_trend_characteristics(data):
    y = data['y'].values
    x = np.arange(len(y))
    
    slope, intercept, _, _, _ = linregress(x, y)
    total_change = (y[-1] - y[0]) / y[0] if y[0] != 0 else 0
    rolling_std = pd.Series(y).rolling(window=30, min_periods=1).std().values
    
    if len(y) > 30:
        recent_slope = linregress(np.arange(30), y[-30:])[0]
    else:
        recent_slope = slope
    
    daily_changes = np.diff(y)
    max_daily_change = np.percentile(np.abs(daily_changes), 95) if len(daily_changes) > 0 else 0.01 * np.mean(y)
    avg_daily_change = np.mean(daily_changes) if len(daily_changes) > 0 else 0
    
    if len(y) >= 7:
        recent_trend = linregress(np.arange(7), y[-7:])[0]
    else:
        recent_trend = slope
    
    hist_volatility = np.std(y)
    hist_avg_daily_change = np.mean(np.abs(daily_changes)) if len(daily_changes) > 0 else 0.01 * np.mean(y)
    hist_max_daily_change = np.max(np.abs(daily_changes)) if len(daily_changes) > 0 else 0.02 * np.mean(y)
    
    if recent_trend < 0:
        min_reasonable_mmr = max(MIN_MMR, np.percentile(y, 25))
        days_to_min = (min_reasonable_mmr - y[-1]) / recent_trend if recent_trend != 0 else PREDICTION_LENGTH
        reversal_point = min(PREDICTION_LENGTH, max(14, int(days_to_min * 0.7)))
    else:
        reversal_point = PREDICTION_LENGTH
    
    return {
        'slope': slope,
        'intercept': intercept,
        'total_change': total_change,
        'avg_volatility': np.mean(rolling_std),
        'trend_type': 'growing' if total_change > 0.1 else 'declining' if total_change < -0.1 else 'stable',
        'recent_slope': recent_slope,
        'max_daily_change': max_daily_change,
        'avg_daily_change': avg_daily_change,
        'daily_change_std': np.std(daily_changes) if len(daily_changes) > 0 else 0.01 * np.mean(y),
        'recent_trend': recent_trend,
        'reversal_point': reversal_point,
        'hist_volatility': hist_volatility,
        'hist_avg_daily_change': hist_avg_daily_change,
        'hist_max_daily_change': hist_max_daily_change
    }

def calculate_historical_components(data):
    decomposition = decompose_timeseries(data)
    values = data['y'].values
    
    weekly_pattern = np.array([decomposition['seasonal'][data['ds'].dt.dayofweek == i].mean() 
                             for i in range(7)])
    monthly_pattern = np.array([decomposition['seasonal'][data['ds'].dt.month == i].mean() 
                              for i in range(1, 13)])
    
    trend = decomposition['trend']
    noise = decomposition['residual']
    volatility = np.std(noise)
    
    if len(trend) >= 14:
        short_term_trend = linregress(np.arange(14), trend[-14:])[0]
    else:
        short_term_trend = linregress(np.arange(len(trend)), trend)[0] if len(trend) > 1 else 0
    
    long_term_trend = linregress(np.arange(len(trend)), trend)[0] if len(trend) > 1 else 0
    
    if len(trend) >= 7:
        momentum = np.mean(np.diff(trend[-7:]))
    else:
        momentum = np.mean(np.diff(trend)) if len(trend) > 1 else 0
    
    return {
        'weekly_pattern': weekly_pattern,
        'monthly_pattern': monthly_pattern,
        'trend': trend,
        'noise': noise,
        'volatility': volatility,
        'last_value': values[-1],
        'last_trend': trend[-1] - trend[-2] if len(trend) > 1 else 0,
        'combined_trend': max(0.1, (short_term_trend * 0.7 + long_term_trend * 0.3)) * decomposition['trend_strength'],
        'recent_values': values[-30:] if len(values) >= 30 else values,
        'trend_strength': decomposition['trend_strength'],
        'seasonal_strength': decomposition['seasonal_strength'],
        'momentum': momentum
    }

def enforce_net_increase(predictions, historical_data, target_pct_increase):
    hist = calculate_historical_components(historical_data)
    current_value = hist['last_value']
    target_value = current_value * (1 + target_pct_increase)
    
    required_daily_increase = (target_value - current_value) / len(predictions)
    baseline = np.linspace(current_value, target_value, len(predictions))
    adjusted = predictions * 0.7 + baseline * 0.3
    
    if adjusted[-1] < target_value:
        adjustment_factor = target_value / adjusted[-1]
        adjusted = adjusted * adjustment_factor
    
    fluctuations = np.random.normal(0, hist['volatility'] * 0.5, len(adjusted))
    adjusted = adjusted + fluctuations
    adjusted = np.maximum(adjusted, MIN_MMR)
    adjusted = np.minimum(adjusted, MAX_MMR)
    
    window_size = min(31, len(adjusted))
    if window_size % 2 == 0:
        window_size -= 1
    if window_size > 3:
        adjusted = savgol_filter(adjusted, window_size, 2)
    
    return adjusted

def generate_realistic_predictions(raw_predictions, historical_data):
    hist = calculate_historical_components(historical_data)
    trend_analysis = analyze_trend_characteristics(historical_data)
    last_value = historical_data['y'].iloc[-1]
    
    if len(raw_predictions) > PREDICTION_LENGTH:
        preds = np.array(raw_predictions[:PREDICTION_LENGTH]).flatten()
    elif len(raw_predictions) < PREDICTION_LENGTH:
        if trend_analysis['trend_type'] == 'stable':
            extension = np.full(PREDICTION_LENGTH - len(raw_predictions), np.mean(hist['trend'][-30:]))
        else:
            extension = np.linspace(
                raw_predictions[-1],
                raw_predictions[-1] + trend_analysis['slope'] * (PREDICTION_LENGTH - len(raw_predictions)),
                PREDICTION_LENGTH - len(raw_predictions)
            )
        preds = np.concatenate([raw_predictions, extension])
    else:
        preds = np.array(raw_predictions).flatten()
    
    preds[0] = last_value
    
    hist_volatility = trend_analysis['hist_volatility']
    hist_avg_change = trend_analysis['hist_avg_daily_change']
    hist_max_change = trend_analysis['hist_max_daily_change']
    
    max_daily_change = min(hist_max_change * 1.2, 50)
    avg_daily_change = hist_avg_change
    daily_change_std = max(1, hist_volatility * 0.5)
    recent_trend = trend_analysis['recent_trend']
    reversal_point = trend_analysis['reversal_point']
    
    for i in range(1, len(preds)):
        day_of_week = (historical_data['ds'].iloc[-1].dayofweek + i) % 7
        month = (historical_data['ds'].iloc[-1].month + (i // 30)) % 12
        month = month if month != 0 else 12
        
        if recent_trend < 0:
            if i < reversal_point:
                trend_effect = recent_trend * (1 - (i / (reversal_point * 1.5)))
            else:
                progress = min(1, (i - reversal_point) / (PREDICTION_LENGTH - reversal_point))
                trend_effect = -recent_trend * 0.5 * progress
        else:
            trend_effect = recent_trend * max(0.5, 1 - (i / (PREDICTION_LENGTH * 2)))
            
        base_change = min(0.01, max(-0.01, trend_effect / hist['last_value'])) if hist['last_value'] != 0 else 0
        seasonality = (hist['weekly_pattern'][day_of_week] * 0.2 + 
                      hist['monthly_pattern'][month-1] * 0.05) * hist['seasonal_strength']
        momentum_effect = hist['momentum'] * (0.3 + 0.02 * np.random.normal())
        variation = daily_change_std * 0.5 * np.random.normal(0, 0.5)
        
        daily_change = (base_change * hist['last_value'] + 
                       0.2 * seasonality + 
                       0.1 * momentum_effect + 
                       variation)
        
        daily_change = max(-max_daily_change, min(max_daily_change, daily_change))
        
        if i > 1:
            prev_change = preds[i-1] - preds[i-2]
            daily_change = 0.7 * daily_change + 0.3 * prev_change
            
        new_val = preds[i-1] + daily_change
        preds[i] = np.clip(new_val, MIN_MMR, MAX_MMR)
    
    smoothing_factor = max(0.3, min(0.7, 1 - (hist_volatility / 100)))
    if trend_analysis['trend_type'] == 'stable':
        window_size = min(int(31 * smoothing_factor), len(preds))
        polyorder = 2
    else:
        window_size = min(int(15 * smoothing_factor), len(preds))
        polyorder = 3
    
    if window_size % 2 == 0:
        window_size -= 1
    if window_size > 3:
        preds = savgol_filter(preds, window_size, polyorder)
    
    preds = preds * (1 + (np.random.normal(0, 0.001 * (hist_volatility / 50), len(preds)) if hist_volatility > 0 else 1))
    preds = enforce_net_increase(preds, historical_data, TARGET_INCREASE_PCT)
    preds[0] = last_value
    
    if len(preds) > 5:
        recent_history = historical_data['y'].values[-7:]
        if len(recent_history) > 1:
            hist_trend = np.mean(np.diff(recent_history))
            for i in range(1, min(6, len(preds))):
                preds[i] = preds[i-1] + (0.8 * hist_trend + 0.2 * (preds[i] - preds[i-1]))
    
    return np.clip(preds, MIN_MMR, MAX_MMR)

def prepare_future_dataset(training, last_date, last_time_idx):
    future_dates = pd.date_range(
        start=last_date + timedelta(days=1),
        periods=PREDICTION_LENGTH,
        freq='D'
    )
    
    future_df = pd.DataFrame({
        'ds': future_dates,
        'y': np.zeros(PREDICTION_LENGTH),
        'time_idx': np.arange(last_time_idx + 1, last_time_idx + 1 + PREDICTION_LENGTH),
        'constant_id': "series_1",
    })
    
    future_df = extract_date_features(future_df)
    
    known_reals = ["time_idx", "month", "day", "day_of_week", "day_of_year", 
                  "week_of_year", "quarter", "is_weekend", "is_month_start", "is_month_end"]
    
    return TimeSeriesDataSet(
        future_df,
        time_idx="time_idx",
        target="y",
        group_ids=["constant_id"],
        min_encoder_length=60,
        max_encoder_length=120,
        min_prediction_length=1,
        max_prediction_length=PREDICTION_LENGTH,
        time_varying_known_reals=known_reals,
        time_varying_unknown_reals=["y"],
        static_categoricals=["constant_id"],
        add_relative_time_idx=True,
        add_target_scales=True,
        target_normalizer=None,
        allow_missing_timesteps=True,
        predict_mode=True
    )

#-----------------------------------------------------------
# Main Button Functions
#-----------------------------------------------------------
def pred_button_pressed():
    global df, progress_bar, progress_label, status_label, main_frame
    
    if df is None:
        status_label.configure(
            text="Error: Please import a CSV file first",
            text_color=ERROR_COLOR
        )
        return
    
    loading_overlay = LoadingOverlay(main_frame)
    
    try:
        progress_bar.set(0)
        progress_label.configure(text="Initializing...")
        status_label.configure(text="Starting prediction process", text_color=TEXT_COLOR)
        app.update()
        
        df = df.sort_values('ds')
        df['ds'] = pd.to_datetime(df['ds'])
        df = df.dropna(subset=['ds', 'y'])
        
        if len(df) < 60:
            raise ValueError(f"Need at least 60 data points, got {len(df)}")
        
        df = extract_date_features(df)
        last_date = df['ds'].max()
        last_value = df['y'].iloc[-1]
        min_date = df['ds'].min()
        
        df['time_idx'] = (df['ds'] - min_date).dt.days
        df['constant_id'] = "series_1"
        
        features = ["time_idx", "month", "day", "day_of_week", "day_of_year", 
                  "week_of_year", "quarter", "is_weekend", "is_month_start", "is_month_end"]
        
        training = TimeSeriesDataSet(
            df,
            time_idx="time_idx",
            target="y",
            group_ids=["constant_id"],
            min_encoder_length=60,
            max_encoder_length=120,
            min_prediction_length=1,
            max_prediction_length=PREDICTION_LENGTH,
            time_varying_known_reals=features,
            time_varying_unknown_reals=["y"],
            static_categoricals=["constant_id"],
            add_relative_time_idx=True,
            add_target_scales=True,
            target_normalizer=None,
            allow_missing_timesteps=True
        )
        
        model = TemporalFusionTransformer.from_dataset(
            training,
            learning_rate=0.03,
            hidden_size=32,
            attention_head_size=1,
            dropout=0.1,
            hidden_continuous_size=16,
            output_size=1,
            loss=EnhancedMSELoss(),
            lstm_layers=2,
            reduce_on_plateau_patience=3
        )
        
        early_stop_callback = EarlyStopping(
            monitor="val_loss",
            min_delta=1e-3,
            patience=7,
            verbose=False,
            mode="min"
        )
        
        progress_callback = ProgressCallback(progress_bar, progress_label)
        
        trainer = pl.Trainer(
            max_epochs=30,
            accelerator='auto',
            callbacks=[early_stop_callback, progress_callback],
            enable_progress_bar=False,
            logger=False,
            gradient_clip_val=0.5,
            limit_train_batches=1.0,
            limit_val_batches=1.0
        )
        
        val_size = max(int(len(df) * 0.2), 30)
        train_df = df.iloc[:-val_size]
        val_df = df.iloc[-val_size:]
        
        train_ds = TimeSeriesDataSet.from_dataset(training, train_df)
        val_ds = TimeSeriesDataSet.from_dataset(training, val_df)
        
        train_loader = train_ds.to_dataloader(
            train=True, 
            batch_size=min(128, len(train_df)),
            num_workers=0,
            persistent_workers=False,
            pin_memory=True
        )
        val_loader = val_ds.to_dataloader(
            train=False, 
            batch_size=min(128, len(val_df)),
            num_workers=0,
            persistent_workers=False,
            pin_memory=True
        )
        
        tft = EnhancedTFT(model)
        trainer.fit(tft, train_loader, val_loader)
        
        future_ds = prepare_future_dataset(training, last_date, df['time_idx'].max())
        future_loader = future_ds.to_dataloader(batch_size=128, train=False, num_workers=0)
        
        raw_predictions = trainer.predict(tft, future_loader)
        
        if raw_predictions:
            pred_values = np.concatenate([p.cpu().numpy().flatten() for p in raw_predictions if p is not None])
            if len(pred_values) > PREDICTION_LENGTH:
                pred_values = pred_values[:PREDICTION_LENGTH]
            elif len(pred_values) < PREDICTION_LENGTH:
                trend_analysis = analyze_trend_characteristics(df)
                if trend_analysis['trend_type'] == 'stable':
                    extension = np.full(PREDICTION_LENGTH - len(pred_values), np.mean(df['y'].values[-30:]))
                else:
                    extension = np.linspace(
                        pred_values[-1],
                        pred_values[-1] + trend_analysis['slope'] * (PREDICTION_LENGTH - len(pred_values)),
                        PREDICTION_LENGTH - len(pred_values)
                    )
                pred_values = np.concatenate([pred_values, extension])
        else:
            trend_analysis = analyze_trend_characteristics(df)
            if trend_analysis['trend_type'] == 'stable':
                pred_values = np.full(PREDICTION_LENGTH, np.mean(df['y'].values[-30:]))
            else:
                pred_values = np.linspace(
                    df['y'].values[-1],
                    df['y'].values[-1] + trend_analysis['slope'] * PREDICTION_LENGTH,
                    PREDICTION_LENGTH
                )
        
        final_predictions = generate_realistic_predictions(pred_values, df)
        
        future_dates = pd.date_range(
            start=last_date + timedelta(days=1),
            periods=PREDICTION_LENGTH,
            freq='D'
        )
        
        if len(future_dates) != len(final_predictions):
            min_length = min(len(future_dates), len(final_predictions))
            future_dates = future_dates[:min_length]
            final_predictions = final_predictions[:min_length]
        
        fig = plt.figure(figsize=(10, 5))
        plt.plot(df['ds'], df['y'], 'b-', label='Historical MMR', linewidth=2, alpha=0.8)
        plt.plot(future_dates, final_predictions, 'r-', label='Predicted MMR', linewidth=2)
        plt.plot([df['ds'].iloc[-1], future_dates[0]], 
                [df['y'].iloc[-1], final_predictions[0]], 
                'r-', linewidth=2)
        plt.axvline(x=last_date, color='gray', linestyle='--', alpha=0.7, linewidth=1.5)
        
        target_value = last_value * (1 + TARGET_INCREASE_PCT)
        plt.axhline(y=target_value, color='green', linestyle='--', alpha=0.5, 
                   label=f'Target (+{TARGET_INCREASE_PCT*100:.0f}%)')
        
        plt.xlabel("Date", fontsize=10)
        plt.ylabel("MMR", fontsize=10)
        plt.title(f"MMR Prediction ({PREDICTION_LENGTH} Days Forecast)", fontsize=12, pad=10)
        plt.legend(fontsize=8, loc='upper left')
        plt.grid(True, linestyle='--', alpha=0.3)
        
        y_min = max(MIN_MMR, min(df['y'].min(), final_predictions.min()) * 0.95)
        y_max = min(MAX_MMR, max(df['y'].max(), final_predictions.max(), target_value) * 1.05)
        plt.ylim(y_min, y_max)
        
        plt.gcf().autofmt_xdate()
        plt.tight_layout()
        
        update_viz_frame(fig)
        
        status_label.configure(
            text="Prediction completed successfully!",
            text_color=HIGHLIGHT_COLOR
        )
        progress_label.configure(text="Complete", text_color=HIGHLIGHT_COLOR)
        progress_bar.set(1.0)

    except Exception as e:
        status_label.configure(
            text=f"Error during prediction: {str(e)}",
            text_color=ERROR_COLOR
        )
        progress_label.configure(text="Error", text_color=ERROR_COLOR)
        progress_bar.set(0)
        traceback.print_exc()
    finally:
        loading_overlay.fade_out()

def quit_button_pressed():
    global app
    if app is not None:
        app.quit()

#-----------------------------------------------------------
# Main Execution
#-----------------------------------------------------------
if __name__ == "__main__":
    app = create_gui()
    app.mainloop()