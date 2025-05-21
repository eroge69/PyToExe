import tkinter as tk
from tkinter import ttk, messagebox
import subprocess
import sys
import os
from tkinter import font as tkfont

def is_admin():
    try:
        return os.getuid() == 0
    except AttributeError:
        import ctypes
        return ctypes.windll.shell32.IsUserAnAdmin() != 0

def run_as_admin():
    if not is_admin():
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
        sys.exit()

def fix_vibration():
    try:
        # نصب درایورهای لازم
        commands = [
            'pnputil /add-driver "C:\\Windows\\System32\\DriverStore\\FileRepository\\sdvcontroller.inf_amd64_*\\sdvcontroller.inf" /install',
            'pnputil /add-driver "C:\\Windows\\System32\\DriverStore\\FileRepository\\hidserv.inf_amd64_*\\hidserv.inf" /install',
            'reg add "HKLM\\SYSTEM\\CurrentControlSet\\Services\\hidserv" /v "Start" /t REG_DWORD /d "2" /f',
            'sc config hidserv start= auto',
            'sc start hidserv'
        ]
        
        for cmd in commands:
            subprocess.run(cmd, shell=True, check=True)
            
        messagebox.showinfo("موفقیت", "درایورها و سرویس‌های لازم با موفقیت نصب شدند.\nلطفاً کنترلر را دوباره وصل کنید.")
        
    except subprocess.CalledProcessError as e:
        messagebox.showerror("خطا", f"خطا در اجرای دستورات:\n{e}")

def create_gui():
    root = tk.Tk()
    root.title("رفع مشکل ویبره استدیا گو - نسخه 1.0")
    root.geometry("500x350")
    root.resizable(False, False)
    
    # تم دارک
    root.configure(bg='#2d2d2d')
    style = ttk.Style()
    style.theme_use('clam')
    
    style.configure('TFrame', background='#2d2d2d')
    style.configure('TLabel', background='#2d2d2d', foreground='white')
    style.configure('TButton', background='#3e3e3e', foreground='white', borderwidth=1)
    style.map('TButton', background=[('active', '#4e4e4e')])
    style.configure('TNotebook', background='#2d2d2d', borderwidth=0)
    style.configure('TNotebook.Tab', background='#3e3e3e', foreground='white', padding=[10, 5])
    style.map('TNotebook.Tab', background=[('selected', '#1e1e1e')])
    
    # فونت‌ها
    title_font = tkfont.Font(family="Segoe UI", size=14, weight="bold")
    text_font = tkfont.Font(family="Segoe UI", size=10)
    
    # محتوای اصلی
    main_frame = ttk.Frame(root)
    main_frame.pack(pady=20, padx=20, fill='both', expand=True)
    
    ttk.Label(main_frame, text="رفع مشکل ویبره دسته کنترلر استدیا گو", font=title_font).pack(pady=10)
    
    ttk.Label(main_frame, 
              text="این ابزار مشکل عدم کارکرد ویبره دسته کنترلر استدیا گو در ویندوز را حل می‌کند.",
              font=text_font, wraplength=400).pack(pady=10)
    
    ttk.Label(main_frame, 
              text="لطفاً قبل از ادامه:\n1. کنترلر را از طریق بلوتوث به کامپیوتر متصل کنید\n2. مطمئن شوید به اینترنت متصل هستید\n3. این برنامه را با حقوق مدیر اجرا کنید",
              font=text_font, wraplength=400, justify='left').pack(pady=20)
    
    ttk.Button(main_frame, text="رفع مشکل ویبره", command=fix_vibration).pack(pady=20)
    
    ttk.Label(main_frame, 
              text="پس از اتمام کار، کنترلر را دوباره راه‌اندازی کنید.",
              font=text_font, wraplength=400).pack()
    
    root.mainloop()

if __name__ == "__main__":
    if not is_admin():
        messagebox.showerror("خطای دسترسی", "لطفاً این برنامه را با حقوق مدیر (Run as Administrator) اجرا کنید.")
        sys.exit(1)
    create_gui()