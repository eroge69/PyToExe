
import os
import tkinter as tk
from tkinter import messagebox

def start_hotspot():
    ssid = ssid_entry.get()
    password = password_entry.get()

    if len(password) < 8:
        messagebox.showerror("خطأ", "كلمة السر لازم تكون 8 حروف أو أكثر.")
        return

    os.system(f'netsh wlan set hostednetwork mode=allow ssid={ssid} key={password}')
    os.system('netsh wlan start hostednetwork')
    messagebox.showinfo("نجاح", f"تم تشغيل الشبكة باسم: {ssid}")

def stop_hotspot():
    os.system('netsh wlan stop hostednetwork')
    messagebox.showinfo("تم الإيقاف", "تم إيقاف الشبكة بنجاح.")

# واجهة البرنامج
root = tk.Tk()
root.title("7mas - WiFi Hotspot")
root.geometry("300x200")

tk.Label(root, text="اسم الشبكة (SSID):").pack()
ssid_entry = tk.Entry(root)
ssid_entry.pack()

tk.Label(root, text="كلمة المرور:").pack()
password_entry = tk.Entry(root, show="*")
password_entry.pack()

tk.Button(root, text="تشغيل الشبكة", command=start_hotspot).pack(pady=5)
tk.Button(root, text="إيقاف الشبكة", command=stop_hotspot).pack()

root.mainloop()
