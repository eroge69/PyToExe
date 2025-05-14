import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import pandas as pd

# Neue Spalten (die in der CSV vorhanden sind, aber nicht in der GUI angezeigt werden)
all_labels = ["FirstName", "LastName", "Company", "Mobile", "Home", "Title", "Business", "Business2", "Email", "BusinessFax", "Department", "Pager"]

# Nur die relevanten Labels, die in der GUI angezeigt werden
visible_labels = ["FirstName", "LastName", "Company", "Mobile", "Email"]

contact_data = {}

# Beispielhafte Daten im DataFrame
initial_data = [
    {"FirstName": "Max", "LastName": "Mustermann", "Company": "Mustermann GmbH", "Mobile": "123456789", "Home": "", 
     "Title": "Herr", "Business": "", "Business2": "", "Email": "max@mustermann.de", "BusinessFax": "", 
     "Department": "", "Pager": ""},
    {"FirstName": "Anna", "LastName": "Müller", "Company": "Müller AG", "Mobile": "987654321", "Home": "", 
     "Title": "Frau", "Business": "", "Business2": "", "Email": "anna@mueller.de", "BusinessFax": "", 
     "Department": "", "Pager": ""}
]
df = pd.DataFrame(initial_data)

# Hauptanwendung
class KontaktverwaltungApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Pauly 3cx Kontaktmanager 2025")
        self.root.configure(bg="yellow")
        
        self.data = df
        self.selected_contact = None

        # Treeview mit Checkbox-Spalte (wird durch Text ersetzt)
        self.tree = ttk.Treeview(root, columns=["Select"] + visible_labels, show="headings")
        self.tree.pack(padx=10, pady=10, fill="both", expand=True)

        self.tree.heading("Select", text="✔")
        self.tree.column("Select", width=50)

        for col in visible_labels:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=100)

        self.check_vars = {}  # Dictionary für Checkbox-Variablen
        self.update_treeview()

        # Schaltflächen
        self.add_button = tk.Button(root, text="Kontakt hinzufügen", command=self.add_contact)
        self.add_button.pack(side="left", padx=10, pady=10)

        self.edit_button = tk.Button(root, text="Kontakt bearbeiten", command=self.edit_contact)
        self.edit_button.pack(side="left", padx=10, pady=10)

        self.delete_button = tk.Button(root, text="Kontakte löschen", command=self.delete_contact)
        self.delete_button.pack(side="left", padx=10, pady=10)

        self.import_button = tk.Button(root, text="Importieren", command=self.import_contacts)
        self.import_button.pack(side="left", padx=10, pady=10)

        self.export_button = tk.Button(root, text="Exportieren", command=self.export_contacts)
        self.export_button.pack(side="left", padx=10, pady=10)

    def update_treeview(self):
        self.tree.delete(*self.tree.get_children())
        self.check_vars.clear()

        # Für jedes Kontakt-Datensatz eine Checkbox (als Text) hinzufügen
        for idx, row in self.data.iterrows():
            var = tk.BooleanVar(value=False)
            self.check_vars[idx] = var
            checkbox_symbol = "✔" if var.get() else "✘"
            self.tree.insert("", "end", iid=idx, values=(checkbox_symbol,) + tuple(row[visible_labels]))

        # Klick-Event für die Checkboxen
        self.tree.bind("<Button-1>", self.toggle_checkbox)

    def toggle_checkbox(self, event):
        row_id = self.tree.identify_row(event.y)
        if row_id:
            row_id = int(row_id)
            current_state = self.check_vars[row_id].get()
            self.check_vars[row_id].set(not current_state)

            # Checkbox-Symbol aktualisieren
            checkbox_symbol = "✔" if self.check_vars[row_id].get() else "✘"
            self.tree.item(row_id, values=(checkbox_symbol,) + tuple(self.data.iloc[row_id][visible_labels]))

    def delete_contact(self):
        to_delete = [idx for idx, var in self.check_vars.items() if var.get()]
        if not to_delete:
            messagebox.showwarning("Warnung", "Kein Kontakt ausgewählt!")
            return

        self.data.drop(to_delete, inplace=True)
        self.data.reset_index(drop=True, inplace=True)
        self.update_treeview()

    def add_contact(self):
        # Ein Toplevel-Fenster zur Eingabe der Kontaktinformationen
        add_window = tk.Toplevel(self.root)
        add_window.title("Neuen Kontakt hinzufügen")

        # Eingabefelder für jedes Label
        entries = {}
        for idx, label in enumerate(visible_labels):
            tk.Label(add_window, text=label).grid(row=idx, column=0, padx=10, pady=5, sticky="w")
            entry = tk.Entry(add_window)
            entry.grid(row=idx, column=1, padx=10, pady=5)
            entries[label] = entry

        def save_new_contact():
            # Die neuen Eingabewerte holen und dem DataFrame hinzufügen
            new_contact = {label: entries[label].get() for label in visible_labels}
            self.data = self.data.append(new_contact, ignore_index=True)
            self.update_treeview()
            add_window.destroy()  # Fenster nach dem Hinzufügen schließen

        save_button = tk.Button(add_window, text="Speichern", command=save_new_contact)
        save_button.grid(row=len(visible_labels), column=0, columnspan=2, pady=10)

    def edit_contact(self):
        # Der Benutzer wählt den zu bearbeitenden Kontakt
        selected_items = self.tree.selection()
        if not selected_items:
            messagebox.showwarning("Warnung", "Kein Kontakt ausgewählt!")
            return
        
        row_id = int(selected_items[0])  # Die ausgewählte Zeile
        contact = self.data.iloc[row_id]

        # Ein Toplevel-Fenster zur Bearbeitung des Kontakts
        edit_window = tk.Toplevel(self.root)
        edit_window.title("Kontakt bearbeiten")

        # Eingabefelder für jedes Label mit dem aktuellen Wert des Kontakts
        entries = {}
        for idx, label in enumerate(visible_labels):
            tk.Label(edit_window, text=label).grid(row=idx, column=0, padx=10, pady=5, sticky="w")
            entry = tk.Entry(edit_window)
            entry.insert(0, contact[label])  # Aktuellen Wert einfügen
            entry.grid(row=idx, column=1, padx=10, pady=5)
            entries[label] = entry

        def save_edited_contact():
            # Die bearbeiteten Eingabewerte holen und im DataFrame speichern
            for label in visible_labels:
                self.data.at[row_id, label] = entries[label].get()
            self.update_treeview()
            edit_window.destroy()  # Fenster nach dem Bearbeiten schließen

        save_button = tk.Button(edit_window, text="Speichern", command=save_edited_contact)
        save_button.grid(row=len(visible_labels), column=0, columnspan=2, pady=10)

    def import_contacts(self):
        # Datei-Dialog zum Auswählen einer CSV-Datei
        file_path = filedialog.askopenfilename(title="Kontakte importieren", filetypes=[("CSV-Dateien", "*.csv")])
        if file_path:
            try:
                # CSV-Datei laden und an die aktuelle Daten anhängen
                imported_data = pd.read_csv(file_path)
                self.data = pd.concat([self.data, imported_data], ignore_index=True)
                self.update_treeview()
                messagebox.showinfo("Erfolg", "Kontakte wurden erfolgreich importiert.")
            except Exception as e:
                messagebox.showerror("Fehler", f"Fehler beim Importieren der Datei: {e}")

    def export_contacts(self):
        # Datei-Dialog zum Speichern der CSV-Datei
        file_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV-Dateien", "*.csv")])
        if file_path:
            try:
                # Daten als CSV-Datei speichern
                self.data.to_csv(file_path, index=False)
                messagebox.showinfo("Erfolg", "Kontakte wurden erfolgreich exportiert.")
            except Exception as e:
                messagebox.showerror("Fehler", f"Fehler beim Exportieren der Datei: {e}")

# Tkinter-Anwendung starten
if __name__ == "__main__":
    root = tk.Tk()
    app = KontaktverwaltungApp(root)
    root.mainloop()

