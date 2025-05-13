import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from tkcalendar import Calendar
import MetaTrader5 as mt5
import os
from datetime import datetime, timedelta

root = tk.Tk()
root.title("\U0001F4CA MT5 Multi-Terminal Dashboard")
root.geometry("1250x850")

main_canvas = tk.Canvas(root)
main_canvas.pack(side="left", fill="both", expand=True)
scrollbar = tk.Scrollbar(root, orient="vertical", command=main_canvas.yview)
scrollbar.pack(side="right", fill="y")
main_canvas.configure(yscrollcommand=scrollbar.set)
main_frame = tk.Frame(main_canvas)
main_canvas.create_window((0, 0), window=main_frame, anchor="nw")
main_frame.bind("<Configure>", lambda e: main_canvas.configure(scrollregion=main_canvas.bbox("all")))

tabs = ttk.Notebook(main_frame)
tabs.pack(fill="both", expand=True)

summary_frame = tk.Frame(tabs)
tabs.add(summary_frame, text="\U0001F4CB Summary")

summary_labels = {
    "TotalBalance": tk.Label(summary_frame, text="Total Balance: \u20B90.00", font=("Arial", 12)),
    "TotalEquity": tk.Label(summary_frame, text="Total Equity: \u20B90.00", font=("Arial", 12)),
    "TotalFloating": tk.Label(summary_frame, text="Total Floating PnL: \u20B90.00", font=("Arial", 12)),
    "TotalCredit": tk.Label(summary_frame, text="Total Credit: \u20B90.00", font=("Arial", 12))
}
for label in summary_labels.values():
    label.pack(anchor="w", padx=20, pady=5)

alert_margin_level = 150
alerted_terminals = set()

terminal_table = ttk.Treeview(summary_frame, columns=("terminal", "id", "name", "company", "margin"), show="headings")
for col in terminal_table["columns"]:
    terminal_table.heading(col, text=col.upper())
    terminal_table.column(col, width=150)
terminal_table.pack(fill="x", padx=10, pady=10)

terminal_paths = []


