import subprocess
import os
import ctypes
import tkinter as tk
from tkinter import messagebox

reg_files = {
    "alfrygamingV2.reg": """Windows Registry Editor Version 5.00
[HKEY_CURRENT_USER\\Software\\AlfryGaming]
"Setting"="Enabled"
""",
    "cs1.6.reg": """Windows Registry Editor Version 5.00
[HKEY_CURRENT_USER\\Software\\CS1.6]
"GameEnabled"="1"
""",
    "cs2.reg": """Windows Registry Editor Version 5.00
[HKEY_CURRENT_USER\\Software\\CS2]
"GameEnabled"="1"
""",
    "fivem.reg": """Windows Registry Editor Version 5.00
[HKEY_CURRENT_USER\\Software\\fivem]
"GameEnabled"="1"
""",
    "win10.reg": """Windows Registry Editor Version 5.00
[HKEY_CURRENT_USER\\Software\\win10]
"GameEnabled"="1"
"""
}

def show_message(title, text, icon=0):
    # ikonok: 0=info, 16=error
    ctypes.windll.user32.MessageBoxW(0, text, title, icon)

def save_and_import(filename, content):
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(content)
        # reg import parancs
        subprocess.run(['reg', 'import', filename], check=True)
        os.remove(filename)
        show_message("Kész", "Sikeres aktiválás!", 0x40)  # MB_ICONINFORMATION
    except Exception as e:
        show_message("Hiba", f"Nem sikerült fájlt írni vagy importálni!\n{e}", 0x10)  # MB_ICONERROR

def on_button_click(key):
    filename = key
    content = reg_files[key]
    save_and_import(filename, content)

root = tk.Tk()
root.title("Reg Aktivátor")
root.geometry("300x300")

btn1 = tk.Button(root, text="AlfryGaming aktiválása", command=lambda: on_button_click("alfrygamingV2.reg"))
btn1.pack(pady=10)

btn2 = tk.Button(root, text="CS1.6 aktiválása", command=lambda: on_button_click("cs1.6.reg"))
btn2.pack(pady=10)

btn3 = tk.Button(root, text="CS2 aktiválása", command=lambda: on_button_click("cs2.reg"))
btn3.pack(pady=10)

btn4 = tk.Button(root, text="fivem aktiválása", command=lambda: on_button_click("fivem.reg"))
btn4.pack(pady=10)

btn5 = tk.Button(root, text="win10 aktiválása", command=lambda: on_button_click("win10.reg"))
btn5.pack(pady=10)

root.mainloop()
