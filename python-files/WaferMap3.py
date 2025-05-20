import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from collections import defaultdict, Counter
import xml.etree.ElementTree as ET
import shutil
import csv
from PIL import Image, ImageTk

def parse_map_data(file_path):
    tree = ET.parse(file_path)
    root = tree.getroot()
    namespace = {'ns': 'http://www.semi.org'}
    rows = root.find('.//ns:Device/ns:Data', namespace).findall('ns:Row', namespace)
    map_data = [row.text.strip().split() for row in rows]
    flat = [cell for row in map_data for cell in row]
    bin_counter = Counter(flat)
    return map_data, bin_counter, tree, root

def merge_maps(files, output_file, fail_code, include_bins=None, exclude_bins=None):
    maps = []
    for file in files:
        map_data, _, tree, root = parse_map_data(file)
        maps.append(map_data)

    merged_map = [row[:] for row in maps[0]]
    row_count = len(merged_map)
    col_count = len(merged_map[0])

    for i in range(row_count):
        for j in range(col_count):
            if any(maps[k][i][j] == fail_code for k in range(len(maps))):
                merged_map[i][j] = fail_code
            else:
                selected = None
                for k in range(len(maps)):
                    val = maps[k][i][j]
                    if (include_bins is None or val in include_bins) and (exclude_bins is None or val not in exclude_bins):
                        selected = val
                        break
                if selected:
                    merged_map[i][j] = selected

    namespace = {'ns': 'http://www.semi.org'}
    rows = root.find('.//ns:Device/ns:Data', namespace).findall('ns:Row', namespace)
    for i, row in enumerate(rows):
        row.text = ' '.join(merged_map[i])

    tree.write(output_file)

def group_files_by_prefix(directory, prefix_length=16):
    grouped = defaultdict(list)
    for filename in os.listdir(directory):
        if filename.endswith(".xml") and len(filename) >= prefix_length:
            grouped[filename[:prefix_length]].append(os.path.join(directory, filename))
    return grouped

