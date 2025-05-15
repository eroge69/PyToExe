import tkinter as tk
from tkinter import filedialog, ttk, messagebox
import xml.etree.ElementTree as ET
import chardet

all_settings = []


def parse_xml(file_path):
    global all_settings
    try:
        with open(file_path, 'rb') as f:
            raw_data = f.read()
            result = chardet.detect(raw_data)
            encoding = result['encoding']

        text = raw_data.decode(encoding)
        root = ET.fromstring(text)

        all_settings = []
        for scalar in root.iter('ScalarSetting'):
            name = scalar.attrib.get('Name')
            value = scalar.attrib.get('Value')
            if name and value:
                all_settings.append((name, value))
        return all_settings
    except Exception as e:
        messagebox.showerror("Fehler",
                             f"Fehler beim Verarbeiten der Datei:\n{e}")
        return []


def open_file():
    file_path = filedialog.askopenfilename(filetypes=[("XML-Dateien",
                                                       "*.xml")])
    if file_path:
        parse_xml(file_path)
        update_table(all_settings)


def update_table(data):
    for row in treeview.get_children():
        treeview.delete(row)
    for name, value in data:
        treeview.insert("", "end", values=(name, value))


def filter_table(*args):
    query = search_var.get().lower()
    filtered = [
        entry for entry in all_settings
        if query in entry[0].lower() or query in entry[1].lower()
    ]
    update_table(filtered)


# GUI Setup
root = tk.Tk()
root.title("XML ScalarSetting Viewer mit Suche und Scrollbar")
root.geometry("800x600")

frame = ttk.Frame(root, padding=10)
frame.pack(fill="both", expand=True)

button = ttk.Button(frame, text="XML-Datei öffnen", command=open_file)
button.pack(pady=5)

search_var = tk.StringVar()
search_var.trace_add("write", filter_table)

search_entry = ttk.Entry(frame, textvariable=search_var)
search_entry.pack(fill="x", padx=5, pady=5)
search_entry.insert(0, "🔍 Suche nach Parameter oder Wert...")

# Scrollbar + Treeview
tree_frame = ttk.Frame(frame)
tree_frame.pack(fill="both", expand=True)

scrollbar = ttk.Scrollbar(tree_frame)
scrollbar.pack(side="right", fill="y")

treeview = ttk.Treeview(tree_frame,
                        columns=("Parameter", "Wert"),
                        show="headings",
                        yscrollcommand=scrollbar.set)
treeview.heading("Parameter", text="Parameter")
treeview.heading("Wert", text="Wert")
treeview.column("Parameter", width=350)
treeview.column("Wert", width=350)
treeview.pack(fill="both", expand=True)

scrollbar.config(command=treeview.yview)

root.mainloop()
