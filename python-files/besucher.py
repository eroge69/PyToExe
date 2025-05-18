import tkinter as tk
from tkinter import messagebox
import pandas as pd
import os

EXCEL_DATEI = "besucher.xlsx"

# DataFrame laden oder neu erstellen
if os.path.exists(EXCEL_DATEI):
    df = pd.read_excel(EXCEL_DATEI)
else:
    df = pd.DataFrame(columns=["Vorname", "Nachname", "Geburtsdatum", "Ankunftsdatum", "Ankunftszeit",
                               "Abreisedatum", "Abreisezeit", "Bemerkung", "Eintrittsverbot",
                               "VerbotGrund", "VerbotVon", "VerbotBis"])

def daten_speichern():
    global df
    vorname = entry_vorname.get().strip()
    nachname = entry_nachname.get().strip()
    geburtsdatum = entry_geburtsdatum.get().strip()
    ankunftsdatum = entry_ankunftsdatum.get().strip()
    ankunftszeit = entry_ankunftszeit.get().strip()
    abreisedatum = entry_abreisedatum.get().strip()
    abreisezeit = entry_abreisezeit.get().strip()
    bemerkung = text_bemerkung.get("1.0", tk.END).strip()
    eintrittsverbot = var_verbot.get()
    verbot_grund = entry_verbot_grund.get().strip()
    verbot_von = entry_verbot_von.get().strip()
    verbot_bis = entry_verbot_bis.get().strip()

    if not (vorname and nachname and geburtsdatum):
        messagebox.showerror("Fehler", "Vorname, Nachname und Geburtsdatum sind Pflichtfelder.")
        return

    maske = (df["Vorname"].str.lower() == vorname.lower()) & \
            (df["Nachname"].str.lower() == nachname.lower()) & \
            (df["Geburtsdatum"].astype(str) == geburtsdatum)

    if maske.any():
        eintrag = df.loc[maske].iloc[0]
        if eintrag["Eintrittsverbot"]:
            msg = f"Besucher hat ein Eintrittsverbot!\nGrund: {eintrag['VerbotGrund']}\n" \
                  f"Von: {eintrag['VerbotVon']} Bis: {eintrag['VerbotBis']}"
            messagebox.showwarning("Eintrittsverbot", msg)

        neuer_eintrag = {
            "Vorname": vorname,
            "Nachname": nachname,
            "Geburtsdatum": geburtsdatum,
            "Ankunftsdatum": ankunftsdatum,
            "Ankunftszeit": ankunftszeit,
            "Abreisedatum": abreisedatum,
            "Abreisezeit": abreisezeit,
            "Bemerkung": bemerkung,
            "Eintrittsverbot": eintrittsverbot,
            "VerbotGrund": verbot_grund,
            "VerbotVon": verbot_von,
            "VerbotBis": verbot_bis
        }
        df = df.append(neuer_eintrag, ignore_index=True)
    else:
        neuer_eintrag = {
            "Vorname": vorname,
            "Nachname": nachname,
            "Geburtsdatum": geburtsdatum,
            "Ankunftsdatum": ankunftsdatum,
            "Ankunftszeit": ankunftszeit,
            "Abreisedatum": abreisedatum,
            "Abreisezeit": abreisezeit,
            "Bemerkung": bemerkung,
            "Eintrittsverbot": eintrittsverbot,
            "VerbotGrund": verbot_grund,
            "VerbotVon": verbot_von,
            "VerbotBis": verbot_bis
        }
        df = df.append(neuer_eintrag, ignore_index=True)

    df.to_excel(EXCEL_DATEI, index=False)
    messagebox.showinfo("Erfolg", "Daten wurden gespeichert.")
    formular_anzeigen()

def formular_anzeigen():
    entry_vorname.delete(0, tk.END)
    entry_nachname.delete(0, tk.END)
    entry_geburtsdatum.delete(0, tk.END)
    entry_ankunftsdatum.delete(0, tk.END)
    entry_ankunftszeit.delete(0, tk.END)
    entry_abreisedatum.delete(0, tk.END)
    entry_abreisezeit.delete(0, tk.END)
    text_bemerkung.delete("1.0", tk.END)
    var_verbot.set(False)
    entry_verbot_grund.delete(0, tk.END)
    entry_verbot_von.delete(0, tk.END)
    entry_verbot_bis.delete(0, tk.END)

root = tk.Tk()
root.title("Besucher-Registrierung")

tk.Label(root, text="Vorname:").grid(row=0, column=0, sticky="e")
entry_vorname = tk.Entry(root)
entry_vorname.grid(row=0, column=1)

tk.Label(root, text="Nachname:").grid(row=1, column=0, sticky="e")
entry_nachname = tk.Entry(root)
entry_nachname.grid(row=1, column=1)

tk.Label(root, text="Geburtsdatum (YYYY-MM-DD):").grid(row=2, column=0, sticky="e")
entry_geburtsdatum = tk.Entry(root)
entry_geburtsdatum.grid(row=2, column=1)

tk.Label(root, text="Ankunftsdatum (YYYY-MM-DD):").grid(row=3, column=0, sticky="e")
entry_ankunftsdatum = tk.Entry(root)
entry_ankunftsdatum.grid(row=3, column=1)

tk.Label(root, text="Ankunftszeit (HH:MM):").grid(row=4, column=0, sticky="e")
entry_ankunftszeit = tk.Entry(root)
entry_ankunftszeit.grid(row=4, column=1)

tk.Label(root, text="Abreisedatum (YYYY-MM-DD):").grid(row=5, column=0, sticky="e")
entry_abreisedatum = tk.Entry(root)
entry_abreisedatum.grid(row=5, column=1)

tk.Label(root, text="Abreisezeit (HH:MM):").grid(row=6, column=0, sticky="e")
entry_abreisezeit = tk.Entry(root)
entry_abreisezeit.grid(row=6, column=1)

tk.Label(root, text="Bemerkung:").grid(row=7, column=0, sticky="ne")
text_bemerkung = tk.Text(root, height=3, width=30)
text_bemerkung.grid(row=7, column=1)

var_verbot = tk.BooleanVar()
check_verbot = tk.Checkbutton(root, text="Eintrittsverbot", variable=var_verbot)
check_verbot.grid(row=8, column=1, sticky="w")

tk.Label(root, text="Grund für Verbot:").grid(row=9, column=0, sticky="e")
entry_verbot_grund = tk.Entry(root)
entry_verbot_grund.grid(row=9, column=1)

tk.Label(root, text="Verbot von (YYYY-MM-DD):").grid(row=10, column=0, sticky="e")
entry_verbot_von = tk.Entry(root)
entry_verbot_von.grid(row=10, column=1)

tk.Label(root, text="Verbot bis (YYYY-MM-DD):").grid(row=11, column=0, sticky="e")
entry_verbot_bis = tk.Entry(root)
entry_verbot_bis.grid(row=11, column=1)

btn_speichern = tk.Button(root, text="Speichern", command=daten_speichern)
btn_speichern.grid(row=12, column=1, pady=10)

root.mainloop()
