import tkinter as tk
from tkinter import ttk, messagebox
import requests

currency_rates = {
    "USD": 1.00, "EUR": 0.91, "GBP": 0.79, "JPY": 157.19, "AUD": 1.51,
    "CAD": 1.36, "CHF": 0.91, "CNY": 7.24, "INR": 83.30, "BRL": 5.14,
    "ZAR": 18.50, "SGD": 1.35, "NZD": 1.64, "RUB": 89.56, "TRY": 32.20,
    "MXN": 16.75, "KRW": 1375.00, "THB": 36.20, "IDR": 16000.00,
    "PHP": 57.35, "SEK": 10.71, "NOK": 10.74, "DKK": 6.78, "MYR": 4.71
}

currency_names = {
    "USD": "US Dollar", "EUR": "Euro", "GBP": "British Pound", "JPY": "Japanese Yen",
    "AUD": "Australian Dollar", "CAD": "Canadian Dollar", "CHF": "Swiss Franc",
    "CNY": "Chinese Yuan", "INR": "Indian Rupee", "BRL": "Brazilian Real",
    "ZAR": "South African Rand", "SGD": "Singapore Dollar", "NZD": "New Zealand Dollar",
    "RUB": "Russian Ruble", "TRY": "Turkish Lira", "MXN": "Mexican Peso",
    "KRW": "South Korean Won", "THB": "Thai Baht", "IDR": "Indonesian Rupiah",
    "PHP": "Philippine Peso", "SEK": "Swedish Krona", "NOK": "Norwegian Krone",
    "DKK": "Danish Krone", "MYR": "Malaysian Ringgit"
}

display_name_to_code = {f"{name} ({code})": code for code, name in currency_names.items()}
dropdown_options = sorted(display_name_to_code.keys())

current_theme = "light"

def convert_currency():
    from_key = from_currency_cb.get()
    to_key = to_currency_cb.get()
    try:
        amount = float(amount_entry.get())
    except ValueError:
        messagebox.showerror("Invalid Input", "Please enter a valid number.")
        return

    if from_key not in display_name_to_code or to_key not in display_name_to_code:
        messagebox.showerror("Invalid Currency", "Please select valid currencies from the list.")
        return

    from_code = display_name_to_code[from_key]
    to_code = display_name_to_code[to_key]

    if from_code not in currency_rates or to_code not in currency_rates:
        messagebox.showerror("Unsupported Currency", "Currency not supported.")
        return

    usd_amount = amount / currency_rates[from_code]
    result = usd_amount * currency_rates[to_code]
    result_label.config(
        text=f"{amount:.2f} {from_code} = {result:.2f} {to_code}"
    )

def toggle_theme():
    global current_theme
    if current_theme == "light":
        current_theme = "dark"
        root.config(bg="#222222")
        content_frame.config(bg="#222222")
        welcome_frame.config(bg="#222222")
        branding_label.config(fg="#F1C40F", bg="#222222")
        news_label.config(fg="#F1C40F", bg="#222222")
        about_label.config(fg="white", bg="#222222")
        faq_btn.config(bg="#27AE60", fg="white", activebackground="#229954")
        theme_btn.config(text="Switch to Light Mode", bg="#27AE60", fg="white", activebackground="#229954")
        menu_frame.config(bg="#1B2631")
        box_frame.config(bg="#1B2631")
        label.config(bg="#1B2631")
        tab_frame.config(bg="#1B2631")
        update_crypto_theme("dark")
    else:
        current_theme = "light"
        root.config(bg="white")
        content_frame.config(bg="white")
        welcome_frame.config(bg="white")
        branding_label.config(fg="#2E86C1", bg="white")
        news_label.config(fg="#2E86C1", bg="white")
        about_label.config(fg="black", bg="white")
        faq_btn.config(bg="#2ECC71", fg="white", activebackground="#27AE60")
        theme_btn.config(text="Switch to Dark Mode", bg="#2ECC71", fg="white", activebackground="#27AE60")
        menu_frame.config(bg="#34495E")
        box_frame.config(bg="#2C3E50")
        label.config(bg="#2C3E50")
        tab_frame.config(bg="#34495E")
        update_crypto_theme("light")

