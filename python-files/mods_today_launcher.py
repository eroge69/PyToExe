
import tkinter as tk
from tkinter import messagebox
import webbrowser
import os

def open_link(url):
    webbrowser.open(url)

def launch_game():
    messagebox.showinfo("Launch Game", "Launching Command & Conquer: Generals Zero Hour...")

def open_folder():
    path = os.path.expanduser("~")
    os.startfile(path)

root = tk.Tk()
root.title("MODS TODAY Launcher")
root.geometry("600x500")
root.configure(bg="#1e1e1e")

logo = tk.PhotoImage(file="channels4_profile.png")
logo_label = tk.Label(root, image=logo, bg="#1e1e1e")
logo_label.pack(pady=10)

title = tk.Label(root, text="MODS TODAY Launcher", font=("Segoe UI", 18, "bold"), bg="#1e1e1e", fg="#f4c842")
title.pack(pady=5)

def add_mod(name, link):
    frame = tk.Frame(root, bg="#2e2e2e", pady=5, padx=10)
    frame.pack(fill='x', pady=5, padx=10)
    label = tk.Label(frame, text=name, font=("Segoe UI", 12, "bold"), bg="#2e2e2e", fg="white")
    label.pack(anchor='w')
    btn = tk.Button(frame, text="Download", bg="#f4c842", command=lambda: open_link(link))
    btn.pack(anchor='e')

add_mod("Contra 009 Final", "https://www.moddb.com/mods/contra/downloads/contra-009-final")
add_mod("ShockWave 1.201", "https://www.moddb.com/mods/cc-shockwave/downloads/shockwave-version-12")
add_mod("Cold War Crisis v1.5 Final", "https://www.moddb.com/mods/cold-war-crisis/downloads/cold-war-crisis-v15-final-v469")

btn_frame = tk.Frame(root, bg="#1e1e1e")
btn_frame.pack(pady=20)

launch_btn = tk.Button(btn_frame, text="🎮 Launch Game", command=launch_game, bg="#f4c842", font=("Segoe UI", 10, "bold"))
launch_btn.grid(row=0, column=0, padx=10)

folder_btn = tk.Button(btn_frame, text="📁 Open Game Folder", command=open_folder, bg="#f4c842", font=("Segoe UI", 10, "bold"))
folder_btn.grid(row=0, column=1, padx=10)

guide_btn = tk.Button(btn_frame, text="🛠 Installation Guide", command=lambda: messagebox.showinfo("Guide", "Please read the readme.txt file."), bg="#f4c842", font=("Segoe UI", 10, "bold"))
guide_btn.grid(row=0, column=2, padx=10)

root.mainloop()
