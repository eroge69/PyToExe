import time
import threading
import itertools
import sys
import os
import requests
import webbrowser
import logging
import re
import asyncio
import argparse
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.progress import Progress, BarColumn, TextColumn, TimeElapsedColumn, TimeRemainingColumn

# Initialize console
console = Console()

# Large ASCII Title
ascii_title = r"""
███████╗██████╗     ███████╗███████╗██████╗ ██╗   ██╗███████╗██████╗     
██╔════╝╚════██╗    ██╔════╝██╔════╝██╔══██╗██║   ██║██╔════╝██╔══██╗    
███████╗ █████╔╝    ███████╗█████╗  ██████╔╝██║   ██║█████╗  ██████╔╝    
╚════██║██╔═══╝     ╚════██║██╔══╝  ██╔══██╗╚██╗ ██╔╝██╔══╝  ██╔══██╗    
███████║███████╗    ███████║███████╗██║  ██║ ╚████╔╝ ███████╗██║  ██║    
╚══════╝╚══════╝    ╚══════╝╚══════╝╚═╝  ╚═╝  ╚═══╝  ╚══════╝╚═╝  ╚═╝    
                                                                          
         ██████╗██╗      ██████╗ ███╗   ██╗███████╗██████╗               
        ██╔════╝██║     ██╔═══██╗████╗  ██║██╔════╝██╔══██╗              
        ██║     ██║     ██║   ██║██╔██╗ ██║█████╗  ██████╔╝              
        ██║     ██║     ██║   ██║██║╚██╗██║██╔══╝  ██╔══██╗              
        ╚██████╗███████╗╚██████╔╝██║ ╚████║███████╗██║  ██║              
         ╚═════╝╚══════╝ ╚═════╝ ╚═╝  ╚═══╝╚══════╝╚═╝  ╚═╝              
                                                                          
                          ⚡ Server Cloner ⚡
"""

# Symbols
symbols = {
    "check": "✅",
    "cross": "❌",
    "star": "✨",
    "warn": "⚠️",
    "rocket": "🚀",
    "loading": "⏳"
}

# Console Setup
console = Console()

# User Input Validation
def is_valid_url(url):
    pattern = re.compile(r"^(https?|ftp)://[^\s/$.?#].[^\s]*$", re.IGNORECASE)
    return re.match(pattern, url) is not None

def get_webhook_url():
    webhook_url = input("[+] Webhook URL: ")
    if is_valid_url(webhook_url):
        return webhook_url
    else:
        print("Invalid URL. Please enter a valid URL.")
        return get_webhook_url()

# Argument Parsing and Logging Setup
def parse_arguments():
    parser = argparse.ArgumentParser(description="S2 Server Cloner")
    parser.add_argument('--loglevel', type=str, default='INFO', help='Set the logging level (DEBUG, INFO, ERROR)')
    return parser.parse_args()


def setup_logging(loglevel):
    levels = {
        'DEBUG': logging.DEBUG,
        'INFO': logging.INFO,
        'ERROR': logging.ERROR
    }
    logging.basicConfig(level=levels.get(loglevel, logging.INFO))

# Beep Sound
def beep():
    sys.stdout.write('\a')
    sys.stdout.flush()

# Animated Loading Text
def animated_loading_text(text="Starting Up", cycles=3):
    for _ in range(cycles):
        for dots in range(4):
            display = text + "." * dots
            sys.stdout.write(f"\r{display}   ")
            sys.stdout.flush()
            time.sleep(0.4)
    sys.stdout.write("\n")

# Send Logs to Webhook
def send_log(webhook_url, message):
    try:
        data = {"content": message}
        requests.post(webhook_url, json=data)
    except:
        pass  # Ignore if webhook fails

# Asynchronous Task for Cloning
async def clone_server_async():
    console.print("[green]Cloning server...[/green]")
    await asyncio.sleep(3)  # Simulate long cloning task
    console.print("[green]Cloning complete![/green]")

# Loading Bar Enhancement
def loading_bar():
    with Progress(
        TextColumn("[progress.description]{task.description}"),
        BarColumn(bar_width=None),
        "[progress.percentage]{task.percentage:>3.0f}%",
        TimeElapsedColumn(),
        TimeRemainingColumn(),
        console=console,
        transient=True
    ) as progress:
        task = progress.add_task("[cyan]Cloning in progress...", total=100)
        while not progress.finished:
            progress.update(task, advance=1)
            time.sleep(0.1)

