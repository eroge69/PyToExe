Python 3.13.3 (tags/v3.13.3:6280bb5, Apr  8 2025, 14:47:33) [MSC v.1943 64 bit (AMD64)] on win32
Enter "help" below or click "Help" above for more information.
>>> import pyautogui
... import time
... 
... # Helper function for stable execution
... def delay():
...     time.sleep(0.5)
... 
... # Step 1: Click in the middle of the screen
... screen_width, screen_height = pyautogui.size()
... pyautogui.click(x=screen_width//2, y=screen_height//2)
... delay()
... 
... # Step 2: Type "FIND"
... pyautogui.write("FIND")
... delay()
... 
... # Step 3: Press Enter key
... pyautogui.press("enter")
... 
... # List of characters to cycle through
... characters = "ABCDEFGHIJKLMNOPQRSTUVWXYZ[];',./`"
... 
... # Loop through each character
... for char in characters:
...     pyautogui.press(char)  # Step 4: Press key
...     pyautogui.press("tab")  # Step 5
...     pyautogui.hotkey("alt", "shift")  # Step 6: Change language
...     pyautogui.press(char)  # Step 7: Press same key
...     pyautogui.press("tab", presses=5)  # Step 8
...     pyautogui.press("enter", presses=6)  # Step 9
...     pyautogui.press("tab", presses=8)  # Step 10
...     pyautogui.hotkey("alt", "shift")  # Step 11: Change language
...     pyautogui.hotkey("shift", char.lower())  # Step 12: Small letter variant
...     pyautogui.press("tab", presses=6)  # Step 13
...     pyautogui.press("enter", presses=6)  # Step 14
...     pyautogui.press("tab", presses=8)  # Step 15
...     
