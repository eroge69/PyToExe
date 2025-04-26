
import pandas as pd
import matplotlib.pyplot as plt
import tkinter as tk
from tkinter import filedialog, messagebox
import os

def lag_graf(filbane, startdato, sluttdato, overskrift, temp_min, temp_max, rh_min, rh_max, co2_min, co2_max):
    try:
        df = pd.read_excel(filbane, sheet_name="Measured_Values")

        # Leser etter kolonnenummer (ikke navn)
        dato_tid = pd.to_datetime(df.iloc[:, 0], format="%d.%m.%y %H:%M:%S", errors="coerce")
        temperatur = pd.to_numeric(df.iloc[:, 1], errors="coerce")
        rh = pd.to_numeric(df.iloc[:, 2], errors="coerce")
        co2 = pd.to_numeric(df.iloc[:, 4], errors="coerce")

        df = pd.DataFrame({
            "DatoTid": dato_tid,
            "Temperature °C": temperatur,
            "RH %": rh,
            "CO2 ppm": co2
        })

        df = df.dropna(subset=["DatoTid"])

        # Filtrer ønsket tidsperiode
        start = pd.to_datetime(startdato)
        end = pd.to_datetime(sluttdato)
        df_filtered = df[(df["DatoTid"] >= start) & (df["DatoTid"] <= end)]

        # Tegn graf
        fig, ax1 = plt.subplots(figsize=(14, 7))

        ax1.plot(df_filtered["DatoTid"], df_filtered["CO2 ppm"], color="green")
        ax1.set_ylabel("CO2 ppm", color="green")
        ax1.tick_params(axis='y', labelcolor="green")
        ax1.set_ylim(co2_min, co2_max)
        ax1.set_xlabel("Dato og Tid")

        ax2 = ax1.twinx()
        ax2.spines["left"].set_position(("outward", 60))
        ax2.yaxis.set_label_position("left")
        ax2.yaxis.tick_left()
        ax2.plot(df_filtered["DatoTid"], df_filtered["Temperature °C"], color="red")
        ax2.set_ylabel("T, °C", color="red")
        ax2.tick_params(axis='y', labelcolor="red")
        ax2.set_ylim(temp_min, temp_max)

        ax3 = ax1.twinx()
        ax3.spines["left"].set_position(("outward", 120))
        ax3.yaxis.set_label_position("left")
        ax3.yaxis.tick_left()
        ax3.plot(df_filtered["DatoTid"], df_filtered["RH %"], color="blue")
        ax3.set_ylabel("RH, %", color="blue")
        ax3.tick_params(axis='y', labelcolor="blue")
        ax3.set_ylim(rh_min, rh_max)

        plt.title(overskrift)
        ax1.grid(True)
        plt.tight_layout()

        # Velg hvor grafen skal lagres
        save_path = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG filer", "*.png")])
        if save_path:
            plt.savefig(save_path)
            plt.close()
            messagebox.showinfo("Ferdig!", f"Graf lagret som:\n{save_path}")
        else:
            plt.close()

    except Exception as e:
        messagebox.showerror("Feil", str(e))

def generer_graf():
    filbane = filedialog.askopenfilename(filetypes=[("Excel-filer", "*.xlsx")])
    if not filbane:
        return

    startdato = f"{startaar.get()}-{startmaaned.get()}-{startdag.get()}"
    sluttdato = f"{sluttaar.get()}-{sluttmaaned.get()}-{sluttdag.get()}"
    overskrift = overskrift_entry.get()
    temp_min = int(temp_min_entry.get())
    temp_max = int(temp_max_entry.get())
    rh_min = int(rh_min_entry.get())
    rh_max = int(rh_max_entry.get())
    co2_min = int(co2_min_entry.get())
    co2_max = int(co2_max_entry.get())

    lag_graf(filbane, startdato, sluttdato, overskrift, temp_min, temp_max, rh_min, rh_max, co2_min, co2_max)

# GUI
vindu = tk.Tk()
vindu.title("Bedriftshelsetjenesten i Bergen – Comet Graf Lager")
vindu.geometry("650x550")

header = tk.Label(vindu, text="Bedriftshelsetjenesten i Bergen – Comet Graf Lager", font=("Arial", 16, "bold"))
header.pack(pady=10)

# Datoer
dato_frame = tk.Frame(vindu)
dato_frame.pack(pady=5)

tk.Label(dato_frame, text="Startdato (DD MM YYYY):").grid(row=0, column=0)
startdag = tk.Entry(dato_frame, width=5)
startmaaned = tk.Entry(dato_frame, width=5)
startaar = tk.Entry(dato_frame, width=8)
startdag.grid(row=0, column=1)
startmaaned.grid(row=0, column=2)
startaar.grid(row=0, column=3)

tk.Label(dato_frame, text="Sluttdato (DD MM YYYY):").grid(row=1, column=0)
sluttdag = tk.Entry(dato_frame, width=5)
sluttmaaned = tk.Entry(dato_frame, width=5)
sluttaar = tk.Entry(dato_frame, width=8)
sluttdag.grid(row=1, column=1)
sluttmaaned.grid(row=1, column=2)
sluttaar.grid(row=1, column=3)

# Overskrift
tk.Label(vindu, text="Overskrift på graf:").pack(pady=5)
overskrift_entry = tk.Entry(vindu, width=50)
overskrift_entry.pack()

# Y-akse innstillinger
yakse_frame = tk.Frame(vindu)
yakse_frame.pack(pady=10)

tk.Label(yakse_frame, text="Temp Min:").grid(row=0, column=0)
temp_min_entry = tk.Entry(yakse_frame, width=5)
temp_min_entry.insert(0, "16")
temp_min_entry.grid(row=0, column=1)

tk.Label(yakse_frame, text="Temp Max:").grid(row=0, column=2)
temp_max_entry = tk.Entry(yakse_frame, width=5)
temp_max_entry.insert(0, "30")
temp_max_entry.grid(row=0, column=3)

tk.Label(yakse_frame, text="RH% Min:").grid(row=1, column=0)
rh_min_entry = tk.Entry(yakse_frame, width=5)
rh_min_entry.insert(0, "0")
rh_min_entry.grid(row=1, column=1)

tk.Label(yakse_frame, text="RH% Max:").grid(row=1, column=2)
rh_max_entry = tk.Entry(yakse_frame, width=5)
rh_max_entry.insert(0, "60")
rh_max_entry.grid(row=1, column=3)

tk.Label(yakse_frame, text="CO2 Min:").grid(row=2, column=0)
co2_min_entry = tk.Entry(yakse_frame, width=5)
co2_min_entry.insert(0, "0")
co2_min_entry.grid(row=2, column=1)

tk.Label(yakse_frame, text="CO2 Max:").grid(row=2, column=2)
co2_max_entry = tk.Entry(yakse_frame, width=5)
co2_max_entry.insert(0, "3000")
co2_max_entry.grid(row=2, column=3)

# Generer graf-knapp
generer_knapp = tk.Button(vindu, text="Generer graf", command=generer_graf, font=("Arial", 14))
generer_knapp.pack(pady=20)

# Signatur nederst
signatur = tk.Label(vindu, text="Laget av Ørjan Anderson & Espen Raa Nilsen", font=("Arial", 10), fg="gray")
signatur.pack(side="bottom", pady=10)

vindu.mainloop()
