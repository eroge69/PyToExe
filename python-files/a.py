import pyautogui
import time
import keyboard

text = "Hello please call me Parisa" 
delay = 0.1  
time.sleep(10)    

while True:
    if keyboard.is_pressed('.'):
        break
    pyautogui.typewrite(text)
    pyautogui.press('enter')
    time.sleep(delay)
