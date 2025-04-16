import os
import csv

def genera_report(directory, report_csv):
    """Genera un report CSV con path assoluto e dimensione in byte"""
    with open(report_csv, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['path', 'size'])  # Intestazione
        for root, _, files in os.walk(directory):
            for name in files:
                full_path = os.path.abspath(os.path.join(root, name))
                try:
                    size = os.path.getsize(full_path)
                    writer.writerow([full_path, size])
                except Exception as e:
                    print(f"Errore su {full_path}: {e}")
    print(f"✅ Report CSV generato: {report_csv}")

def leggi_report_csv(report_csv):
    """Legge un report CSV e restituisce un dizionario path -> size"""
    dati = {}
    with open(report_csv, 'r') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            path = row['path']
            size = int(row['size'])
            dati[path] = size
    return dati

def confronta_report(report_vecchio_csv, report_nuovo_csv):
    """Confronta due report CSV e stampa differenze"""
    vecchio = leggi_report_csv(report_vecchio_csv)
    nuovo = leggi_report_csv(report_nuovo_csv)

    print("\n📋 Differenze tra report:")

    # File aggiunti o modificati
    for path, size_nuovo in nuovo.items():
        if path not in vecchio:
            print(f"🆕 Aggiunto: {path}")
        elif vecchio[path] != size_nuovo:
            print(f"✏️  Modificato: {path} (da {vecchio[path]} a {size_nuovo} byte)")

    # File rimossi
    for path in vecchio:
        if path not in nuovo:
            print(f"❌ Rimosso: {path}")

# --- USO DA TERMINALE ---
if __name__ == "__main__":
    import sys
    if len(sys.argv) < 4:
        print("Uso:")
        print("  python filetracker.py genera <directory> <report.csv>")
        print("  python filetracker.py confronta <vecchio.csv> <nuovo.csv>")
        sys.exit(1)

    comando = sys.argv[1]
    if comando == "genera":
        directory = sys.argv[2]
        report = sys.argv[3]
        genera_report(directory, report)
    elif comando == "confronta":
        vecchio = sys.argv[2]
        nuovo = sys.argv[3]
        confronta_report(vecchio, nuovo)
    else:
        print(f"Comando sconosciuto: {comando}")
