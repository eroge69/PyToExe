import pyperclip
import keyboard
import time

def replace_on_copy():
    while True:
        keyboard.wait('ctrl+c')
        time.sleep(0.05)  # Give clipboard time to update
        text = pyperclip.paste()
        if text:
            modified = text.replace('-', '_')
            pyperclip.copy(modified)
            print(f"Modified: {modified}")

replace_on_copy()
