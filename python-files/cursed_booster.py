
import os
import shutil
import string
import colorama
from colorama import Fore, Style

colorama.init(autoreset=True)

def print_logo():
    logo = "Cursed Booster"
    terminal_width = shutil.get_terminal_size().columns
    centered_logo = logo.center(terminal_width)
    print("=" * terminal_width)
    print(Fore.RED + centered_logo)
    print("=" * terminal_width)

def list_drives():
    drives = [f"{d}:\\" for d in string.ascii_uppercase if os.path.exists(f"{d}:\\")]
    for i, drive in enumerate(drives):
        print(f"{i + 1}. {drive}")
    return drives

def get_user_drive(drives):
    while True:
        try:
            choice = int(input("Select the number corresponding to the drive where Dota 2 is installed: "))
            if 1 <= choice <= len(drives):
                return drives[choice - 1]
            else:
                print("Invalid number. Try again.")
        except ValueError:
            print("Please enter a valid number.")

def delete_paths(base_drive):
    relative_paths = [
        r"SteamLibrary\steamapps\common\dota 2 beta\game\dota\maps\backgrounds",
        r"SteamLibrary\steamapps\common\dota 2 beta\game\dota\models\heroes"
    ]

    for rel_path in relative_paths:
        full_path = os.path.join(base_drive, rel_path)
        if os.path.exists(full_path):
            shutil.rmtree(full_path)
            print(f"[✓] Deleted: {full_path}")
        else:
            print(f"[!] Path not found: {full_path}")

if __name__ == "__main__":
    print_logo()
    drives = list_drives()
    selected_drive = get_user_drive(drives)
    delete_paths(selected_drive)
    print("\nAll specified paths have been processed.")
