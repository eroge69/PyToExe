import threading
import tkinter as tk
from tkinter import simpledialog, filedialog, messagebox, scrolledtext, Toplevel, Text
import os
import json
import time
import math
import datetime
import requests
import webbrowser

# -------- Konfiguration --------
STARTKOORDINATEN = (50.767500, 6.082250)  # Beethovenstraße Ecke Südstraße Aachen
GESPERRTE_DATEI = "genutzte_sehenswuerdigkeiten.json"
LETZTER_SPEICHERPFAD_DATEI = "letzter_speicherpfad.txt"

# -------- Globale Variablen --------
letzter_speicherpfad = None
genutzte_sehenswuerdigkeiten = set()

# -------- Hilfsfunktionen --------
def lade_genutzte_sehenswuerdigkeiten():
    global genutzte_sehenswuerdigkeiten
    if os.path.exists(GESPERRTE_DATEI):
        try:
            with open(GESPERRTE_DATEI, "r", encoding="utf-8") as f:
                genutzte_sehenswuerdigkeiten = set(json.load(f))
        except Exception as e:
            print(f"Fehler beim Laden der genutzten Sehenswürdigkeiten: {e}")

def speichere_genutzte_sehenswuerdigkeiten():
    try:
        serialisierbare_liste = [str(e) for e in genutzte_sehenswuerdigkeiten]
        with open(GESPERRTE_DATEI, "w", encoding="utf-8") as f:
            json.dump(serialisierbare_liste, f)
    except Exception as e:
        print(f"Fehler beim Speichern der genutzten Sehenswürdigkeiten: {e}")

def lade_letzten_speicherpfad():
    global letzter_speicherpfad
    if os.path.exists(LETZTER_SPEICHERPFAD_DATEI):
        try:
            with open(LETZTER_SPEICHERPFAD_DATEI, "r", encoding="utf-8") as f:
                letzter_speicherpfad = f.read().strip()
                if not os.path.isdir(letzter_speicherpfad):
                    letzter_speicherpfad = None
        except Exception as e:
            print(f"Fehler beim Laden des letzten Speicherpfads: {e}")

def speichere_letzten_speicherpfad(pfad):
    global letzter_speicherpfad
    letzter_speicherpfad = pfad
    try:
        with open(LETZTER_SPEICHERPFAD_DATEI, "w", encoding="utf-8") as f:
            f.write(pfad)
    except Exception as e:
        print(f"Fehler beim Speichern des Speicherpfads: {e}")

def entfernung_km(coord1, coord2):
    lat1, lon1 = coord1
    lat2, lon2 = coord2
    R = 6371.0
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)
    a = math.sin(delta_phi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

# -------- APIs --------
def suche_sehenswuerdigkeit(umkreis_km):
    try:
        lat, lon = STARTKOORDINATEN
        lat_radius = umkreis_km / 111.0
        lon_radius = umkreis_km / (111.0 * math.cos(math.radians(lat)))
        viewbox = f"{lon - lon_radius},{lat + lat_radius},{lon + lon_radius},{lat - lat_radius}"

        url = f"https://nominatim.openstreetmap.org/search?format=json&q=attraction&limit=50&bounded=1&viewbox={viewbox}"
        headers = {"User-Agent": "MotorradtourenPlaner"}
        response = requests.get(url, headers=headers)
        ergebnisse = response.json()
        for eintrag in ergebnisse:
            name = eintrag.get("display_name")
            lat = float(eintrag.get("lat"))
            lon = float(eintrag.get("lon"))
            distanz = entfernung_km(STARTKOORDINATEN, (lat, lon))
            if isinstance(name, str) and name not in genutzte_sehenswuerdigkeiten and 20 <= distanz <= umkreis_km:
                genutzte_sehenswuerdigkeiten.add(name)
                speichere_genutzte_sehenswuerdigkeiten()
                return (name, lat, lon)
    except Exception as e:
        print(f"Fehler bei der Sehenswürdigkeitensuche: {e}")
    return None

# -------- GUI --------
def generiere_tour():
    try:
        umkreis_str = simpledialog.askstring("Umkreis", "Gib den Umkreis in km an:")
        if umkreis_str is None:
            return
        umkreis_km = int(umkreis_str)
        if umkreis_km <= 0:
            raise ValueError("Ungültiger Umkreis")

        status_label.config(text="Suche nach Sehenswürdigkeit...")
        root.update()

        ergebnis = suche_sehenswuerdigkeit(umkreis_km)
        if ergebnis:
            name, lat, lon = ergebnis
            status_label.config(text=f"Gefunden: {name}")
            webbrowser.open(f"https://www.google.com/maps/dir/?api=1&origin={STARTKOORDINATEN[0]},{STARTKOORDINATEN[1]}&destination={lat},{lon}&travelmode=driving")
        else:
            status_label.config(text="Keine Sehenswürdigkeit gefunden.")

    except Exception as e:
        status_label.config(text=f"Fehler: {e}")


def starte_gui():
    global root, status_label
    root = tk.Tk()
    root.title("Rezas Tourgenerator")

    frame = tk.Frame(root, padx=20, pady=20)
    frame.pack()

    titel = tk.Label(frame, text="Motorradtour mit Sehenswürdigkeit", font=("Arial", 16))
    titel.pack(pady=(0, 10))

    button = tk.Button(frame, text="Tour generieren", font=("Arial", 12), command=generiere_tour)
    button.pack(pady=(0, 10))

    status_label = tk.Label(frame, text="Bereit.", font=("Arial", 10))
    status_label.pack()

    root.mainloop()

# -------- Start --------
if __name__ == "__main__":
    lade_genutzte_sehenswuerdigkeiten()
    lade_letzten_speicherpfad()
    starte_gui()