# Main Menu
def main_menu():
    os.system('cls' if os.name == 'nt' else 'clear')
    console.print(Panel.fit(ascii_title, style="bold magenta"))

    table = Table(show_header=False, header_style="bold cyan", border_style="bright_blue")
    table.add_row("1️⃣", "[bold cyan]Clone Server (User Token)[/bold cyan]")
    table.add_row("2️⃣", "[bold green]Clone Server (OAuth2 Bot)[/bold green]")
    table.add_row("3️⃣", "[bold yellow]Visit Website 🌐[/bold yellow]")
    table.add_row("4️⃣", "[bold magenta]Join Discord Server 🚀[/bold magenta]")
    
    console.print(table)

    choice = console.input("\n[bold white]Select an option:[/bold white] ")

    if choice == "1":
        console.print(f"{symbols['rocket']} [bold green]Starting User Token Cloner...[/bold green]")
        beep()
        start_cloning()
    elif choice == "2":
        console.print(f"{symbols['rocket']} [bold green]OAuth2 Bot Cloner (Coming Soon)[/bold green]")
        beep()
        time.sleep(3)
        main_menu()
    elif choice == "3":
        webbrowser.open("https://your-website.com")
        console.print(f"{symbols['star']} [bold yellow]Opening Website...[/bold yellow]")
        time.sleep(2)
        main_menu()
    elif choice == "4":
        webbrowser.open("https://discord.gg/your-invite")
        console.print(f"{symbols['star']} [bold magenta]Opening Discord Server...[/bold magenta]")
        time.sleep(2)
        main_menu()
    else:
        console.print(f"{symbols['cross']} [bold red]Invalid choice, try again![/bold red]")
        time.sleep(2)
        main_menu()

# Start Cloning Process
def start_cloning():
    args = parse_arguments()
    setup_logging(args.loglevel)

    use_webhook = console.input("[bold blue][+] Webhook Logging (y/n):[/bold blue] ").strip().lower()
    webhook_url = None

    if use_webhook == "y":
        webhook_url = get_webhook_url()

    token = console.input("[bold blue]Enter your Discord token:[/bold blue] ").strip()
    source_guild_id = console.input("[bold blue]Enter Source Server ID:[/bold blue] ").strip()
    destination_guild_id = console.input("[bold blue]Enter Destination Server ID:[/bold blue] ").strip()

    headers = {
        "Authorization": token,
        "Content-Type": "application/json"
    }

    with Progress(
        TextColumn("[progress.description]{task.description}"),
        BarColumn(bar_width=None),
        "[progress.percentage]{task.percentage:>3.0f}%",
        TimeElapsedColumn(),
        TimeRemainingColumn(),
        console=console,
        transient=True
    ) as progress:

        main_task = progress.add_task("[cyan]Starting cloning...", total=5)

        # 1. Fetch roles
        progress.update(main_task, description="[cyan]Fetching roles...")
        roles = requests.get(f"https://discord.com/api/v9/guilds/{source_guild_id}/roles", headers=headers).json()
        time.sleep(1)
        progress.advance(main_task)
        beep()
        if webhook_url:
            send_log(webhook_url, "Fetched roles from source server.")

        # 2. Fetch channels
        progress.update(main_task, description="[cyan]Fetching channels...")
        channels = requests.get(f"https://discord.com/api/v9/guilds/{source_guild_id}/channels", headers=headers).json()
        time.sleep(1)
        progress.advance(main_task)
        beep()
        if webhook_url:
            send_log(webhook_url, "Fetched channels from source server.")

        # 3. Create roles in destination
        progress.update(main_task, description="[cyan]Cloning roles...")
        for role in roles[::-1]:  # reverse to keep permission hierarchy
            if role['name'] != "@everyone":
                payload = {
                    "name": role['name'],
                    "permissions": role['permissions'],
                    "color": role['color'],
                    "hoist": role['hoist'],
                    "mentionable": role['mentionable']
                }
                r = requests.post(f"https://discord.com/api/v9/guilds/{destination_guild_id}/roles", headers=headers, json=payload)
                if webhook_url:
                    send_log(webhook_url, f"Created role: {role['name']}")
                time.sleep(0.5)
        progress.advance(main_task)
        beep()

        # 4. Create categories
        progress.update(main_task, description="[cyan]Cloning categories...")
        for channel in channels:
            if channel['type'] == 4:  # category
                payload = {
                    "name": channel['name'],
                    "type": 4,
                    "permission_overwrites": channel.get('permission_overwrites', [])
                }
                r = requests.post(f"https://discord.com/api/v9/guilds/{destination_guild_id}/channels", headers=headers, json=payload)
                if webhook_url:
                    send_log(webhook_url, f"Created category: {channel['name']}")
                time.sleep(0.5)
        progress.advance(main_task)
        beep()

        # 5. Create text/voice channels
        progress.update(main_task, description="[cyan]Cloning channels...")
        for channel in channels:
            if channel['type'] in (0, 2):  # 0=text, 2=voice
                payload = {
                    "name": channel['name'],
                    "type": channel['type'],
                    "permission_overwrites": channel.get('permission_overwrites', []),
                    "parent_id": channel.get('parent_id')
                }
                r = requests.post(f"https://discord.com/api/v9/guilds/{destination_guild_id}/channels", headers=headers, json=payload)
                if webhook_url:
                    send_log(webhook_url, f"Created channel: {channel['name']}")
                time.sleep(0.5)
        progress.advance(main_task)
        beep()

    console.print(f"\n{symbols['check']} [bold green]Server cloning completed successfully![/bold green]")
    if webhook_url:
        send_log(webhook_url, "✅ Server cloning completed successfully!")

    time.sleep(3)
    main_menu()

# Main Execution Flow
if __name__ == "__main__":
    os.system('cls' if os.name == 'nt' else 'clear')
    animated_loading_text("Initializing S2 Server Cloner")
    main_menu()
