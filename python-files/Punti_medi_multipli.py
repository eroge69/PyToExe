import tkinter as tk
from tkinter import filedialog, messagebox
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk

class PuntoMedioApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Calcolatore Punti Medi")
        self.file_path = ""
        self.punti = None
        self.punti_medi = None

        # Pulsanti
        self.carica_button = tk.Button(root, text="📂 Carica CSV", command=self.carica_file)
        self.carica_button.pack(pady=5)

        self.visualizza_button = tk.Button(root, text="📊 Visualizza Punti", command=self.visualizza_punti)
        self.visualizza_button.pack(pady=5)

        self.salva_button = tk.Button(root, text="💾 Salva CSV Punti Medi", command=self.salva_file)
        self.salva_button.pack(pady=5)

        # Area messaggi
        self.messaggi = tk.Label(root, text="", fg="green")
        self.messaggi.pack(pady=10)

        # Area grafico
        self.figura = plt.Figure(figsize=(5, 4), dpi=100)
        self.canvas = None
        self.toolbar = None

    def carica_file(self):
        self.file_path = filedialog.askopenfilename(filetypes=[("File CSV", "*.csv")])
        if self.file_path:
            try:
                self.punti = pd.read_csv(self.file_path)
                if 'LATITUDINE' not in self.punti.columns or 'LONGITUDINE' not in self.punti.columns:
                    messagebox.showerror("Errore", "Il file deve contenere colonne 'LATITUDINE' e 'LONGITUDINE'")
                    return
                self.calcola_punti_medi()
                self.messaggi.config(text="✅ File caricato correttamente!")
            except Exception as e:
                messagebox.showerror("Errore", f"Errore durante il caricamento: {e}")

    def calcola_punti_medi(self):
        lat_medi = (self.punti['LATITUDINE'].shift(-1) + self.punti['LATITUDINE']) / 2
        lon_medi = (self.punti['LONGITUDINE'].shift(-1) + self.punti['LONGITUDINE']) / 2
        self.punti_medi = pd.DataFrame({
            'LATITUDINE': lat_medi[:-1],
            'LONGITUDINE': lon_medi[:-1]
        })

    def visualizza_punti(self):
        if self.punti is None or self.punti_medi is None:
            messagebox.showwarning("Attenzione", "Devi prima caricare un file!")
            return
        
        # Pulisci il grafico precedente
        self.figura.clf()

        ax = self.figura.add_subplot(111)
        ax.plot(self.punti['LONGITUDINE'], self.punti['LATITUDINE'], 'bo-', label='Punti originali')
        ax.plot(self.punti_medi['LONGITUDINE'], self.punti_medi['LATITUDINE'], 'ro--', label='Punti medi')
        ax.set_xlabel('Longitudine')
        ax.set_ylabel('Latitudine')
        ax.set_title('Punti Originali e Punti Medi')
        ax.legend()
        ax.grid(True)

        if self.canvas:
            self.canvas.get_tk_widget().destroy()
            self.toolbar.destroy()

        self.canvas = FigureCanvasTkAgg(self.figura, master=self.root)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack()

        self.toolbar = NavigationToolbar2Tk(self.canvas, self.root)
        self.toolbar.update()
        self.canvas.get_tk_widget().pack()

    def salva_file(self):
        if self.punti_medi is None:
            messagebox.showwarning("Attenzione", "Non ci sono punti medi da salvare!")
            return
        save_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("File CSV", "*.csv")])
        if save_path:
            self.punti_medi.to_csv(save_path, index=False)
            self.messaggi.config(text="✅ File salvato con successo!")

if __name__ == "__main__":
    root = tk.Tk()
    app = PuntoMedioApp(root)
    root.mainloop()
