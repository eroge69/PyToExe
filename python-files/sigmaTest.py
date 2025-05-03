import os
import tkinter as tk
from tkinter import messagebox
import subprocess
import datetime
import math

LOG_FILE = "cleaner_log.txt"

def log_action(action):
    with open(LOG_FILE, "a") as log:
        log.write(f"{datetime.datetime.now()}: {action}\n")

def confirm_and_run(command, title, description, warning):
    confirm = messagebox.askyesno(title, f"{description}\n\n{warning}\n\nMöchten Sie den Vorgang ausführen?")
    if confirm:
        try:
            subprocess.call(command, shell=True)
            log_action(f"Ausgeführt: {description}")
            messagebox.showinfo("Erfolg", f"{description} abgeschlossen.")
        except Exception as e:
            log_action(f"Fehler: {description} - {str(e)}")
            messagebox.showerror("Fehler", str(e))

# Functions
def clean_temp():
    confirm_and_run("del /f /s /q %TEMP%\\*", "Temporäre Dateien löschen",
                    "Löscht temporäre Dateien für den aktuellen Benutzer.", "")
def clean_prefetch():
    confirm_and_run("del /f /s /q C:\\Windows\\Prefetch\\*", "Prefetch löschen",
                    "Löscht Prefetch-Dateien zur Beschleunigung des Systemstarts.", "")
def clean_recent():
    confirm_and_run("del /f /s /q %APPDATA%\\Microsoft\\Windows\\Recent\\*", "Zuletzt verwendete Dateien löschen",
                    "Entfernt die Liste der zuletzt geöffneten Dateien.", "")
def clean_crashdumps():
    confirm_and_run("del /f /s /q %LOCALAPPDATA%\\CrashDumps\\*", "Crash Dumps löschen",
                    "Löscht Absturzprotokolle nach Programmabstürzen.", "")
def clean_eventlog():
    confirm_and_run("wevtutil cl System & wevtutil cl Application & wevtutil cl Security", "Ereignisprotokolle löschen",
                    "Löscht alle Windows-Ereignisprotokolle.", "Erfordert Administratorrechte.")
def clean_mru():
    confirm_and_run("reg delete HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\RunMRU /f",
                    "MRU-Einträge löschen", "Löscht zuletzt ausgeführte Programme im Ausführen-Dialog.", "")
def clean_shellbags():
    confirm_and_run("reg delete HKCU\\Software\\Microsoft\\Windows\\Shell\\BagMRU /f",
                    "ShellBags löschen", "Entfernt gespeicherte Ordneransichten und Explorer-Verlauf.", "")
def clean_dns():
    confirm_and_run("ipconfig /flushdns", "DNS-Cache leeren",
                    "Leert den lokalen DNS-Cache.", "")
def clean_internet_temp():
    confirm_and_run("RunDll32.exe InetCpl.cpl,ClearMyTracksByProcess 8", "Internet-Temporärdateien löschen",
                    "Löscht temporäre Internetdateien des Internet Explorers.", "")
def empty_recycle_bin():
    confirm_and_run("PowerShell -Command Clear-RecycleBin -Force", "Papierkorb leeren",
                    "Leert den Papierkorb für alle Laufwerke.", "")
def clear_fivem_cache():
    confirm_and_run("rmdir /s /q %localappdata%\\FiveM\\FiveM.app\\data\\cache",
                    "FiveM Cache leeren", "Löscht den FiveM-Cache zur Fehlerbehebung.", "")
def defragment_disk():
    confirm_and_run("defrag C: /O", "Festplatte defragmentieren",
                    "Optimiert und defragmentiert das Systemlaufwerk.", "")

def restart_pc():
    confirm_and_run("shutdown /r /t 0", "PC neu starten",
                    "Startet den Computer sofort neu.", "Nicht gespeicherte Daten gehen verloren.")
def shutdown_pc():
    confirm_and_run("shutdown /s /t 0", "PC herunterfahren",
                    "Fährt den Computer sofort herunter.", "Nicht gespeicherte Daten gehen verloren.")
