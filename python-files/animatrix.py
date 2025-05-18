import os
import sys
import time
import ctypes
from colorama import init, Fore, Back, Style
from pyfiglet import figlet_format
import winreg as reg

init(autoreset=True)

def clear(): os.system("cls" if os.name == "nt" else "clear")

def print_banner():
    banner = figlet_format("Animatrix", font="slant")
    print(Fore.MAGENTA + banner)
    print(Fore.CYAN + "Windows Animation Controller - by Moai
")
    print(Fore.YELLOW + "[1] ✨ Apply Clean Animations")
    print("[2] ⚡ Apply Minimal Animations")
    print("[3] 💫 Apply Fancy Animations")
    print("[4] ♻️ Reset to Default")
    print("[5] 🎨 Theme: Neon Purple")
    print("[6] 🎨 Theme: Cyber Green")
    print("[7] 🎨 Theme: Matrix Blue")
    print("[8] 🧩 Extra Tweaks (Taskbar)")
    print("[9] ❌ Exit")

def set_animation(clean=True, fancy=False):
    try:
        key = r"Control Panel\Desktop\WindowMetrics"
        reg_key = reg.OpenKey(reg.HKEY_CURRENT_USER, key, 0, reg.KEY_SET_VALUE)
        val = "0" if not clean else "1"
        reg.SetValueEx(reg_key, "MinAnimate", 0, reg.REG_SZ, "1" if fancy else val)
        reg.CloseKey(reg_key)
        print(Fore.GREEN + "✔ Animation settings applied.")
    except Exception as e:
        print(Fore.RED + f"Error: {e}")

def apply_theme(color):
    os.system("color " + color)

def extra_tweaks():
    print(Fore.YELLOW + "Taskbar tweaks coming soon...")

def main():
    while True:
        clear()
        print_banner()
        choice = input(Fore.CYAN + "
Select option: ")

        if choice == "1":
            set_animation(clean=True)
        elif choice == "2":
            set_animation(clean=False)
        elif choice == "3":
            set_animation(fancy=True)
        elif choice == "4":
            set_animation(clean=True)
        elif choice == "5":
            apply_theme("D5")  # Purple
        elif choice == "6":
            apply_theme("A2")  # Green
        elif choice == "7":
            apply_theme("2A")  # Matrix
        elif choice == "8":
            extra_tweaks()
        elif choice == "9":
            print("Exiting...")
            break
        else:
            print(Fore.RED + "Invalid option.")

        input(Fore.CYAN + "
Press Enter to return to menu...")

if __name__ == "__main__":
    if os.name != "nt":
        print("This tool is for Windows only.")
        sys.exit()
    main()
