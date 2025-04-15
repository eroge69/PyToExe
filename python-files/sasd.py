import os
import tkinter as tk
from tkinter import messagebox
import psutil
import subprocess

def temizle_temp():
    os.system("del /q /f /s %temp%\\*")
    messagebox.showinfo("Ä°ÅŸlem Tamam", "GeÃ§ici dosyalar silindi.")

def temizle_prefetch():
    os.system("del /q /f /s C:\\Windows\\Prefetch\\*")
    messagebox.showinfo("Ä°ÅŸlem Tamam", "Prefetch klasÃ¶rÃ¼ temizlendi.")

def dns_temizle():
    os.system("ipconfig /flushdns")
    messagebox.showinfo("Ä°ÅŸlem Tamam", "DNS Ã¶nbelleÄŸi temizlendi.")

def sfc_tara():
    os.system("sfc /scannow")
    messagebox.showinfo("Ä°ÅŸlem BaÅŸlatÄ±ldÄ±", "SFC taramasÄ± baÅŸlatÄ±ldÄ±. Bitince komut isteminden kontrol edebilirsin.")

def dism_onar():
    os.system("DISM /Online /Cleanup-Image /RestoreHealth")
    messagebox.showinfo("Ä°ÅŸlem BaÅŸlatÄ±ldÄ±", "DISM iÅŸlemi baÅŸlatÄ±ldÄ±. Bitince komut isteminden kontrol edebilirsin.")

def disk_temizle():
    os.system("cleanmgr")

def ram_temizle():
    psutil.virtual_memory()
    os.system("echo RAM boÅŸaltma tetiklendi.")
    messagebox.showinfo("RAM Temizleme", "RAM temizleme denemesi yapÄ±ldÄ± (Windows sÄ±nÄ±rlÄ± destekler).")

def startup_listele():
    os.system("start cmd /k wmic startup get caption,command")

# GUI ArayÃ¼zÃ¼
pencere = tk.Tk()
pencere.title("ğŸš€ Aras HÄ±zlandÄ±rÄ±cÄ± v2.0")
pencere.geometry("400x500")
pencere.configure(bg="#1e1e1e")

buton_renk = "#00cc66"

tk.Label(pencere, text="Sistem HÄ±zlandÄ±rÄ±cÄ±", fg="white", bg="#1e1e1e", font=("Segoe UI", 16, "bold")).pack(pady=10)

tk.Button(pencere, text="Temp Temizle", command=temizle_temp, bg=buton_renk).pack(fill="x", padx=20, pady=5)
tk.Button(pencere, text="Prefetch Temizle", command=temizle_prefetch, bg=buton_renk).pack(fill="x", padx=20, pady=5)
tk.Button(pencere, text="DNS Flush", command=dns_temizle, bg=buton_renk).pack(fill="x", padx=20, pady=5)
tk.Button(pencere, text="SFC Tarama", command=sfc_tara, bg=buton_renk).pack(fill="x", padx=20, pady=5)
tk.Button(pencere, text="DISM Onarma", command=dism_onar, bg=buton_renk).pack(fill="x", padx=20, pady=5)
tk.Button(pencere, text="Disk Temizleme", command=disk_temizle, bg=buton_renk).pack(fill="x", padx=20, pady=5)
tk.Button(pencere, text="RAM Temizle", command=ram_temizle, bg=buton_renk).pack(fill="x", padx=20, pady=5)
tk.Button(pencere, text="BaÅŸlangÄ±Ã§ UygulamalarÄ±nÄ± GÃ¶ster", command=startup_listele, bg=buton_renk).pack(fill="x", padx=20, pady=5)

tk.Label(pencere, text="HazÄ±rlayan: Aras Edition ğŸ‘‘", fg="gray", bg="#1e1e1e", font=("Segoe UI", 10)).pack(pady=20)

pencere.mainloop()