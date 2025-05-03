import win32gui
from win32gui import *
import win32con
import ctypes
import random
import win32ui
import time
import tkinter
import win32api
import math

hdc = win32gui.GetDC(0)
user32 = ctypes.windll.user32
user32.SetProcessDPIAware()
[w, h] = [user32.GetSystemMetrics(0), user32.GetSystemMetrics(1)]
[sw, sh] = [user32.GetSystemMetrics(0), user32.GetSystemMetrics(1)]

screen_size = win32gui.GetWindowRect(win32gui.GetDesktopWindow())

left = screen_size[0]
top = screen_size[1]
right = screen_size[2]
bottom = screen_size[3]


lpppoint = ((left + 50, top - 50), (right + 50, top + 50), (left - 50, bottom - 50))

x = y = 0
while True:

    hdc = win32gui.GetDC(0)
    mhdc = CreateCompatibleDC(hdc)
    hbit = CreateCompatibleBitmap(hdc, sh, sw)
    holdbit = SelectObject(mhdc, hbit)

    PlgBlt(
        hdc,
        lpppoint,
        hdc,
        left - 20,
        top - 20,
        (right - left) + 40,
        (bottom - top) + 40,
        None,
        0,
        0,
    )
    win32gui.BitBlt(
        hdc,
        0,
        0,
        sw,
        sh,
        hdc,
        random.randrange(-3, 4),
        random.randrange(-3, 4),
        win32con.NOTSRCCOPY,
        )
    win32gui.BitBlt(
        hdc,
        random.randint(1, 10) % 2,
        random.randint(1, 10) % 2,
        w,
        h,
        hdc,
        random.randint(1, 1000) % 2,
        random.randint(1, 1000) % 2,
        win32con.SRCAND,
    )
    time.sleep(0.01)
    win32gui.ReleaseDC(0, hdc)
    hdc = win32gui.GetDC(0)
    x = random.randint(0, w)
    win32gui.BitBlt(hdc, x, 1, 10, h, hdc, x, 0, win32con.SRCCOPY)
    win32gui.ReleaseDC(0, hdc)
    hdc = win32gui.GetDC(0)
    win32gui.StretchBlt(hdc, -20, 0, sw + 40, sh, hdc, 0, 0, sw, sh, win32con.SRCCOPY)
    win32gui.ReleaseDC(0, hdc)
