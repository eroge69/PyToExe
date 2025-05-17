 import os
import hashlib
import shutil
import requests
import threading
import webbrowser

import customtkinter as ctk
from tkinter import filedialog, messagebox
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# GUI theme setup
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

# Quarantine and signature DB paths
QUARANTINE_FOLDER = "quarantine"
SIGNATURES_FILE = "signatures.txt"
SIGNATURES_URL = "https://example.com/signatures.txt"  # Replace with your actual URL

# Load malware signatures (SHA256 hashes)
def load_signatures():
    if not os.path.exists(SIGNATURES_FILE):
        return []
    with open(SIGNATURES_FILE, "r") as f:
        return [line.strip() for line in f if line.strip()]

# Download updated signature file
def update_signatures():
    try:
        response = requests.get(SIGNATURES_URL)
        if response.status_code == 200:
            with open(SIGNATURES_FILE, "w") as f:
                f.write(response.text)
            messagebox.showinfo("Update", "Signatures updated successfully.")
        else:
            messagebox.showwarning("Update Failed", "Could not update signatures.")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to update signatures: {e}")

# Hash file using SHA256
def hash_file(file_path):
    try:
        with open(file_path, "rb") as f:
            sha = hashlib.sha256()
            while chunk := f.read(8192):
                sha.update(chunk)
            return sha.hexdigest()
    except Exception:
        return None

# Quarantine file by moving it
def quarantine_file(file_path):
    if not os.path.exists(QUARANTINE_FOLDER):
        os.makedirs(QUARANTINE_FOLDER)
    base_name = os.path.basename(file_path)
    dest = os.path.join(QUARANTINE_FOLDER, base_name)
    try:
        shutil.move(file_path, dest)
        return dest
    except Exception:
        return None

# Scan a file and take action
def scan_file(file_path):
    signatures = load_signatures()
    file_hash = hash_file(file_path)
    if file_hash in signatures:
        quarantined_path = quarantine_file(file_path)
        if quarantined_path:
            return f"Infected! File moved to quarantine: {quarantined_path}"
        else:
            return "Infected! Failed to quarantine."
    return "Clean."

# Folder scanner
def scan_folder(folder_path):
    infected = []
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            full_path = os.path.join(root, file)
            result = scan_file(full_path)
            if "Infected" in result:
                infected.append((full_path, result))
    return infected

# Real-time file watcher
class ScanEventHandler(FileSystemEventHandler):
    def on_created(self, event):
        if not event.is_directory:
            result = scan_file(event.src_path)
            print(f"[Monitor] {event.src_path}: {result}")

def start_watcher(path="."):
    observer = Observer()
    handler = ScanEventHandler()
    observer.schedule(handler, path, recursive=True)
    observer.start()
    threading.Thread(target=observer.join).start()

# File picker and scan handler
def pick_and_scan_file():
    file_path = filedialog.askopenfilename()
    if not file_path:
        return
    result = scan_file(file_path)
    messagebox.showinfo("Scan Result", result)

# Folder picker and scan handler
def pick_and_scan_folder():
    folder_path = filedialog.askdirectory()
    if not folder_path:
        return
    infected = scan_folder(folder_path)
    if infected:
        msg = "\n".join([f"{fp}: {res}" for fp, res in infected])
        messagebox.showwarning("Infections Found", msg)
    else:
        messagebox.showinfo("Scan Result", "No infections found.")

# GUI setup
app = ctk.CTk()
app.geometry("400x420")
app.title("ShieldScan - Free Antivirus")

# Title
label = ctk.CTkLabel(app, text="🛡️ ShieldScan Antivirus", font=ctk.CTkFont(size=20, weight="bold"))
label.pack(pady=(20, 5))

# Discord clickable label
def open_discord():
    webbrowser.open("https://discord.gg/5SeAnPRM")

discord_label = ctk.CTkLabel(
    app,
    text="Join the server: https://discord.gg/5SeAnPRM",
    font=ctk.CTkFont(size=12, underline=True),
    text_color="#00aff4",
    cursor="hand2"
)
discord_label.pack(pady=(0, 20))
discord_label.bind("<Button-1>", lambda e: open_discord())

# Buttons
scan_file_button = ctk.CTkButton(app, text="Scan File", command=pick_and_scan_file)
scan_file_button.pack(pady=5)

scan_folder_button = ctk.CTkButton(app, text="Scan Folder", command=pick_and_scan_folder)
scan_folder_button.pack(pady=5)

update_button = ctk.CTkButton(app, text="Update Signatures", command=update_signatures)
update_button.pack(pady=5)

# Real-time watcher toggle logic
watching = [False]

def toggle_watcher():
    if not watching[0]:
        start_watcher(".")
        start_watcher_button.configure(text="Stop Real-Time Watcher")
        watching[0] = True
    else:
        messagebox.showinfo("Stop Watcher", "Please restart the app to stop the watcher.")

start_watcher_button = ctk.CTkButton(app, text="Start Real-Time Watcher", command=toggle_watcher)
start_watcher_button.pack(pady=5)

app.mainloop()
