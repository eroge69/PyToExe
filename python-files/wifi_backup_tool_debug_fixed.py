
import tkinter as tk
from tkinter import filedialog, messagebox
import subprocess
import os
import datetime

def log_message(message):
    with open("wifi_backup_log.txt", "a") as log_file:
        log_file.write(f"[{datetime.datetime.now()}] {message}\n")

def export_wifi_profiles():
    folder = filedialog.askdirectory(title="Select folder to export Wi-Fi profiles")
    if not folder:
        return

    log_message(f"Selected folder for export: {folder}")
    try:
        profiles_output = subprocess.check_output("netsh wlan show profiles", shell=True, text=True)
        profiles = []
        for line in profiles_output.splitlines():
            if "All User Profile" in line:
                profile_name = line.split(":")[1].strip()
                profiles.append(profile_name)

        if not profiles:
            messagebox.showwarning("No Profiles", "No Wi-Fi profiles found.")
            log_message("No profiles found to export.")
            return

        exported_count = 0
        quoted_folder = f'\"{folder}\"'
        for profile in profiles:
            log_message(f"Attempting to export profile: {profile}")
            result = subprocess.run(
                f'netsh wlan export profile name="{profile}" folder={quoted_folder} key=clear',
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            if result.returncode == 0:
                log_message(f"Successfully exported: {profile}")
                exported_count += 1
            else:
                log_message(f"Failed to export {profile}: {result.stderr.strip()}")

        messagebox.showinfo("Export Complete", f"Exported {exported_count} Wi-Fi profiles to:\n{folder}")
    except Exception as e:
        log_message(f"Exception during export: {str(e)}")
        messagebox.showerror("Error", f"An error occurred:\n{e}")

def import_wifi_profiles():
    folder = filedialog.askdirectory(title="Select folder with Wi-Fi profiles to import")
    if not folder:
        return

    log_message(f"Selected folder for import: {folder}")
    try:
        files = [f for f in os.listdir(folder) if f.endswith(".xml")]
        imported_count = 0
        for file in files:
            full_path = os.path.join(folder, file)
            log_message(f"Importing profile from file: {file}")
            result = subprocess.run(
                f'netsh wlan add profile filename="{full_path}" user=current',
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            if result.returncode == 0:
                log_message(f"Successfully imported: {file}")
                imported_count += 1
            else:
                log_message(f"Failed to import {file}: {result.stderr.strip()}")

        messagebox.showinfo("Import Complete", f"Imported {imported_count} Wi-Fi profiles from:\n{folder}")
    except Exception as e:
        log_message(f"Exception during import: {str(e)}")
        messagebox.showerror("Error", f"An error occurred:\n{e}")

root = tk.Tk()
root.title("Wi-Fi Profile Backup Tool")
root.geometry("320x180")

export_btn = tk.Button(root, text="Export Wi-Fi Profiles", command=export_wifi_profiles, width=30)
export_btn.pack(pady=15)

import_btn = tk.Button(root, text="Import Wi-Fi Profiles", command=import_wifi_profiles, width=30)
import_btn.pack(pady=15)

root.mainloop()
