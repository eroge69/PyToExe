
import subprocess
import webbrowser
import tkinter as tk
from tkinter import messagebox

def get_volume_ids():
    try:
        result = subprocess.check_output("wmic logicaldisk get VolumeSerialNumber", shell=True)
        return result.decode()
    except Exception as e:
        return ""

def check_usb_connected(target_id):
    volumes = get_volume_ids()
    return target_id in volumes

def open_portal():
    if check_usb_connected("16D2-6C99"):
        webbrowser.open("https://portal.office.com")
    else:
        messagebox.showerror("خطأ", "الفلاشة غير متصلة، لا يمكن تشغيل السيرفر.")

root = tk.Tk()
root.title("تشغيل السيرفر")
root.geometry("300x150")
button = tk.Button(root, text="تشغيل السيرفر", command=open_portal, font=("Arial", 12), width=20, height=2)
button.pack(expand=True)
root.mainloop()
