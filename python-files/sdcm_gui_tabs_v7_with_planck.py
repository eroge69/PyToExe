# v7: obsługa ANSI, IEC, Własna norma
import math
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import pandas as pd
import os

ansi_centers = {2700: (0.4578, 0.4101), 3000: (0.4339, 0.4033), 4000: (0.3818, 0.3797), 5000: (0.3446, 0.3551), 5700: (0.3287, 0.3425), 6500: (0.3123, 0.3283)}
iec_centers = {2700: (0.463, 0.42), 3000: (0.44, 0.403), 4000: (0.38, 0.38), 5000: (0.346, 0.359), 6500: (0.313, 0.337)}
custom_centers = {1800: (0.54924, 0.40823), 2100: (0.51596, 0.4146), 2400: (0.4861184, 0.4146904), 2700: (0.459838, 0.4106192), 3000: (0.4369156, 0.4040903), 4000: (0.3804363, 0.3767725), 5700: (0.3280569, 0.3372127), 6000: (0.322091, 0.331791), 6500: (0.3135363, 0.3236729)}
default_ellipse_params = {2700: (0.004, 0.0028, 74.0), 3000: (0.0054, 0.0036, 72.0), 3500: (0.0049, 0.003, 71.0), 4000: (0.0044, 0.0024, 70.0), 5000: (0.0038, 0.0021, 68.0), 5700: (0.0034, 0.002, 66.0), 6000: (0.0033, 0.002, 66.0), 6500: (0.0032, 0.002, 65.0), 1800: (0.004, 0.0028, 74.0), 2100: (0.004, 0.0028, 74.0), 2400: (0.0042, 0.0029, 74.0)}


results = []
figures = []


# --- SPECTRUM NORMA (szacowana z wykresów) ---
spectrum_centers = {
    1800: (0.5492, 0.4082),
    2200: (0.5159, 0.4146),
    2400: (0.4861, 0.4147),
    2700: (0.4598, 0.4106),
    3000: (0.4305, 0.4035),
    3500: (0.4050, 0.3900),
    4000: (0.3804, 0.3768),
    4500: (0.3560, 0.3660),
    5000: (0.3460, 0.3590),
    5500: (0.3360, 0.3490),
    6000: (0.3221, 0.3318),
    6500: (0.3135, 0.3237),
    2200: (0.5159, 0.4146),
    2400: (0.4861, 0.4147),
    2200: (0.5159, 0.4146),
    2400: (0.4861, 0.4147),
    2700: (0.4598, 0.4106),
    3000: (0.4345, 0.4030),
    4000: (0.3804, 0.3768),
    6000: (0.3221, 0.3318),
}

spectrum_ellipse_params = {
    1800: (0.0065, 0.0030, 65),
    2200: (0.0057, 0.0027, 62),
    2400: (0.0054, 0.0026, 60),
    2700: (0.0051, 0.0025, 59),
    3000: (0.0075, 0.0036, 70),
    3500: (0.0050, 0.0026, 60),
    4000: (0.0048, 0.0024, 51),
    4500: (0.0046, 0.0023, 49),
    5000: (0.0044, 0.0022, 47),
    5500: (0.0040, 0.0020, 45),
    6000: (0.0037, 0.0018, 42),
    6500: (0.0035, 0.0017, 41),
    2200: (0.0057, 0.0027, 62),
    2400: (0.0054, 0.0026, 60),
    2200: (0.0057, 0.0027, 62),
    2400: (0.0052, 0.0025, 60),
    2700: (0.0048, 0.0023, 58),
    3000: (0.0052, 0.0028, 63),
    4000: (0.0048, 0.0024, 51),
    6000: (0.0037, 0.0018, 42),
}


def get_ellipse_data(cct, norm):
    if norm == "IEC":
        centers = iec_centers
    elif norm == "ANSI":
        centers = ansi_centers
    elif norm == "SPECTRUM":
        centers = spectrum_centers
    else:
        centers = custom_centers
    nearest_cct = min(centers.keys(), key=lambda t: abs(t - cct))
    x0, y0 = centers[nearest_cct]
    a, b, angle_deg = (
        spectrum_ellipse_params.get(nearest_cct)
        if norm == 'SPECTRUM' else
        default_ellipse_params.get(nearest_cct, (0.004, 0.0028, 70.0))
    )
    return x0, y0, a, b, angle_deg, nearest_cct


# PLANCK: funkcja obliczająca SDCM jako odległość od krzywej Plancka (Δuv / 0.0017)
def xy_to_uv(x, y):
    denom = (-2 * x + 12 * y + 3)
    if denom == 0:
        return 0, 0
    u = (4 * x) / denom
    v = (6 * y) / denom
    return u, v

def planckian_locus_xy():
    cct_vals = range(1000, 10001, 25)
    data = []
    for t in cct_vals:
        if t <= 4000:
            x = -0.2661239e9 / t**3 - 0.2343580e6 / t**2 + 0.8776956e3 / t + 0.179910
        else:
            x = -3.0258469e9 / t**3 + 2.1070379e6 / t**2 + 0.2226347e3 / t + 0.240390
        y = -1.1063814 * x**3 - 1.34811020 * x**2 + 2.18555832 * x - 0.20219683
        data.append((t, x, y))
    return data

planck_curve = planckian_locus_xy()

