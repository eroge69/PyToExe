
import tkinter as tk
from tkinter import messagebox, filedialog
import pandas as pd

def calculate_and_save():
    try:
        # Λήψη εισόδων
        total_cost = float(entry_total_cost.get())

        # Λίστες για θερμίδες και ώρες
        θερμίδες = []
        ώρες = []

        for i in range(6):
            θερμίδες.append(float(entries_therm[i].get()))
            ώρες.append(float(entries_hours[i].get()))

        # Υπολογισμοί
        df = pd.DataFrame({
            "Διαμέρισμα": ["Α", "Β", "Γ", "Δ", "Ε", "ΣΤ"],
            "Θερμίδες": θερμίδες,
            "Ώρες": ώρες
        })

        df["Γ"] = df["Θερμίδες"] / df["Θερμίδες"].sum()
        df["Δ"] = df["Ώρες"] * df["Γ"]
        df["Ε"] = df["Δ"] / df["Δ"].sum()

        A = total_cost * 0.20
        B = total_cost * 0.80

        df["Ποσό1 (Α x Γ)"] = A * df["Γ"]
        df["Ποσό2 (Β x Ε)"] = B * df["Ε"]
        df["Τελικό Ποσό (€)"] = df["Ποσό1 (Α x Γ)"] + df["Ποσό2 (Β x Ε)"]

        # Επιλογή τοποθεσίας αποθήκευσης
        file_path = filedialog.asksaveasfilename(defaultextension=".xlsx",
                                                 filetypes=[("Excel files", "*.xlsx")])
        if file_path:
            df.to_excel(file_path, index=False)
            messagebox.showinfo("Επιτυχία", "Το αρχείο αποθηκεύτηκε επιτυχώς!")

    except Exception as e:
        messagebox.showerror("Σφάλμα", str(e))

# GUI setup
root = tk.Tk()
root.title("Κατανομή Πετρελαίου (20/80)")

tk.Label(root, text="Συνολική Δαπάνη Πετρελαίου (€):").grid(row=0, column=0, columnspan=2)
entry_total_cost = tk.Entry(root)
entry_total_cost.grid(row=0, column=2, columnspan=2)

tk.Label(root, text="Διαμέρισμα").grid(row=1, column=0)
tk.Label(root, text="Θερμίδες").grid(row=1, column=1)
tk.Label(root, text="Ώρες").grid(row=1, column=2)

entries_therm = []
entries_hours = []

for i, label in enumerate(["Α", "Β", "Γ", "Δ", "Ε", "ΣΤ"]):
    tk.Label(root, text=label).grid(row=i+2, column=0)
    e1 = tk.Entry(root)
    e1.grid(row=i+2, column=1)
    entries_therm.append(e1)
    e2 = tk.Entry(root)
    e2.grid(row=i+2, column=2)
    entries_hours.append(e2)

tk.Button(root, text="Υπολογισμός & Αποθήκευση", command=calculate_and_save).grid(row=9, column=0, columnspan=3)

root.mainloop()
