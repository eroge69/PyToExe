import os
import glob
import tkinter as tk
from tkinter import filedialog

def swap_chron_norm(input_folder):
    # Utwórz folder 'norchr', jeśli nie istnieje
    output_folder = os.path.join(input_folder, 'norchr')
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    
    # Znajdź wszystkie pliki XML w folderze
    xml_files = glob.glob(os.path.join(input_folder, '*.xml'))
    
    for xml_file in xml_files:
        # Odczytaj zawartość pliku
        with open(xml_file, 'r', encoding='utf-8') as file:
            content = file.read()
        
        # Użyj tymczasowego zamiennika, aby uniknąć kolizji
        content = content.replace('chron', 'TEMPORARY')
        content = content.replace('norm', 'chron')
        content = content.replace('TEMPORARY', 'norm')
        
        # Utwórz ścieżkę do zapisu w folderze 'norchr'
        output_file = os.path.join(output_folder, os.path.basename(xml_file))
        
        # Zapisz zmodyfikowany plik
        with open(output_file, 'w', encoding='utf-8') as file:
            file.write(content)
        
        print(f"Przetworzono: {xml_file} -> {output_file}")

if __name__ == "__main__":
    # Utwórz główne okno Tkinter (ukryte)
    root = tk.Tk()
    root.withdraw()  # Ukryj główne okno
    
    # Otwórz okno dialogowe do wyboru folderu
    folder_path = filedialog.askdirectory(title="Wybierz folder z plikami XML")
    
    # Sprawdź, czy wybrano folder
    if folder_path:
        swap_chron_norm(folder_path)
        input("Naciśnij Enter, aby zamknąć...")

    else:
        print("Nie wybrano folderu.")
        input("Naciśnij Enter, aby zamknąć...")

    
    # Zniszcz obiekt Tkinter
    root.destroy()