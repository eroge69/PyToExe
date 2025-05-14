
import tkinter as tk
from tkinter import filedialog, messagebox
import pandas as pd

def genera_file_amazon():
    try:
        prodotti_path = filedialog.askopenfilename(title="Seleziona il file prodotti.csv")
        combinazioni_path = filedialog.askopenfilename(title="Seleziona il file combinazioni.csv")

        if not prodotti_path or not combinazioni_path:
            messagebox.showwarning("Attenzione", "Seleziona entrambi i file.")
            return

        df_prodotti = pd.read_csv(prodotti_path, sep=";", encoding="utf-8")
        df_combinazioni = pd.read_csv(combinazioni_path, sep=";", encoding="utf-8")

        df_combinazioni["Impatto prezzo"] = (
            df_combinazioni["Impatto prezzo"].astype(str).str.replace(",", ".").astype(float)
        )

        # Estrazione immagini
        df_prodotti["Main Image URL"] = df_prodotti["Image Url"].apply(lambda x: str(x).split(",")[0])
        for i in range(1, 6):
            df_prodotti[f"Other Image URL{i}"] = df_prodotti["Image Url"].apply(
                lambda x: str(x).split(",")[i] if len(str(x).split(",")) > i else ""
            )

        df_prodotti["Search Terms"] = df_prodotti["Tags"]

        immagini_colonne = ["Main Image URL"] + [f"Other Image URL{i}" for i in range(1, 6)]
        df_extra = df_prodotti[["Product ID", "Search Terms"] + immagini_colonne]
        df_merged = df_combinazioni.merge(df_prodotti, on="Product ID", suffixes=("_var", "_prod"))
        df_merged = df_merged.merge(df_extra, on="Product ID")

        records = []
        mappa_dimensioni = {}
        for dim_raw in df_merged["Value (Value:Position)"].dropna().unique():
            dim_clean = dim_raw.split(":")[0].strip().replace(" cm", "")
            if "x" in dim_clean:
                try:
                    larghezza, altezza = map(int, dim_clean.split("x"))
                    mappa_dimensioni[f"{larghezza}x{altezza} cm"] = {
                        "length": max(larghezza, altezza),
                        "width": min(larghezza, altezza),
                        "unit": "Centimetri"
                    }
                except:
                    continue

        for _, row in df_merged.iterrows():
            dim_full = row["Value (Value:Position)"].split(":")[0].strip()
            dim_label = dim_full + " cm" if "cm" not in dim_full else dim_full
            dimensioni = mappa_dimensioni.get(dim_label)
            if not dimensioni:
                continue

            parent_sku = row["Reference_prod"]
            child_sku = row["Reference_var"]
            titolo_base = row["Name"]
            prezzo = round(row["Impatto prezzo"] * 1.098, 2)

            if not any(r.get("SKU") == parent_sku for r in records):
                parent_row = {
                    "SKU": parent_sku,
                    "Title": titolo_base,
                    "Brand Name": "CheQuadro!",
                    "Parentage": "parent",
                    "Parent SKU": "",
                    "Relationship Type": "",
                    "Variation Theme": "FORMATO",
                    "Size Name": "",
                    "Standard Price": "",
                    "Item Length": "",
                    "Item Length Unit": "",
                    "Item Width": "",
                    "Item Width Unit": "",
                    "Search Terms": row["Search Terms"]
                }
                for col in immagini_colonne:
                    parent_row[col] = row[col]
                records.append(parent_row)

            child_row = {
                "SKU": child_sku,
                "Title": f"{titolo_base} {dim_label}",
                "Brand Name": "CheQuadro!",
                "Parentage": "child",
                "Parent SKU": parent_sku,
                "Relationship Type": "variation",
                "Variation Theme": "FORMATO",
                "Size Name": dim_label,
                "Standard Price": prezzo,
                "Item Length": dimensioni["length"],
                "Item Length Unit": dimensioni["unit"],
                "Item Width": dimensioni["width"],
                "Item Width Unit": dimensioni["unit"],
                "Search Terms": row["Search Terms"]
            }
            for col in immagini_colonne:
                child_row[col] = row[col]
            records.append(child_row)

        df_output = pd.DataFrame(records)
        output_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV", "*.csv")])
        if output_path:
            df_output.to_csv(output_path, index=False, sep=";", encoding="utf-8")
            messagebox.showinfo("Successo", f"File generato: {output_path}")

    except Exception as e:
        messagebox.showerror("Errore", str(e))

app = tk.Tk()
app.title("Generatore File Amazon - CheQuadro")
app.geometry("400x200")
label = tk.Label(app, text="Genera file Amazon da prodotti e combinazioni PrestaShop", wraplength=300, pady=20)
label.pack()
btn = tk.Button(app, text="Seleziona file e genera CSV", command=genera_file_amazon)
btn.pack(pady=10)
app.mainloop()
