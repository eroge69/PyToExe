import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import math

root = tk.Tk()
root.title("Tabbed R&D Test Report")
root.geometry("1300x750")

notebook = ttk.Notebook(root)
notebook.pack(expand=1, fill='both')

# Tabs
tab1 = ttk.Frame(notebook)
tab2 = ttk.Frame(notebook)
tab3 = ttk.Frame(notebook)
notebook.add(tab1, text='Audio Testing')
notebook.add(tab2, text='Volume Curve')
notebook.add(tab3, text='Frequency Response')

# ----------------------------
# Tab 1: Audio Testing
# ----------------------------
def build_audio_tab(tab):
    tk.Label(tab, text="Audio Testing", font=("Arial", 16, "bold")).pack(pady=10)

    top = tk.Frame(tab)
    top.pack()

    source_var = tk.StringVar(value="RF")
    tk.Label(top, text="Source:").grid(row=0, column=0)
    ttk.Combobox(top, textvariable=source_var, values=["RF", "AV", "HDMI", "USB"], width=10).grid(row=0, column=1)

    spk_imp = tk.StringVar(value="8")
    tk.Label(top, text="Speaker Impedance:").grid(row=0, column=2)
    ttk.Combobox(top, textvariable=spk_imp, values=[4, 6, 8, 12, 16], width=10).grid(row=0, column=3)

    hp_imp = tk.StringVar(value="32")
    tk.Label(top, text="HP Impedance:").grid(row=0, column=4)
    tk.Entry(top, textvariable=hp_imp, width=10).grid(row=0, column=5)

    headers = [
        "Condition", "Right Voltage (V)", "Left Voltage (V)", "Distortion (%)",
        "Right Watt", "Left Watt", "HP Left Voltage (V)", "HP Right Voltage (V)", "HP Left Watt", "HP Right Watt"
    ]
    conditions = [
        "AVL OFF / SURROUND OFF", "AVL OFF / SURROUND ON",
        "AVL ON / SURROUND OFF", "AVL ON / SURROUND ON"
    ]
    entries = []

    table = tk.Frame(tab)
    table.pack()

    for col, h in enumerate(headers):
        tk.Label(table, text=h, width=18, relief="solid").grid(row=0, column=col)

    for i, cond in enumerate(conditions):
        row_data = {}
        tk.Label(table, text=cond, width=18, relief="solid").grid(row=i+1, column=0)
        for j, h in enumerate(headers[1:], 1):
            var = tk.StringVar()
            if "Watt" in h:
                tk.Label(table, textvariable=var, width=18, relief="ridge", bg="lightgray").grid(row=i+1, column=j)
            else:
                tk.Entry(table, textvariable=var, width=18).grid(row=i+1, column=j)
            row_data[h] = var
        entries.append(row_data)

    def calculate():
        try:
            R_spk = float(spk_imp.get())
            R_hp = float(hp_imp.get())
            for row in entries:
                rv = float(row["Right Voltage (V)"].get() or 0)
                lv = float(row["Left Voltage (V)"].get() or 0)
                hpl = float(row["HP Left Voltage (V)"].get() or 0)
                hpr = float(row["HP Right Voltage (V)"].get() or 0)
                row["Right Watt"].set(f"{(rv**2)/R_spk:.2f}")
                row["Left Watt"].set(f"{(lv**2)/R_spk:.2f}")
                row["HP Left Watt"].set(f"{(hpl**2)/R_hp:.2f}")
                row["HP Right Watt"].set(f"{(hpr**2)/R_hp:.2f}")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def export():
        data = []
        for i, cond in enumerate(conditions):
            row = {"Condition": cond}
            row.update({k: v.get() for k, v in entries[i].items()})
            data.append(row)
        df = pd.DataFrame(data)
        file = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel Files", "*.xlsx")])
        if file:
            df.to_excel(file, index=False)
            messagebox.showinfo("Exported", f"Data saved to {file}")

    def clear():
        for row in entries:
            for key, var in row.items():
                var.set("")
        # Reset dropdowns and entry values
        source_var.set("RF")
        spk_imp.set("8")
        hp_imp.set("32")


   
    tk.Button(tab, text="Calculate", command=calculate).pack(pady=5)
    tk.Button(tab, text="Export to Excel", command=export).pack(pady=5)
    tk.Button(tab, text="Clear", command=clear).pack(pady=5)
