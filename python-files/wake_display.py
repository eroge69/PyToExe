
import pyautogui
import time

time.sleep(2)
x, y = pyautogui.position()
pyautogui.moveTo(x + 1, y)
pyautogui.moveTo(x, y)
