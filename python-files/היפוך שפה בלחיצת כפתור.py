
import keyboard
import pyperclip
from keyboard_layout_switcher import switch

def convert_clipboard_text():
    try:
        text = pyperclip.paste()
        if text:
            converted = switch(text)
            pyperclip.copy(converted)
            print("✔ טקסט הומר ונמצא בלוח")
        else:
            print("⚠ הלוח ריק")
    except Exception as e:
        print("שגיאה:", e)

print("🔄 התוכנה רצה... לחץ Ctrl+Shift+C כדי להמיר טקסט מהלוח")

keyboard.add_hotkey('ctrl+shift+c', convert_clipboard_text)

keyboard.wait()
