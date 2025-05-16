import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import requests
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
# --- Color Palette (Louis Vuitton Inspired) ---
BITCOIN_YELLOW = "#5D3A00"  # Background
ENTRY_BG = "#4B2C00"         # Entry & Chart background
ENTRY_TEXT = "#FFD700"       # Text
CHART_BG = "#4B2C00"
TEXT_COLOR = "#FFD700"
TIFFANY_BLUE = "#FFD700"
BUTTONS = "#FFD700"

# --- Coin List ---
POPULAR_COINS = {
    "bitcoin": "bitcoin",
    "ethereum": "ethereum",
    "solana": "solana",
    "dogecoin": "dogecoin",
    "cardano": "cardano",
    "ripple": "ripple",
    "litecoin": "litecoin"
}

# --- Historical Data for Coins (2010-2025) ---
PAST_TRENDS = {
    "bitcoin": list(range(2010, 2026)),
    "ethereum": list(range(2015, 2026)),
    "solana": list(range(2020, 2026)),
    "dogecoin": list(range(2013, 2026)),
    "cardano": list(range(2017, 2026)),
    "ripple": list(range(2012, 2026)),
    "litecoin": list(range(2011, 2026))
}

def get_crypto_data(crypto_id):
    try:
        url = f"https://api.coingecko.com/api/v3/coins/{crypto_id}"
        response = requests.get(url)
        if response.status_code != 200:
            return None, None
        data = response.json()

        prices_url = f"https://api.coingecko.com/api/v3/coins/{crypto_id}/market_chart?vs_currency=usd&days=30&interval=daily"
        history_response = requests.get(prices_url)
        if history_response.status_code != 200:
            return None, None
        prices = [price[1] for price in history_response.json().get("prices", [])]

        if not prices:
            return None, None

        return data, prices
    except:
        return None, None

def analyze_crypto(crypto_id, bank_balance):
    data, price_history = get_crypto_data(crypto_id)
    if not data or not price_history:
        chat_box.insert(tk.END, "\nCryptera: Could not fetch data. Try again.\n")
        return

    name = data["name"]
    current_price = data["market_data"]["current_price"]["usd"]
    change_24h = data["market_data"]["price_change_percentage_24h"]
    market_cap = data["market_data"]["market_cap"]["usd"]

    risk_level = "High" if max(price_history) - min(price_history) > current_price * 0.15 else "Low"
    advice = (
        "Positive trend. Consider investing." if change_24h > 2 else
        "Dropping fast. Avoid for now." if change_24h < -2 else
        "Stable. Monitor before deciding."
    )

    chat_box.insert(tk.END, f"\nCryptera Report: {name}\nPrice: ${current_price:,.2f}\n24h Change: {change_24h:.2f}%\nMarket Cap: ${market_cap:,.2f}\nRisk: {risk_level}\nAdvice: {advice}\n")
    draw_chart(price_history, name)

def draw_chart(prices, name):
    fig = plt.Figure(figsize=(8, 6.5), dpi=100, facecolor=CHART_BG)
    ax = fig.add_subplot(111)
    ax.plot(prices, color=TEXT_COLOR)
    ax.set_title(f"{name} Price (30 Days)", color=TEXT_COLOR)
    ax.set_ylabel("Price (USD)", color=TEXT_COLOR)
    ax.set_xticks([])
    ax.tick_params(axis='y', colors=TEXT_COLOR)
    fig.tight_layout()

    for widget in chart_frame.winfo_children():
        widget.destroy()

    chart = FigureCanvasTkAgg(fig, master=chart_frame)
    chart.draw()
    chart.get_tk_widget().pack()

def on_enter(event=None):
    global state, bank_balance
    user_input = user_input_box.get()
    chat_box.insert(tk.END, f"You: {user_input}\n")

    if state == 0 and user_input.lower() == "hello":
        chat_box.insert(tk.END, "Cryptera: What's your current bank balance?\n")
        state = 1
    elif state == 1:
        try:
            bank_balance = float(user_input)
            chat_box.insert(tk.END, "Cryptera: Great! Which coin would you like info on?\n")
            state = 2
        except ValueError:
            chat_box.insert(tk.END, "Cryptera: Enter a valid number.\n")
    elif state == 2:
        coin = next((POPULAR_COINS[name] for name in POPULAR_COINS if name in user_input.lower()), None)
        if coin:
            chat_box.insert(tk.END, f"Cryptera: Fetching data on {coin.title()}...\n")
            analyze_crypto(coin, bank_balance)
        else:
            chat_box.insert(tk.END, "Cryptera: Coin not recognized. Try again.\n")

    user_input_box.delete(0, tk.END)

