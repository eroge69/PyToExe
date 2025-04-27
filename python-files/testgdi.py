import win32api 
import win32con 
import win32gui 
import math 
from random import * 
import random 
import time 

def sines(): 
    desktop = win32gui.GetDesktopWindow() 
    hdc = win32gui.GetWindowDC(desktop) 
    sw = win32api.GetSystemMetrics(0) 
    sh = win32api.GetSystemMetrics(1) 
    angle = 0 

    while True: 
        hdc = win32gui.GetWindowDC(desktop) 
        for i in range(int(sw + sh)): 
            a = int(math.sin(angle) * randrange(999)) 
            win32gui.BitBlt(hdc, randrange(99), i, sw, randrange(99), hdc, 0, i, win32con.SRCCOPY) 
            angle += math.pi / random.randint(10, 999) 
        win32gui.ReleaseDC(desktop, hdc) 
        time.sleep(0.01) 

if __name__ == '__main__': 
    sines()