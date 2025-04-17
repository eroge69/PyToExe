import tkinter as tk
from tkinter import ttk, messagebox

# Dictionnaire pour stocker les entretiens
maintenance_records = []

def enregistrer_entretien():
    equipement = equipement_entry.get()
    heures = heures_entry.get()
    kilometrage = kilometrage_entry.get()
    type_huile = huile_entry.get()
    operations = operations_entry.get()
    pieces = pieces_entry.get()

    if equipement and (heures or kilometrage) and type_huile:
        record = {
            'Equipement': equipement,
            'Heures': heures,
            'Kilometrage': kilometrage,
            'Huile': type_huile,
            'Operations': operations,
            'Pieces': pieces
        }
        maintenance_records.append(record)
        rafraichir_tableau()
        vider_champs()
    else:
        messagebox.showwarning("Attention", "Veuillez remplir les champs obligatoires (Equipement, Heures/Km, Huile)")

def rafraichir_tableau():
    for row in tree.get_children():
        tree.delete(row)
    for rec in maintenance_records:
        tree.insert('', 'end', values=(rec['Equipement'], rec['Heures'], rec['Kilometrage'], rec['Huile'], rec['Operations'], rec['Pieces']))

def vider_champs():
    equipement_entry.delete(0, tk.END)
    heures_entry.delete(0, tk.END)
    kilometrage_entry.delete(0, tk.END)
    huile_entry.delete(0, tk.END)
    operations_entry.delete(0, tk.END)
    pieces_entry.delete(0, tk.END)

# Fenetre principale
root = tk.Tk()
root.title("Logiciel de eMaintenance Matériel BTP")
root.geometry('950x600')
root.configure(bg='#0b1d3a')  # Bleu nuit

# Labels
tk.Label(root, text="Equipement", bg='#0b1d3a', fg='white').pack(pady=5)
equipement_entry = tk.Entry(root)
equipement_entry.pack(pady=5)

tk.Label(root, text="Nombre d'heures (250h) / أو عدد الساعات", bg='#0b1d3a', fg='white').pack(pady=5)
heures_entry = tk.Entry(root)
heures_entry.pack(pady=5)

tk.Label(root, text="Kilométrage (5000 Km) / أو عدد الكيلومترات", bg='#0b1d3a', fg='white').pack(pady=5)
kilometrage_entry = tk.Entry(root)
kilometrage_entry.pack(pady=5)

tk.Label(root, text="Type d'huile utilisé / نوع الزيت", bg='#0b1d3a', fg='white').pack(pady=5)
huile_entry = tk.Entry(root)
huile_entry.pack(pady=5)

tk.Label(root, text="Opérations de maintenance diverses / عمليات صيانة مختلفة", bg='#0b1d3a', fg='white').pack(pady=5)
operations_entry = tk.Entry(root)
operations_entry.pack(pady=5)

tk.Label(root, text="Pièces de rechange utilisées / قطع الغيار", bg='#0b1d3a', fg='white').pack(pady=5)
pieces_entry = tk.Entry(root)
pieces_entry.pack(pady=5)

# Bouton d'enregistrement
tk.Button(root, text="Enregistrer l'entretien / تسجيل الصيانة", command=enregistrer_entretien, bg='lightblue').pack(pady=20)

# Tableau pour afficher les entretiens
columns = ('Equipement', 'Heures', 'Kilometrage', 'Huile', 'Operations', 'Pieces')
tree = ttk.Treeview(root, columns=columns, show='headings')
for col in columns:
    tree.heading(col, text=col)
    tree.column(col, width=140)
tree.pack(expand=True, fill='both', pady=20)

root.mainloop()
