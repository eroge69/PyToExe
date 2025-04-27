import time
import sys

RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
PURPLE = "\033[95m"
CYAN = "\033[96m"
RESET = "\033[0m"

print(RED+"""
    ██████╗██╗  ██╗ ██████╗╗███████╗████████╗
  ██╔════╝ ██║  ██║██╔═══██╗██╔════╝╚══██╔══╝
  ██║  ███╗███████║██║   ██║███████╗   ██║   
  ██║   ██║██╔══██║██║   ██║ ╚═══██║   ██║   
  ╚██████╔╝██║  ██║╚██████╔╝███████║   ██║   
   ╚═════╝ ╚═╝  ╚═╝ ╚═════╝ ╚══════╝   ╚═╝   
      """)

input(RESET+"Enter License Key: ")

spinner = ['|', '/', '-', '\\']  # the spinner frames

print(CYAN+"Loading ", end="", flush=True)

for _ in range(25):  # how long to spin (20 frames = about 5 seconds)
    for frame in spinner:
        print(f"\b{frame}", end="", flush=True)
        time.sleep(0.1)

print(GREEN+"\nPlease Start The Game Now!")
time.sleep(5)