# --- GUI Setup ---
root = tk.Tk()
root.title("Cryptera Crypto Advisor")
root.geometry("1000x700")
root.configure(bg=BITCOIN_YELLOW)

notebook = ttk.Notebook(root)
notebook.pack(expand=1, fill="both")

# --- Tabs ---
tab1 = tk.Frame(notebook, bg=BITCOIN_YELLOW)
tab2 = tk.Frame(notebook, bg=BITCOIN_YELLOW)
tab3 = tk.Frame(notebook, bg=BITCOIN_YELLOW)
tab4 = tk.Frame(notebook, bg=BITCOIN_YELLOW)
tab5 = tk.Frame(notebook, bg=BITCOIN_YELLOW)
notebook.add(tab1, text="Cryptera Bot")
notebook.add(tab2, text="FAQ")
notebook.add(tab3, text="Tutorial")
notebook.add(tab4, text="Developers")
notebook.add(tab5, text="Past Trends")

# --- Title ---
title = tk.Label(tab1, text="Cryptera", font=("Georgia", 24, "bold"), bg=BITCOIN_YELLOW, fg=BUTTONS)
title.grid(row=0, column=0, columnspan=3, pady=10)

# --- Layout Frames ---
chat_frame = tk.Frame(tab1, bg=BITCOIN_YELLOW)
chat_frame.grid(row=1, column=0, sticky="nsew", padx=10)

button_frame = tk.Frame(tab1, bg=BITCOIN_YELLOW)
button_frame.grid(row=1, column=1, sticky="ns")

output_frame = tk.Frame(tab1, bg=BITCOIN_YELLOW)
output_frame.grid(row=1, column=2, sticky="nsew", padx=10)

# --- Chat Elements ---
chat_box = tk.Text(chat_frame, height=25, width=45, wrap=tk.WORD, font=("Arial", 12), bg=ENTRY_BG, fg=ENTRY_TEXT, bd=0, highlightthickness=0)
chat_box.pack(pady=10)
chat_box.insert(tk.END, "Cryptera: Hi! Type 'hello' to start.\n")

user_input_box = tk.Entry(chat_frame, font=("Arial", 12), bg=ENTRY_BG, fg=ENTRY_TEXT, insertbackground=ENTRY_TEXT, bd=0, highlightthickness=0)
user_input_box.pack(pady=10, fill="x")
user_input_box.bind("<Return>", on_enter)

# --- Side Buttons ---
def clear_chat():
    chat_box.delete(1.0, tk.END)
    chat_box.insert(tk.END, "Cryptera: Hi! Type 'hello' to start.\n")

def stop_chat():
    chat_box.insert(tk.END, "\nCryptera: Stopping the conversation.\n")

def print_report():
    report_text = chat_box.get("1.0", tk.END).strip()
    if not report_text or "Cryptera Report" not in report_text:
        chat_box.insert(tk.END, "\nCryptera: No report available to print.\n")
        return
    try:
        with open("cryptera_report.txt", "w", encoding="utf-8") as file:
            file.write(report_text)
        chat_box.insert(tk.END, "\nCryptera: Report saved to 'cryptera_report.txt'\n")
    except Exception as e:
        chat_box.insert(tk.END, f"\nCryptera: Failed to save report: {e}\n")

def open_comparison_window():
    def run_comparison():
        result_label.config(text="AI is Analyzing...", fg=ENTRY_TEXT)
        window.update()

        coin1 = dropdown1.get().lower()
        coin2 = dropdown2.get().lower()

        if coin1 == coin2 or coin1 not in POPULAR_COINS or coin2 not in POPULAR_COINS:
            result_label.config(text="Choose two different valid coins.")
            return

        id1 = POPULAR_COINS[coin1]
        id2 = POPULAR_COINS[coin2]

        data1, prices1 = get_crypto_data(id1)
        data2, prices2 = get_crypto_data(id2)

        if not data1 or not data2:
            result_label.config(text="Could not fetch data. Try again.")
            return

        change1 = data1["market_data"]["price_change_percentage_24h"]
        change2 = data2["market_data"]["price_change_percentage_24h"]

        volatility1 = max(prices1) - min(prices1)
        volatility2 = max(prices2) - min(prices2)

        score1 = change1 - volatility1
        score2 = change2 - volatility2

        better = coin1 if score1 > score2 else coin2
        conclusion = f"{better.capitalize()} appears better for investment right now."

        result_label.config(text=conclusion, fg="#32CD32")

    window = tk.Toplevel(root)
    window.title("Compare Cryptos")
    window.geometry("400x300")
    window.configure(bg=BITCOIN_YELLOW)

    tk.Label(window, text="Select Two Cryptos to Compare", font=("Arial", 14, "bold"), bg=BITCOIN_YELLOW, fg=ENTRY_TEXT).pack(pady=10)
    dropdown1 = ttk.Combobox(window, values=list(POPULAR_COINS.keys()), font=("Arial", 12)); dropdown1.set("bitcoin"); dropdown1.pack(pady=10)
    dropdown2 = ttk.Combobox(window, values=list(POPULAR_COINS.keys()), font=("Arial", 12)); dropdown2.set("ethereum"); dropdown2.pack(pady=10)
    tk.Button(window, text="Compare", command=run_comparison, font=("Arial", 12), bg=ENTRY_TEXT, fg="black").pack(pady=15)
    result_label = tk.Label(window, text="", font=("Arial", 12), bg=BITCOIN_YELLOW, fg=ENTRY_TEXT)
    result_label.pack(pady=10)

