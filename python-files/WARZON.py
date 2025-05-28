import tkinter as tk
from tkinter import messagebox
import subprocess
import platform
import threading

# لیست IPهای سرورهای Warzone (تقریبی)
servers = {
    "Europe (Germany)": "18.185.0.1",
    "Asia (Singapore)": "13.228.0.1",
    "US East": "3.86.0.1",
    "US West": "13.57.0.1",
    "Middle East (UAE)": "3.28.0.1"
}

# گرفتن پینگ برای یک سرور
def ping(ip):
    param = "-n" if platform.system().lower() == "windows" else "-c"
    command = ["ping", param, "3", ip]
    try:
        output = subprocess.check_output(command, universal_newlines=True)
        for line in output.splitlines():
            if "Average" in line:
                avg_str = line.split("Average =")[-1].strip().replace("ms", "")
                return int(avg_str)
            elif "avg" in line.lower():
                numbers = [int(s.replace("ms", "")) for s in line.split("/") if s.strip().isdigit()]
                if numbers:
                    return numbers[1]
    except:
        return None
    return None

# فعالسازی محدودیت اتصال فقط به یک IP
def set_firewall(ip):
    try:
        subprocess.call(
            'netsh advfirewall firewall add rule name="WZ_Lock" dir=out action=block remoteip=0.0.0.0-255.255.255.255 enable=yes',
            shell=True
        )
        subprocess.call(
            f'netsh advfirewall firewall add rule name="WZ_Allow" dir=out action=allow remoteip={ip} enable=yes',
            shell=True
        )
        return True
    except:
        return False

# حذف محدودیت‌ها
def disable_firewall():
    try:
        subprocess.call('netsh advfirewall firewall delete rule name="WZ_Lock"', shell=True)
        subprocess.call('netsh advfirewall firewall delete rule name="WZ_Allow"', shell=True)
        return True
    except:
        return False

# اجرای پینگ در ترد جداگانه
def run_ping():
    results = {}
    status_label.config(text="در حال بررسی پینگ...")
    for name, ip in servers.items():
        ping_val = ping(ip)
        if ping_val is not None:
            results[name] = (ip, ping_val)
        root.update()
    if results:
        best = min(results.items(), key=lambda x: x[1][1])
        best_label.config(text=f"بهترین سرور: {best[0]} ({best[1][1]} ms)")
        global best_ip
        best_ip = best[1][0]
        set_button.config(state="normal")
    else:
        best_label.config(text="هیچ سروری پاسخ نداد.")
    status_label.config(text="")

# کلیک برای فعال کردن قانون firewall
def on_set():
    if best_ip:
        ok = set_firewall(best_ip)
        if ok:
            messagebox.showinfo("موفق", f"تنظیم انجام شد: فقط IP {best_ip} آزاد است.")
        else:
            messagebox.showerror("خطا", "نتوانستم firewall را تنظیم کنم.")

# کلیک برای حذف قوانین
def on_disable():
    ok = disable_firewall()
    if ok:
        messagebox.showinfo("غیرفعال", "تمام محدودیت‌ها حذف شدند.")
    else:
        messagebox.showerror("خطا", "نتوانستم قوانین را حذف کنم.")

# رابط گرافیکی
root = tk.Tk()
root.title("Warzone Ping Selector")
root.geometry("400x300")

status_label = tk.Label(root, text="", fg="blue")
status_label.pack(pady=10)

ping_button = tk.Button(root, text="شروع بررسی پینگ", command=lambda: threading.Thread(target=run_ping).start())
ping_button.pack(pady=10)

best_label = tk.Label(root, text="هنوز سروری انتخاب نشده")
best_label.pack(pady=10)

set_button = tk.Button(root, text="فعال‌سازی فقط این سرور", command=on_set, state="disabled")
set_button.pack(pady=10)

disable_button = tk.Button(root, text="غیرفعال‌سازی محدودیت‌ها", command=on_disable)
disable_button.pack(pady=10)

best_ip = None

root.mainloop()
