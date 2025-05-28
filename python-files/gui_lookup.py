
import tkinter as tk

from tkinter import messagebox, Listbox, Scrollbar, Button, Label, PhotoImage, StringVar, OptionMenu, Checkbutton, BooleanVar
import os
import subprocess
import json
from datetime import datetime
from PIL import Image, ImageTk

import sys

# --- PATH SETUP ---
def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS  # PyInstaller temp folder
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

INDEX_FILE = r"F:\Prints & Controls\LookupTool\part_index.json"
LOGO_PATH = resource_path("logo.gif")

# --- GLOBALS ---
results = []
recent_searches = []
theme_mode = "light"

# --- FUNCTIONS ---
def load_index():
    if not os.path.exists(INDEX_FILE):
        messagebox.showerror("Error", f"Index file not found:\n{INDEX_FILE}")
        exit()
    with open(INDEX_FILE, 'r') as f:
        return json.load(f)

def search_parts(query):
    index = load_index()
    
    return [(part, path) for part, path in index.items() if query.lower() in part.lower()]

def open_selected_files(event=None):
    selections = result_listbox.curselection()
    if not selections:
        messagebox.showinfo("No Selection", "Select one or more results to open.")
        return
    for index in selections:
        _, path = results[index]
        if os.path.exists(path):
            subprocess.Popen([path], shell=True)
        else:
            messagebox.showerror("Error", f"File not found:\n{path}")

def on_search(event=None):
    query = entry.get().strip()
    if not query:
        messagebox.showinfo("Input Needed", "Enter a part number or keyword.")
        return

    if query not in recent_searches:
        recent_searches.insert(0, query)
        if len(recent_searches) > 5:
            recent_searches.pop()
        update_recent_dropdown()

    global results
    results = search_parts(query)
    result_listbox.delete(0, tk.END)

    for part, path in results:
        ext = os.path.splitext(path)[1].upper().replace('.', '')
        modified = datetime.fromtimestamp(os.path.getmtime(path)).strftime('%m/%d/%Y')
        display_text = f"{part} ({ext} - {modified})"
        result_listbox.insert(tk.END, display_text)

def use_recent_search(selection):
    entry.delete(0, tk.END)
    entry.insert(0, selection)

def update_recent_dropdown():
    recent_menu['menu'].delete(0, 'end')
    for item in recent_searches:
        recent_menu['menu'].add_command(label=item, command=lambda v=item: use_recent_search(v))
    selected_recent.set(recent_searches[0] if recent_searches else "None")





# --- GUI SETUP ---
root = tk.Tk()
root.title("Part Lookup Tool")
root.geometry("850x650")
root.configure(bg="#f0f0f0")

# --- Logo ---
try:
    original_logo = Image.open(LOGO_PATH)
    resized_logo = original_logo.resize((130, 90))
    logo_img = ImageTk.PhotoImage(resized_logo)
    logo_label = Label(root, image=logo_img, bg="#f0f0f0")
    logo_label.pack(pady=5)
except Exception as e:
    print("Logo failed to load:", e)

# --- Title ---
Label(root, text="Part Lookup:", font=('Arial', 16, 'bold'), bg="#f0f0f0").pack(pady=(10, 0))

# --- Search ---
entry = tk.Entry(root, font=('Arial', 14))
entry.pack(pady=5, fill=tk.X, padx=20)
entry.bind("<Return>", on_search)
entry.focus()

#Button(root, text="Search", command=on_search, font=('Arial', 12)).pack()



# --- Recent Dropdown ---
Label(root, text="Recent Searches:", font=('Arial', 12), bg="#f0f0f0").pack()
selected_recent = StringVar()
selected_recent.set("None")
recent_menu = OptionMenu(root, selected_recent, "None")
recent_menu.pack(pady=5)
recent_menu.config(width=25, font=('Arial', 11))

# --- Tip ---
Label(root, text="Hold Ctrl or Shift to select multiple", font=('Arial', 10), fg="gray", bg="#f0f0f0").pack()

# --- List Label ---
Label(root, text="Part List", font=('Arial', 14, 'bold'), bg="#f0f0f0").pack(pady=(5, 0))

# --- Results List ---
frame = tk.Frame(root)
frame.pack(expand=True, fill=tk.BOTH, padx=20, pady=5)

scrollbar = Scrollbar(frame)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

result_listbox = Listbox(frame, font=('Courier', 11), selectmode=tk.EXTENDED)
result_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
result_listbox.config(yscrollcommand=scrollbar.set)
scrollbar.config(command=result_listbox.yview)




# --- Open  Button ---
Button(root, text="Open Selected", command=open_selected_files, font=('Arial', 12)).pack(pady=10)
entry.bind("<space>", open_selected_files)

root.mainloop()