def show_history(frame, path):
    history_frame = tk.Frame(frame)
    history_frame.pack(fill="both", expand=True, padx=10, pady=10)

    tk.Label(history_frame, text="\U0001F501 Trade, Deposit & Withdrawal History", font=("Arial", 12, "bold")).pack(pady=5)
    filter_frame = tk.Frame(history_frame)
    filter_frame.pack(pady=5)

    tk.Label(filter_frame, text="Start Date:").grid(row=0, column=0, padx=5)
    start_date_var = tk.StringVar()
    start_date_entry = ttk.Entry(filter_frame, textvariable=start_date_var, width=12)
    start_date_entry.grid(row=0, column=1, padx=5)

    start_cal_frame = tk.Frame(filter_frame)
    start_calendar = Calendar(start_cal_frame, date_pattern="yyyy-mm-dd", font=("Arial", 11))
    start_calendar.pack()
    start_cal_frame.grid(row=1, column=1)
    start_cal_frame.grid_remove()
    start_date_entry.bind("<Button-1>", lambda e: start_cal_frame.grid())
    start_calendar.bind("<<CalendarSelected>>", lambda e: (start_date_var.set(start_calendar.get_date()), start_cal_frame.grid_remove()))

    tk.Label(filter_frame, text="End Date:").grid(row=0, column=2, padx=5)
    end_date_var = tk.StringVar()
    end_date_entry = ttk.Entry(filter_frame, textvariable=end_date_var, width=12)
    end_date_entry.grid(row=0, column=3, padx=5)

    end_cal_frame = tk.Frame(filter_frame)
    end_calendar = Calendar(end_cal_frame, date_pattern="yyyy-mm-dd", font=("Arial", 11))
    end_calendar.pack()
    end_cal_frame.grid(row=1, column=3)
    end_cal_frame.grid_remove()
    end_date_entry.bind("<Button-1>", lambda e: end_cal_frame.grid())
    end_calendar.bind("<<CalendarSelected>>", lambda e: (end_date_var.set(end_calendar.get_date()), end_cal_frame.grid_remove()))

    trade_table = ttk.Treeview(history_frame, columns=("ticket", "symbol", "volume", "price", "profit", "time"), show="headings")
    for col in trade_table["columns"]:
        trade_table.heading(col, text=col.upper())
        trade_table.column(col, width=100)
    trade_table.pack(fill="x", padx=10, pady=5)

    deposit_table = ttk.Treeview(history_frame, columns=("time", "amount", "comment"), show="headings")
    for col in deposit_table["columns"]:
        deposit_table.heading(col, text=col.upper())
        deposit_table.column(col, width=120)
    deposit_table.pack(fill="x", padx=10, pady=5)

    withdraw_table = ttk.Treeview(history_frame, columns=("time", "amount", "comment"), show="headings")
    for col in withdraw_table["columns"]:
        withdraw_table.heading(col, text=col.upper())
        withdraw_table.column(col, width=120)
    withdraw_table.pack(fill="x", padx=10, pady=5)

    def filter_history():
        start_str, end_str = start_date_var.get(), end_date_var.get()
        try:
            start = datetime.strptime(start_str, "%Y-%m-%d")
            end = datetime.strptime(end_str, "%Y-%m-%d") + timedelta(days=1)
        except ValueError:
            return

        trade_table.delete(*trade_table.get_children())
        deposit_table.delete(*deposit_table.get_children())
        withdraw_table.delete(*withdraw_table.get_children())

        if mt5.initialize(path=path):
            deals = mt5.history_deals_get(start, end)
            if deals:
                for deal in deals:
                    if deal.type in [mt5.DEAL_TYPE_BUY, mt5.DEAL_TYPE_SELL]:
                        trade_table.insert("", "end", values=(deal.ticket, deal.symbol, deal.volume, deal.price, deal.profit, datetime.fromtimestamp(deal.time)))
                    elif deal.type == mt5.DEAL_TYPE_BALANCE:
                        if "deposit" in deal.comment.lower():
                            deposit_table.insert("", "end", values=(datetime.fromtimestamp(deal.time), deal.profit, deal.comment))
                        elif "withdraw" in deal.comment.lower():
                            withdraw_table.insert("", "end", values=(datetime.fromtimestamp(deal.time), deal.profit, deal.comment))
            mt5.shutdown()

    tk.Button(filter_frame, text="Apply Date Filter", command=filter_history, bg="blue", fg="white").grid(row=2, columnspan=4, pady=10)


def add_terminal():
    path = filedialog.askopenfilename(title="Select terminal64.exe", filetypes=[("EXE files", "terminal64.exe")])
    if path and os.path.exists(path):
        terminal_paths.append(path)
        create_terminal_tab(path)


