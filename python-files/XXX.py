import random
import time
import os
import sys
import threading
import subprocess

def generate_random_string(length=8):
    symbols = ['$', '#', '2', '!', '%', '&', '*', '+', '^', '@']
    return ''.join(random.choice(symbols) for _ in range(length))

def escape_special_chars(title):
    special_chars = ['&', '|', ';', '<', '>', '^']
    for char in special_chars:
        title = title.replace(char, f"^{char}")
    return title

def title_spam():
    while True:
        random_title = generate_random_string(10)
        if sys.platform == "win32":
            escaped_title = escape_special_chars(random_title)
            os.system(f'title "{escaped_title}" > nul 2>&1')
        else:
            sys.stdout.write(f"\033]0;{random_title}\007")
        time.sleep(0.5)

def login():
    password = "WEB"
    user_input = input("Enter password: ")
    if user_input == password:
        print("Login successful!")
        return True
    else:
        print("Incorrect password. Exiting...")
        return False

def run_batch_commands():
    batch_commands = """
    @echo off
    color 2
    start http://192.168.1.20/DenizXXX/
    """

    batch_file = "temp_script.bat"
    with open(batch_file, "w") as f:
        f.write(batch_commands)

    subprocess.run(batch_file, shell=True)

    os.remove(batch_file)

threading.Thread(target=title_spam, daemon=True).start()

if login():
    os.system('cls' if sys.platform == "win32" else 'clear')
    print("You're in")
    run_batch_commands()
    print("")
    exit
    sys.exit()
