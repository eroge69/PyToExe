import os
import shutil
import subprocess
import sys
import tkinter as tk
from tkinter import messagebox

title_text = "【３０３　Ｃｌｅａｎｅｒ】"

def get_hwid():
    try:
        output = subprocess.check_output("vol C:", shell=True, text=True)
        for line in output.splitlines():
            if "Serial Number is" in line:
                serial = line.strip().split("Serial Number is")[-1].strip()
                return serial.lower()
    except Exception:
        return None

allowed_hwids = [
    "3824-6a31",  # příklad
]

def check_access():
    hwid = get_hwid()
    return hwid in allowed_hwids

def full_cleanup():
    try:
        subprocess.run(["taskkill", "/f", "/im", "explorer.exe"],
                       check=True,
                       stdout=subprocess.DEVNULL,
                       stderr=subprocess.DEVNULL,
                       creationflags=subprocess.CREATE_NO_WINDOW)

        subprocess.Popen("explorer.exe",
                         stdout=subprocess.DEVNULL,
                         stderr=subprocess.DEVNULL,
                         creationflags=subprocess.CREATE_NO_WINDOW)

        reg_keys = [
            r"HKCU\Software\Microsoft\Windows\CurrentVersion\Explorer\RunMRU",
            r"HKCU\Software\Microsoft\Windows\CurrentVersion\Explorer\ComDlg32\LastVisitedPidlMRU",
            r"HKCU\Software\Microsoft\Windows\CurrentVersion\Explorer\ComDlg32\OpenSavePidlMRU",
            r"HKCU\Software\Microsoft\Windows\CurrentVersion\Explorer\Map Network Drive MRU",
            r"HKCU\Software\Microsoft\Windows\CurrentVersion\Explorer\MountPoints2"
        ]

        for key in reg_keys:
            subprocess.run(["reg", "delete", key, "/f"],
                           check=True,
                           stdout=subprocess.DEVNULL,
                           stderr=subprocess.DEVNULL,
                           creationflags=subprocess.CREATE_NO_WINDOW)

        temp_path = os.path.join(os.getenv("LOCALAPPDATA"), "Temp")
        recent_path = os.path.join(os.getenv("APPDATA"), "Microsoft\\Windows\\Recent")

        for folder in [temp_path, recent_path]:
            if os.path.exists(folder):
                for item in os.listdir(folder):
                    item_path = os.path.join(folder, item)
                    try:
                        if os.path.isfile(item_path) or os.path.islink(item_path):
                            os.unlink(item_path)
                        elif os.path.isdir(item_path):
                            shutil.rmtree(item_path)
                    except:
                        pass  # Potlačit chyby bez výpisu

        messagebox.showinfo("Done", "System has been successfully cleaned.")
    except subprocess.CalledProcessError as e:
        messagebox.showerror("Error", f"Cleanup error: {e}")
    except Exception as e:
        messagebox.showerror("Error", f"An unexpected error occurred: {e}")

def main():
    if not check_access():
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror("Access Denied", "This software is not authorized to run on this device.")
        sys.exit()

    root = tk.Tk()
    root.title("303 Cleaner")
    root.geometry("420x220")
    root.resizable(False, False)
    root.configure(bg="#1c1c1c")
    root.overrideredirect(True)

    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    x = (screen_width // 2) - (420 // 2)
    y = (screen_height // 2) - (220 // 2)
    root.geometry(f"+{x}+{y}")

    tk.Label(
        root,
        text=title_text,
        font=("Segoe UI", 16, "bold"),
        bg="#1c1c1c",
        fg="#ffffff"
    ).pack(pady=20)

    tk.Button(
        root,
        text="🧹 Run Full Cleanup",
        command=full_cleanup,
        width=35,
        height=3,
        bg="#ff5555",
        fg="white",
        font=("Segoe UI", 10, "bold"),
        activebackground="#ff7777"
    ).pack(pady=10)

    tk.Label(
        root,
        text="⚠️ Run as administrator!",
        fg="#ffcc00",
        bg="#1c1c1c",
        font=("Segoe UI", 9, "italic")
    ).pack(pady=5)

    root.mainloop()

if __name__ == "__main__":
    main()
