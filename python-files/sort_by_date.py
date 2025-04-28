import os
import shutil
from datetime import datetime

# Verzeichnis des Skripts
script_dir = os.path.dirname(os.path.abspath(__file__))

# Dateien im Verzeichnis durchlaufen
for filename in os.listdir(script_dir):
    file_path = os.path.join(script_dir, filename)

    # Nur Dateien betrachten, keine Verzeichnisse
    if os.path.isfile(file_path):
        # Änderungsdatum abrufen
        mod_time = os.path.getmtime(file_path)
        mod_date = datetime.fromtimestamp(mod_time).strftime("%d_%m_%Y")

        # Zielverzeichnis erstellen
        target_dir = os.path.join(script_dir, mod_date)
        os.makedirs(target_dir, exist_ok=True)

        # Datei verschieben
        shutil.move(file_path, os.path.join(target_dir, filename))

print("Dateien wurden nach Änderungsdatum sortiert und verschoben.")
