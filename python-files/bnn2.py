
import os
import pandas as pd # Konvention: Pandas als 'pd' importieren
from pathlib import Path
aktuelles_verzeichnis=os.getcwd()
vzmodern=str(Path.cwd())+'\\bnn.txt.txt'
print("Verz"+aktuelles_verzeichnis)
print(vzmodern)
datei_pfad = r'c:\\bnn\\bnn.txt.txt'
try:
    # CSV direkt in einen Pandas DataFrame einlesen
    # Pandas versucht, Trennzeichen und Header oft automatisch zu erkennen!
    # Ggf. muss man delimiter=';' oder andere Parameter angeben.
    daten_df = pd.read_csv(vzmodern, encoding='latin1', delimiter=';', skiprows=1, decimal=',', header=None, usecols=[4, 36, 37, 38])
    # Zeige die ersten 5 Zeilen des DataFrames an
    print("\n--- Daten gelesen mit Pandas (erste 5 Zeilen): ---")
    # print(daten_df.head(20))
    df=pd.DataFrame(daten_df)
    df=df.dropna(subset=4)
    df[4]=df[4].astype("int64")
    df[39]=df[36]+0.2
    
    df[39]=df[39].round(2)
   # print(daten_df.columns)

    
    print(daten_df.head(20))
    print(daten_df.columns)  # Welche Spalten gibt es?

    

   # print(daten_df.dtypes)

    
   
    
    
    # leere EAN Spalten überspringen
    
except FileNotFoundError:
    print(f"FEHLER: Die Datei '{datei_pfad}' wurde nicht gefunden.")
except pd.errors.EmptyDataError: # Spezifischer Pandas-Fehler für leere Dateien
    print(f"FEHLER: Die Datei '{datei_pfad}' ist leer.")
except Exception as e:
    print(f"FEHLER beim Lesen mit Pandas: {e}")

df.to_csv(str(vzmodern)+'ausgabe.txt', decimal=',',sep=";", header=False, index=False)


    # Users\cbuch\OneDrive - C & M Buch GmbH\Desktop\dennree

    #spalte leer noch beachten
