import sys
import pandas as pd
import numpy as np

def skaiciuoti_plotus(df):
    results = []
    grouped = df.groupby("id")
    for id_val, group in grouped:
        group = group.sort_values("dist")
        x = group["dist"].values
        y = group["h"].values

        ilgis = x[-1] - x[0]
        h_pradzia = y[0]
        h_pabaiga = y[-1]
        h_vidurkis = (h_pradzia + h_pabaiga) / 2

        min_area = min(h_pradzia, h_pabaiga) * ilgis
        avg_area = h_vidurkis * ilgis

        # Linest analogas: sumodeliuotas h = tiesės nuo pradzios iki pabaigos
        h_lin = h_pradzia + (x - x[0]) * (h_pabaiga - h_pradzia) / (x[-1] - x[0])
        diff = y - h_lin
        lin_area = np.trapz(diff, x)

        results.append((id_val, round(min_area, 2), round(avg_area, 2), round(lin_area, 2)))
    return results

def main():
    if len(sys.argv) < 2:
        print("Naudojimas: python profile_report_select.py failas.txt")
        return

    failas = sys.argv[1]
    try:
        df = pd.read_csv(failas, sep=r'[\t,; ]+', engine="python", decimal=",")
    except Exception as e:
        print(f"Klaida skaitant „{failas}“: {e}")
        return

    # Turi būti bent 3 stulpeliai: id, dist, h
    if df.shape[1] < 3:
        print(f"Klaida: tikėtasi bent 3 stulpelių, bet rasta {df.shape[1]}")
        return

    df.columns = ['id', 'dist', 'h']
    results = skaiciuoti_plotus(df)

    print("Rezultatai (id, Minimalus, Vidutinis, Linest):")
    for r in results:
        print(f"{r[0]}\t{r[1]}\t{r[2]}\t{r[3]}")

if __name__ == "__main__":
    main()
