import pandas as pd
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog, messagebox

# Tkinter GUI maken
root = tk.Tk()
root.title("Parquet File Viewer")

# Schermbreedte en -hoogte ophalen
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()

# Venstergrootte instellen op de schermgrootte
root.geometry(f"{screen_width}x{screen_height}")

# Functie om gegevens te tonen in de Treeview
def show_data(file_path):
    try:
        # Cursor instellen op wachtstatus
        root.config(cursor="wait")
        root.update()

        # Parquet-bestand lezen
        df = pd.read_parquet(file_path)

        # Oude kolommen en rijen wissen
        tree.delete(*tree.get_children())
        tree["columns"] = list(df.columns)

        # Kolomkoppen opnieuw instellen en breedte optimaliseren
        for col in df.columns:
            max_width = max(df[col].astype(str).apply(len).max(), len(col)) + 2
            tree.heading(col, text=col)
            tree.column(col, width=max_width * 7, anchor="w", stretch=False)

        # Data toevoegen aan de Treeview
        for index, row in df.iterrows():
            tree.insert("", tk.END, values=list(row))
        
        # Update the window title with the file name
        root.title(f"Parquet File Viewer - {file_path.split('/')[-1]}")
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred while reading the file:\n{e}")
    finally:
        # Cursor terugzetten naar normaal
        root.config(cursor="")
        root.update()

# Functie om het Parquet-schema in de Treeview te tonen
def show_schema(file_path):
    try:
        # Cursor instellen op wachtstatus
        root.config(cursor="wait")
        root.update_idletasks()  # Force immediate UI refres
        root.update() 

        # Schema ophalen van het Parquet-bestand
        df = pd.read_parquet(file_path)
        schema_tree.delete(*schema_tree.get_children())

        # Kolommen en datatypes weergeven
        for col, dtype in zip(df.columns, df.dtypes):
            schema_tree.insert("", tk.END, text=f"{col}: {dtype}")
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred while reading the schema:\n{e}")
    finally:
        # Cursor terugzetten naar normaal
        root.config(cursor="")
        root.update()
        root.update_idletasks()  # Force immediate UI refres

# Functie om een Parquet-bestand te selecteren en gegevens weer te geven
def select_file():
    file_path = filedialog.askopenfilename(filetypes=[("Parquet files", "*.parquet")])
    if file_path:
        show_data(file_path)
        show_schema(file_path)

# Functie om de applicatie af te sluiten
def exit_application():
    root.quit()

# Create a top menu item 'File' with subitems 'Open' and 'Exit'
menu_bar = tk.Menu(root)
file_menu = tk.Menu(menu_bar, tearoff=0)
file_menu.add_command(label="Open", command=select_file)
file_menu.add_separator()
file_menu.add_command(label="Exit", command=exit_application)
menu_bar.add_cascade(label="File", menu=file_menu)
root.config(menu=menu_bar)

# Frame voor Treeviews
frame = ttk.Frame(root)
frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

# Treeview voor schema (links)
schema_frame = ttk.Frame(frame)
schema_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

schema_tree = ttk.Treeview(schema_frame, show="tree")

# Scrollbars voor schema Treeview
scroll_schema_y = ttk.Scrollbar(schema_frame, orient=tk.VERTICAL, command=schema_tree.yview)
scroll_schema_x = ttk.Scrollbar(schema_frame, orient=tk.HORIZONTAL, command=schema_tree.xview)
schema_tree.configure(yscrollcommand=scroll_schema_y.set, xscrollcommand=scroll_schema_x.set)

scroll_schema_y.pack(side=tk.RIGHT, fill=tk.Y)
scroll_schema_x.pack(side=tk.BOTTOM, fill=tk.X)
schema_tree.pack(fill=tk.BOTH, expand=True)

# Treeview voor data (rechts)
data_frame = ttk.Frame(frame)
data_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

tree = ttk.Treeview(data_frame, show="headings")

scroll_y = ttk.Scrollbar(data_frame, orient=tk.VERTICAL, command=tree.yview)
scroll_x = ttk.Scrollbar(data_frame, orient=tk.HORIZONTAL, command=tree.xview)
tree.configure(yscrollcommand=scroll_y.set, xscrollcommand=scroll_x.set)

scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
scroll_x.pack(side=tk.BOTTOM, fill=tk.X)
tree.pack(fill=tk.BOTH, expand=True)

# GUI starten
root.mainloop()
