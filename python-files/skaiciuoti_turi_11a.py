from tkinter import *
from tkinter import filedialog, messagebox
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.interpolate import griddata
from datetime import datetime

try:
    import laspy
    LASPY_AVAILABLE = True
except ImportError:
    LASPY_AVAILABLE = False

def skaiciuoti():
    try:
        fig_file = entry_fig.get()
        base_file = entry_base.get()
        grid_step = float(entry_grid.get())
        iso_count = int(entry_iso.get())

        def parse_file(path):
            points = []
            labels = []
            if path.lower().endswith(".las") and LASPY_AVAILABLE:
                las = laspy.read(path)
                x, y, z = las.x, las.y, las.z
                return np.column_stack((x, y, z)), ["V"] * len(x)
            with open(path, "r", encoding="utf-8") as f:
                for line in f:
                    parts = line.strip().replace(",", ".").split()
                    if len(parts) >= 4 and parts[0].upper().startswith(('P', 'V')):
                        try:
                            x, y, z = map(float, parts[1:4])
                            points.append([x, y, z])
                            labels.append(parts[0].upper())
                        except ValueError:
                            continue
                    elif len(parts) >= 3:
                        try:
                            x, y, z = map(float, parts[:3])
                            points.append([x, y, z])
                            labels.append("")
                        except ValueError:
                            continue
            return np.array(points), labels

        pad_height = float(entry_pad_height.get())

        fig_points, labels = parse_file(fig_file)

        has_p = any(lbl.upper().startswith("P") for lbl in labels)
        has_v = any(lbl.upper().startswith("V") for lbl in labels)

        if has_p and has_v:
            base_pts = np.array([pt for pt, lbl in zip(fig_points, labels) if lbl.upper().startswith("P")])
            top_pts = np.array([pt for pt, lbl in zip(fig_points, labels) if lbl.upper().startswith("V")])
        elif has_v:
            top_pts = np.array([pt for pt, lbl in zip(fig_points, labels) if lbl.upper().startswith("V")])
            base_pts = np.array([[x, y, pad_height] for x, y, _ in top_pts])
        else:
            top_pts = fig_points
            base_pts = np.array([[x, y, pad_height] for x, y, _ in top_pts])

        if base_file:
            base_pts, _ = parse_file(base_file)

        grid_x, grid_y = np.meshgrid(
            np.arange(base_pts[:, 0].min(), base_pts[:, 0].max(), grid_step),
            np.arange(base_pts[:, 1].min(), base_pts[:, 1].max(), grid_step)
        )

        grid_top = griddata(top_pts[:, :2], top_pts[:, 2], (grid_x, grid_y), method='linear')
        grid_base = griddata(base_pts[:, :2], base_pts[:, 2], (grid_x, grid_y), method='linear')

        valid = ~np.isnan(grid_top) & ~np.isnan(grid_base)
        height_diff = np.zeros_like(grid_top)
        height_diff[valid] = grid_top[valid] - grid_base[valid]
        height_diff[height_diff < 0] = 0

        volume = np.sum(height_diff[valid] * grid_step * grid_step)

        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        out_dir = os.path.abspath("duomenys")
        os.makedirs(out_dir, exist_ok=True)

        df = pd.DataFrame({
            'X': grid_x[valid].flatten(),
            'Y': grid_y[valid].flatten(),
            'Height_Diff_m': height_diff[valid].flatten()
        })
        df.to_csv(os.path.join(out_dir, f"aukscio_skirtumas_{timestamp}.csv"), index=False, float_format='%.3f')

        with open(os.path.join(out_dir, f"turio_skaiciavimas_{timestamp}.txt"), "w", encoding='utf-8') as f:
            f.write(f"Skaičiavimo data: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Tūris: {volume:.3f} m³\n")

        messagebox.showinfo("Rezultatas", f"Tūris: {volume:.2f} m³\nRezultatai išsaugoti į {out_dir}")

    except Exception as e:
        messagebox.showerror("Klaida", f"Klaida: {str(e)}")

root = Tk()
root.title("Tūrio skaičiavimas 11")

Label(root, text="Figūros (krūvos) failas:").grid(row=0, column=0, sticky=W)
entry_fig = Entry(root, width=50)
entry_fig.grid(row=0, column=1)
Button(root, text="Pasirinkti", command=lambda: entry_fig.insert(0, filedialog.askopenfilename())).grid(row=0, column=2)

Label(root, text="Pado failas (pasirinktinai):").grid(row=1, column=0, sticky=W)
entry_base = Entry(root, width=50)
entry_base.grid(row=1, column=1)
Button(root, text="Pasirinkti", command=lambda: entry_base.insert(0, filedialog.askopenfilename())).grid(row=1, column=2)

Label(root, text="Pado aukštis (jei nėra):").grid(row=2, column=0, sticky=W)
entry_pad_height = Entry(root)
entry_pad_height.insert(0, "0.0")
entry_pad_height.grid(row=2, column=1)

Label(root, text="Tinklelio žingsnis (0.1–1.0 m):").grid(row=3, column=0, sticky=W)
entry_grid = Entry(root)
entry_grid.insert(0, "0.5")
entry_grid.grid(row=3, column=1)

Label(root, text="Izoliacijų kiekis:").grid(row=4, column=0, sticky=W)
entry_iso = Entry(root)
entry_iso.insert(0, "15")
entry_iso.grid(row=4, column=1)

Button(root, text="Skaičiuoti tūrį", command=skaiciuoti).grid(row=5, column=1, pady=10)

root.mainloop()