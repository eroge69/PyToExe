import tkinter as tk
from tkinter import filedialog, messagebox
import re
import pandas as pd
import os

def read_asc_trace_by_msgname(file_path, target_name):
    timestamps = []
    # Regex matches lines with CANFD, Rx, and the target message name (case-insensitive)
    pattern = re.compile(r"^\s*(\d+\.\d+)\s+CANFD\s+\d+\s+Rx\s+[^\s]+\s+" + re.escape(target_name) + r"\b", re.IGNORECASE)

    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
        for line in f:
            if pattern.search(line):
                match = pattern.search(line)
                if match:
                    try:
                        timestamp = float(match.group(1))
                        timestamps.append(timestamp)
                    except ValueError:
                        continue
    return timestamps

def calculate_cycle_times(timestamps):
    if len(timestamps) < 2:
        return []
    # Calculate cycle times in milliseconds with decimal precision
    return [(timestamps[i+1] - timestamps[i]) * 1000 for i in range(len(timestamps) - 1)]

def browse_file():
    file_path = filedialog.askopenfilename(filetypes=[("ASC files", "*.asc")])
    if file_path:
        file_entry.delete(0, tk.END)
        file_entry.insert(0, file_path)

def process_trace():
    file_path = file_entry.get().strip()
    msg_name = msg_entry.get().strip()
    output_file = output_entry.get().strip()

    if not file_path or not msg_name:
        messagebox.showerror("Error", "Please provide the trace file and message name.")
        return

    # If output file is empty, auto-generate default filename
    if not output_file:
        base, _ = os.path.splitext(file_path)
        output_file = base + f"_{msg_name}_cycle_time.xlsx"
        output_entry.delete(0, tk.END)
        output_entry.insert(0, output_file)
    else:
        if not output_file.lower().endswith(".xlsx"):
            output_file += ".xlsx"
            output_entry.delete(0, tk.END)
            output_entry.insert(0, output_file)

    timestamps = read_asc_trace_by_msgname(file_path, msg_name)
    if len(timestamps) < 2:
        messagebox.showerror("Error", f"Not enough messages found for '{msg_name}' to calculate cycle time.")
        return

    cycle_times = calculate_cycle_times(timestamps)
    df = pd.DataFrame({
        "Timestamp (s)": timestamps[:-1],
        "CycleTime (ms)": cycle_times
    })

    try:
        df.to_excel(output_file, index=False)
        messagebox.showinfo("Success", f"Cycle time data saved to:\n{output_file}")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to save Excel file:\n{e}")

# GUI Setup
root = tk.Tk()
root.title("CAN Trace Cycle Time Checker")

# Trace file selection
tk.Label(root, text="ASC Trace File:").grid(row=0, column=0, sticky="e", padx=5, pady=5)
file_entry = tk.Entry(root, width=50)
file_entry.grid(row=0, column=1, padx=5)
tk.Button(root, text="Browse", command=browse_file).grid(row=0, column=2, padx=5)

# Message name input
tk.Label(root, text="Message Name:").grid(row=1, column=0, sticky="e", padx=5, pady=5)
msg_entry = tk.Entry(root, width=30)
msg_entry.grid(row=1, column=1, padx=5)

# Output Excel file path input (optional)
tk.Label(root, text="Output Excel File (optional):").grid(row=2, column=0, sticky="e", padx=5, pady=5)
output_entry = tk.Entry(root, width=50)
output_entry.grid(row=2, column=1, padx=5)

# Process button
tk.Button(root, text="Process", command=process_trace).grid(row=3, column=1, pady=15)

root.mainloop()
