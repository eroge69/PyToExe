
import tkinter as tk
from tkinter import ttk, messagebox

# --- Main Window ---
root = tk.Tk()
root.title("Focus Mediazone Billing Software")
root.geometry("800x600")

# --- Invoice Type ---
invoice_type_label = tk.Label(root, text="Invoice Type:")
invoice_type_label.grid(row=0, column=0, padx=10, pady=10, sticky="e")
invoice_type = ttk.Combobox(root, values=["GST Invoice", "Classic Invoice"])
invoice_type.current(0)
invoice_type.grid(row=0, column=1, padx=10, pady=10, sticky="w")

# --- Customer Name ---
name_label = tk.Label(root, text="Customer Name:")
name_label.grid(row=1, column=0, padx=10, pady=10, sticky="e")
name_entry = tk.Entry(root, width=40)
name_entry.grid(row=1, column=1, padx=10, pady=10, sticky="w")

# --- GSTIN Entry ---
gstin_label = tk.Label(root, text="GSTIN:")
gstin_label.grid(row=2, column=0, padx=10, pady=10, sticky="e")
gstin_entry = tk.Entry(root, width=40)
gstin_entry.grid(row=2, column=1, padx=10, pady=10, sticky="w")

# --- Item Table ---
item_frame = tk.LabelFrame(root, text="Items")
item_frame.grid(row=3, column=0, columnspan=3, padx=10, pady=10, sticky="nsew")

columns = ("S.No", "Description", "Qty", "Rate", "Amount")
tree = ttk.Treeview(item_frame, columns=columns, show="headings")
for col in columns:
    tree.heading(col, text=col)
    tree.column(col, width=100, anchor="center")
tree.pack(fill="both", expand=True)

# --- Footer ---
footer = tk.Label(root, text="Authorized Signatory: Arihant Bellanke", font=("Arial", 10, "italic"))
footer.grid(row=5, column=0, columnspan=3, pady=20)

root.mainloop()
