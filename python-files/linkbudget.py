import tkinter as tk
from tkinter import messagebox
import math

def calculate_received_power():
    try:
        pt = float(entry_pt.get())          # Transmit power in Watt
        gt = float(entry_gt.get())          # Transmit antenna gain (dB)
        gr = float(entry_gr.get())          # Receive antenna gain (dB)
        d = float(entry_d.get())            # Distance in km
        f = float(entry_f.get())            # Frequency in MHz
        labs = float(entry_labs.get())      # Absorption loss in dB
        latm = float(entry_latm.get())      # Atmospheric loss in dB

        pt_mw = pt * 1000
        pt_dbm = 10 * math.log10(pt_mw)

        # No need to convert gt and gr, they are entered as dB
        lfs = 20 * math.log10(d) + 20 * math.log10(f) + 32.44
        l_total = lfs + labs + latm
        pr = pt_dbm + gt + gr - l_total

        result_var.set(f"Received Power: {pr:.2f} dBm")
    except Exception as e:
        messagebox.showerror("Error", f"Invalid input: {e}")

root = tk.Tk()
root.title("Received Power Calculator")
root.geometry("550x500")
root.config(bg="#e9e3fc")

font1 = ("Arial", 5)
font2 = ("Arial", 5, "bold")

# Use grid for better layout
frame = tk.Frame(root, bg="#e9e3fc")
frame.pack(pady=30)

tk.Label(frame, text="Transmit Power (Watt):", font=font1, bg="#e9e3fc").grid(row=0, column=0, sticky='e', padx=(0,16), pady=8)
entry_pt = tk.Entry(frame, font=font1, width=14)
entry_pt.grid(row=0, column=1, pady=8)

tk.Label(frame, text="Tx Antenna Gain (dB):", font=font1, bg="#e9e3fc").grid(row=1, column=0, sticky='e', padx=(0,16), pady=8)
entry_gt = tk.Entry(frame, font=font1, width=14)
entry_gt.grid(row=1, column=1, pady=8)

tk.Label(frame, text="Rx Antenna Gain (dB):", font=font1, bg="#e9e3fc").grid(row=2, column=0, sticky='e', padx=(0,16), pady=8)
entry_gr = tk.Entry(frame, font=font1, width=14)
entry_gr.grid(row=2, column=1, pady=8)

tk.Label(frame, text="Distance (km):", font=font1, bg="#e9e3fc").grid(row=3, column=0, sticky='e', padx=(0,16), pady=8)
entry_d = tk.Entry(frame, font=font1, width=14)
entry_d.grid(row=3, column=1, pady=8)

tk.Label(frame, text="Frequency (MHz):", font=font1, bg="#e9e3fc").grid(row=4, column=0, sticky='e', padx=(0,16), pady=8)
entry_f = tk.Entry(frame, font=font1, width=14)
entry_f.grid(row=4, column=1, pady=8)

tk.Label(frame, text="Absorption Loss (dB):", font=font1, bg="#e9e3fc").grid(row=5, column=0, sticky='e', padx=(0,16), pady=8)
entry_labs = tk.Entry(frame, font=font1, width=14)
entry_labs.grid(row=5, column=1, pady=8)

tk.Label(frame, text="Atmospheric Loss (dB):", font=font1, bg="#e9e3fc").grid(row=6, column=0, sticky='e', padx=(0,16), pady=8)
entry_latm = tk.Entry(frame, font=font1, width=14)
entry_latm.grid(row=6, column=1, pady=8)

result_var = tk.StringVar()
result_label = tk.Label(root, textvariable=result_var, font=font2, bg="#e9e3fc", fg="#4b3f72")
result_label.pack(pady=20)

calc_btn = tk.Button(root, text="Calculate Received Power", font=font1, bg="#b8b2e9", fg="black",
                     command=calculate_received_power)
calc_btn.pack(pady=10)

root.mainloop()