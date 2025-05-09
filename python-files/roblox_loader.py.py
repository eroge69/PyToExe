import time
import random
import os
import sys
from colorama import init, Fore, Style
import ctypes

# Set fake console title
ctypes.windll.kernel32.SetConsoleTitleW("Roblox AimHelper v1.3")

# Initialize colorama
init(autoreset=True)

def print_matrix_line(width=80):
    line = ''.join(random.choice('01ABCDEFGHIJKLMNOPQRSTUVWXYZ') for _ in range(width))
    print(Fore.GREEN + line)

def matrix_intro(duration=3):
    end_time = time.time() + duration
    while time.time() < end_time:
        print_matrix_line()
        time.sleep(0.05)

def fake_loader():
    steps = [
        "Checking for Roblox Beta process...",
        "Injecting DLL...",
        "Bypassing anti-cheat...",
        "Aim module loaded successfully."
    ]
    delays = [2, 2, 3, 2]

    for step, delay in zip(steps, delays):
        print(Fore.CYAN + "\n>>> " + step)
        time.sleep(delay)

    print(Fore.GREEN + Style.BRIGHT + "\n[+] Loader finished. Ready to aim.")

matrix_intro()
fake_loader()
