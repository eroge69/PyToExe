import os
import getpass
import pandas as pd

# Aktueller Benutzername
user = getpass.getuser()

# Pfade
input_excel = fr"C:\Users\{user}\CMM_ABAQUS_MATERIAL_DATABASE\Material_Database.xlsx"
output_folder = fr"C:\Users\{user}\Desktop\Hyperview_Legends"

# Zielordner erstellen, falls nicht vorhanden
os.makedirs(output_folder, exist_ok=True)

# Excel einlesen (nur der Reiter "Isotropic Materials")
df = pd.read_excel(input_excel, sheet_name="Isotropic Materials", header=0)

# Schleife über Materialien
for index, row in df.iterrows():
    material = str(row.iloc[0]).strip()
    yield_stress = row.iloc[4]
    uts = row.iloc[5]

    if pd.isna(material) or pd.isna(yield_stress) or pd.isna(uts):
        continue

    # Legendenwerte
    max_value = uts + 100
    values = [0, yield_stress, uts, max_value]

    # Safe Dateiname
    safe_material_name = material.replace(" ", "_").replace("/", "_")
    tcl_filename = os.path.join(output_folder, f"{safe_material_name}.tcl")

    # TCL Inhalt generieren (ohne Kommentare und mit korrekter Struktur)
    tcl_content = f'''proc ::post::LoadSettings {{ legend_handle }} {{ 
 $legend_handle SetType user 
 $legend_handle SetFilter Linear
 $legend_handle SetPosition upperleft
 $legend_handle SetNumericFormat "fixed"
 $legend_handle SetNumericPrecision "0"
 $legend_handle SetReverseEnable false
 $legend_handle SetSeparatorWidth 0
 $legend_handle SetNumberOfColors 9 
 $legend_handle SetColor 0 "165 165 165" 
 $legend_handle SetColor 1 " 21 121 255" 
 $legend_handle SetColor 2 "  0 199 221" 
 $legend_handle SetColor 3 " 40 255 185" 
 $legend_handle SetColor 4 " 57 255   0" 
 $legend_handle SetColor 5 "170 255   0" 
 $legend_handle SetColor 6 "255 227   0" 
 $legend_handle SetColor 7 "255 113   0" 
 $legend_handle SetColor 8 "112  48 160" 
 $legend_handle SetColor 9 "192 192 192" 
 $legend_handle OverrideValue 7 {yield_stress} true
 $legend_handle OverrideValue 8 {uts} true
 $legend_handle OverrideValue 9 {max_value} false
 $legend_handle GetHeaderAttributeHandle attr_handle 
 attr_handle SetVisibility false
 catch {{ attr_handle SetFont "Noto Sans"}};
 attr_handle SetHeight 10
 attr_handle SetColor "255 255 255" 
 attr_handle SetSlant "regular" 
 attr_handle SetWeight "regular" 
 attr_handle ReleaseHandle 
 $legend_handle GetTitleAttributeHandle attr_handle 
 attr_handle SetVisibility true
 catch {{ attr_handle SetFont "Noto Sans"}};
 attr_handle SetHeight 20
 attr_handle SetColor "255 255 255" 
 attr_handle SetSlant "regular" 
 attr_handle SetWeight "regular" 
 attr_handle ReleaseHandle 
 $legend_handle GetNumberAttributeHandle attr_handle 
 catch {{ attr_handle SetFont "Noto Sans"}};
 attr_handle SetHeight 28
 attr_handle SetColor "255 255 255" 
 attr_handle SetSlant "regular" 
 attr_handle SetWeight "regular" 
 attr_handle ReleaseHandle 
 $legend_handle SetMinMaxVisibility false max
 $legend_handle SetMinMaxVisibility false min
 $legend_handle SetMinMaxVisibility false max_local
 $legend_handle SetMinMaxVisibility false min_local
 $legend_handle SetMinMaxVisibility true entity
 $legend_handle SetMinMaxVisibility false bymodel
 $legend_handle SetTransparency true 
 $legend_handle SetBackgroundColor " 44  85 126" 
 $legend_handle GetFooterAttributeHandle attr_handle 
 attr_handle SetVisibility false
 catch {{ attr_handle SetFont "Noto Sans"}};
 attr_handle SetHeight 10
 attr_handle SetColor "255 255 255" 
 attr_handle SetSlant "regular" 
 attr_handle SetWeight "regular" 
 attr_handle ReleaseHandle 
 }} 
'''

    # Schreiben oder Überschreiben der Datei
    with open(tcl_filename, 'w', encoding='utf-8') as f:
        f.write(tcl_content)

print(f"Alle TCL-Dateien erfolgreich erstellt in:\n{output_folder}")
