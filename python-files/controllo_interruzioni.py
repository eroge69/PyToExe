import tkinter as tk
from tkinter import filedialog, messagebox
import re
from math import sqrt
from xml.etree.ElementTree import Element, SubElement, ElementTree
import os

# Funzioni base

def estrai_movimenti_g01(file_path):
    with open(file_path, "r") as file:
        lines = file.readlines()

    penna_giu = False
    punti = []

    for line in lines:
        line = line.strip()
        if line.startswith("G00") or line.startswith("G01"):
            z_match = re.search(r'Z([\-\d\.]+)', line)
            if z_match:
                z = float(z_match.group(1))
                penna_giu = z <= 0

            if penna_giu and line.startswith("G01"):
                x_match = re.search(r'X([\-\d\.]+)', line)
                y_match = re.search(r'Y([\-\d\.]+)', line)
                if x_match and y_match:
                    x = float(x_match.group(1))
                    y = float(y_match.group(1))
                    punti.append((x, y))
    return punti

def trova_interruzioni(punti, soglia):
    interruzioni = []
    for i in range(1, len(punti)):
        x1, y1 = punti[i - 1]
        x2, y2 = punti[i]
        distanza = sqrt((x2 - x1)**2 + (y2 - y1)**2)
        if distanza > soglia:
            interruzioni.append({
                'indice': i,
                'distanza': distanza,
                'da': (x1, y1),
                'a': (x2, y2)
            })
    return interruzioni

def genera_svg_con_interruzioni(punti, interruzioni, output_file):
    svg = Element('svg', xmlns="http://www.w3.org/2000/svg", version="1.1",
                  width="300mm", height="300mm", viewBox="0 0 300 300")

    for i in range(1, len(punti)):
        x1, y1 = punti[i - 1]
        x2, y2 = punti[i]
        colore = "black"
        spessore = "0.2"
        if any(err['indice'] == i for err in interruzioni):
            colore = "red"
            spessore = "0.5"

        SubElement(svg, 'line', {
            'x1': str(x1), 'y1': str(300 - y1),
            'x2': str(x2), 'y2': str(300 - y2),
            'stroke': colore,
            'stroke-width': spessore
        })

    ElementTree(svg).write(output_file)

# GUI

def scegli_file():
    file_path = filedialog.askopenfilename(filetypes=[("G-code files", "*.gcode")])
    if file_path:
        file_entry.delete(0, tk.END)
        file_entry.insert(0, file_path)

def analizza_file():
    file_path = file_entry.get()
    soglia = float(soglia_entry.get())

    if not os.path.exists(file_path):
        messagebox.showerror("Errore", "File non trovato!")
        return

    punti = estrai_movimenti_g01(file_path)
    interruzioni = trova_interruzioni(punti, soglia)

    global punti_globali, interruzioni_globali
    punti_globali = punti
    interruzioni_globali = interruzioni

    risultato_label.config(text=f"{len(interruzioni)} interruzioni trovate")

def genera_svg():
    if not punti_globali or not interruzioni_globali:
        messagebox.showwarning("Attenzione", "Prima analizza un file.")
        return
    output_file = "interruzioni.svg"
    genera_svg_con_interruzioni(punti_globali, interruzioni_globali, output_file)
    messagebox.showinfo("Fatto!", f"SVG salvato come: {output_file}")

# Inizializzazione GUI
root = tk.Tk()
root.title("Controllo Interruzioni G-code")
root.geometry("450x200")

file_entry = tk.Entry(root, width=40)
file_entry.grid(row=0, column=1, padx=5, pady=10)
file_btn = tk.Button(root, text="Scegli file G-code", command=scegli_file)
file_btn.grid(row=0, column=0, padx=5)

soglia_label = tk.Label(root, text="Soglia distanza (mm):")
soglia_label.grid(row=1, column=0, padx=5)
soglia_entry = tk.Entry(root, width=10)
soglia_entry.insert(0, "0.5")
soglia_entry.grid(row=1, column=1, sticky='w')

analizza_btn = tk.Button(root, text="✓ Analizza", command=analizza_file)
analizza_btn.grid(row=2, column=0, pady=10)
risultato_label = tk.Label(root, text="Nessuna analisi eseguita")
risultato_label.grid(row=2, column=1)

genera_btn = tk.Button(root, text="Genera SVG", command=genera_svg)
genera_btn.grid(row=3, column=0, columnspan=2, pady=10)

punti_globali = []
interruzioni_globali = []

root.mainloop()
