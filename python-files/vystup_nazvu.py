import os
import re

# Nastav si priečinok, kde máš .strm súbory
PRIECINOK = os.path.dirname(os.path.abspath(__file__))  # aktuálny priečinok

# Ktoré jazyky/dabingy budeme hľadať
DABINGY = ['CZ', 'SK', 'EN']

# Zoznam pre výstup
vystup = []

# Debug výpis priečinku
print(f"Priečinok: {PRIECINOK}")
print("Hľadám .strm súbory...")

# Prejdi všetky .strm súbory v priečinku
for subor in os.listdir(PRIECINOK):
    if subor.lower().endswith('.strm'):
        cesta = os.path.join(PRIECINOK, subor)
        
        # Názov bez prípony
        nazov = os.path.splitext(subor)[0]
        
        # Veľkosť v KB
        velkost_kb = os.path.getsize(cesta) // 1024
        
        # Detekcia dabingu
        dabing = "NEZNÁMY"
        for d in DABINGY:
            if re.search(r'\b' + d + r'\b', nazov, re.IGNORECASE):
                dabing = d
                break
        
        # Zloženie riadku
        riadok = f"{nazov} - {velkost_kb} KB - {dabing}"
        vystup.append(riadok)

# Ak nie sú žiadne súbory, vypíšme varovanie
if not vystup:
    print("Žiadne .strm súbory neboli nájdené.")
else:
    print(f"Spracovaných {len(vystup)} súborov.")

# Zapíš do vystup.txt
vystup_file = os.path.join(PRIECINOK, 'vystup.txt')
with open(vystup_file, 'w', encoding='utf-8') as f:
    for riadok in vystup:
        f.write(riadok + '\n')

# Informovanie o výsledku
print(f"Výstup uložený do '{vystup_file}'.")
input("Stlač Enter pre ukončenie...")
