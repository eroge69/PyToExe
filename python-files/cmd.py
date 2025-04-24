import pyautogui
import subprocess
import time

# Open Notepad
subprocess.Popen(['notepad.exe'])

# Wait for Notepad to open
time.sleep(2)

# Type "Hello, World!" in Notepad
pyautogui.write("Hello, World!")