def update_crypto_theme(theme):
    if hasattr(root, "crypto_tree"):
        style = ttk.Style()
        style.theme_use('clam')
        if theme == "light":
            style.configure("Treeview", background="white", foreground="black",
                            fieldbackground="white", rowheight=25, font=("Arial", 12))
            style.map('Treeview', background=[('selected', '#2ECC71')])
            root.crypto_tree.tag_configure('oddrow', background='white')
            root.crypto_tree.tag_configure('evenrow', background='#f0f0f0')
        else:
            style.configure("Treeview", background="#222222", foreground="white",
                            fieldbackground="#222222", rowheight=25, font=("Arial", 12))
            style.map('Treeview', background=[('selected', '#27AE60')])
            root.crypto_tree.tag_configure('oddrow', background='#2C3E50')
            root.crypto_tree.tag_configure('evenrow', background='#1B2631')

def show_faq():
    faq_text = (
        "Q: How do I convert currencies?\n"
        "A: Click the 'Blurge Money Converter' box in the menu.\n\n"
        "Q: What currencies are supported?\n"
        "A: Most major world currencies.\n\n"
        "Q: Can I change themes?\n"
        "A: Yes! Use the theme toggle button on the homepage.\n\n"
        "For more info, visit our website."
    )
    messagebox.showinfo("Help & FAQ", faq_text)

def show_welcome():
    for widget in content_frame.winfo_children():
        widget.destroy()

    global welcome_frame
    welcome_frame = tk.Frame(content_frame, bg="white" if current_theme=="light" else "#222222")
    welcome_frame.pack(expand=True, fill=tk.BOTH)

    global branding_label
    branding_label = tk.Label(welcome_frame, text="💸 Blurge Money", font=("Arial", 40, "bold"),
                              fg="#2E86C1" if current_theme=="light" else "#F1C40F",
                              bg=welcome_frame["bg"])
    branding_label.pack(pady=40)

    global news_label
    news_label = tk.Label(welcome_frame, text="📈 Latest Currency News: \n- USD rises against EUR\n- GBP steady amid market volatility",
                          font=("Arial", 14),
                          fg="#2E86C1" if current_theme=="light" else "#F1C40F",
                          bg=welcome_frame["bg"], justify=tk.LEFT)
    news_label.pack(pady=20)

    global about_label
    about_label = tk.Label(welcome_frame,
                           text="Welcome to Blurge Money, your go-to app for fast and easy currency conversions.\n"
                                "Convert with many of the world currencies. Also we include live rates and simple tools.",
                           font=("Arial", 14),
                           fg="black" if current_theme=="light" else "white",
                           bg=welcome_frame["bg"], justify=tk.CENTER)
    about_label.pack(pady=30)

    tab_frame.pack(side=tk.BOTTOM, pady=20, padx=10)

