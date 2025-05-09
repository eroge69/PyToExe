import tkinter as tk
from tkinter import ttk
import threading
import random
import time
import hashlib
import base58
from coincurve import PrivateKey
import requests

START_HASH = int('400000000000000000', 16)
END_HASH = int('7fffffffffffffffff', 16)
TARGET_ADDRESS = "1PWo3JeB9jrGwfHDNpdGK54CRas7fsVzXU"

def get_address_info():
    try:
        r = requests.get(f"https://mempool.space/api/address/{TARGET_ADDRESS}")
        sats = r.json().get("chain_stats", {}).get("funded_txo_sum", 0) - r.json().get("chain_stats", {}).get("spent_txo_sum", 0)
        price = requests.get("https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd").json()
        btc_price = price["bitcoin"]["usd"]
        btc_balance = sats / 1e8
        usd_balance = btc_balance * btc_price
        return btc_balance, usd_balance
    except Exception:
        return None, None

class BitcoinFinderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Bitcoin Address Finder")
        self.running = False
        self.thread = None

        self.total_checked = 0
        self.matches = {"1PWo": 0, "1PWo3": 0, "1PWo3J": 0, "full": 0}
        self.last_gui_update = 0
        self.start_time = None
        self.match_addresses = {"1PWo": [], "1PWo3": [], "1PWo3J": []}
        self.current_bits = None
        self.current_position = 0
        self.found_in_current_position = False
        self.last_balance_update = 0
        self.last_btc_balance = None
        self.last_usd_balance = None

        self.build_interface()

    def build_interface(self):
        frame = ttk.Frame(self.root)
        frame.pack(padx=10, pady=5)

        ttk.Label(frame, text="Текущая позиция: ").grid(row=0, column=0)
        self.position_label = ttk.Label(frame, text="0")
        self.position_label.grid(row=0, column=1)

        ttk.Button(frame, text="Старт", command=self.start_search).grid(row=0, column=2, padx=10)
        ttk.Button(frame, text="Стоп", command=self.stop_search).grid(row=0, column=3)

        info_frame = ttk.LabelFrame(self.root, text="Информация")
        info_frame.pack(padx=10, pady=5, fill="x")
        self.info_label = tk.Label(info_frame, text="", justify="left", font=("Courier", 10))
        self.info_label.pack(anchor="w")

        self.match_label = tk.Label(self.root, text="", font=("Courier", 10))
        self.match_label.pack(pady=2)

        self.addr_panels = {}
        for prefix in ["1PWo", "1PWo3", "1PWo3J"]:
            lbl = tk.Label(self.root, text="Последние 3 адреса: " + prefix, font=("Courier", 10))
            lbl.pack(pady=(4, 0))
            txt = tk.Text(self.root, height=3, font=("Courier", 10), state="disabled", bg="#f0f0f0")
            txt.pack(padx=10, fill="x")
            self.addr_panels[prefix] = txt

        art_frame = ttk.LabelFrame(self.root, text="Битовое представление (последнее совпадение)")
        art_frame.pack(padx=10, pady=5, fill="both", expand=True)
        self.canvas = tk.Canvas(art_frame, width=320, height=320, bg="black")
        self.canvas.pack()

        self.balance_label = tk.Label(self.root, text="", font=("Courier", 10))
        self.balance_label.pack(pady=5)

        target_frame = ttk.LabelFrame(self.root, text="Целевой адрес")
        target_frame.pack(padx=10, pady=5, fill="x")
        ttk.Label(target_frame, text="Цель:", font=("Courier", 10)).pack(side="left")
        ttk.Label(target_frame, text=TARGET_ADDRESS, font=("Courier", 10, "bold"), foreground="blue").pack(side="left", padx=5)

    def start_search(self):
        if not self.running:
            self.running = True
            self.total_checked = 0
            self.matches = {"1PWo": 0, "1PWo3": 0, "1PWo3J": 0, "full": 0}
            self.match_addresses = {"1PWo": [], "1PWo3": [], "1PWo3J": []}
            self.current_bits = None
            self.current_position = random.randint(0, 999999999999999)
            self.found_in_current_position = False
            self.start_time = time.time()
            self.last_balance_update = 0
            self.thread = threading.Thread(target=self.search_loop)
            self.thread.start()

    def stop_search(self):
        self.running = False

    def search_loop(self):
        total_positions = 1000000000000000
        part_size = (END_HASH - START_HASH) // total_positions

        while self.running:
            if self.found_in_current_position:
                self.current_position = random.randint(0, 999999999999999)
                self.found_in_current_position = False

            start = START_HASH + part_size * self.current_position
            end = start + part_size

            priv_int = random.randint(start, end)
            wif, addr = self.get_keys(priv_int)
            self.total_checked += 1

            matched_prefix = None
            if addr == TARGET_ADDRESS:
                self.matches["full"] += 1
                matched_prefix = "full"
                self.save_match("found_exact.txt", addr, wif, priv_int)
                self.found_in_current_position = True
            elif addr.startswith("1PWo3J"):
                self.matches["1PWo3J"] += 1
                matched_prefix = "1PWo3J"
                self.save_match("found_1PWo3J.txt", addr, wif, priv_int)
                self.found_in_current_position = True
            elif addr.startswith("1PWo3"):
                self.matches["1PWo3"] += 1
                matched_prefix = "1PWo3"
                self.save_match("found_1PWo3.txt", addr, wif, priv_int)
                self.found_in_current_position = True
            elif addr.startswith("1PWo"):
                self.matches["1PWo"] += 1
                matched_prefix = "1PWo"
                self.save_match("found_1PWo.txt", addr, wif, priv_int)
                self.found_in_current_position = True

            if matched_prefix:
                self.update_matches(addr, priv_int)

            if time.time() - self.last_gui_update >= 1:
                self.update_info(addr, priv_int)
                self.update_match_counters()
                self.position_label.config(text=str(self.current_position))
                self.last_gui_update = time.time()

    def get_keys(self, priv_int):
        priv_bytes = priv_int.to_bytes(32, 'big')
        wif = base58.b58encode_check(b'\x80' + priv_bytes + b'\x01').decode()
        pubkey = PrivateKey(priv_bytes).public_key.format(compressed=True)
        sha = hashlib.sha256(pubkey).digest()
        ripe = hashlib.new('ripemd160', sha).digest()
        addr = base58.b58encode_check(b'\x00' + ripe).decode()
        return wif, addr

    def save_match(self, filename, addr, wif, priv_int):
        with open(filename, "a") as f:
            f.write(addr + " | " + wif + " | " + hex(priv_int) + "\n")

    def update_info(self, addr, priv_int):
        speed = self.total_checked / (time.time() - self.start_time + 0.001)

        if time.time() - self.last_balance_update >= 60 or self.last_btc_balance is None:
            self.last_btc_balance, self.last_usd_balance = get_address_info()
            self.last_balance_update = time.time()

        balance_text = "Баланс цели: недоступен"
        if self.last_btc_balance is not None:
            balance_text = "Баланс цели: {:.8f} BTC\n~{:.2f} USD".format(self.last_btc_balance, self.last_usd_balance)

        text = "Проверено: {}\nСкорость: {:.2f} хэшей/сек\nАдрес: {}\nХэш: {}".format(
            self.total_checked, speed, addr, hex(priv_int)
        )
        self.info_label.config(text=text)
        self.balance_label.config(text=balance_text)

    def update_match_counters(self):
        text = "Совпадения:  1PWo ({})   1PWo3 ({})   1PWo3J ({})".format(
            self.matches["1PWo"], self.matches["1PWo3"], self.matches["1PWo3J"]
        )
        self.match_label.config(text=text)

    def update_matches(self, addr, priv_int):
        prefix = None
        for p in ["1PWo3J", "1PWo3", "1PWo"]:
            if addr.startswith(p):
                prefix = p
                break
        if not prefix:
            return

        self.match_addresses[prefix].insert(0, addr)
        self.match_addresses[prefix] = self.match_addresses[prefix][:3]

        for pfx, panel in self.addr_panels.items():
            panel.config(state="normal")
            panel.delete("1.0", tk.END)
            for a in self.match_addresses[pfx]:
                panel.insert(tk.END, a + "\n")
            panel.config(state="disabled")

        self.current_bits = bin(priv_int)[2:].zfill(256)
        self.update_bit_canvas()

    def update_bit_canvas(self):
        self.canvas.delete("all")
        if not self.current_bits:
            return
        cell_size = 20
        for i in range(16):
            for j in range(16):
                bit = self.current_bits[i * 16 + j]
                color = "#ff3333" if bit == "1" else "#ccffcc"
                x1 = j * cell_size
                y1 = i * cell_size
                x2 = x1 + cell_size - 2
                y2 = y1 + cell_size - 2
                self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline="#222")

if __name__ == "__main__":
    root = tk.Tk()
    app = BitcoinFinderApp(root)
    root.mainloop()