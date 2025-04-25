from openpyxl import load_workbook

sciezka_excel = r"C:\Users\Automatics\Desktop\Nowy folder\Spare Parts NEW - kopia.xlsx"
nazwa_arkusza = "Arkusz1"
kolumna_id = 0       # kolumna A
kolumna_ilosc = 8    # kolumna I

def zmniejsz_ilosc(kod_z_qr):
    try:
        wb = load_workbook(sciezka_excel)
        ws = wb[nazwa_arkusza]

        for row in ws.iter_rows(min_row=2):
            cell_value = str(row[kolumna_id].value).strip() if row[kolumna_id].value is not None else ""
            if cell_value == kod_z_qr.strip():
                ilosc = row[kolumna_ilosc].value
                if isinstance(ilosc, (int, float)) and ilosc > 0:
                    row[kolumna_ilosc].value = ilosc - 1
                    wb.save(sciezka_excel)
                break
    except:
        pass  # Ciche działanie bez komunikatów

# Główna pętla
while True:
    try:
        kod_z_qr = input().strip()
        if kod_z_qr.lower() == "exit":
            break
        zmniejsz_ilosc(kod_z_qr)
    except:
        break


