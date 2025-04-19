import os
import time
import threading
import tkinter as tk
from tkinter import ttk, scrolledtext
from pathlib import Path

def get_latest_log_file(log_dir):
    log_files = list(Path(log_dir).glob('*.log'))
    if not log_files:
        return None
    latest_file = max(log_files, key=lambda f: f.stat().st_mtime)
    return latest_file

def monitor_log_file(file_path, text_widget):
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
        file.seek(0, os.SEEK_END)
        while True:
            line = file.readline()
            if line:
                if "[FLog::Output] Nothing" in line:
                    continue  # Skip irrelevant lines
                text_widget.insert(tk.END, line)
                text_widget.see(tk.END)
            else:
                time.sleep(0.1)

def start_monitoring(log_dir, text_widget):
    latest_log = get_latest_log_file(log_dir)
    if latest_log:
        monitor_thread = threading.Thread(target=monitor_log_file, args=(latest_log, text_widget), daemon=True)
        monitor_thread.start()
    else:
        text_widget.insert(tk.END, "No log files found.\n")

def main():
    # Determine the log directory based on the operating system
    if os.name == 'nt':  # Windows
        log_dir = os.path.join(os.getenv('LOCALAPPDATA'), 'Roblox', 'logs')
    else:  # macOS
        log_dir = os.path.expanduser('~/Library/Logs/Roblox/')

    # Create the main window
    window = tk.Tk()
    window.title("Roblox Log Monitor")
    window.geometry("800x600")

    # Create a frame for better layout control
    frame = ttk.Frame(window, padding="10")
    frame.pack(expand=True, fill='both')

    # Create a label
    label = ttk.Label(frame, text="Filtered Roblox Logs:", font=("Segoe UI", 12))
    label.pack(anchor='w')

    # Create a scrollable text area with improved styling
    text_area = scrolledtext.ScrolledText(frame, wrap=tk.WORD, font=("Consolas", 10), background="#1e1e1e", foreground="#d4d4d4", insertbackground="white")
    text_area.pack(expand=True, fill='both')

    # Start monitoring in a separate thread
    start_monitoring(log_dir, text_area)

    # Run the GUI event loop
    window.mainloop()

if __name__ == "__main__":
    main()