def show_converter():
    for widget in content_frame.winfo_children():
        widget.destroy()

    converter_frame = tk.Frame(content_frame, padx=40, pady=40, bg="white" if current_theme=="light" else "#222222")
    converter_frame.pack(expand=True, fill=tk.BOTH)

    tk.Label(converter_frame, text="💸 Blurge Money Converter", font=("Arial", 26, "bold"),
             fg="#2E86C1" if current_theme=="light" else "#F1C40F",
             bg=converter_frame["bg"]).grid(row=0, column=0, columnspan=2, pady=(0,30))

    tk.Label(converter_frame, text="From Currency:", font=("Arial", 14), bg=converter_frame["bg"]).grid(row=1, column=0, sticky='w', pady=10)
    global from_currency_cb
    from_currency_cb = ttk.Combobox(converter_frame, values=dropdown_options, width=40, font=("Arial", 12))
    from_currency_cb.grid(row=1, column=1, sticky='ew', pady=10)

    tk.Label(converter_frame, text="To Currency:", font=("Arial", 14), bg=converter_frame["bg"]).grid(row=2, column=0, sticky='w', pady=10)
    global to_currency_cb
    to_currency_cb = ttk.Combobox(converter_frame, values=dropdown_options, width=40, font=("Arial", 12))
    to_currency_cb.grid(row=2, column=1, sticky='ew', pady=10)

    tk.Label(converter_frame, text="Amount to Convert:", font=("Arial", 14), bg=converter_frame["bg"]).grid(row=3, column=0, sticky='w', pady=10)
    global amount_entry
    amount_entry = tk.Entry(converter_frame, width=30, font=("Arial", 16, "bold"),
                            bg="white", fg="#000000", relief="solid", bd=2)
    amount_entry.grid(row=3, column=1, sticky='ew', pady=10)

    global result_label
    result_label = tk.Label(converter_frame, text="", font=("Arial", 18, "bold"), bg=converter_frame["bg"])
    result_label.grid(row=4, column=0, columnspan=2, pady=30)

    convert_btn = tk.Button(converter_frame, text="Convert", font=("Arial", 14, "bold"),
                            bg="#2980B9", fg="white", command=convert_currency)
    convert_btn.grid(row=5, column=0, columnspan=2, pady=10, sticky='ew')

    back_btn = tk.Button(converter_frame, text="← Back to Menu", font=("Arial", 12),
                         bg="#2980B9", fg="white", command=show_welcome)
    back_btn.grid(row=6, column=0, columnspan=2, pady=15, sticky='ew')

def show_crypto_prices():
    for widget in content_frame.winfo_children():
        widget.destroy()

    crypto_frame = tk.Frame(content_frame, bg="white" if current_theme=="light" else "#222222", padx=20, pady=20)
    crypto_frame.pack(expand=True, fill=tk.BOTH)

    tk.Label(crypto_frame, text="📈 Live Cryptocurrency Prices", font=("Arial", 24, "bold"),
             fg="#2980B9" if current_theme=="light" else "#F1C40F", bg=crypto_frame["bg"]).pack(pady=15)

    search_var = tk.StringVar()
    search_entry = tk.Entry(crypto_frame, textvariable=search_var, font=("Arial", 14), width=30)
    search_entry.pack(pady=10)

    columns = ("Name", "Symbol", "Price (USD)", "Market Cap", "24h Change")
    global crypto_tree
    crypto_tree = ttk.Treeview(crypto_frame, columns=columns, show="headings", height=20)
    root.crypto_tree = crypto_tree

    style = ttk.Style()
    style.theme_use('clam')

    if current_theme == "light":
        style.configure("Treeview", background="white", foreground="black",
                        fieldbackground="white", rowheight=25, font=("Arial", 12))
        style.map('Treeview', background=[('selected', '#2ECC71')])
        crypto_tree.tag_configure('oddrow', background='white')
        crypto_tree.tag_configure('evenrow', background='#f0f0f0')
    else:
        style.configure("Treeview", background="#222222", foreground="white",
                        fieldbackground="#222222", rowheight=25, font=("Arial", 12))
        style.map('Treeview', background=[('selected', '#27AE60')])
        crypto_tree.tag_configure('oddrow', background='#2C3E50')
        crypto_tree.tag_configure('evenrow', background='#1B2631')

    for col in columns:
        crypto_tree.heading(col, text=col)
        crypto_tree.column(col, anchor=tk.CENTER)

    crypto_tree.pack(fill=tk.BOTH, expand=True)

    all_crypto_data = []

    def update_crypto_table():
        nonlocal all_crypto_data
        url = "https://api.coingecko.com/api/v3/coins/markets"
        params = {
            "vs_currency": "usd",
            "order": "market_cap_desc",
            "per_page": 250,
            "page": 1,
            "sparkline": "false"
        }
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            all_crypto_data = response.json()
            filter_crypto_table()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to fetch crypto data:\n{e}")

    def filter_crypto_table(*args):
        search_text = search_var.get().lower()
        crypto_tree.delete(*crypto_tree.get_children())
        for i, coin in enumerate(all_crypto_data):
            name = coin['name'].lower()
            symbol = coin['symbol'].lower()
            if search_text in name or search_text in symbol:
                tag = 'evenrow' if i % 2 == 0 else 'oddrow'
                crypto_tree.insert(
                    "", "end",
                    values=(
                        coin['name'],
                        coin['symbol'].upper(),
                        f"${coin['current_price']:.2f}",
                        f"${coin['market_cap']:,}",
                        f"{coin['price_change_percentage_24h']:.2f}%"
                    ),
                    tags=(tag,)
                )

    search_var.trace_add('write', filter_crypto_table)

    update_crypto_table()

    refresh_btn = tk.Button(crypto_frame, text="Refresh Prices", command=update_crypto_table,
                            bg="#27AE60", fg="white", font=("Arial", 14, "bold"))
    refresh_btn.pack(pady=15)

    back_btn = tk.Button(crypto_frame, text="← Back to Menu", command=show_welcome,
                         bg="#2980B9", fg="white", font=("Arial", 12, "bold"))
    back_btn.pack(side=tk.LEFT, pady=10)

    tab_frame.pack_forget()

