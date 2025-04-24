import os
import pandas as pd
import shutil
from pathlib import Path
from datetime import datetime

def data_analyzer():
    # Benutzeraufforderung f�r den Pfad
    path = input("Geben Sie den Pfad zur Dokumentenstruktur ein: ")

    # Funktion zum rekursiven Durchsuchen von Verzeichnissen
    def list_files(startpath):
        file_list = []
        for root, dirs, files in os.walk(startpath):
            for name in files:
                file_path = os.path.join(root, name)
                # Informationen �ber die Datei sammeln
                file_size_bytes = os.path.getsize(file_path)  # Gr��e in Bytes
                file_size_mbytes = file_size_bytes / (1024 * 1024)  # Gr��e in Megabytes
                modification_time = os.path.getmtime(file_path)  # Zeitstempel der letzten �nderung
                # Umwandlung des Zeitstempels in ein lesbares Datumsformat
                modification_time_readable = datetime.fromtimestamp(modification_time).strftime('%Y-%m-%d %H:%M:%S')
                # Relativen Pfad berechnen
                relative_path = os.path.relpath(file_path, startpath)
                # Dateiendung extrahieren
                file_extension = os.path.splitext(name)[1]  # Die Dateiendung (inklusive Punkt)
                # Hinzuf�gen der Informationen zur Liste
                file_list.append((relative_path, modification_time_readable, file_size_mbytes, file_extension))
        return file_list

    # �berpr�fen, ob der Pfad existiert
    if os.path.exists(path):
        # Auflisten aller Dateien und Verzeichnisse
        all_files = list_files(path)

        # Benutzeraufforderung f�r den Speicherort der Excel-Datei
        excel_path = input("Geben Sie den Pfad zum Speichern der Excel-Datei ein (z.B. C:\\Pfad\\Dateiliste.xlsx): ")

        # �berpr�fen, ob der Pfad die Endung .xlsx hat
        if not excel_path.endswith('.xlsx'):
            print("Bitte geben Sie einen gueltigen Excel-Dateipfad mit der Endung .xlsx an.")
            return

        # Erstellen eines DataFrames von den Ergebnissen
        df = pd.DataFrame(all_files, columns=["Pfad", "Letzte Aenderung", "Groesse (MB)", "Dateiendung"])
        # Exportieren in die angegebene Excel-Datei
        df.to_excel(excel_path, index=False)
        print(f"Die Dateiliste wurde erfolgreich in {excel_path} gespeichert.")
    else:
        print(f"Der angegebene Pfad existiert nicht: {path}")

def folder_creator():
    def load_excel(file_path):
        return pd.read_excel(file_path, header=None)

    def create_folders(data, target_path):
        for index, row in data.iterrows():
            folder_a = row[0] if pd.notna(row[0]) else None
            folder_b = row[1] if pd.notna(row[1]) else None
            folder_c = row[2] if pd.notna(row[2]) else None

            if folder_a:
                a_path = os.path.join(target_path, folder_a)
                os.makedirs(a_path, exist_ok=True)
            if folder_b:
                b_path = os.path.join(a_path, folder_b)
                os.makedirs(b_path, exist_ok=True)
            if folder_c:
                c_path = os.path.join(b_path, folder_c)
                os.makedirs(c_path, exist_ok=True)

    excel_path = input("Geben Sie den Pfad zur Excel-Datei ein: ")
    target_path = input("Geben Sie den Zielpfad fuer die Ordnerstruktur ein: ")
    data = load_excel(excel_path)

    # �berpr�fen, ob der Zielpfad bereits existiert
    if any(os.listdir(target_path)):
        action = input("Es existiert bereits eine Ordnerstruktur. Moechten Sie: 1. Neue Struktur erstellen oder 2. Nichts machen? (1/2): ")
        if action == "1":
            create_folders(data.iloc[2:], target_path)
            print("Ordnerstruktur erfolgreich erstellt.")
        else:
            print("Keine Ordnerstruktur erstellt.")
    else:
        create_action = input("Es existiert keine Ordnerstruktur. Moechten Sie eine neue Struktur erstellen? (ja/nein): ")
        if create_action.lower() in ['ja', 'j']:
            create_folders(data.iloc[2:], target_path)
            print("Ordnerstruktur erfolgreich erstellt.")
        else:
            print("Keine Ordnerstruktur erstellt.")


def copy_folder():
    def copy_structure(src, dest):
        for item in os.listdir(src):
            src_path = os.path.join(src, item)
            dest_path = os.path.join(dest, item)

            try:
                if os.path.isdir(src_path):  # Wenn es ein Ordner ist
                    if os.path.exists(dest_path):
                        # Wenn der Ordner im Zielverzeichnis existiert, kopiere den Inhalt
                        print(f"Kopiere Inhalt von '{src_path}' nach '{dest_path}'")
                        copy_structure(src_path, dest_path)
                    else:
                        # Wenn der Ordner nicht existiert, kopiere ihn mit "_OLD"
                        new_dest_path = dest_path + "_OLD"
                        print(f"Kopiere '{src_path}' nach '{new_dest_path}'")
                        shutil.copytree(src_path, new_dest_path)
                else:  # Wenn es eine Datei ist
                    if os.path.exists(dest_path):
                        print(f"Die Datei '{dest_path}' existiert bereits. Sie wird uebersprungen.")
                    else:
                        print(f"Kopiere Datei '{src_path}' nach '{dest_path}'")
                        shutil.copy2(src_path, dest_path)
            except Exception as e:
                print(f"Fehler beim Kopieren von '{src_path}': {e}")

    src_path = input("Geben Sie den Pfad zur alten Ordnerstruktur ein: ")
    dest_path = input("Geben Sie den Pfad zur neuen Ordnerstruktur ein: ")

    if not os.path.exists(src_path):
        print("Der angegebene Quellordner existiert nicht.")
        return
    if not os.path.exists(dest_path):
        print("Der angegebene Zielordner existiert nicht. Er wird erstellt.")
        os.makedirs(dest_path)

    copy_structure(src_path, dest_path)
    print("Kopieroperation abgeschlossen.")

def main():
    print("Waehlen Sie eine Option:")
    print("1) Data Analyzer")
    print("2) Folder Creator")
    print("3) Copy Folder")
    
    choice = input("Geben Sie Ihre Wahl ein (1/2/3): ")

    if choice == "1":
        data_analyzer()
    elif choice == "2":
        folder_creator()
    elif choice == "3":
        copy_folder()
    else:
        print("Ungueltige Auswahl. Bitte versuchen Sie es erneut.")

if __name__ == "__main__":
    main()