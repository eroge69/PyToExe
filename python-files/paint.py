import tkinter as tk
from tkinter import ttk
import csv
import os

CSV_FILE = "paintcodes.csv"
data_list = []

def load_data():
    global data_list
    if not os.path.exists(CSV_FILE):
        with open(CSV_FILE, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(["Brand", "Code", "Paint", "Metallic", "3 Stage"])
        data_list = []
    else:
        with open(CSV_FILE, mode='r', newline='') as file:
            reader = csv.DictReader(file)
            data_list = list(reader)

def perform_search():
    brand = brand_entry.get().strip().lower()
    code = code_entry.get().strip().lower()
    paint = paint_entry.get().strip().lower()
    metallic = metallic_var.get()
    stage3 = stage3_var.get()

    for row in tree.get_children():
        tree.delete(row)

    matches = []
    for row in data_list:
        row_brand = row["Brand"].strip().lower()
        row_code = row["Code"].strip().lower()
        row_paint = row["Paint"].strip().lower()
        row_metallic = row["Metallic"].strip().lower() == "true"
        row_stage3 = row["3 Stage"].strip().lower() == "true"

        if (
            (brand and brand in row_brand) or
            (code and code in row_code) or
            (paint and paint in row_paint) or
            (metallic == row_metallic and metallic) or
            (stage3 == row_stage3 and stage3)
        ):
            matches.append(row)

    for row in matches[:3]:
        tree.insert("", tk.END, values=(
            row["Brand"],
            row["Code"],
            row["Paint"],
            row["Metallic"],
            row["3 Stage"]
        ))

def add_entry():
    brand = brand_entry.get().strip()
    code = code_entry.get().strip()
    paint = paint_entry.get().strip()
    metallic = metallic_var.get()
    stage3 = stage3_var.get()

    if not (brand or code or paint):
        return

    new_row = {
        "Brand": brand,
        "Code": code,
        "Paint": paint,
        "Metallic": str(metallic),
        "3 Stage": str(stage3)
    }

    data_list.append(new_row)

    with open(CSV_FILE, mode='a', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=["Brand", "Code", "Paint", "Metallic", "3 Stage"])
        writer.writerow(new_row)

    for row in tree.get_children():
        tree.delete(row)
    tree.insert("", tk.END, values=(brand, code, paint, str(metallic), str(stage3)))

    brand_entry.delete(0, tk.END)
    code_entry.delete(0, tk.END)
    paint_entry.delete(0, tk.END)
    metallic_var.set(False)
    stage3_var.set(False)

# Setup UI
root = tk.Tk()
root.title("Paint Code App")
root.geometry("600x300")

top_frame = tk.Frame(root)
top_frame.pack(pady=10, padx=10)

tk.Label(top_frame, text="Brand").grid(row=0, column=0)
brand_entry = tk.Entry(top_frame)
brand_entry.grid(row=1, column=0, padx=5)

tk.Label(top_frame, text="Code").grid(row=0, column=1)
code_entry = tk.Entry(top_frame)
code_entry.grid(row=1, column=1, padx=5)

tk.Label(top_frame, text="Paint").grid(row=0, column=2)
paint_entry = tk.Entry(top_frame)
paint_entry.grid(row=1, column=2, padx=5)

metallic_var = tk.BooleanVar()
stage3_var = tk.BooleanVar()
metallic_check = tk.Checkbutton(top_frame, text="Metallic", variable=metallic_var)
stage3_check = tk.Checkbutton(top_frame, text="3 Stage", variable=stage3_var)
metallic_check.grid(row=1, column=3, padx=5)
stage3_check.grid(row=1, column=4, padx=5)

search_button = tk.Button(top_frame, text="Search", command=perform_search)
search_button.grid(row=1, column=5, padx=5)

add_button = tk.Button(top_frame, text="+", width=2, command=add_entry)
add_button.grid(row=1, column=6, padx=5)

columns = ("Brand", "Code", "Paint", "Metallic", "3 Stage")
tree = ttk.Treeview(root, columns=columns, show="headings", height=3)
for col in columns:
    tree.heading(col, text=col)
    tree.column(col, anchor="center")

tree.pack(padx=10, pady=10, fill="x")

load_data()
root.mainloop()
