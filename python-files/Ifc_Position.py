import tkinter as tk
from tkinter import filedialog, messagebox
import ifcopenshell
import ifcpatch
import os

def select_file():
    filepath = filedialog.askopenfilename(filetypes=[("IFC-Dateien", "*.ifc")])  # Nur IFC-Dateien zulassen
    if filepath:
        file_entry.delete(0, tk.END)
        file_entry.insert(0, filepath)  # Direkt speichern ohne repr()

def validate_floats():
    """Prüft, ob alle Float-Eingaben gültige Zahlen sind. Falls leer, wird 0.0 gesetzt."""
    float_values = {}
    invalid_params = []  # Liste für ungültige Eingaben

    for label in labels:
        value = float_vars[label].get().strip()  # Leerzeichen entfernen
        if value == "":  # Falls das Feld leer ist
            float_values[label] = 0.0
        else:
            try:
                float_values[label] = float(value)
            except ValueError:
                invalid_params.append(label)

    if invalid_params:
        messagebox.showerror("Fehler", f"Ungültige Eingabe für: {', '.join(invalid_params)}.\nBitte gültige Zahlenwerte eingeben!")
        return None

    return float_values

def run_script():
    input_path = file_entry.get()
    if not input_path.endswith(".ifc"):
        messagebox.showerror("Fehler", "Bitte wählen Sie eine gültige IFC-Datei aus.")
        return

    float_values = validate_floats()
    if float_values is None:
        return  # Fehlerhafte Eingaben abbrechen

    # Basisname und Erweiterung trennen
    base, extension = os.path.splitext(input_path)
    output_path = base + "-Moved" + extension

    # Werte aus UI abrufen
    x, y, z, xr, yr, zr = [float_values[label] for label in labels]
    rotate_first_var = rotate_first_var_UI.get()

    # IFC Verarbeitung
    model = ifcopenshell.open(input_path)
    output = ifcpatch.execute({
        "input": input_path,
        "file": model,
        "recipe": "OffsetObjectPlacements",
        "arguments": [x, y, z, rotate_first_var, xr, yr, zr]
    })

    model.write(output_path)

    # Erfolgsmeldung mit OK-Button
    messagebox.showinfo("Erfolgreich", f"Die Datei wurde erfolgreich verarbeitet:\n{output_path}")
    root.quit()  # Programm beenden nach OK-Klick

# UI erstellen
root = tk.Tk()
root.title("IFC Datei Transformation")

tk.Label(root, text="Dateipfad:").grid(row=0, column=0)
file_entry = tk.Entry(root, width=50)
file_entry.grid(row=0, column=1)
tk.Button(root, text="Durchsuchen", command=select_file).grid(row=0, column=2)

# Eingabefelder für x, y, z, rx, ry, rz mit Standardwerten
float_vars = {}
labels = ["x", "y", "z", "rx", "ry", "rz"]
for i, label in enumerate(labels):
    tk.Label(root, text=f"{label}:").grid(row=i+1, column=0)
    float_vars[label] = tk.StringVar(value="0.0")  # Standardwert 0.0 setzen
    tk.Entry(root, textvariable=float_vars[label]).grid(row=i+1, column=1)

# Rotate First Checkbox
rotate_first_var_UI = tk.BooleanVar()
tk.Checkbutton(root, text="Rotate First", variable=rotate_first_var_UI).grid(row=7, column=0, columnspan=2)

tk.Button(root, text="Start", command=run_script).grid(row=8, column=0, columnspan=2)

root.mainloop()
