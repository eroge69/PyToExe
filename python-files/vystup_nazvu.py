import os
import re

# Nastav si priečinok, kde máš .strm súbory
PRIECINOK = os.path.dirname(os.path.abspath(__file__))  # aktuálny priečinok

# Ktoré jazyky/dabingy budeme hľadať
DABINGY = ['CZ', 'SK', 'EN']

# Zoznam pre výstup
vystup = []

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

# Zapíš do vystup.txt
with open(os.path.join(PRIECINOK, 'vystup.txt'), 'w', encoding='utf-8') as f:
    for riadok in vystup:
        f.write(riadok + '\n')

print("Hotovo! Výstup uložený do 'vystup.txt'.")
input("Stlač Enter pre ukončenie...")
