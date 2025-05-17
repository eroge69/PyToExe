import tkinter as tk
from tkinter import messagebox, filedialog

class NotizApp:
    def __init__(self, root):
        self.root = root
        self.root.title("TEST")
        self.root.geometry("600x400")

        # Textfeld
        self.text_area = tk.Text(self.root, font=("Arial", 12))
        self.text_area.pack(expand=True, fill="both")

        # Menü
        self.menu = tk.Menu(self.root)
        self.root.config(menu=self.menu)

        file_menu = tk.Menu(self.menu, tearoff=0)
        self.menu.add_cascade(label="Datei", menu=file_menu)
        file_menu.add_command(label="Neu", command=self.neu)
        file_menu.add_command(label="Öffnen", command=self.öffnen)
        file_menu.add_command(label="Speichern", command=self.speichern)
        file_menu.add_separator()
        file_menu.add_command(label="Beenden", command=self.root.quit)

    def neu(self):
        self.text_area.delete(1.0, tk.END)

    def öffnen(self):
        datei = filedialog.askopenfilename(defaultextension=".txt",
                                            filetypes=[("Textdateien", "*.txt"), ("Alle Dateien", "*.*")])
        if datei:
            with open(datei, "r", encoding="utf-8") as f:
                inhalt = f.read()
                self.text_area.delete(1.0, tk.END)
                self.text_area.insert(tk.END, inhalt)

    def speichern(self):
        datei = filedialog.asksaveasfilename(defaultextension=".txt",
                                              filetypes=[("Textdateien", "*.txt"), ("Alle Dateien", "*.*")])
        if datei:
            try:
                with open(datei, "w", encoding="utf-8") as f:
                    f.write(self.text_area.get(1.0, tk.END))
                messagebox.showinfo("Gespeichert", "Die Datei wurde erfolgreich gespeichert.")
            except Exception as e:
                messagebox.showerror("Fehler", f"Fehler beim Speichern: {e}")

# App starten
if __name__ == "__main__":
    root = tk.Tk()
    app = NotizApp(root)
    root.mainloop()