def run_merge_gui():
    def browse_input():
        path = filedialog.askdirectory()
        if path:
            input_var.set(path)
            if same_folder_check.get():
                output_var.set(path)

    def browse_output():
        path = filedialog.askdirectory()
        if path:
            output_var.set(path)

    def update_same_folder():
        if same_folder_check.get():
            output_var.set(input_var.get())
        else:
            output_var.set("")

    def preview_files():
        prefix = prefix_var.get().strip()
        input_path = input_var.get()
        for row in preview_tree.get_children():
            preview_tree.delete(row)
        if not prefix or len(prefix) < 8:
            messagebox.showerror("Error", "Prefix must be at least 8 characters.")
            return
        if not os.path.isdir(input_path):
            messagebox.showerror("Error", "Invalid input directory.")
            return

        groups = group_files_by_prefix(input_path)
        matches = 0
        for key, files in groups.items():
            if key.startswith(prefix) and len(files) > 1:
                matches += 1
                for file in files:
                    _, counter, _, _ = parse_map_data(file)
                    all_bins = ", ".join([f"{k}:{v}" for k, v in sorted(counter.items())])
                    preview_tree.insert("", "end", values=(key, os.path.basename(file), all_bins))
        if matches == 0:
            messagebox.showinfo("No Matches", "No matching files found.")

    def merge_files():
        prefix = prefix_var.get().strip()
        input_path = input_var.get()
        output_path = output_var.get()
        fail_code = fail_var.get().strip()

        if not os.path.isdir(input_path) or not os.path.isdir(output_path):
            messagebox.showerror("Error", "Valid input/output folders required.")
            return
        if not fail_code:
            messagebox.showerror("Error", "FAIL bin code must be specified.")
            return

        include_bins = set(include_var.get().strip().split(",")) if include_check.get() else None
        exclude_bins = set(exclude_var.get().strip().split(",")) if exclude_check.get() else None
        delete_originals = same_folder_check.get()

        log_entries = []
        backup_dir = os.path.join(output_path, "deleted_originals_backup")
        os.makedirs(backup_dir, exist_ok=True)

        groups = group_files_by_prefix(input_path)
        count = 0

        for key, files in groups.items():
            if key.startswith(prefix) and len(files) > 1:
                output_file = os.path.join(output_path, f"{key}.xml")
                merge_maps(files, output_file, fail_code, include_bins, exclude_bins)

                deleted_files = []
                if delete_originals:
                    for file in files:
                        if os.path.abspath(file) != os.path.abspath(output_file):
                            shutil.move(file, os.path.join(backup_dir, os.path.basename(file)))
                            deleted_files.append(os.path.basename(file))

                log_entries.append({
                    "Group": key,
                    "MergedFile": os.path.basename(output_file),
                    "FilesMerged": "; ".join(os.path.basename(f) for f in files),
                    "Deleted": "; ".join(deleted_files) if delete_originals else "No"
                })
                count += 1

        # Save CSV log
        log_path = os.path.join(output_path, "merge_log.csv")
        with open(log_path, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=["Group", "MergedFile", "FilesMerged", "Deleted"])
            writer.writeheader()
            writer.writerows(log_entries)

        messagebox.showinfo("Done", f"Merged {count} group(s).\nLog saved to: merge_log.csv")

    # GUI Window
    root = tk.Tk()
    root.title("WaferMap Merger")

    # Load logo (PNG, optional, with aspect ratio preserved)
    try:
        img = Image.open(r"C:\Users\echristo\PycharmProjects\pythonProject\logo.png")
        max_size = (100, 100)
        img.thumbnail(max_size, Image.ANTIALIAS)  # Preserve aspect ratio
        root.logo_img = ImageTk.PhotoImage(img)  # Save as attribute to prevent garbage collection
        tk.Label(root, image=root.logo_img).grid(row=0, column=0, rowspan=2, padx=5, pady=5)
    except Exception as e:
        print(f"Logo not loaded: {e}")

    # GUI Controls
    tk.Label(root, text="8-char Recipe Prefix:").grid(row=0, column=1, sticky="e")
    prefix_var = tk.StringVar()
    tk.Entry(root, textvariable=prefix_var).grid(row=0, column=2, padx=5, pady=5)

    tk.Label(root, text="Input Folder:").grid(row=1, column=1, sticky="e")
    input_var = tk.StringVar()
    tk.Entry(root, textvariable=input_var, width=40).grid(row=1, column=2)
    tk.Button(root, text="Browse", command=browse_input).grid(row=1, column=3)

    same_folder_check = tk.BooleanVar()
    tk.Checkbutton(root, text="Use same folder and delete originals (backup kept)", variable=same_folder_check, command=update_same_folder).grid(row=2, column=1, columnspan=3, sticky="w", padx=5)

    tk.Label(root, text="Output Folder:").grid(row=3, column=1, sticky="e")
    output_var = tk.StringVar()
    tk.Entry(root, textvariable=output_var, width=40).grid(row=3, column=2)
    tk.Button(root, text="Browse", command=browse_output).grid(row=3, column=3)

    tk.Label(root, text="FAIL Bin Code:").grid(row=4, column=1, sticky="e")
    fail_var = tk.StringVar(value="040")
    tk.Entry(root, textvariable=fail_var).grid(row=4, column=2, columnspan=2, sticky="we", padx=5)

    include_check = tk.BooleanVar()
    tk.Checkbutton(root, text="Activate Include BinCodes", variable=include_check).grid(row=5, column=1, sticky="e")
    include_var = tk.StringVar()
    tk.Entry(root, textvariable=include_var).grid(row=5, column=2, columnspan=2, sticky="we", padx=5)

    exclude_check = tk.BooleanVar()
    tk.Checkbutton(root, text="Activate Exclude BinCodes", variable=exclude_check).grid(row=6, column=1, sticky="e")
    exclude_var = tk.StringVar()
    tk.Entry(root, textvariable=exclude_var).grid(row=6, column=2, columnspan=2, sticky="we", padx=5)

    tk.Button(root, text="Preview Matching Files", command=preview_files).grid(row=7, column=1, columnspan=2, pady=5)
    tk.Button(root, text="Merge and Save", command=merge_files).grid(row=7, column=3, pady=5)

    preview_tree = ttk.Treeview(root, columns=("Prefix", "Filename", "Bin Summary"), show="headings", height=12)
    preview_tree.heading("Prefix", text="Prefix")
    preview_tree.heading("Filename", text="Filename")
    preview_tree.heading("Bin Summary", text="BinCode Counts")
    preview_tree.grid(row=8, column=0, columnspan=4, padx=10, pady=10, sticky="nsew")

    root.mainloop()

if __name__ == "__main__":
    run_merge_gui()
