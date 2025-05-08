import os
import pandas as pd
import tkinter as tk
from tkinter import filedialog, messagebox

class FileRenamerApp:
    def __init__(self, master):
        self.master = master
        master.title("Rinominatore di File")

        self.folder_path = ""
        self.excel_path = ""

        self.label1 = tk.Label(master, text="Seleziona la cartella dei file:")
        self.label1.pack()

        self.folder_button = tk.Button(master, text="Scegli Cartella", command=self.select_folder)
        self.folder_button.pack()

        self.label2 = tk.Label(master, text="Seleziona il foglio di lavoro Excel:")
        self.label2.pack()

        self.excel_button = tk.Button(master, text="Scegli Excel", command=self.select_excel)
        self.excel_button.pack()

        self.rename_button = tk.Button(master, text="Esegui Rinominazione", command=self.rename_files)
        self.rename_button.pack()

        self.exit_button = tk.Button(master, text="Esci", command=master.quit)
        self.exit_button.pack()

    def select_folder(self):
        self.folder_path = filedialog.askdirectory()
        if self.folder_path:
            messagebox.showinfo("Cartella Selezionata", self.folder_path)

    def select_excel(self):
        self.excel_path = filedialog.askopenfilename(filetypes=[("Excel files", "*.xlsx;*.xls")])
        if self.excel_path:
            messagebox.showinfo("Excel Selezionato", self.excel_path)

    def rename_files(self):
        if not self.folder_path or not self.excel_path:
            messagebox.showerror("Errore", "Seleziona sia la cartella che il file Excel.")
            return

        try:
            df = pd.read_excel(self.excel_path)
            for index, row in df.iterrows():
                old_name = row[0]
                new_name = row[1]
                old_file_path = os.path.join(self.folder_path, old_name)
                new_file_path = os.path.join(self.folder_path, new_name)

                if os.path.exists(old_file_path):
                    os.rename(old_file_path, new_file_path)
                else:
                    messagebox.showwarning("Attenzione", f"File non trovato: {old_name}")

            messagebox.showinfo("Completato", "Rinominazione completata.")
        except Exception as e:
            messagebox.showerror("Errore", str(e))

if __name__ == "__main__":
    root = tk.Tk()
    app = FileRenamerApp(root)
    root.mainloop()