def restart_explorer():
    confirm_and_run("taskkill /f /im explorer.exe & start explorer.exe", "Explorer neu starten",
                    "Startet den Windows Explorer neu (Taskleiste & Fenster).", "")
def renew_ip():
    confirm_and_run("ipconfig /release & ipconfig /renew", "IP-Adresse erneuern",
                    "Fordert eine neue IP-Adresse vom Router an.", "Die Verbindung kann kurzzeitig unterbrochen werden.")
def reset_network():
    confirm_and_run("netsh winsock reset & netsh int ip reset", "Netzwerk zurücksetzen",
                    "Setzt das Netzwerkprotokoll (Winsock, TCP/IP) auf Standard zurück.",
                    "Die Verbindung kann verloren gehen. Ein Neustart wird empfohlen.")
def clean_windows_update_cache():
    confirm_and_run("del /f /s /q C:\\Windows\\SoftwareDistribution\\Download\\*",
                    "Windows-Update-Cache löschen", "Löscht heruntergeladene Update-Dateien.", "")
def run_disk_cleanup():
    confirm_and_run("cleanmgr /sagerun:1", "Datenträgerbereinigung starten",
                    "Startet die erweiterte Windows-Datenträgerbereinigung.", "")
def delete_restore_points():
    confirm_and_run("vssadmin delete shadows /all /quiet", "Wiederherstellungspunkte löschen",
                    "Löscht alle Systemwiederherstellungspunkte.", "Diese Aktion kann nicht rückgängig gemacht werden.")

# New Category Functions
def open_task_manager():
    subprocess.call("taskmgr", shell=True)

def open_autostart_folder():
    autostart_path = os.path.expandvars(r"%USERPROFILE%\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup")
    subprocess.call(f"explorer {autostart_path}", shell=True)

def open_appdata_folder():
    appdata_path = os.path.expandvars(r"%USERPROFILE%\AppData")
    subprocess.call(f"explorer {appdata_path}", shell=True)

def open_programs_uninstall():
    subprocess.call("appwiz.cpl", shell=True)

def exit_app():
    if messagebox.askyesno("Beenden", "Möchten Sie das Programm wirklich schließen?"):
        root.destroy()

# GUI
root = tk.Tk()
root.title("made by canelios - sigmaClean")
root.geometry("800x600")
root.minsize(800, 600)  # Set minimum size
root.maxsize(800, 600)  # Set maximum size to be the same as the minimum
root.resizable(False, False)  # Disable resizing
root.configure(bg="black")

# Add the Kurdistan flag as a background (scalable with the window)
def draw_flag(canvas):
    canvas.create_rectangle(0, 0, 800, 200, fill="red")
    canvas.create_rectangle(0, 200, 800, 400, fill="white")
    canvas.create_rectangle(0, 400, 800, 600, fill="green")
    
    # Drawing the yellow sun (with rays)
    canvas.create_oval(300, 150, 500, 350, fill="yellow", outline="yellow")  # Sun
    
    # Drawing the 21 rays around the sun
    for i in range(21):
        angle = i * (360 / 21)
        x1 = 400 + 100 * math.cos(math.radians(angle))
        y1 = 250 + 100 * math.sin(math.radians(angle))
        x2 = 400 + 120 * math.cos(math.radians(angle))
        y2 = 250 + 120 * math.sin(math.radians(angle))
        canvas.create_line(x1, y1, x2, y2, fill="yellow", width=2)

canvas = tk.Canvas(root, width=800, height=600)
canvas.place(x=0, y=0)

draw_flag(canvas)

title = tk.Label(root, text="made by canelios - sigmaClean", bg="black", fg="white", font=("Segoe UI", 16, "bold"))
title.pack(pady=10)

# Categories
frame_paths = tk.LabelFrame(root, text="Paths", bg="black", fg="white", padx=10, pady=10)
frame_programs = tk.LabelFrame(root, text="Programs", bg="black", fg="white", padx=10, pady=10)
frame_windows = tk.LabelFrame(root, text="Windows", bg="black", fg="white", padx=10, pady=10)
frame_system = tk.LabelFrame(root, text="System", bg="black", fg="white", padx=10, pady=10)
frame_network = tk.LabelFrame(root, text="Network", bg="black", fg="white", padx=10, pady=10)
frame_cleanup = tk.LabelFrame(root, text="Cleanup", bg="black", fg="white", padx=10, pady=10)
frame_deepclean = tk.LabelFrame(root, text="Deep Clean", bg="black", fg="white", padx=10, pady=10)
frame_tools = tk.LabelFrame(root, text="Tools", bg="black", fg="white", padx=10, pady=10)

