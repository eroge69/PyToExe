
import tkinter as tk
import os
import webbrowser
from tkinter import messagebox

def open_browser():
    os.system("start chrome https://google.com")

def open_galaxy_store():
    webbrowser.open("https://www.samsung.com/global/galaxy/apps/galaxy-store/")

def open_odin():
    os.system("start Odin3.exe")

app = tk.Tk()
app.title("Samsung FRP Tool")
app.geometry("400x300")

tk.Label(app, text="Samsung FRP Bypass Tool", font=("Arial", 14)).pack(pady=10)
tk.Button(app, text="MTP Method: Open Browser", command=open_browser).pack(pady=10)
tk.Button(app, text="MTP Method: Open Galaxy Store", command=open_galaxy_store).pack(pady=10)

tk.Label(app, text="Download Mode FRP Method", font=("Arial", 12)).pack(pady=15)
tk.Button(app, text="Launch Odin", command=open_odin).pack(pady=10)

app.mainloop()
