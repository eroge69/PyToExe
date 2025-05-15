import os
import csv

def rename_files(csv_filename):
# Lese die CSV-Datei
    with open(csv_filename, 'r', newline='', encoding='utf-8') as csv_file:
        csv_reader = csv.DictReader(csv_file, delimiter=';')
        barcode_mapping = {row['Barcodenummer']: row['Dateibezeichnung'] for row in csv_reader}

# Durchsuche den aktuellen Ordner nach Dateien
    for filename in os.listdir('.'):
        if os.path.isfile(filename):
# Extrahiere die Barcodenummer aus dem Dateinamen
            barcode, extension = os.path.splitext(filename)

# Überprüfe, ob die Barcodenummer in der CSV-Datei vorhanden ist
            if barcode in barcode_mapping:
                new_filename = barcode_mapping[barcode] + extension

# Umbenenne die Datei
                os.rename(filename, new_filename)
                print(f'{filename} wurde zu {new_filename} umbenannt.')

# Hier den Dateinamen deiner CSV-Datei angeben
csv_filename = 'barcodes.csv'

# Funktionsaufruf
rename_files(csv_filename)