root = tk.Tk()
root.title("Blurge Money - Currency & Crypto Converter")
root.geometry("900x700")
root.config(bg="white")

menu_frame = tk.Frame(root, bg="#34495E", width=220)
menu_frame.pack(side=tk.LEFT, fill=tk.Y)

box_frame = tk.Frame(menu_frame, bg="#2C3E50")
box_frame.pack(pady=40, padx=20)

label = tk.Label(box_frame, text="Blurge Money", font=("Arial", 22, "bold"),
                 fg="white", bg="#2C3E50")
label.pack()

btn1 = tk.Button(menu_frame, text="Blurge Money Converter", font=("Arial", 14),
                 bg="#2980B9", fg="white", command=show_converter)  # Changed to blue
btn1.pack(fill=tk.X, padx=10, pady=(40,10))

btn2 = tk.Button(menu_frame, text="Cryptocurrency Prices", font=("Arial", 14),
                 bg="#2980B9", fg="white", command=show_crypto_prices)
btn2.pack(fill=tk.X, padx=10, pady=10)

faq_btn = tk.Button(menu_frame, text="Help & FAQ", font=("Arial", 12),
                    bg="#2ECC71", fg="white", command=show_faq)
faq_btn.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=(0, 10))

theme_btn = tk.Button(menu_frame, text="Switch to Dark Mode", font=("Arial", 12),
                      bg="#2ECC71", fg="white", command=toggle_theme)
theme_btn.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=10)

content_frame = tk.Frame(root, bg="white")
content_frame.pack(expand=True, fill=tk.BOTH)

tab_frame = tk.Frame(root, bg="#34495E", height=40)
tab_frame.pack(side=tk.BOTTOM, pady=20, padx=10)

welcome_tab_btn = tk.Button(tab_frame, text="Home", font=("Arial", 12), bg="#2ECC71", fg="white", command=show_welcome)
welcome_tab_btn.pack(side=tk.LEFT, padx=5)

converter_tab_btn = tk.Button(tab_frame, text="Converter", font=("Arial", 12), bg="#2980B9", fg="white", command=show_converter)
converter_tab_btn.pack(side=tk.LEFT, padx=5)

crypto_tab_btn = tk.Button(tab_frame, text="Crypto Prices", font=("Arial", 12), bg="#2980B9", fg="white", command=show_crypto_prices)
crypto_tab_btn.pack(side=tk.LEFT, padx=5)

show_welcome()

root.mainloop()
