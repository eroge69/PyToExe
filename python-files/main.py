import pandas as pd
import tkinter as tk
from tkinter import filedialog, messagebox
import os

# Conversione da mm:ss.d a secondi float
def parse_time(t):
    try:
        minutes, rest = t.split(":")
        return int(minutes) * 60 + float(rest)
    except:
        return None

# Conversione da secondi a mm:ss.d
def seconds_to_str(t):
    minutes = int(t // 60)
    seconds = t % 60
    return f"{minutes:02d}:{seconds:04.1f}"

def confronta_timestamp(file_path, output_path):
    df = pd.read_csv(file_path, sep=';', dtype=str).dropna()

    video_times = df['video'].map(parse_time).dropna().tolist()
    audio_times = df['audio'].map(parse_time).dropna().tolist()
    tolerance = 0.5

    true_positives = []
    false_positives = []
    video_matched = set()

    for a_time in audio_times:
        match_found = False
        for idx, v_time in enumerate(video_times):
            if abs(a_time - v_time) <= tolerance and idx not in video_matched:
                true_positives.append((a_time, v_time))
                video_matched.add(idx)
                match_found = True
                break
        if not match_found:
            false_positives.append(a_time)

    false_negatives = [video_times[i] for i in range(len(video_times)) if i not in video_matched]

    # Dettagli
    tp = [{"Categoria": "TP", "Timestamp_Audio": a, "Timestamp_Video": v} for a, v in true_positives]
    fp = [{"Categoria": "FP", "Timestamp_Audio": a, "Timestamp_Video": ""} for a in false_positives]
    fn = [{"Categoria": "FN", "Timestamp_Audio": "", "Timestamp_Video": v} for v in false_negatives]

    results = tp + fp + fn
    df_out = pd.DataFrame(results)

    df_out['Timestamp_Audio'] = df_out['Timestamp_Audio'].apply(lambda x: seconds_to_str(x) if x != "" else "")
    df_out['Timestamp_Video'] = df_out['Timestamp_Video'].apply(lambda x: seconds_to_str(x) if x != "" else "")

    # Salva nel percorso scelto
    df_out.to_csv(output_path, index=False)

# GUI
def scegli_file():
    file_path = filedialog.askopenfilename(
        title="Seleziona file CSV", filetypes=[("CSV files", "*.csv")]
    )
    if file_path:
        output_path = filedialog.asksaveasfilename(
            title="Salva il file dei risultati",
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv")],
            initialfile="risultati_confronto.csv"
        )
        if output_path:
            try:
                confronta_timestamp(file_path, output_path)
                messagebox.showinfo("Completato", f"File salvato con successo:\n{output_path}")
            except Exception as e:
                messagebox.showerror("Errore", f"Errore durante l'elaborazione:\n{e}")
        else:
            messagebox.showwarning("Annullato", "Salvataggio annullato.")

# Setup GUI
root = tk.Tk()
root.title("Confronto Timestamp Audio/Video")
root.geometry("600x400")
root.resizable(False, False)

label = tk.Label(root, text="Confronta Timestamp Audio/Video\n(tolleranza 0.5 secondi)", font=("Helvetica", 12), pady=20)
label.pack()

btn = tk.Button(root, text="Seleziona File CSV e Salva Risultato", command=scegli_file, font=("Helvetica", 12), padx=20, pady=10)
btn.pack()

root.mainloop()
