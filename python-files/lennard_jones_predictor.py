# Lennard-Jones Parameters Prediction for Polymers and Copolymers
# Final Professional Version - May 2025
# Developed by: Mohammad Ehsan Ozeyri

import numpy as np
import pandas as pd
from xgboost import XGBRegressor
from sklearn.preprocessing import StandardScaler

# -----------------------------------------------
# معادله لنارد-جونز
def lj_phi(r, A, B):
    return B / r**9 - A / (8 * r**3)

def calculate_r0_and_phi0(A, B):
    r0 = (3 * B / A) ** (1/6)
    phi0 = lj_phi(r0, A, B)
    return r0, phi0

# -----------------------------------------------
class PolymerPredictor:
    def __init__(self):
        self.model_A = XGBRegressor(n_estimators=300, learning_rate=0.05, random_state=42)
        self.model_B = XGBRegressor(n_estimators=300, learning_rate=0.05, random_state=42)
        self.scaler_X = StandardScaler()
        self.scaler_A = StandardScaler()
        self.scaler_B = StandardScaler()
        self.feature_names = ['Mw', 'Density', 'Tg', 'Tm']

    def preprocess(self, X):
        """مدیریت None در Tm"""
        X = X.copy()
        X['Tm'] = X['Tm'].fillna(-999)
        return X

    def fit(self, X, y_A, y_B):
        X = self.preprocess(X)
        X_scaled = self.scaler_X.fit_transform(X)
        y_scaled_A = self.scaler_A.fit_transform(y_A.values.reshape(-1,1)).ravel()
        y_scaled_B = self.scaler_B.fit_transform(y_B.values.reshape(-1,1)).ravel()
        self.model_A.fit(X_scaled, y_scaled_A)
        self.model_B.fit(X_scaled, y_scaled_B)

    def predict(self, Mw, Density, Tg, Tm):
        X_new = pd.DataFrame([[Mw, Density, Tg, Tm]], columns=self.feature_names)
        X_new = self.preprocess(X_new)
        X_scaled = self.scaler_X.transform(X_new)

        A_scaled_pred = self.model_A.predict(X_scaled)
        B_scaled_pred = self.model_B.predict(X_scaled)

        A_pred = self.scaler_A.inverse_transform(A_scaled_pred.reshape(-1,1)).ravel()[0]
        B_pred = self.scaler_B.inverse_transform(B_scaled_pred.reshape(-1,1)).ravel()[0]

        r0, phi0 = calculate_r0_and_phi0(A_pred, B_pred)
        return A_pred, B_pred, r0, phi0

# -----------------------------------------------
def load_training_data():
    """داده‌های آموزشی واقعی‌تر"""
    data = {
        'Polymer': ['Polyethylene', 'Polystyrene', 'PMMA', 'Nylon 6', 'PVC', 'PET', 'Polycarbonate', 'PTFE', 'POM', 'Polypropylene'],
        'Mw': [28000, 220000, 120000, 15000, 45000, 31000, 45000, 100000, 30000, 40000],
        'Density': [0.92, 1.05, 1.18, 1.14, 1.38, 1.39, 1.20, 2.2, 1.41, 0.91],
        'Tg': [-125, 100, 105, 50, 80, 70, 150, 115, -60, -10],
        'Tm': [135, None, None, 220, 210, 265, None, 327, 175, 160],
        'A': [5500, 8800, 4700, 6000, 7200, 7500, 8700, 9000, 6500, 5800],
        'B': [320, 440, 300, 370, 400, 430, 460, 480, 350, 310]
    }
    return pd.DataFrame(data)

# -----------------------------------------------
def get_copolymer_features():
    """گرفتن ویژگی‌های کوپلیمر بر اساس نسبت وزنی"""
    print("➔ لطفاً ویژگی‌های پلیمر اول را وارد کنید:")
    Mw1 = float(input(" جرم مولکولی Mw1 (g/mol): "))
    Density1 = float(input(" چگالی Density1 (g/cm³): "))
    Tg1 = float(input(" دمای گذار شیشه‌ای Tg1 (°C): "))
    Tm1_input = input(" دمای ذوب Tm1 (°C) (در صورت نداشتن Enter بزنید): ")
    Tm1 = float(Tm1_input) if Tm1_input.strip() else None
    weight1 = float(input(" نسبت وزنی پلیمر اول (مثلا 70 برای 70%): "))

    print("\n➔ لطفاً ویژگی‌های پلیمر دوم را وارد کنید:")
    Mw2 = float(input(" جرم مولکولی Mw2 (g/mol): "))
    Density2 = float(input(" چگالی Density2 (g/cm³): "))
    Tg2 = float(input(" دمای گذار شیشه‌ای Tg2 (°C): "))
    Tm2_input = input(" دمای ذوب Tm2 (°C) (در صورت نداشتن Enter بزنید): ")
    Tm2 = float(Tm2_input) if Tm2_input.strip() else None
    weight2 = float(input(" نسبت وزنی پلیمر دوم (مثلا 30 برای 30%): "))

    w1 = weight1 / (weight1 + weight2)
    w2 = weight2 / (weight1 + weight2)

    Mw_mix = w1 * Mw1 + w2 * Mw2
    Density_mix = w1 * Density1 + w2 * Density2
    Tg_mix = w1 * Tg1 + w2 * Tg2

    if Tm1 is None and Tm2 is None:
        Tm_mix = None
    elif Tm1 is None:
        Tm_mix = Tm2
    elif Tm2 is None:
        Tm_mix = Tm1
    else:
        Tm_mix = w1 * Tm1 + w2 * Tm2

    return Mw_mix, Density_mix, Tg_mix, Tm_mix

# -----------------------------------------------
if __name__ == "__main__":
    print("✅ آموزش مدل روی دیتای پلیمرها در حال انجام...")

    # آموزش مدل
    data = load_training_data()
    predictor = PolymerPredictor()
    predictor.fit(
        data[['Mw', 'Density', 'Tg', 'Tm']],
        data['A'],
        data['B']
    )

    print("✅ آموزش کامل شد!\n")
    print("➔ نوع ماده را انتخاب کنید:")
    print("1 - پلیمر ساده")
    print("2 - کوپلیمر (ترکیب دو پلیمر)")

    choice = input("انتخاب (1 یا 2): ").strip()

    if choice == "1":
        mw = float(input(" جرم مولکولی Mw (g/mol): "))
        density = float(input(" چگالی (g/cm³): "))
        Tg = float(input(" دمای گذار شیشه‌ای Tg (°C): "))
        Tm_input = input(" دمای ذوب Tm (°C) (در صورت نداشتن Enter بزنید): ")
        Tm = float(Tm_input) if Tm_input.strip() else None

    elif choice == "2":
        mw, density, Tg, Tm = get_copolymer_features()
    else:
        print("❌ انتخاب نامعتبر! برنامه خاتمه یافت.")
        exit()

    # پیش‌بینی ضرایب
    A_pred, B_pred, r0, phi0 = predictor.predict(mw, density, Tg, Tm)

    print("\n🎯 نتایج پیش‌بینی شده:")
    print(f"A = {A_pred:.2f} (kJ·Å³/mol)")
    print(f"B = {B_pred:.2f} (kJ·Å⁹/mol)")
    print(f"r₀ = {r0:.6f} Å")
    print(f"φ₀ = {phi0:.6f} kJ/mol")
