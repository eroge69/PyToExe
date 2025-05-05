import tkinter as tk
from tkinter import messagebox
import pyodbc
from datetime import datetime

# SQL connection setup
def insert_to_db(machine_id, cassette_id, lot_id, bin_val, tester, force, machine_mode):
    try:
        conn_str = (
            f'DRIVER={{ODBC Driver 17 for SQL Server}};'
            f'SERVER=10.84.48.24;'
            f'DATABASE=Traceability;'
            f'UID=EngTrace;'
            f'PWD=3Ngt4a23=1c1ce;'
            f'Encrypt=yes;'
            f'TrustServerCertificate=yes;'
        )
        conn = pyodbc.connect(conn_str)
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO dbo.t_aoi_disc_force_log (
                [datetime], machine_id, cassette_id, lot_id,
                bin, tester, force, machine_mode
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            datetime.now(),
            machine_id,
            cassette_id,
            lot_id,
            bin_val,
            tester,
            float(force),
            machine_mode
        ))

        conn.commit()
        cursor.close()
        conn.close()
        return True
    except Exception as e:
        print("DB Error:", e)
        return str(e)

# GUI setup
root = tk.Tk()
root.title("Insert AOI Log")
root.geometry("400x400")

fields = ["Machine ID", "Cassette ID", "Lot ID", "Bin", "Tester", "Force", "Machine Mode"]
entries = {}

for i, field in enumerate(fields):
    tk.Label(root, text=field).grid(row=i, column=0, pady=5, padx=5, sticky="w")
    entry = tk.Entry(root, width=30)
    entry.grid(row=i, column=1)
    entries[field] = entry

def submit():
    values = [entries[f].get() for f in fields]
    if "" in values:
        messagebox.showwarning("Input Error", "All fields are required.")
        return

    result = insert_to_db(*values)
    if result is True:
        messagebox.showinfo("Success", "Row inserted into database.")
        for e in entries.values():
            e.delete(0, tk.END)
    else:
        messagebox.showerror("Error", f"Insert failed:\n{result}")

tk.Button(root, text="Save to Database", command=submit, width=20).grid(row=len(fields), column=0, columnspan=2, pady=20)

root.mainloop()