frame_paths.place(x=20, y=60, width=180, height=230)
frame_programs.place(x=220, y=60, width=180, height=230)
frame_windows.place(x=420, y=60, width=180, height=230)
frame_system.place(x=20, y=310, width=180, height=230)
frame_network.place(x=220, y=310, width=180, height=230)
frame_cleanup.place(x=420, y=310, width=180, height=230)
frame_deepclean.place(x=620, y=60, width=180, height=230)
frame_tools.place(x=620, y=310, width=180, height=230)

# Buttons for the Windows section
tk.Button(frame_windows, text="Clean Event Log", command=clean_eventlog, width=20).pack(pady=5)
tk.Button(frame_windows, text="Clean Shellbags", command=clean_shellbags, width=20).pack(pady=5)
tk.Button(frame_windows, text="Clean Run MRU", command=clean_mru, width=20).pack(pady=5)
tk.Button(frame_windows, text="Flush DNS Cache", command=clean_dns, width=20).pack(pady=5)
tk.Button(frame_windows, text="Internet Temp Files", command=clean_internet_temp, width=20).pack(pady=5)

# Buttons for the Cleanup section
tk.Button(frame_cleanup, text="Empty Recycle Bin", command=empty_recycle_bin, width=20).pack(pady=5)
tk.Button(frame_cleanup, text="Disk Defragmentation", command=defragment_disk, width=20).pack(pady=5)

# Buttons for the Paths section
tk.Button(frame_paths, text="Clean Temp", command=clean_temp, width=20).pack(pady=5)
tk.Button(frame_paths, text="Clean Prefetch", command=clean_prefetch, width=20).pack(pady=5)
tk.Button(frame_paths, text="Clean Recent", command=clean_recent, width=20).pack(pady=5)
tk.Button(frame_paths, text="Clean Crashdumps", command=clean_crashdumps, width=20).pack(pady=5)

# Buttons for the Programs section
tk.Button(frame_programs, text="FiveM Cache Clear", command=clear_fivem_cache, width=20).pack(pady=5)
tk.Button(frame_programs, text="Uninstall Programs", command=open_programs_uninstall, width=20).pack(pady=5)

# Buttons for the System section
tk.Button(frame_system, text="Restart PC", command=restart_pc, width=20).pack(pady=5)
tk.Button(frame_system, text="Shutdown PC", command=shutdown_pc, width=20).pack(pady=5)
tk.Button(frame_system, text="Restart Explorer", command=restart_explorer, width=20).pack(pady=5)

# Buttons for the Network section
tk.Button(frame_network, text="Renew IP", command=renew_ip, width=20).pack(pady=5)
tk.Button(frame_network, text="Reset Network", command=reset_network, width=20).pack(pady=5)

# Buttons for the Deep Clean section
tk.Button(frame_deepclean, text="Clean Win Update Cache", command=clean_windows_update_cache, width=20).pack(pady=5)
tk.Button(frame_deepclean, text="Run Disk Cleanup", command=run_disk_cleanup, width=20).pack(pady=5)
tk.Button(frame_deepclean, text="Delete Restore Points", command=delete_restore_points, width=20).pack(pady=5)

# Buttons for the Tools section
tk.Button(frame_tools, text="Open Task Manager", command=open_task_manager, width=20).pack(pady=5)
tk.Button(frame_tools, text="Open Autostart Folder", command=open_autostart_folder, width=20).pack(pady=5)
tk.Button(frame_tools, text="Open AppData Folder", command=open_appdata_folder, width=20).pack(pady=5)

# Exit
tk.Button(root, text="Exit", command=exit_app, width=10).place(x=700, y=560)

root.mainloop()
