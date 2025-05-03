import ctypes
import subprocess
import sys
import os

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

# Vérification des droits administratifs
if not is_admin():
    print("Admin privileges required, relaunching as admin...")
    ctypes.windll.shell32.ShellExecuteW(None, 'runas', sys.executable, sys.argv[0], None, 1)
    sys.exit()

def is_process_running(process_name):
    result = subprocess.run(['tasklist'], capture_output=True, text=True)
    return process_name.lower() in result.stdout.lower()

def stop_process(process_name):
    subprocess.call(['taskkill', '/f', '/im', process_name], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

def start_process(process_name):
    subprocess.call(['start', process_name], shell=True)

# ASCII art with "QUI.BYPASS"
ascii_art = """
░▒▓████████▓▒░▒▓███████▓▒░░▒▓████████▓▒░▒▓████████▓▒░      ░▒▓███████▓▒░ ░▒▓██████▓▒░       ░▒▓█▓▒░ 
░▒▓█▓▒░      ░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░      ░▒▓█▓▒░             ░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░      ░▒▓█▓▒░ 
░▒▓█▓▒░      ░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░      ░▒▓█▓▒░             ░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░             ░▒▓█▓▒░ 
░▒▓██████▓▒░ ░▒▓███████▓▒░░▒▓██████▓▒░ ░▒▓██████▓▒░        ░▒▓███████▓▒░░▒▓█▓▒░             ░▒▓█▓▒░ 
░▒▓█▓▒░      ░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░      ░▒▓█▓▒░             ░▒▓█▓▒░      ░▒▓█▓▒░             ░▒▓█▓▒░ 
░▒▓█▓▒░      ░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░      ░▒▓█▓▒░             ░▒▓█▓▒░      ░▒▓█▓▒░░▒▓█▓▒░              
░▒▓█▓▒░      ░▒▓█▓▒░░▒▓█▓▒░▒▓████████▓▒░▒▓████████▓▒░      ░▒▓█▓▒░       ░▒▓██████▓▒░       ░▒▓█▓▒░ 
                                                                                                    
                                                                                                    
"""

print(ascii_art)

process = "WpcMon.exe"

if is_process_running(process):
    print(f"{process} is running. Stopping it...")
    stop_process(process)
else:
    print(f"{process} is not running. Starting it...")
    start_process("C:\\Windows\\System32\\WpcMon.exe")  # Assure-toi que le chemin est correct

print("Done.")

# Garder le terminal ouvert jusqu'à ce que l'utilisateur appuie sur une touche
input("Press any key to exit...")  # Cette ligne attend une entrée de l'utilisateur