# ----------------------------
# Tab 2: Volume Curve
# ----------------------------
def build_volume_tab(tab):
    tk.Label(tab, text="Volume Curve", font=("Arial", 16, "bold")).pack(pady=10)
    frame = tk.Frame(tab)
    frame.pack()

    source_var = tk.StringVar(value="RF")
    tk.Label(frame, text="Source:").grid(row=0, column=0)
    ttk.Combobox(frame, textvariable=source_var, values=["RF", "AV", "HDMI", "USB"], width=10).grid(row=0, column=1)

    imp = tk.DoubleVar(value=8)
    tk.Label(frame, text="Impedance:").grid(row=0, column=2)
    ttk.Combobox(frame, textvariable=imp, values=[4, 6, 8, 12, 16], width=10).grid(row=0, column=3)

    table = tk.Frame(tab)
    table.pack()

    headers = ["Volume", "Right Voltage", "Left Voltage", "Distortion", "Right Watt", "Left Watt", "Total Watt"]
    levels = [1,2,3,4,5,10,20,30,40,50,60,70,80,90,100]
    entries = []

    for j, h in enumerate(headers):
        tk.Label(table, text=h, relief="solid", width=15).grid(row=0, column=j)

    for i, v in enumerate(levels):
        row = [tk.Label(table, text=str(v), relief="solid", width=15)]
        row[0].grid(row=i+1, column=0)
        for j in range(1, len(headers)):
            e = tk.Entry(table, width=15)
            e.grid(row=i+1, column=j)
            row.append(e)
        entries.append(row)

    def calc():
        for row in entries:
            try:
                rv = float(row[1].get() or 0)
                lv = float(row[2].get() or 0)
                rw = (rv**2)/imp.get()
                lw = (lv**2)/imp.get()
                row[4].delete(0, tk.END); row[4].insert(0, f"{rw:.2f}")
                row[5].delete(0, tk.END); row[5].insert(0, f"{lw:.2f}")
                row[6].delete(0, tk.END); row[6].insert(0, f"{rw+lw:.2f}")
            except: continue

    def export():
        data = []
        for i, v in enumerate(levels):
            row = {"Volume": v}
            for j, h in enumerate(headers[1:], 1):
                row[h] = entries[i][j].get()
            data.append(row)
        df = pd.DataFrame(data)
        file = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel Files", "*.xlsx")])
        if file:
            df.to_excel(file, index=False)
            messagebox.showinfo("Exported", f"Data saved to {file}")

    def plot():
        x, y = [], []
        for i, row in enumerate(entries):
            try:
                x.append(levels[i])
                y.append(float(row[6].get()))
            except: continue
        fig, ax = plt.subplots()
        ax.plot(x, y, marker='o')
        ax.set_title("Volume vs Total Watt")
        ax.set_xlabel("Volume Level")
        ax.set_ylabel("Total Watt")
        plt.grid(True)
        plt.show()

    def clear():
        for row in entries:
            for cell in row[1:]:  # skip the volume label
                cell.delete(0, tk.END)
        source_var.set("RF")
        imp.set(8)


    tk.Button(tab, text="Calculate", command=calc).pack(pady=5)
    tk.Button(tab, text="Plot Graph", command=plot).pack(pady=5)
    tk.Button(tab, text="Export to Excel", command=export).pack(pady=5)
    tk.Button(tab, text="Clear", command=clear).pack(pady=5)
    

