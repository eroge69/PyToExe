import os
import tkinter as tk
from tkinter import filedialog, messagebox

# Λίστα με "ύποπτες" επεκτάσεις αρχείων
SUSPICIOUS_EXTENSIONS = ['.exe', '.bat', '.vbs', '.scr', '.js']

def scan_folder(path):
    suspicious_files = []
    for root, dirs, files in os.walk(path):
        for file in files:
            ext = os.path.splitext(file)[1].lower()
            if ext in SUSPICIOUS_EXTENSIONS:
                suspicious_files.append(os.path.join(root, file))
    return suspicious_files

def browse_folder():
    folder_selected = filedialog.askdirectory()
    if folder_selected:
        result_list.delete(0, tk.END)
        suspicious = scan_folder(folder_selected)
        if suspicious:
            for f in suspicious:
                result_list.insert(tk.END, f)
            messagebox.showwarning("Προσοχή", f"Βρέθηκαν {len(suspicious)} ύποπτα αρχεία!")
        else:
            messagebox.showinfo("Καθαρό", "Δεν βρέθηκαν ύποπτα αρχεία!")

# GUI
root = tk.Tk()
root.title("Απλός Scanner Φακέλου")

btn_browse = tk.Button(root, text="Επίλεξε φάκελο για σάρωση", command=browse_folder)
btn_browse.pack(pady=10)

result_list = tk.Listbox(root, width=100)
result_list.pack(padx=10, pady=10)

root.geometry("800x400")
root.mainloop()
