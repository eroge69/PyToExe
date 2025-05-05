import numpy as np
import scipy.stats as stats
import matplotlib.pyplot as plt
import os
import tkinter as tk
from tkinter import messagebox

# Tabel met Q-crit voor Dean & Dixon (95%)
Q_TABLE_95 = {
    3: 0.941, 4: 0.765, 5: 0.642, 6: 0.560,
    7: 0.507, 8: 0.468, 9: 0.437, 10: 0.412
}

def get_q_crit(n):
    return Q_TABLE_95.get(n, 0.412)  # Gebruik veiligste waarde voor n > 10

def dean_dixon_outliers(data):
    data_sorted = sorted(data)
    n = len(data_sorted)
    data_range = max(data_sorted) - min(data_sorted)
    if n < 3 or data_range == 0:
        return data_sorted, 0, False, 0, False, n

    lowest_dev = data_sorted[1] - data_sorted[0]
    highest_dev = data_sorted[-1] - data_sorted[-2]

    Q_low = lowest_dev / data_range
    Q_high = highest_dev / data_range

    Q_crit = get_q_crit(n)

    is_low_outlier = Q_low > Q_crit
    is_high_outlier = Q_high > Q_crit

    cleaned_data = data_sorted[:]
    if is_high_outlier:
        cleaned_data.pop()
    if is_low_outlier:
        cleaned_data.pop(0)

    return cleaned_data, Q_low, is_low_outlier, Q_high, is_high_outlier, Q_crit

def compute_stats(data, confidence=0.95):
    mean = np.mean(data)
    std_dev = np.std(data, ddof=1)
    n = len(data)
    t_critical = stats.t.ppf((1 + confidence) / 2, df=n - 1)
    margin = t_critical * (std_dev / np.sqrt(n))
    return mean, std_dev, margin, (mean - margin, mean + margin)

def get_next_graph_filename(prefix="grafiek_", extension=".png"):
    i = 1
    while os.path.exists(f"{prefix}{i}{extension}"):
        i += 1
    return f"{prefix}{i}{extension}"

def save_summary(filename_base, original, removed, cleaned, mean, std_dev, margin, conf, q_low, q_high, q_crit, unsorted):
    with open(f"{filename_base}.txt", "w", encoding="utf-8") as f:
        f.write("🧾 Analyse Samenvatting\n")
        f.write("----------------------\n")
        f.write(f"Originele data (ingevoerde volgorde): {unsorted}\n")
        f.write(f"Originele data (gesorteerd): {sorted(original)}\n")
        if removed:
            f.write(f"Uitschieters verwijderd: {sorted(removed)}\n")
        else:
            f.write("Geen uitschieters gevonden.\n")
        f.write(f"Gebruikte data (in oorspronkelijke volgorde): {cleaned}\n\n")
        f.write(f"Q-crit: {q_crit:.3f}\n")
        f.write(f"Q laag: {q_low:.3f}  → {'Uitschieter' if q_low > q_crit else 'Geen uitschieter'}\n")
        f.write(f"Q hoog: {q_high:.3f} → {'Uitschieter' if q_high > q_crit else 'Geen uitschieter'}\n\n")
        f.write(f"Gemiddelde: {mean:.4f}\n")
        f.write(f"Standaardafwijking: {std_dev:.4f}\n")
        f.write(f"{int(conf*100)}% Betrouwbaarheidsinterval: {mean:.4f} ± {margin:.4f}\n")


