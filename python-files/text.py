import os
import webbrowser
import socket
import subprocess
import shutil
import time
import random
import tkinter as tk
from tkinter import messagebox

RED = "\033[91m"
RESET = "\033[0m"

ascii_title = """
██╗░░░░░██╗░░██╗███████╗██╗░░░██╗  ████████╗░█████╗░░█████╗░██╗░░░░░
██║░░░░░╚██╗██╔╝╚════██║╚██╗░██╔╝  ╚══██╔══╝██╔══██╗██╔══██╗██║░░░░░
██║░░░░░░╚███╔╝░░░███╔═╝░╚████╔╝░  ░░░██║░░░██║░░██║██║░░██║██║░░░░░
██║░░░░░░██╔██╗░██╔══╝░░░░╚██╔╝░░  ░░░██║░░░██║░░██║██║░░██║██║░░░░░
███████╗██╔╝╚██╗███████╗░░░██║░░░  ░░░██║░░░╚█████╔╝╚█████╔╝███████╗
╚══════╝╚═╝░░╚═╝╚══════╝░░░╚═╝░░░  ░░░╚═╝░░░░╚════╝░░╚════╝░╚══════╝
"""

menu_options_list = [
    "(1) Discord                 (5) Redeem Code",
    "(2) Local IP Address        (6) Network Scan",
    "(3) Port Scanner            (7) SenoX Discord",
    "(4) Ping Scanner            (8) soon"
]

def center_text(text):
    terminal_width = shutil.get_terminal_size().columns
    return "\n".join([line.center(terminal_width) for line in text.strip("\n").split("\n")])

def clear():
    os.system("cls" if os.name == "nt" else "clear")

def admin_panel():
    window = tk.Tk()
    window.title("Admin Panel - Terminal Style")
    window.geometry("800x600")
    window.configure(bg="black")

    # Add a label with ASCII art at the top
    label = tk.Label(window, text=ascii_title, font=("Courier", 8), fg="red", bg="black", anchor="w", justify="left")
    label.pack(fill="both", padx=10, pady=10)

    # Create a frame for commands
    command_frame = tk.Frame(window, bg="black")
    command_frame.pack(fill="both", padx=10, pady=10)

    output_text = tk.Text(command_frame, wrap="word", height=15, width=90, font=("Courier", 10), fg="green", bg="black")
    output_text.pack(padx=10, pady=10)
    output_text.insert(tk.END, "Welcome to the Admin Panel.\nType 'help' for available commands.\n")

    def handle_command():
        command = command_entry.get().strip().lower()
        if command == "help":
            output_text.insert(tk.END, "\nAvailable commands:\n  1: Start Dancing\n  2: Exit\n  3: Show Codes\n")
        elif command == "1":
            dance_ascii_guy()
        elif command == "2":
            window.destroy()  # Close the admin panel window
        elif command == "3":
            show_all_codes()
        else:
            output_text.insert(tk.END, f"\n[✘] Invalid command: {command}\n")

    def dance_ascii_guy():
        output_text.insert(tk.END, "\nStarting ASCII dance...\n")
        time.sleep(1)
        dance_frames = [
            """\o/
             |
            / \\""",
            """ o/
            <|
            /\\
            """
        ]
        for frame in dance_frames:
            clear()
            output_text.insert(tk.END, frame + "\n")
            window.update_idletasks()
            time.sleep(0.5)

    def show_all_codes():
        output_text.insert(tk.END, "\n[✓] Available Codes:\n")
        output_text.insert(tk.END, "AdminSindrichtigeSigmas!202504 - Admin panel\n")
        output_text.insert(tk.END, "LxzyIsCooked - Parrot Unlock\n")
        output_text.insert(tk.END, "SenoX2025 - Geometry Dash Unlock\n")
        output_text.insert(tk.END, "4ltro4488 - Discord link\n")

    command_entry = tk.Entry(window, font=("Courier", 12), bg="black", fg="green")
    command_entry.pack(pady=20, padx=10)

    enter_button = tk.Button(window, text="Enter", font=("Courier", 12), fg="black", bg="green", command=handle_command)
    enter_button.pack(pady=10)

    window.mainloop()

def main():
    clear()
    print(RED + center_text(ascii_title) + RESET)
    print()
    for option in menu_options_list:
        print(RED + option.center(shutil.get_terminal_size().columns) + RESET)
    print("\n[answer] type 'help' for commands.\n")

    while True:
        try:
            command = input("answer> ").strip().lower()

            if command == "help":
                print("Available commands:")
                print("  help     - show this help")
                print("  exit     - quit the tool")
                print("  1        - open Discord")
                print("  2        - show Local IP Address")
                print("  3        - perform Port Scan")
                print("  4        - perform Ping Scan")
                print("  5        - Redeem Code")
                print("  6        - Network Scan")
                print("  7        - open SenoX Discord")
                print("  8        - soon")
                print("")

            elif command == "exit":
                print("Goodbye.")
                break
            elif command == "1":
                print("Opening Discord link...\n[✓] Discord module initialized.")
                webbrowser.open("https://discord.gg/y25VtUAzhf")
            elif command == "2":
                ip = socket.gethostname()
                local_ip = socket.gethostbyname(ip)
                print(f"Your local IP address is: {local_ip}")
            elif command == "3":
                ip = input("Enter the IP address to scan: ").strip()
                print(f"Scanning ports on {ip}...")
            elif command == "4":
                ip = input("Enter the IP address to ping: ").strip()
                print(f"Pinging {ip}...")
            elif command == "5":
                code = input("Enter Redeem Code: ").strip()
                if code == "AdminSindrichtigeSigmas!202504":
                    admin_panel()
                else:
                    print("[✘] Incorrect Redeem Code.")
            elif command == "6":
                print("[✓] Starting network scan...")
            elif command == "7":
                print("[✓] Opening SenoX Discord...")
                webbrowser.open("https://discord.gg/Anx96YVYur")
            elif command == "8":
                print("[~] Coming soon...")
            else:
                print("[✘] Invalid command. Type 'help' for a list of commands.")
        except Exception as e:
            print(f"[✘] Error: {e}")

if __name__ == "__main__":
    main()
