import time
import os
import subprocess
from configparser import ConfigParser

INI_PATH = r"C:\Program Files\ThrottleStop\ThrottleStop.ini"
PROFILE_BATTERY = "0"
PROFILE_PLUGGED = "1"
COMMAND_60HZ = [r"C:\Windows\QRes.exe", "/r:60"]
COMMAND_120HZ = [r"C:\Windows\QRes.exe", "/r:120"]
POLL_INTERVAL = 2  # secondi

last_profile = None

def get_current_profile():
    config = ConfigParser()
    config.read(INI_PATH)
    try:
        return config.get('Options', 'TSProfile')
    except:
        return None

def on_profile_change(new_profile):
    if new_profile == PROFILE_BATTERY:
        subprocess.Popen(COMMAND_60HZ)
    elif new_profile == PROFILE_PLUGGED:
        subprocess.Popen(COMMAND_120HZ)

def main():
    global last_profile
    if not os.path.exists(INI_PATH):
        return

    last_profile = get_current_profile()
    while True:
        current_profile = get_current_profile()
        if current_profile != last_profile:
            on_profile_change(current_profile)
            last_profile = current_profile
        time.sleep(POLL_INTERVAL)

if __name__ == "__main__":
    main()
