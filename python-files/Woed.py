import os
import tkinter as tk
from tkinter import filedialog, messagebox

def split_text_file(file_path, chunk_size=950):
    with open(file_path, 'r', encoding='utf-8') as file:
        text = file.read()

    words = text.split()
    total_words = len(words)
    file_base = os.path.splitext(os.path.basename(file_path))[0]
    folder = os.path.dirname(file_path)

    parts = (total_words + chunk_size - 1) // chunk_size
    for i in range(parts):
        start = i * chunk_size
        end = min(start + chunk_size, total_words)
        chunk_words = words[start:end]
        out_filename = f"{file_base}_output_{i+1}.txt"
        out_path = os.path.join(folder, out_filename)
        with open(out_path, 'w', encoding='utf-8') as out_file:
            out_file.write(' '.join(chunk_words))
    return parts

def select_and_split():
    file_path = filedialog.askopenfilename(title="Select a .txt file", filetypes=[("Text Files", "*.txt")])
    if not file_path:
        return

    try:
        parts = split_text_file(file_path)
        messagebox.showinfo("Done", f"✅ {parts} files created successfully in the same folder.")
    except Exception as e:
        messagebox.showerror("Error", str(e))

root = tk.Tk()
root.withdraw()
select_and_split()
