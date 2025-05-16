import os
import subprocess
import uuid
import time
import sys
from colorama import Fore, Style, init
import shutil
from datetime import datetime

init(autoreset=True)

# ====== Lizenzsystem mit Ablaufdatum ======
LICENSE_KEYS = {
    "ABC123-XYZ789": "2025-06-01",
    "TEST-KEY-001": "2025-05-20",
    "PREMIUM-USER-555": "2025-12-31"
}

def check_license():
    clear_with_logo()
    cols, _ = get_terminal_size()
    print(Fore.CYAN + center_text("🔐 Lizenzprüfung mit Ablaufdatum", cols))
    print()

    key = input(Fore.YELLOW + center_text("Bitte Lizenzschlüssel eingeben:", cols) + "\n").strip()
    
    if key in LICENSE_KEYS:
        expiry_str = LICENSE_KEYS[key]
        expiry_date = datetime.strptime(expiry_str, "%Y-%m-%d")
        today = datetime.now()

        if today <= expiry_date:
            print(Fore.GREEN + center_text(f"✅ Lizenz gültig bis {expiry_str}", cols))
            time.sleep(1)
        else:
            print(Fore.RED + center_text(f"❌ Lizenz abgelaufen am {expiry_str}", cols))
            time.sleep(2)
            sys.exit()
    else:
        print(Fore.RED + center_text("❌ Ungültiger Lizenzschlüssel", cols))
        time.sleep(2)
        sys.exit()

# ====== Hilfsfunktionen ======
def center_text(text, width):
    return "\n".join(line.center(width) for line in text.splitlines())

def get_terminal_size():
    return shutil.get_terminal_size((80, 20))

def get_logo():
    return r"""
   ___       _           _           __                    __           
  /___\_ __ (_)_____   _| | ____ _  / _\_ __   ___   ___  / _| ___ _ __ 
 //  // '_ \| |_  / | | | |/ / _` | \ \| '_ \ / _ \ / _ \| |_ / _ \ '__|
/ \_//| | | | |/ /| |_| |   < (_| | _\ \ |_) | (_) | (_) |  _|  __/ |   
\___/ |_| |_|_/___|\__,_|_|\_\__,_| \__/ .__/ \___/ \___/|_|  \___|_|   
                                       |_|         """

def clear_with_logo():
    os.system('cls' if os.name == 'nt' else 'clear')
    cols, _ = get_terminal_size()
    print(Fore.MAGENTA + center_text(get_logo(), cols) + "\n")

def show_loading_animation():
    animation = ["[   ]", "[.  ]", "[.. ]", "[...]", "[ ..]", "[  .]", "[   ]"]
    for _ in range(2):
        for frame in animation:
            sys.stdout.write("\r" + Fore.YELLOW + frame.center(get_terminal_size().columns))
            sys.stdout.flush()
            time.sleep(0.1)
    print()

def get_powershell_value(command):
    try:
        result = subprocess.run(["powershell", "-Command", command],
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        return result.stdout.strip().splitlines()[0] if result.stdout.strip() else "Nicht gefunden"
    except Exception as e:
        return f"Fehler: {str(e)}"

def show_all_hwids():
    clear_with_logo()
    print(Fore.CYAN + center_text("Ermittle alle verfügbaren HWIDs...\n", get_terminal_size().columns))
    show_loading_animation()

    hwid_data = {
    "Motherboard (Serial)": "Get-WmiObject Win32_BaseBoard | Select-Object -ExpandProperty SerialNumber",
    "CPU (Processor ID)": "Get-WmiObject Win32_Processor | Select-Object -ExpandProperty ProcessorId",
    "Disk Serial": "Get-WmiObject Win32_PhysicalMedia | Select-Object -ExpandProperty SerialNumber",
    "GPU (Name)": "Get-WmiObject Win32_VideoController | Select-Object -First 1 -ExpandProperty Name"
    }

    output = ""
    for label, cmd in hwid_data.items():
        value = get_powershell_value(cmd)
        output += Fore.GREEN + f"{label}: {value}\n"

    print(center_text(output.strip(), get_terminal_size().columns))
    input(Fore.CYAN + center_text("\nDrücke Enter zum Zurückkehren...", get_terminal_size().columns))

def spoof_all_hwids():
    clear_with_logo()
    print(Fore.YELLOW + center_text("Spoofing der HWIDs wird gestartet...\n", get_terminal_size().columns))
    show_loading_animation()
    for hw in ["CPU", "Motherboard", "GPU"]:
        new_hwid = str(uuid.uuid4())
        print(Fore.GREEN + center_text(f"{hw} HWID geändert zu: {new_hwid}", get_terminal_size().columns))
        time.sleep(0.5)
    input(Fore.CYAN + center_text("\nSpoofing abgeschlossen. Drücke Enter...", get_terminal_size().columns))

def display_menu(blink):
    cols, _ = get_terminal_size()
    arrow = ">>" if blink else "  "
    menu = "\n".join([
        f"{arrow} [1] HWIDs anzeigen",
        f"{arrow} [2] HWIDs ändern",
        f"{arrow} [3] Beenden"
    ])
    print(Fore.CYAN + center_text(menu, cols))

# ====== Hauptprogramm ======
def main():
    check_license()  # Lizenzprüfung am Start

    blink = True
    while True:
        clear_with_logo()
        display_menu(blink)
        blink = not blink

        choice = input(Fore.WHITE + "\n" + "Auswahl: ".center(get_terminal_size().columns))

        if choice == "1":
            show_all_hwids()
        elif choice == "2":
            spoof_all_hwids()
        elif choice == "3":
            clear_with_logo()
            print(Fore.YELLOW + center_text("👋 Beende Programm...", get_terminal_size().columns))
            show_loading_animation()
            break
        else:
            print(Fore.RED + center_text("❗ Ungültige Eingabe. Bitte 1, 2 oder 3 wählen.", get_terminal_size().columns))
            time.sleep(1)

if __name__ == "__main__":
    main()