def analyse_dataset(data, confidence):
    original_data = data[:]           # Bewaar originele data
    unsorted_data = data[:]           # Ook bewaren voor log en grafiek
    removed_values = []
    iteration = 0

    while True:
        iteration += 1
        cleaned_data_sorted, Q_low, is_low_outlier, Q_high, is_high_outlier, Q_crit = dean_dixon_outliers(data)
        if not is_low_outlier and not is_high_outlier:
            break
        if is_high_outlier:
            high = max(data)
            removed_values.append(high)
            data.remove(high)
        if is_low_outlier:
            low = min(data)
            removed_values.append(low)
            data.remove(low)

    cleaned_data_unsorted = [x for x in unsorted_data if x not in removed_values]

    mean, std_dev, margin, conf_interval = compute_stats(cleaned_data_unsorted, confidence)

    print("\n=== Resultaten ===")
    print(f"Dean & Dixon Q-crit = {Q_crit:.3f}")
    print(f"  Q laag = {Q_low:.3f} → {'Uitschieter' if Q_low > Q_crit else 'Geen uitschieter'}")
    print(f"  Q hoog = {Q_high:.3f} → {'Uitschieter' if Q_high > Q_crit else 'Geen uitschieter'}")

    print(f"\nOriginele data: {original_data}")
    if removed_values:
        print(f"Verwijderd: {sorted(removed_values)}")
    print(f"Gebruikte data: {cleaned_data_unsorted}")

    print("\nStatistieken:")
    print(f"  Gemiddelde = {mean:.4f}")
    print(f"  Standaardafwijking = {std_dev:.4f}")
    print(f"  {int(confidence*100)}% Betrouwbaarheidsinterval = {mean:.4f} ± {margin:.4f}")

    # === Grafiek ===
    x_full = list(range(1, len(unsorted_data) + 1))
    x_clean = [i+1 for i, val in enumerate(unsorted_data) if val not in removed_values]

    plt.figure(figsize=(10, 5))
    plt.plot(x_full, unsorted_data, 'o-', label='📘 Originele data', color='blue')
    plt.plot(x_clean, cleaned_data_unsorted, 'o-', label='✅ Zonder uitschieters', color='green')
    plt.axhline(mean, color='red', linestyle='--', label='Gemiddelde')
    plt.fill_between(x_clean, mean - margin, mean + margin, color='red', alpha=0.2, label='BI')
    plt.title('📊 Analyse van meetdata')
    plt.xlabel('Meting nummer')
    plt.ylabel('Waarde')
    plt.legend()
    plt.grid(True)
    plt.tight_layout()

    filename_png = get_next_graph_filename()
    filename_base = filename_png.replace(".png", "")
    plt.savefig(filename_png)
    plt.show()
    print(f"✅ Grafiek opgeslagen als '{filename_png}'")

    save_summary(filename_base, original_data, removed_values, cleaned_data_unsorted, mean, std_dev, margin, confidence, Q_low, Q_high, Q_crit, unsorted_data)
    print(f"📄 Samenvatting opgeslagen als '{filename_base}.txt'")


# === GUI Setup ===

def on_analyse():
    try:
        # Read input values
        data_input = entry_data.get().strip()
        if not data_input:
            messagebox.showerror("⚠️ Fout", "Voer alstublieft de gegevens in.")
            return
        data = [float(x.strip()) for x in data_input.split(',') if x.strip()]
        if len(data) < 3:
            messagebox.showerror("⚠️ Fout", "Minimaal 3 waarden vereist.")
            return

        confidence_input = entry_confidence.get().strip()
        confidence = float(confidence_input) if confidence_input else 0.95  # Default to 0.95 if empty
        
        # Analyse the dataset
        analyse_dataset(data, confidence)

        messagebox.showinfo("✅ Succes", "De analyse is voltooid en de grafiek is opgeslagen.")
    except ValueError:
        messagebox.showerror("❌ Fout", "Ongeldige invoer. Gebruik alleen getallen, gescheiden door komma’s.")

# Setup the GUI window
root = tk.Tk()
root.title("📊 Data Analyse Tool")

label_data = tk.Label(root, text="📥 Voer je data in (gescheiden door komma's):")
label_data.pack(padx=10, pady=5)

entry_data = tk.Entry(root, width=50)
entry_data.pack(padx=10, pady=5)

label_confidence = tk.Label(root, text="📉 Betrouwbaarheidsniveau (bv. 0.95 voor 95%, Enter voor standaard):")
label_confidence.pack(padx=10, pady=5)

entry_confidence = tk.Entry(root, width=20)
entry_confidence.pack(padx=10, pady=5)

button_analyse = tk.Button(root, text="🔍 Start Analyse", command=on_analyse)
button_analyse.pack(padx=10, pady=10)

root.mainloop()