def create_terminal_tab(path):
    frame = tk.Frame(tabs)
    tabs.add(frame, text=os.path.basename(path))

    tk.Label(frame, text=f"Terminal: {os.path.basename(path)}", font=("Arial", 14)).pack(pady=5)

    info_labels = {
        "Name": tk.Label(frame, text="Name: -", font=("Arial", 11)),
        "Login": tk.Label(frame, text="Login ID: -", font=("Arial", 11)),
        "Server": tk.Label(frame, text="Server: -", font=("Arial", 11)),
        "Company": tk.Label(frame, text="Company: -", font=("Arial", 11)),
        "Currency": tk.Label(frame, text="Currency: -", font=("Arial", 11)),
        "Balance": tk.Label(frame, text="Balance: -", font=("Arial", 11)),
        "Equity": tk.Label(frame, text="Equity: -", font=("Arial", 11)),
        "FreeMargin": tk.Label(frame, text="Free Margin: -", font=("Arial", 11)),
        "MarginLevel": tk.Label(frame, text="Margin Level: -", font=("Arial", 11)),
        "Credit": tk.Label(frame, text="Credit: -", font=("Arial", 11)),
        "FloatingPnL": tk.Label(frame, text="Floating PnL: -", font=("Arial", 11)),
    }
    for label in info_labels.values():
        label.pack(anchor="w", padx=20, pady=2)

    trades_table = ttk.Treeview(frame, columns=("ticket", "symbol", "volume", "price", "type", "sl", "tp", "profit"), show="headings")
    for col in trades_table["columns"]:
        trades_table.heading(col, text=col.upper())
        trades_table.column(col, width=100)
    trades_table.pack(fill="x", padx=10, pady=5)

    def update_info():
        if not mt5.initialize(path=path):
            for label in info_labels.values():
                label.config(text="\u274C Error")
            trades_table.delete(*trades_table.get_children())
            root.after(500, update_info)  # ✅ 1 second update
            return

        account = mt5.account_info()
        if account:
            info_labels["Name"].config(text=f"Name: {account.name}")
            info_labels["Login"].config(text=f"Login ID: {account.login}")
            info_labels["Server"].config(text=f"Server: {account.server}")
            info_labels["Company"].config(text=f"Company: {account.company}")
            info_labels["Currency"].config(text=f"Currency: {account.currency}")
            info_labels["Balance"].config(text=f"Balance: \u20B9{account.balance:.2f}")
            info_labels["Equity"].config(text=f"Equity: \u20B9{account.equity:.2f}")
            info_labels["FreeMargin"].config(text=f"Free Margin: \u20B9{account.margin_free:.2f}")
            info_labels["MarginLevel"].config(text=f"Margin Level: {account.margin_level:.2f}%")
            info_labels["Credit"].config(text=f"Credit: \u20B9{account.credit:.2f}")
            info_labels["FloatingPnL"].config(text=f"Floating PnL: \u20B9{account.profit:.2f}")

            if account.margin_level < alert_margin_level and path not in alerted_terminals:
                alerted_terminals.add(path)
                messagebox.showwarning("Low Margin Alert", f"{account.name} ({account.login}) margin level low: {account.margin_level:.2f}%")

            terminal_table.insert("", "end", values=(os.path.basename(path), account.login, account.name, account.company, f"{account.margin_level:.2f}%"))

        trades_table.delete(*trades_table.get_children())
        positions = mt5.positions_get()
        if positions:
            for pos in positions:
                trades_table.insert("", "end", values=(pos.ticket, pos.symbol, pos.volume, pos.price_open, pos.type, pos.sl, pos.tp, pos.profit))

        mt5.shutdown()
        root.after(500, update_info)  # ✅ 1 second update

    update_info()
    show_history(frame, path)


def update_summary():
    total_balance = total_equity = total_credit = total_floating = 0.0
    terminal_table.delete(*terminal_table.get_children())
    for path in terminal_paths:
        if mt5.initialize(path=path):
            account = mt5.account_info()
            if account:
                total_balance += account.balance
                total_equity += account.equity
                total_credit += account.credit
                total_floating += account.profit

                if account.margin_level < alert_margin_level and path not in alerted_terminals:
                    alerted_terminals.add(path)
                    messagebox.showwarning("Low Margin Alert", f"{account.name} ({account.login}) margin level low: {account.margin_level:.2f}%")

                terminal_table.insert("", "end", values=(os.path.basename(path), account.login, account.name, account.company, f"{account.margin_level:.2f}%"))
            mt5.shutdown()
    summary_labels["TotalBalance"].config(text=f"Total Balance: \u20B9{total_balance:.2f}")
    summary_labels["TotalEquity"].config(text=f"Total Equity: \u20B9{total_equity:.2f}")
    summary_labels["TotalCredit"].config(text=f"Total Credit: \u20B9{total_credit:.2f}")
    summary_labels["TotalFloating"].config(text=f"Total Floating PnL: \u20B9{total_floating:.2f}")
    root.after(500, update_summary)  # ✅ 1 second update


add_terminal_button = tk.Button(main_frame, text="Add Terminal", command=add_terminal, bg="green", fg="white")
add_terminal_button.pack(pady=10)

update_summary()

root.mainloop()
