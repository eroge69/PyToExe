import tkinter as tk
import subprocess
import os

root = tk.Tk()
root.title("Bypass Software.km")
root.geometry("400x350")

def samsung_frp_mtp():
    os.system("start https://youtube.com/redirect_mtp_exploit")  # Replace with local payload or script

def samsung_frp_download():
    subprocess.call("adb reboot download", shell=True)
    # Odin ya heimdall based script laga sakde aa

def samsung_factory_reset():
    subprocess.call("adb shell recovery --wipe_data", shell=True)

def oppo_vivo_frp():
    os.system("start https://youtube.com/exploit_mtp_oppo")  # Browser launch via MTP

# GUI Buttons
tk.Label(root, text="Samsung A Series Options", font=("Helvetica", 14)).pack(pady=10)
tk.Button(root, text="Samsung FRP Bypass (MTP Mode)", command=samsung_frp_mtp).pack(pady=5)
tk.Button(root, text="Samsung FRP Bypass (Download Mode)", command=samsung_frp_download).pack(pady=5)
tk.Button(root, text="Samsung Factory Reset", command=samsung_factory_reset).pack(pady=5)

tk.Label(root, text="Oppo / Vivo Options", font=("Helvetica", 14)).pack(pady=10)
tk.Button(root, text="Oppo/Vivo FRP Bypass (MTP Mode)", command=oppo_vivo_frp).pack(pady=5)

root.mainloop()
