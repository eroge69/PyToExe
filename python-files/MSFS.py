import os
import time
import subprocess

# Ścieżki do skrótów
base_path = r"C:\Users\PC\Desktop\MSFS"
shortcuts = {
    "map_enhancement": os.path.join(base_path, "MSFS2020_Map_Enhancement.lnk"),
    "fs_realistic": os.path.join(base_path, "FSRealistic.lnk"),
    "couatl": os.path.join(base_path, "Couatl64_MSFS.lnk"),
    "flight_sim": os.path.join(base_path, "MicrosoftFlightSimulator.lnk"),
    "raas_pro": os.path.join(base_path, "RAASProMSFS.lnk")
}

# Funkcja do uruchamiania skrótu
def run_shortcut(path):
    try:
        subprocess.Popen(['cmd', '/c', 'start', '', path], shell=True)
        print(f"Uruchomiono: {path}")
    except Exception as e:
        print(f"Błąd przy uruchamianiu {path}: {e}")

# Uruchomienie pierwszych trzech programów
run_shortcut(shortcuts["map_enhancement"])
run_shortcut(shortcuts["fs_realistic"])
run_shortcut(shortcuts["couatl"])

# Czekaj 15 sekund
time.sleep(15)

# Uruchom Microsoft Flight Simulator
run_shortcut(shortcuts["flight_sim"])

# Czekaj 5 minut
time.sleep(300)

# Uruchom RAAS Pro
run_shortcut(shortcuts["raas_pro"])