import time
import os
import ftplib
import json
import tkinter as tk
from tkinter import filedialog, simpledialog, messagebox
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

CONFIG_FILE = 'ftp_config.json'

# === Load previous config if available ===
def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_config(config):
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f)

# === Define FTP code mappings ===
FTP_LOCATIONS = {
    'code1': ('ftp.example1.com', 'user1', 'pass1', '/upload/path1'),
    'code2': ('ftp.example2.com', 'user2', 'pass2', '/upload/path2'),
    # Add more codes as needed
}

# === Prompt user for configuration ===
root = tk.Tk()
root.withdraw()

config = load_config()

default_code = config.get('ftp_code', '')
default_path = config.get('file_path', '')

use_defaults = messagebox.askyesno("Use Saved Settings", "Use previously saved FTP code and file?")

if use_defaults and default_code in FTP_LOCATIONS and os.path.isfile(default_path):
    ftp_code = default_code
    file_path = default_path
else:
    ftp_code = simpledialog.askstring("FTP Code", "Enter your FTP code:", initialvalue=default_code)
    file_path = filedialog.askopenfilename(title="Select file to monitor", initialdir=os.path.dirname(default_path) if default_path else '')

    if not ftp_code or not file_path:
        print("Operation cancelled.")
        exit()

    config['ftp_code'] = ftp_code
    config['file_path'] = file_path
    save_config(config)

ftp_info = FTP_LOCATIONS.get(ftp_code.lower())

if not ftp_info:
    print("Invalid FTP code.")
    exit()

FTP_HOST, FTP_USER, FTP_PASS, REMOTE_PATH = ftp_info
LOCAL_FILE = file_path

class FileChangeHandler(FileSystemEventHandler):
    def on_modified(self, event):
        if os.path.abspath(event.src_path) == os.path.abspath(LOCAL_FILE):
            print("File changed. Uploading...")
            upload_file()

def upload_file():
    try:
        with ftplib.FTP(FTP_HOST) as ftp:
            ftp.login(FTP_USER, FTP_PASS)
            ftp.cwd(REMOTE_PATH)
            with open(LOCAL_FILE, 'rb') as f:
                ftp.storbinary(f'STOR {os.path.basename(LOCAL_FILE)}', f)
        print("Upload successful.")
    except Exception as e:
        print("FTP upload failed:", e)

if __name__ == "__main__":
    folder_to_watch = os.path.dirname(LOCAL_FILE)
    event_handler = FileChangeHandler()
    observer = Observer()
    observer.schedule(event_handler, folder_to_watch, recursive=False)
    observer.start()
    print(f"Watching: {LOCAL_FILE}")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
