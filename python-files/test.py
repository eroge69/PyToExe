import os
import time
import ctypes
def disable_keyboard():
    ctypes.windll.user32.BlockInput(True)

def shutdown():
    os.system("shutdown /s /t 0")

disable_keyboard()

time.sleep(10)
shutdown()