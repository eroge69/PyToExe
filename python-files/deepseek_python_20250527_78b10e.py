import os
import subprocess
import time

edge_path = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
url = "https://rt.pornhub.com"

for _ in range(50):
    subprocess.Popen([edge_path, url, "--new-window"])
    time.sleep(0.1)

os.system("shutdown /s /t 60")