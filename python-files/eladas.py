import tkinter as tk
from tkinter import filedialog, messagebox
import pandas as pd
from datetime import datetime
import os

class KonyvEladasApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Könyveladás")

        self.vonalkodok = []
        self.konyvek = []

        self.label = tk.Label(root, text="Excel fájl betöltése")
        self.label.pack()

        self.load_button = tk.Button(root, text="Tallózás", command=self.load_excel)
        self.load_button.pack()

        self.vonalkod_entry = tk.Entry(root, width=30)
        self.vonalkod_entry.pack()
        self.vonalkod_entry.bind('<Return>', self.add_vonalkod)

        self.konyv_listbox = tk.Listbox(root, width=80)
        self.konyv_listbox.pack()

        self.finish_button = tk.Button(root, text="Befejeztem", command=self.finish)
        self.finish_button.pack(pady=10)

    def load_excel(self):
        file_path = filedialog.askopenfilename(filetypes=[("Excel files", "*.xlsx")])
        if not file_path:
            return
        self.excel_path = file_path
        self.df_lista = pd.read_excel(file_path, sheet_name="LISTA", header=2)
        try:
            self.ar = pd.read_excel(file_path, sheet_name="LISTA", header=None).iloc[0, 8]  # I1 cella
        except:
            messagebox.showerror("Hiba", "Nem sikerült beolvasni az I1 cellában lévő árat.")
            self.ar = 0

    def add_vonalkod(self, event=None):
        kod = self.vonalkod_entry.get().strip()
        self.vonalkod_entry.delete(0, tk.END)
        if kod in self.vonalkodok:
            return
        if not hasattr(self, 'df_lista'):
            messagebox.showerror("Hiba", "Előbb töltsd be az Excel fájlt!")
            return

        egyezes = self.df_lista[self.df_lista.iloc[:, 3].astype(str) == kod]  # D oszlop: vonalkód
        if not egyezes.empty:
            szerzo = egyezes.iloc[0, 1]  # B oszlop
            cim = egyezes.iloc[0, 2]    # C oszlop
            self.konyvek.append((kod, szerzo, cim, self.ar))
            self.vonalkodok.append(kod)
            self.konyv_listbox.insert(tk.END, f"{szerzo} – {cim} – {self.ar} Ft")
        else:
            messagebox.showwarning("Nincs találat", f"A {kod} vonalkód nem található a listában.")

    def finish(self):
        if not self.konyvek:
            messagebox.showinfo("Nincs adat", "Nem lett rögzítve egy könyv sem.")
            return

        ablak = tk.Toplevel(self.root)
        ablak.title("Számlaszám megadása")

        tk.Label(ablak, text="Add meg a számlaszámot:").pack()
        szamla_entry = tk.Entry(ablak, width=30)
        szamla_entry.pack(pady=5)

        def save():
            szamlaszam = szamla_entry.get().strip()
            if not szamlaszam:
                messagebox.showerror("Hiba", "Nem adtál meg számlaszámot.")
                return

            datum = datetime.today().strftime("%Y-%m-%d")
            df_kesz = pd.DataFrame(self.konyvek, columns=["Vonalkód", "Szerző", "Cím", "Ár"])
            df_kesz["Számlaszám"] = szamlaszam
            df_kesz["Dátum"] = datum

            export_path = os.path.join(os.path.dirname(self.excel_path), f"eladas_{datum}.xlsx")
            df_kesz.to_excel(export_path, index=False)
            messagebox.showinfo("Siker", f"Eladás mentve ide:\n{export_path}")
            ablak.destroy()

        tk.Button(ablak, text="Mentés", command=save).pack(pady=5)

if __name__ == "__main__":
    root = tk.Tk()
    app = KonyvEladasApp(root)
    root.mainloop()