def sdcm_from_xy(x, y, cct, norm):
    if norm == "PLANCK":
        u1, v1 = xy_to_uv(x, y)
        min_dist = float("inf")
        best_cct = cct
        for t, px, py in planck_curve:
            u2, v2 = xy_to_uv(px, py)
            dist = ((u1 - u2) ** 2 + (v1 - v2) ** 2) ** 0.5
            if dist < min_dist:
                min_dist = dist
                best_cct = t
        sdcm = min_dist / 0.0017
        return sdcm, best_cct, 0, 0, 0, 0, 0

    x0, y0, a, b, angle_deg, nearest_cct = get_ellipse_data(cct, norm)
    angle_rad = math.radians(angle_deg)
    dx = x - x0
    dy = y - y0
    x_rot = dx * math.cos(angle_rad) + dy * math.sin(angle_rad)
    y_rot = -dx * math.sin(angle_rad) + dy * math.cos(angle_rad)
    sdcm = math.sqrt((x_rot / a) ** 2 + (y_rot / b) ** 2)
    return sdcm, nearest_cct, x0, y0, a, b, angle_deg

def draw_ellipses(ax, x0, y0, a, b, angle_deg, x, y, cct):
    angle_rad = np.radians(angle_deg)
    t = np.linspace(0, 2 * np.pi, 200)
    for i in range(1, 7):
        ellipse_x = i * a * np.cos(t)
        ellipse_y = i * b * np.sin(t)
        x_rot = ellipse_x * np.cos(angle_rad) - ellipse_y * np.sin(angle_rad)
        y_rot = ellipse_x * np.sin(angle_rad) + ellipse_y * np.cos(angle_rad)
        ax.plot(x0 + x_rot, y0 + y_rot, label=f'{i} SDCM')
    ax.plot(x, y, 'rx', markersize=8, label='Punkt')
    ax.set_title(f'Elipsy MacAdama ({cct}K)')
    ax.set_xlabel('x')
    ax.set_ylabel('y')
    ax.legend()
    ax.grid(True)
    ax.set_aspect('equal')

def process_input(data_text, notebook, output, norm_var):
    output.delete("1.0", tk.END)
    results.clear()
    figures.clear()
    norm = norm_var.get()
    lines = data_text.strip().splitlines()
    for i, line in enumerate(lines, 1):
        try:
            clean = line.replace(",", ".").strip()
            parts = clean.split()
            if len(parts) < 4:
                raise ValueError("Zbyt mało danych")
            label = parts[0]
            x = float(parts[1])
            y = float(parts[2])
            cct = int(parts[3])
            sdcm, used_cct, x0, y0, a, b, angle = sdcm_from_xy(x, y, cct, norm)

            results.append({
                "Nazwa próbki": label,
                "x": x,
                "y": y,
                "CCT": cct,
                "Norma": norm,
                "CCT (dopasowane)": used_cct,
                "SDCM": round(sdcm, 2),
                "≤ 3 SDCM": "TAK" if sdcm <= 3 else "NIE"
            })

            frame = ttk.Frame(notebook)
            fig, ax = plt.subplots(figsize=(4.5, 4))
            draw_ellipses(ax, x0, y0, a, b, angle, x, y, used_cct)
            canvas = FigureCanvasTkAgg(fig, master=frame)
            canvas.get_tk_widget().pack()
            canvas.draw()
            label_info = tk.Label(frame, text=f'SDCM: {sdcm:.2f} (dla {used_cct}K, norma: {norm})')
            label_info.pack(pady=5)
            notebook.add(frame, text=label)
            figures.append((label, fig))
        except Exception as e:
            output.insert(tk.END, f"Wiersz {i}: Błąd → {str(e)}\n")


def save_to_excel():
    if not results:
        messagebox.showwarning("Brak danych", "Brak wyników do zapisania.")
        return
    file = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel", "*.xlsx")])
    if file:
        df = pd.DataFrame(results)
        df.to_excel(file, index=False)
        messagebox.showinfo("Zapisano", f"Wyniki zapisane do:\n{file}")

def save_figures():
    if not figures:
        messagebox.showwarning("Brak wykresów", "Brak wykresów do zapisania.")
        return
    folder = filedialog.askdirectory()
    if folder:
        for label, fig in figures:
            safe_label = "".join(c if c.isalnum() else "_" for c in label)
            path = os.path.join(folder, f"{safe_label}.png")
            fig.savefig(path)
        messagebox.showinfo("Zapisano", f"Wykresy zapisane do:\n{folder}")

# GUI
root = tk.Tk()
root.title('Kalkulator SDCM – ANSI / IEC / Własna')

tk.Label(root, text='Wklej dane (opis x y CCT – każdy wiersz osobno):').pack()
input_text = tk.Text(root, height=8, width=70)
input_text.pack()

tk.Label(root, text='Wybierz normę:').pack()
norm_var = tk.StringVar(value="ANSI")
tk.OptionMenu(root, norm_var, "ANSI", "IEC", "Własna", "SPECTRUM", "PLANCK").pack()

tk.Button(root, text='Oblicz SDCM', command=lambda: process_input(input_text.get('1.0', tk.END), notebook, output_text, norm_var)).pack(pady=5)

def reset_app():
    input_text.delete("1.0", tk.END)
    output_text.delete("1.0", tk.END)
    for tab in notebook.tabs():
        notebook.forget(tab)
    results.clear()
    figures.clear()
tk.Button(root, text='Resetuj', command=reset_app).pack(pady=2)

output_text = tk.Text(root, height=4, width=70, fg='red')
output_text.pack()

notebook = ttk.Notebook(root)
notebook.pack(fill='both', expand=True)

tk.Button(root, text='Zapisz wyniki do Excela', command=save_to_excel).pack(pady=5)
tk.Button(root, text='Zapisz wykresy do PNG', command=save_figures).pack(pady=2)

root.mainloop()


def reset_app():
    input_text.delete("1.0", tk.END)
    output_text.delete("1.0", tk.END)
    for tab in notebook.tabs():
        notebook.forget(tab)
    results.clear()
    figures.clear()

tk.Button(root, text='Resetuj', command=reset_app).pack(pady=5)
