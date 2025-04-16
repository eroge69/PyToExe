
import tkinter as tk
from tkinter import messagebox
import subprocess

def run_command(cmd):
    try:
        subprocess.run(cmd, shell=True, check=True)
    except subprocess.CalledProcessError:
        messagebox.showerror("خطا", f"خطا در اجرای دستور:\n{cmd}")

def reset_network():
    cmds = [
        "netsh winhttp reset proxy",
        'reg delete "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Internet Settings" /v ProxyServer /f',
        'reg delete "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Internet Settings" /v ProxyEnable /f',
        'reg add "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Internet Settings" /v ProxyEnable /t REG_DWORD /d 0 /f',
        "netsh winsock reset",
        "netsh int ip reset",
        "ipconfig /flushdns",
        "ipconfig /release",
        "ipconfig /renew",
        "net stop dnscache",
        "net start dnscache"
    ]
    for cmd in cmds:
        run_command(cmd)

    messagebox.showinfo("انجام شد", "✅ تنظیمات شبکه و پراکسی ریست شدند!")

def test_ping():
    try:
        output = subprocess.check_output("ping 8.8.8.8 -n 3", shell=True).decode("utf-8")
        messagebox.showinfo("نتیجه Ping", output)
    except subprocess.CalledProcessError:
        messagebox.showerror("خطا", "اتصال به اینترنت برقرار نیست.")

# رابط گرافیکی
root = tk.Tk()
root.title("ResetNetFix GUI - برای v2rayN")
root.geometry("320x200")
root.resizable(False, False)

label = tk.Label(root, text="🔧 ابزار ریست اینترنت و پراکسی", font=("Tahoma", 12, "bold"))
label.pack(pady=10)

btn_reset = tk.Button(root, text="ریست کامل تنظیمات شبکه", font=("Tahoma", 10), command=reset_network)
btn_reset.pack(pady=8)

btn_ping = tk.Button(root, text="تست اتصال به اینترنت", font=("Tahoma", 10), command=test_ping)
btn_ping.pack(pady=8)

btn_exit = tk.Button(root, text="خروج", font=("Tahoma", 10), command=root.quit)
btn_exit.pack(pady=8)

root.mainloop()
