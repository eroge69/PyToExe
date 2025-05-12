import tkinter as tk
from tkinter import filedialog, messagebox
import re

# Functie om software nummers in een BIN bestand te zoeken
def zoek_software_nummer(bin_bestand):
    try:
        with open(bin_bestand, 'rb') as bestand:
            data = bestand.read()

        # Reguliere expressie voor software nummers (standaard VAG patroon)
        patroon = re.compile(rb'\d{4,5}-\d{3}-\d{3}(-[A-Z])?')

        # Zoek software nummers
        software_nummers = patroon.findall(data)

        if software_nummers:
            result = "Gevonden software nummers:\n"
            result += "\n".join([nummer.decode('utf-8') for nummer in software_nummers])
            return result
        else:
            return "Geen software nummers gevonden."

    except FileNotFoundError:
        return "Het BIN bestand is niet gevonden."

# GUI Applicatie
def start_gui():
    root = tk.Tk()
    root.title("BIN Software Nummer Uitlezer")
    root.geometry("400x300")

    def open_file():
        bin_pad = filedialog.askopenfilename(title="Selecteer BIN Bestand", filetypes=[("BIN bestanden", "*.bin"), ("Alle bestanden", "*.*")])
        if bin_pad:
            result = zoek_software_nummer(bin_pad)
            result_text.config(state=tk.NORMAL)
            result_text.delete(1.0, tk.END)
            result_text.insert(tk.END, result)
            result_text.config(state=tk.DISABLED)

    open_button = tk.Button(root, text="Selecteer BIN Bestand", command=open_file)
    open_button.pack(pady=10)

    result_text = tk.Text(root, height=10, width=40, state=tk.DISABLED)
    result_text.pack(pady=10)

    root.mainloop()

if __name__ == '__main__':
    start_gui()
