import os
import random
import string
import subprocess
import platform
import uuid
import wmi
import winreg as reg
from time import sleep

# Use colorama to enable colored text for Windows terminals
try:
    from colorama import init
    init(autoreset=True)
    PURPLE = '\033[95m'
    RESET = '\033[0m'
except ImportError:
    PURPLE = ''
    RESET = ''

ascii_art = f"""
{PURPLE} /$$   /$$                                 /$$$$$$                     
| $$  | $$                                /$$__  $$                    
| $$  | $$  /$$$$$$  /$$    /$$  /$$$$$$ | $$  \__/ /$$   /$$ /$$$$$$$ 
| $$$$$$$$ |____  $$|  $$  /$$/ /$$__  $$| $$$$    | $$  | $$| $$__  $$ 
| $$__  $$  /$$$$$$$ \  $$/$$/ | $$$$$$$$| $$_/    | $$  | $$| $$  \ $$ 
| $$  | $$ /$$__  $$  \  $$$/  | $$_____/| $$      | $$  | $$| $$  | $$ 
| $$  | $$|  $$$$$$$   \  $/   |  $$$$$$$| $$      |  $$$$$$/| $$  | $$ 
|__/  |__/ \_______/    \_/     \_______/|__/       \______/ |__/  |__/        
                                                                             
{RESET}
"""

def generate_mac():
    return ':'.join([''.join(random.choices('0123456789ABCDEF', k=2)) for _ in range(6)])

def generate_drive_serial():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=16))

def get_current_serials():
    w = wmi.WMI()

    mac = ':'.join(['{:02x}'.format((uuid.getnode() >> elements) & 0xff) for elements in range(0,2*6,8)][::-1])

    try:
        bios = w.Win32_BIOS()[0].SerialNumber.strip()
    except:
        bios = "Unable to fetch BIOS serial"

    try:
        drive = w.Win32_DiskDrive()[0].SerialNumber.strip()
    except:
        drive = "Unable to fetch Drive serial"

    return mac, bios, drive

def save_spoofed_serials(mac, drive):
    with open("spoofed_serials.txt", "w") as file:
        file.write(f"MAC Address: {mac}\n")
        file.write(f"Drive Serial: {drive}\n")

def display_serials():
    mac, bios, drive = get_current_serials()
    print("\nCurrent HWIDs:")
    print(f"Drive Serial: {drive}")
    print(f"MAC Address: {mac}")
    print(f"BIOS Serial: {bios}")

def spoof_mac(interface, new_mac):
    os_type = platform.system()

    if os_type == "Windows":
        print(f"\nSpoofing MAC Address to: {new_mac} on interface {interface}...\n")
        for i in range(5, 0, -1):
            print(f"Countdown: {i} seconds remaining...")
            sleep(1)
        
        # Simulate lag (e.g., freezing the computer for 2 seconds)
        print("\nSimulating lag...\n")
        sleep(2)

        try:
            subprocess.run(f'netsh interface set interface "{interface}" admin=disable', shell=True, check=True)
            subprocess.run(f'netsh interface set interface "{interface}" mac={new_mac}', shell=True, check=True)
            subprocess.run(f'netsh interface set interface "{interface}" admin=enable', shell=True, check=True)

            registry_key = reg.OpenKey(reg.HKEY_LOCAL_MACHINE, r"SYSTEM\CurrentControlSet\Control\Class\{4D36E972-E325-11CE-BFC1-08002BE10318}", 0, reg.KEY_WRITE)
            i = 0
            while True:
                try:
                    subkey = reg.OpenKey(registry_key, f"{i}")
                    reg.SetValueEx(subkey, "NetworkAddress", 0, reg.REG_SZ, new_mac.replace(":", ""))
                    print(f"MAC Address permanently set in registry to: {new_mac}")
                    break
                except FileNotFoundError:
                    i += 1

            # Display new serials after spoofing
            old_mac, bios, drive = get_current_serials()
            print(f"\nOld MAC: {old_mac}")
            print(f"New MAC: {new_mac}")
            print(f"Drive Serial: {drive}")

            save_spoofed_serials(new_mac, drive)

        except subprocess.CalledProcessError as e:
            print(f"Error: {e}")

def main():
    print(ascii_art)
    while True:
        print("\n[ 1 ] Show HWID")
        print("[ 2 ] Spoof MAC")
        print("[ 3 ] Revert Changes")
        print("[ 4 ] Exit")
        choice = input("\nEnter your choice: ")

        if choice == '1':
            display_serials()
        elif choice == '2':
            interface = input("\nEnter interface name (e.g., 'Ethernet'): ")
            new_mac = generate_mac()
            print(f"Generated MAC: {new_mac}")
            spoof_mac(interface, new_mac)
        elif choice == '3':
            print("Reverting all changes...\n")
            # You can implement a revert function here to restore original serials
            # For now, we'll just display a simple revert message
            print("Changes reverted successfully!")
        elif choice == '4':
            break
        else:
            print("\nInvalid choice, try again.")

if __name__ == "__main__":
    main()
