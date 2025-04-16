#!/usr/bin/env python3

# Color Variables
CYAN = '\033[0;36m'
BLUE = '\033[0;34m'
GREEN = '\033[0;32m'
RED = '\033[0;31m'
MAGENTA = '\033[0;35m'
YELLOW = '\033[0;33m'
RESET = '\033[0m'
BOLD = '\033[1m'

# Header Print
def print_header():
    print(f"{CYAN}▀███▀▀▀███████▀  ▀████▀▀███▀▀▀██▄ {RESET}")
    print(f"{CYAN}  ██    ▀█ ██      ██    ██   ▀██▄{RESET}")
    print(f"{CYAN}  ██   █   ██      ██    ██   ▄██{RESET}")
    print(f"{CYAN}  ██▀▀██   ██████████    ███████{RESET}")
    print(f"{CYAN}  ██   █   ██      ██    ██  ██▄{RESET}")
    print(f"{CYAN}  ██       ██      ██    ██   ▀██▄{RESET}")
    print(f"{CYAN}▄████▄   ▄████▄  ▄████▄▄████▄ ▄███▄{RESET}")
    
# Sections Print
def print_sections():
    print(f"{YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{RESET}")
    print(f"{CYAN}                 MARKET HACKER ACTIVATE ✅{RESET}")
    print(f"{YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{RESET}")
    print(f"{BLUE}  ┌───────────────────────────────────────┐{RESET}")
    print(f"{BLUE}  │{RESET}            {GREEN}MADE BY BARFI OWNER        {BLUE}│{RESET}")
    print(f"{BLUE}  │{RESET}           {GREEN}TELEGRAM- @Barfibomm        {BLUE}│{RESET}")
    print(f"{BLUE}  │{RESET}       {GREEN}ZOMBE v3.9 FAITH WITH POWER     {BLUE}│{RESET}")
    print(f"{BLUE}  │{RESET}          {GREEN}QUALITY WITH QUANTITY        {BLUE}│{RESET}")
    print(f"{BLUE}  └───────────────────────────────────────┘{RESET}\n")

# Market Pairs with Priority Weighting
pairs = {
    "EURUSD_OTC": 5, "GBPUSD_OTC": 4, "AUDUSD_OTC": 3, "USDCAD_OTC": 2,
    "USDJPY_OTC": 5, "NZDUSD_OTC": 4, "USDCHF_OTC": 3, "GBPJPY_OTC": 2,
    "DOGE_OTC": 5, "PEPE_OTC": 3
}

# Collect User Inputs with Validation
def collect_inputs():
    from datetime import datetime

    print(f"{BLUE}{BOLD}Please configure the signal generator:{RESET}")
    try:
        start_time = input("Start Time (HH:MM): ")
        datetime.strptime(start_time, "%H:%M")

        interval = int(input("Signal Interval (Minutes): "))
        if interval <= 0: raise ValueError

        total_signals = int(input("Total Signals: "))
        if total_signals <= 0: raise ValueError

        signal_type = input("Signal Type (CALL/PUT/BOTH): ").upper()
        if signal_type not in ["CALL", "PUT", "BOTH"]: raise ValueError

        time_format = int(input("Time Format (12/24 Hours): "))
        if time_format not in [12, 24]: raise ValueError

        save_to_file = input("Save to File? (y/n): ").lower()
        if save_to_file == "y":
            file_name = input("File Name (default: signals.log): ") or "signals.log"
            open(file_name, "w").close()
        else:
            file_name = None

        return start_time, interval, total_signals, signal_type, time_format, file_name

    except ValueError:
        print(f"{RED}Invalid input! Exiting...{RESET}")
        exit(1)

# Generate Signals in Batches
def generate_signals(start_time, interval, total_signals, signal_type, time_format, file_name):
    from datetime import datetime, timedelta
    import random

    print(f"\n{GREEN}Generating Signals with Skewed Logic...{RESET}")
    current_time = datetime.strptime(start_time, "%H:%M")
    count = 0

    while count < total_signals:
        print(f"{BLUE}Generating Batch...{RESET}")
        for _ in range(min(10, total_signals - count)):
            pair = random.choices(
                population=list(pairs.keys()),
                weights=list(pairs.values())
            )[0]

            if time_format == 24:
                signal_time = current_time.strftime("%H:%M")
            else:
                signal_time = current_time.strftime("%I:%M %p")

            if signal_type == "BOTH":
                signal_action = random.choice(["CALL", "PUT"])
            else:
                signal_action = signal_type

            signal = f"{signal_time} {pair} {signal_action}"
            print(f"{MAGENTA}{signal}{RESET}")

            if file_name:
                with open(file_name, "a") as file:
                    file.write(f"{signal}\n")

            current_time += timedelta(minutes=interval)
            count += 1

        print(f"{GREEN}Batch Complete!{RESET}\n")

# Main Script Execution
if __name__ == "__main__":
    print_header()
    print_sections()
    inputs = collect_inputs()
    generate_signals(*inputs)