tk.Button(button_frame, text="Clear Chat", font=("Arial", 12), bg=BITCOIN_YELLOW, fg=BUTTONS, command=clear_chat, bd=0).pack(pady=5)
tk.Button(button_frame, text="Stop", font=("Arial", 12), bg=BITCOIN_YELLOW, fg=BUTTONS, command=stop_chat, bd=0).pack(pady=5)
tk.Button(button_frame, text="Compare Cryptos", font=("Arial", 12), bg=BITCOIN_YELLOW, fg=BUTTONS, command=open_comparison_window, bd=0).pack(pady=5)
tk.Button(button_frame, text="Print Report", font=("Arial", 12), bg=BITCOIN_YELLOW, fg=BUTTONS, command=print_report, bd=0).pack(pady=5)

# --- Chart Frame ---
chart_frame = tk.Frame(output_frame, bg=BITCOIN_YELLOW)
chart_frame.pack(pady=20)

# --- Other Tabs ---
tk.Label(tab2, text="Frequently Asked Questions", font=("Arial", 14, "bold"), bg=BITCOIN_YELLOW, fg=ENTRY_TEXT).pack(pady=10)
tk.Label(tab2, text="""1. What is cryptocurrency?\nA digital form of money based on blockchain tech.\n\n2. How to invest?\nUse an exchange (Coinbase, Binance) and get a wallet.\n\n3. What is blockchain?\nA decentralized ledger system.\n\n4. What is mining?\nSolving problems to earn cryptocurrency rewards.\n\n5. How to protect crypto?\nUse strong passwords and hardware wallets.""", font=("Arial", 12), justify="left", bg=BITCOIN_YELLOW, fg=ENTRY_TEXT).pack(pady=10)

tk.Label(tab3, text="Newbie Traders Tutorial", font=("Arial", 14, "bold"), bg=BITCOIN_YELLOW, fg=ENTRY_TEXT).pack(pady=10)
tk.Label(tab3, text="""1. What is Bitcoin?\nThe first and most famous cryptocurrency.\n\n2. Crypto Exchanges:\nCoinbase, Binance, Kraken.\n\n3. Market Cap:\nPrice x circulating supply.\n\n4. Risk Management:\nDiversify and don't go all-in.\n\n5. Security:\nUse 2FA, cold wallets, and beware of scams.""", font=("Arial", 12), justify="left", bg=BITCOIN_YELLOW, fg=ENTRY_TEXT).pack(pady=10)

tk.Label(tab4, text="Developers", font=("Arial", 14, "bold"), bg=BITCOIN_YELLOW, fg=ENTRY_TEXT).pack(pady=10)
tk.Label(tab4, text="Kiaan Dcruz", font=("Arial", 12), bg=BITCOIN_YELLOW, fg=ENTRY_TEXT).pack(pady=10)

tk.Label(tab5, text="Past Trends (2010–2025)", font=("Arial", 14, "bold"), bg=BITCOIN_YELLOW, fg=ENTRY_TEXT).pack(pady=10)
trend_text = "\n".join([f"{coin.capitalize()} Years: {', '.join(map(str, years))}" for coin, years in PAST_TRENDS.items()])
tk.Label(tab5, text=trend_text, font=("Arial", 12), justify="left", bg=BITCOIN_YELLOW, fg=ENTRY_TEXT).pack(pady=10)

tk.Label(root, text="Copyright © 2025 Cryptera", font=("Arial", 10), bg=BITCOIN_YELLOW, fg=ENTRY_TEXT).pack(side="bottom", pady=10)

# --- Global State ---
state = 0
bank_balance = 0

# --- Run App ---
root.mainloop()
