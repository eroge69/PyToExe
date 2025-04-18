import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk

# Datenbank für Jahre & Monate
nettoverdienste = {
    "2024": {
        "Januar": 3896.59,
        "Februar": 3922.88,
        "März": 3874.36,
        "April": 3876.08,
        "Mai": 4057.49,
        "Juni": 4434.25,
        "Juli": 4073.47,
        "August": 4083.00,
        "September": 4077.91,
        "Oktober": 4683.86,
        "November": 7137.09,
        "Dezember": 4102.49,
    },
    "2025": {
        "Januar": 3982.57,
        "Februar": 3900.35,
        "März": 4147.64,
        "April": 0.00
    }
}

# Funktion zur Berechnung und Anzeige
def zeige_verdienst():
    jahr = jahr_entry.get()
    monat = monat_entry.get()

    if jahr in nettoverdienste:
        if monat in nettoverdienste[jahr]:
            betrag = nettoverdienste[jahr][monat]
           # Formatieren (deutsches Format)
            betrag_formatiert = f"{betrag:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

            # Farbe je nach Betrag
            farbe = "green" if betrag >= 4000 else "red"

            # Ergebnis anzeigen mit farblicher Hervorhebung
            ergebnis_label.config(
            text=f"Nettoverdienst im {monat} {jahr}: {betrag_formatiert}€",
            fg=farbe
)
        else:
            messagebox.showerror("Fehler", f"Den Monat '{monat}' gibt es für {jahr} nicht.")
    else:
        messagebox.showerror("Fehler", f"Für das Jahr '{jahr}' gibt es keine Daten.")

# GUI-Fenster erstellen
fenster = tk.Tk()
fenster.title("Nettoverdienst-Abfrage")
fenster.geometry("800x500")

# Bild laden (Pfad anpassen!)
bild = Image.open("Porsche.png")  # z. B. "logo.png"
bild = bild.resize((400, 200))  # optional: Größe anpassen
bild_tk = ImageTk.PhotoImage(bild)

# Bild-Label
bild_label = tk.Label(fenster, image=bild_tk)
bild_label.image = bild_tk  # Referenz behalten!
bild_label.grid(row=0, column=2, rowspan=4, padx=20, pady=20)

# Labels & Eingabefelder
tk.Label(fenster, text="Jahr (z.B. 2024):").grid(row=0, column=0, padx=10, pady=5, sticky="e")
jahr_entry = tk.Entry(fenster)
jahr_entry.grid(row=0, column=1, padx=10, pady=5)

tk.Label(fenster, text="Monat (z.B. März):").grid(row=1, column=0, padx=10, pady=5, sticky="e")
monat_entry = tk.Entry(fenster)
monat_entry.grid(row=1, column=1, padx=10, pady=5)

# Button
tk.Button(fenster, text="Nettoverdienst anzeigen", command=zeige_verdienst).grid(row=2, column=0, columnspan=2, pady=10)

# Ergebnisfeld
ergebnis_label = tk.Label(fenster, text="", fg="blue")
ergebnis_label.grid(row=3, column=0, columnspan=2, pady=10)

# Fenster starten
fenster.mainloop()
