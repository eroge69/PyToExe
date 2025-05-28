import os
import json
import numpy as np
import pandas as pd
import joblib

from scipy.signal import butter, filtfilt, find_peaks
from scipy.fft import fft
from scipy.stats import entropy

# --- Configuration ---
FS = 120
INPUT_FOLDER = "test"
MODEL_DIR = "model"
OUTPUT_CSV = "predictions_with_sqi.csv"
SQI_THRESHOLD = 3.0  # entropy-based SQI threshold
INVALID_VALUES = {-1, 1, 400, 404, 202, 200}

# --- Signal Filtering ---
def bandpass_filter(signal, fs=FS, lowcut=0.4, highcut=11, order=3):
    nyq = 0.5 * fs
    b, a = butter(order, [lowcut / nyq, highcut / nyq], btype='band')
    return filtfilt(b, a, signal)

# --- Signal Quality Index (Entropy) ---
def compute_sqi(signal, bins=50):
    if len(signal) < FS:
        return 0
    hist, _ = np.histogram(signal, bins=bins, density=True)
    return entropy(hist + 1e-6)

# --- Feature Extraction ---
def extract_ppg_features(signal):
    if len(signal) < FS:
        return [0] * 16
    signal = bandpass_filter(signal)
    norm = (signal - np.min(signal)) / (np.max(signal) - np.min(signal))
    peaks, _ = find_peaks(norm, distance=int(FS * 0.4))
    mins, _ = find_peaks(-norm, distance=int(FS * 0.3))
    cycles = []
    for p in peaks:
        left = mins[mins < p]
        right = mins[mins > p]
        if len(left) > 0 and len(right) > 0:
            start, end = left[-1], right[0]
            cycles.append((start, end, norm[start:end]))
    if not cycles:
        return [0] * 16
    start, end, cycle = max(cycles, key=lambda x: np.max(x[2]))
    time = np.linspace(0, (end - start) / FS, end - start)
    d1 = np.gradient(cycle)
    d2 = np.gradient(d1)
    auc = np.trapz(cycle, time)
    pw = time[-1]
    ttp = time[np.argmax(cycle)]
    tdp = time[-1] - ttp
    ratio = ttp / tdp if tdp != 0 else 0
    N = len(cycle)
    freqs = np.fft.fftfreq(N, d=1 / FS)
    fft_vals = np.abs(fft(cycle)[:N // 2])
    freqs = freqs[:N // 2]
    peak_idxs, _ = find_peaks(fft_vals, distance=5)
    sorted_idxs = np.argsort(fft_vals[peak_idxs])[-3:]
    top_freqs = freqs[peak_idxs][sorted_idxs] if len(sorted_idxs) >= 3 else [0, 0, 0]
    top_mags = fft_vals[peak_idxs][sorted_idxs] if len(sorted_idxs) >= 3 else [0, 0, 0]
    return [
        np.max(cycle), pw, ttp, ratio,
        np.max(d1), np.min(d1),
        np.max(d2), np.min(d2),
        auc,
        top_freqs[0], top_mags[0],
        top_freqs[1], top_mags[1],
        top_freqs[2], top_mags[2]
    ]

# --- Load Models ---
scaler = joblib.load(os.path.join(MODEL_DIR, "scaler.pkl"))
sbp_model = joblib.load(os.path.join(MODEL_DIR, "sbp_model.pkl"))
dbp_model = joblib.load(os.path.join(MODEL_DIR, "dbp_model.pkl"))

# --- Predict All Files ---
results = []

for fname in os.listdir(INPUT_FOLDER):
    if not fname.endswith(".json"):
        continue
    path = os.path.join(INPUT_FOLDER, fname)
    try:
        with open(path, 'r', encoding='utf-8') as f:
            lines = [l for l in f if not l.strip().startswith('//')]
            data = json.loads("\n".join(lines))
        pleth = np.array(data.get("Pleth", []))
        sbp_true = data.get("BPSystolic", "")
        dbp_true = data.get("BPDiastolic", "")
        name = os.path.basename(path)

        # --- SQI Check ---
        sqi = compute_sqi(pleth)
        if sqi < SQI_THRESHOLD:
            results.append({
                "Filename": name,
                "SBP_True": sbp_true,
                "DBP_True": dbp_true,
                "SBP_Pred": "",
                "DBP_Pred": "",
                "Reason": f"Low SQI: {sqi:.2f}"
            })
            continue

        # --- Feature Extraction ---
        features = extract_ppg_features(pleth)
        if all(f == 0 for f in features):
            results.append({
                "Filename": name,
                "SBP_True": sbp_true,
                "DBP_True": dbp_true,
                "SBP_Pred": "",
                "DBP_Pred": "",
                "Reason": "Invalid PPG cycle"
            })
            continue

        features += [np.mean(pleth), np.std(pleth), np.max(pleth), np.min(pleth)]
        X_scaled = scaler.transform([features])
        sbp_pred = sbp_model.predict(X_scaled)[0]
        dbp_pred = dbp_model.predict(X_scaled)[0]

        results.append({
            "Filename": name,
            "SBP_True": sbp_true,
            "DBP_True": dbp_true,
            "SBP_Pred": round(sbp_pred, 2),
            "DBP_Pred": round(dbp_pred, 2),
            "Reason": ""
        })

    except Exception as e:
        results.append({
            "Filename": fname,
            "SBP_True": "",
            "DBP_True": "",
            "SBP_Pred": "",
            "DBP_Pred": "",
            "Reason": f"Error: {str(e)}"
        })

# --- Save CSV Report ---
df = pd.DataFrame(results)
df.to_csv(OUTPUT_CSV, index=False)
print(f"\n✅ Predictions (with SQI filtering) saved to '{OUTPUT_CSV}'")