# ----------------------------
# Tab 3: Frequency Response
# ----------------------------
def build_frequency_tab(tab):
    tk.Label(tab, text="Frequency Response", font=("Arial", 16, "bold")).pack(pady=10)
    frame = tk.Frame(tab)
    frame.pack()

    source_var = tk.StringVar(value="RF")
    tk.Label(frame, text="Source:").grid(row=0, column=0)
    ttk.Combobox(frame, textvariable=source_var, values=["RF", "AV", "HDMI", "USB"], width=10).grid(row=0, column=1)

    imp = tk.DoubleVar(value=8)
    tk.Label(frame, text="Impedance:").grid(row=0, column=2)
    ttk.Combobox(frame, textvariable=imp, values=[4, 6, 8, 12, 16], width=10).grid(row=0, column=3)

    mode = tk.StringVar(value="Watt")
    tk.Label(frame, text="Y Axis:").grid(row=0, column=4)
    ttk.Combobox(frame, textvariable=mode, values=["Watt", "dB"], width=10).grid(row=0, column=5)

    # Frequency list
    freqs = [20, 40, 50, 60, 80, 100, 200, 300, 400, 500, 600, 800, 1000,
             2000, 3000, 4000, 5000, 6000, 8000, 10000, 12000, 14000, 16000, 18000, 20000]
    headers = ["Frequency (Hz)", "Right Voltage", "Left Voltage", "Right Watt", "Left Watt", "Right dB", "Left dB"]
    entries = []

    table = tk.Frame(tab)
    table.pack()

    for j, h in enumerate(headers):
        tk.Label(table, text=h, relief="solid", width=15).grid(row=0, column=j)

    for i, f in enumerate(freqs):
        row = [tk.Label(table, text=str(f), relief="solid", width=15)]
        row[0].grid(row=i+1, column=0)
        for j in range(1, len(headers)):
            e = tk.Entry(table, width=15)
            e.grid(row=i+1, column=j)
            row.append(e)
        entries.append(row)

    def calc():
        for row in entries:
            try:
                rv = float(row[1].get() or 0)
                lv = float(row[2].get() or 0)
                rw = (rv ** 2) / imp.get()
                lw = (lv ** 2) / imp.get()
                rdB = 10 * math.log10(rw) if rw > 0 else 0
                ldB = 10 * math.log10(lw) if lw > 0 else 0
                row[3].delete(0, tk.END); row[3].insert(0, f"{rw:.2f}")
                row[4].delete(0, tk.END); row[4].insert(0, f"{lw:.2f}")
                row[5].delete(0, tk.END); row[5].insert(0, f"{rdB:.2f}")
                row[6].delete(0, tk.END); row[6].insert(0, f"{ldB:.2f}")
            except: continue

    def plot():
        x = freqs
        yR, yL = [], []
        for row in entries:
            try:
                if mode.get() == "Watt":
                    yR.append(float(row[3].get()))
                    yL.append(float(row[4].get()))
                else:
                    yR.append(float(row[5].get()))
                    yL.append(float(row[6].get()))
            except:
                yR.append(0)
                yL.append(0)

        fig, ax = plt.subplots()
        ax.plot(x, yR, label="Right Channel", marker='o')
        ax.plot(x, yL, label="Left Channel", marker='x')
        ax.set_title("Frequency Response")
        ax.set_xlabel("Frequency (Hz)")
        ax.set_ylabel("Power (Watt)" if mode.get() == "Watt" else "Level (dB)")
        ax.set_xscale("log")
        ax.grid(True, which="both", linestyle='--', linewidth=0.5)
        ax.legend()
        plt.tight_layout()
        plt.show()

    def export():
        data = []
        for i, f in enumerate(freqs):
            row = {"Frequency": f}
            for j, h in enumerate(headers[1:], 1):
                row[h] = entries[i][j].get()
            data.append(row)
        df = pd.DataFrame(data)
        file = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel Files", "*.xlsx")])
        if file:
            df.to_excel(file, index=False)
            messagebox.showinfo("Exported", f"Data saved to {file}")

    def clear():
        for row in entries:
            for cell in row[1:]:
                cell.delete(0, tk.END)
        source_var.set("RF")
        imp.set(8)
        mode.set("Watt")

    tk.Button(tab, text="Calculate", command=calc).pack(pady=5)
    tk.Button(tab, text="Plot Graph", command=plot).pack(pady=5)
    tk.Button(tab, text="Export to Excel", command=export).pack(pady=5)
    tk.Button(tab, text="Clear", command=clear).pack(pady=5)


# Build all tabs
build_audio_tab(tab1)
build_volume_tab(tab2)
build_frequency_tab(tab3)

##root.mainloop()......
