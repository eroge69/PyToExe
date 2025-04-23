import os
import re
import requests
import pandas as pd
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from openpyxl.utils import column_index_from_string
import tkinter as tk
from tkinter import filedialog, simpledialog, messagebox, ttk

# === PDF letöltés ===
def keres_es_letolt_datasheet(url, cel_konyvtar, log_fajl):
    try:
        resp = requests.get(url, timeout=10)
        soup = BeautifulSoup(resp.text, 'html.parser')

        for a in soup.find_all('a', href=True):
            href = a['href']
            szoveg = a.get_text(strip=True).lower()
            if ('datasheet' in szoveg or 'datasheet' in href.lower()) and href.lower().endswith('.pdf'):
                pdf_url = urljoin(url, href)
                fajlnev = re.sub(r'\W+', '_', a.get_text(strip=True))[:100] + ".pdf"
                fajl_ut = os.path.join(cel_konyvtar, fajlnev)

                pdf_resp = requests.get(pdf_url, timeout=10)
                with open(fajl_ut, 'wb') as f:
                    f.write(pdf_resp.content)

                with open(log_fajl, 'a', encoding='utf-8') as log:
                    log.write(f"SIKERES: {url} -> {fajlnev}\n")

                return True

        with open(log_fajl, 'a', encoding='utf-8') as log:
            log.write(f"NEM TALÁLHATÓ: {url}\n")
        return False
    except Exception as e:
        with open(log_fajl, 'a', encoding='utf-8') as log:
            log.write(f"HIBA: {url} - {str(e)}\n")
        return False

# === GUI alkalmazás ===
def futtat():
    root = tk.Tk()
    root.withdraw()

    excel_path = filedialog.askopenfilename(title="Excel fájl kiválasztása", filetypes=[("Excel files", "*.xlsx")])
    if not excel_path:
        return

    oszlop_betu = simpledialog.askstring("Oszlop kiválasztása", "Add meg az URL-eket tartalmazó oszlop betűjét (pl. C):")
    if not oszlop_betu:
        return

    cel_konyvtar = filedialog.askdirectory(title="Könyvtár kiválasztása PDF-ek mentéséhez")
    if not cel_konyvtar:
        return

    os.makedirs(cel_konyvtar, exist_ok=True)
    log_fajl = os.path.join(cel_konyvtar, "letoltes_log.txt")
    try:
        df = pd.read_excel(excel_path, engine='openpyxl')
        oszlop_index = column_index_from_string(oszlop_betu.upper()) - 1
        url_lista = df.iloc[:, oszlop_index].dropna().tolist()
    except Exception as e:
        messagebox.showerror("Hiba", f"Hiba az Excel feldolgozásakor: {e}")
        return

    # GUI progress bar
    progress_root = tk.Tk()
    progress_root.title("Letöltés folyamatban...")
    ttk.Label(progress_root, text="Letöltés folyamatban...").pack(padx=20, pady=10)
    progress = ttk.Progressbar(progress_root, maximum=len(url_lista), mode='determinate')
    progress.pack(padx=20, pady=10)
    progress_root.update()

    sikeres = 0
    for i, url in enumerate(url_lista):
        if keres_es_letolt_datasheet(url, cel_konyvtar, log_fajl):
            sikeres += 1
        progress['value'] = i + 1
        progress_root.update()

    progress_root.destroy()
    messagebox.showinfo("Kész", f"Letöltés kész: {sikeres} fájl letöltve.\nRészletek: letoltes_log.txt")

if __name__ == '__main__':
    futtat()
