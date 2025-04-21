
import tkinter as tk
from tkinter import scrolledtext
import subprocess
import threading

DOTA2_SERVERS = {
    "Luxembourg (EU West)": "lux.valve.net",
    "Vienna (EU East)": "vie.valve.net",
    "Dubai (Middle East)": "dxb.valve.net",
    "Singapore (SEA)": "sgp-1.valve.net",
    "Japan": "tyo.valve.net",
    "India": "maa.valve.net",
    "Russia": "sto.valve.net",
    "US West": "eat.valve.net",
    "US East": "iad.valve.net",
    "Australia": "syd.valve.net",
    "South Africa": "jnb.valve.net",
    "Brazil": "gru.valve.net",
    "Chile": "scl.valve.net"
}

def ping_server(host):
    try:
        output = subprocess.check_output(["ping", "-n", "1", host], stderr=subprocess.STDOUT, universal_newlines=True)
        for line in output.splitlines():
            if "Average" in line or "avg" in line.lower():
                return line.strip()
            elif "time=" in line:
                return line.strip()
        return "Ping response not found"
    except subprocess.CalledProcessError:
        return "Ping failed"

def run_ping():
    output_area.delete(1.0, tk.END)
    for name, host in DOTA2_SERVERS.items():
        result = ping_server(host)
        output_area.insert(tk.END, f"{name} ({host}): {result}\n")
        output_area.see(tk.END)

def start_ping_thread():
    threading.Thread(target=run_ping).start()

window = tk.Tk()
window.title("Dota 2 Server Ping Checker")
window.geometry("600x400")
window.resizable(False, False)

label = tk.Label(window, text="Dota 2 Server Ping Results", font=("Arial", 14))
label.pack(pady=10)

output_area = scrolledtext.ScrolledText(window, wrap=tk.WORD, width=70, height=20, font=("Consolas", 10))
output_area.pack(padx=10, pady=10)

start_ping_thread()
window.mainloop()
