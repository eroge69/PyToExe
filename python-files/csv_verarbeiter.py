import csv
import os
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk

def convert_type(value):
    """Bestimmt den Datentyp basierend auf dem Präfix."""
    if value.startswith('R'):
        return 'float'
    elif value.startswith('X'):
        return 'bit'
    elif value.startswith('I'):
        return 'int'
    elif value.startswith('S'):
        return 'varchar(50)'
    elif value.startswith('WORD'):
        return 'int'  # WORD wird als int behandelt
    elif value.startswith('D'):
        return 'bigint'  # D wird als bigint behandelt
    else:
        return 'unknown'

def process_csv(input_file, output_file, database_name, table_name):
    with open(input_file, mode='r', newline='', encoding='utf-8') as infile, open(output_file, mode='w', encoding='utf-8') as outfile:
        reader = csv.reader(infile, delimiter=',')  # Hier bleibt der Delimiter ein Komma

        # Hinzufügen der ersten beiden Zeilen
        outfile.write(f'USE [{database_name}]\n')
        outfile.write('GO\n')
        outfile.write('SET ANSI_NULLS ON\n')
        outfile.write('GO\n')
        outfile.write('SET QUOTED_IDENTIFIER ON\n')
        outfile.write('GO\n')
        outfile.write(f'CREATE TABLE [dbo].[{table_name}](\n')  # Verwendung des variablen Tabellennamens
        outfile.write('[ID] [int] IDENTITY(1,1) NOT NULL,\n')
        outfile.write('[UTC_CREATED] [datetime2](0) NULL,\n')

        for row in reader:
            print(f'Gelesene Zeile: {row}')  # Debugging-Ausgabe
            if len(row) < 2:
                print('Überspringe leere Zeile oder ungültige Daten.')
                continue  # Überspringe leere Zeilen oder ungültige Daten
            
            # Splitten der zweiten Spalte, um Adresse und Variable zu trennen
            address_variable = row[1].split(';')
            if len(address_variable) != 2:
                print(f'Ungültiges Format in Zeile: {row}')
                continue
            
            address = address_variable[0].strip()
            variable = address_variable[1].strip()
            data_type = convert_type(address)
            if data_type != 'unknown':
                # Formatierung der Ausgabezeile mit Komma
                output_line = f'[{variable}] [{data_type}] NULL,\n'
                outfile.write(output_line)  # Schreibe die formatierte Zeile
                print(f'Schreibe: {output_line}')  # Debugging-Ausgabe
            else:
                print(f'Ungültiger Datentyp für Adresse: {address}')

        # Hinzufügen der "END"-Zeile
        outfile.write(') ON [PRIMARY]\n')
        outfile.write('GO\n')

def select_input_file():
    """Öffnet einen Dialog zur Auswahl der Eingabedatei."""
    input_file = filedialog.askopenfilename(title="Wählen Sie die Eingabedatei", filetypes=[("CSV-Dateien", "*.csv")])
    input_entry.delete(0, tk.END)  # Löschen des vorherigen Texts
    input_entry.insert(0, input_file)  # Einfügen des ausgewählten Dateipfads

def select_output_directory():
    """Öffnet einen Dialog zur Auswahl des Speicherorts für die Ausgabedatei."""
    output_directory = filedialog.askdirectory(title="Wählen Sie den Speicherort für die Ausgabedatei")
    if output_directory:
        input_file = input_entry.get()
        if input_file:
            # Den Dateinamen von der Eingabedatei extrahieren und die Erweiterung ändern
            base_name = os.path.basename(input_file)
            # Entfernen des Präfixes "s7endpoint_"
            if base_name.startswith("s7endpoint_"):
                output_file_name = base_name[len("s7endpoint_"):].replace(".csv", ".txt")
            else:
                output_file_name = os.path.splitext(base_name)[0] + ".txt"  # Standardverhalten, falls kein Präfix vorhanden
            output_file_path = os.path.join(output_directory, output_file_name)
            output_entry.delete(0, tk.END)  # Löschen des vorherigen Texts
            output_entry.insert(0, output_file_path)  # Einfügen des vollständigen Pfads der Ausgabedatei

def process_files():
    """Verarbeitet die ausgewählten Dateien."""
    input_file = input_entry.get()
    output_file = output_entry.get()
    database_name = database_var.get()  # Datenbankname aus dem Dropdown-Menü abrufen
    table_name = table_entry.get()  # Tabellennamen aus dem Eingabefeld abrufen
    
    if not input_file or not database_name or not table_name:
        messagebox.showerror("Fehler", "Bitte wählen Sie eine Eingabedatei, eine Datenbank und geben Sie einen Tabellennamen ein.")
        return

    # Wenn kein Ausgabeverzeichnis ausgewählt wurde, setze das Ausgabeverzeichnis auf das Verzeichnis der Eingabedatei
    if not output_file:
        output_directory = os.path.dirname(input_file)
        base_name = os.path.basename(input_file)
        if base_name.startswith("s7endpoint_"):
            output_file_name = base_name[len("s7endpoint_"):].replace(".csv", ".txt")
        else:
            output_file_name = os.path.splitext(base_name)[0] + ".txt"  # Standardverhalten, falls kein Präfix vorhanden
        output_file = os.path.join(output_directory, output_file_name)

    # Verarbeiten der CSV-Datei
    try:
        process_csv(input_file, output_file, database_name, table_name)
        messagebox.showinfo("Erfolg", f"Die Datei {output_file} wurde erfolgreich erstellt.")
    except Exception as e:
        messagebox.showerror("Fehler", f"Ein Fehler ist aufgetreten: {str(e)}")

# GUI erstellen
root = tk.Tk()
root.title("S7/TIA zu SQL Query")

# Eingabefeld für die Eingabedatei
input_label = tk.Label(root, text="Eingabedatei:")
input_label.pack()
input_entry = tk.Entry(root, width=50)
input_entry.pack()
input_button = tk.Button(root, text="Durchsuchen...", command=select_input_file)
input_button.pack()

# Eingabefeld für die Ausgabedatei
output_label = tk.Label(root, text="Ausgabeverzeichnis:")
output_label.pack()
output_entry = tk.Entry(root, width=50)
output_entry.pack()
output_button = tk.Button(root, text="Ordner auswählen...", command=select_output_directory)
output_button.pack()

# Dropdown-Menü für die Auswahl der Datenbank
database_label = tk.Label(root, text="Datenbank auswählen:")
database_label.pack()

# Dropdown Optionen
database_options = ["FuelCell_Honda_QS", "FuelCell_Honda_Report", "FuelCell_hvl_Dev", "FuelCell_hvl_Prod", "FuelCell_hvl_QS", "FuelCell_hvl_Report", "fuelcell_pilotlinie"]
database_var = tk.StringVar(value=database_options[0])  # Standardwert

# Dropdown Menü erstellen
database_menu = tk.OptionMenu(root, database_var, *database_options)
database_menu.pack()

# Eingabefeld für den Tabellennamen
table_label = tk.Label(root, text="Tabellenname:")
table_label.pack()
table_entry = tk.Entry(root, width=50)
table_entry.pack()

# Verarbeiten-Button
process_button = tk.Button(root, text="Verarbeiten", command=process_files)
process_button.pack()

# Hauptschleife der GUI
root.mainloop()