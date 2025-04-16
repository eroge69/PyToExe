import os
import subprocess
import psutil

def close_vlc():
    for proc in psutil.process_iter(['name']):
        if proc.info['name'].lower() == 'vlc.exe':
            proc.terminate()

def run_radioboss():
    radioboss_path = r"C:\Program Files (x86)\RadioBOSS\radioboss.exe"
    if os.path.exists(radioboss_path):
        subprocess.Popen(radioboss_path)
    else:
        print("RadioBOSS not found at specified path.")

close_vlc()
run_radioboss()