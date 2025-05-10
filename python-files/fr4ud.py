import json
import os
import secrets
import hashlib
from datetime import datetime, timedelta
import msvcrt
import time
import sys
import socket
import requests
from urllib.parse import urlparse

# ============== CONFIGURATION ==============
LICENSE_KEYS_FILE = "license_keys.json"
STAFF_CREDENTIALS_FILE = "staff_credentials.json"
USER_CREDENTIALS_FILE = "user_credentials.json"
BLACKLIST_FILE = "blacklist.json"
CARD_REQUESTS_FILE = "card_requests.json"
EXPORT_DIR = "license_exports"
WEBHOOK_URL = "https://discord.com/api/webhooks/1370333578554249296/U2RFVOeFVCXFwCnwQXvMDqbLDranj5ndQ7PueqN4CqtmZpbFbu2gP5MwkxPYvzPO7DPB"

# ============== WELCOME SCREEN ==============
def show_welcome_screen():
    print(r"""
███████╗██████╗ ██╗  ██╗██████╗ 
██╔════╝██╔══██╗╚██╗██╔╝╚════██╗
█████╗  ██████╔╝ ╚███╔╝  █████╔╝
██╔══╝  ██╔══██╗ ██╔██╗  ╚═══██╗
███████╗██║  ██║██╔╝ ██╗██████╔╝
╚══════╝╚═╝  ╚═╝╚═╝  ╚═╝╚═════╝ 
""")
    print("\n" + " " * 10 + "AMAZON STORE CARD GENERATOR")
    print("\n" + "=" * 50)
    time.sleep(2)

# ============== LICENSE TIERS ==============
TIERS = {
    "free": {
        "display": "Free Tier",
        "max_balance": 1000,
        "cooldown": 3600,
        "description": "1K cards max, 1h cooldown"
    },
    "standard": {
        "display": "Standard Tier",
        "max_balance": 10000,
        "cooldown": 300,
        "description": "All cards, 5m cooldown"
    },
    "premium": {
        "display": "Premium Tier",
        "max_balance": 10000,
        "cooldown": 0,
        "description": "All cards, no cooldown"
    }
}

CARD_TYPES = {
    "1": {"name": "1K Balance", "value": 1000},
    "2": {"name": "2K Balance", "value": 2000},
    "3": {"name": "5K Balance", "value": 5000},
    "4": {"name": "10K Balance", "value": 10000}
}

# ============== UTILITY FUNCTIONS ==============
def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def print_header(title):
    print(f"\n=== {title.upper()} ===")

def print_success(message):
    print(f"[SUCCESS] {message}")

def print_error(message):
    print(f"[ERROR] {message}")

def get_password_input(prompt="Password: "):
    print(prompt, end='', flush=True)
    password = []
    while True:
        ch = msvcrt.getch().decode('utf-8', 'ignore')
        if ch == '\r':
            print()
            break
        elif ch == '\x08':
            if password:
                password.pop()
                print('\b \b', end='', flush=True)
        else:
            password.append(ch)
            print('*', end='', flush=True)
    return ''.join(password)

def get_ip_address():
    try:
        return socket.gethostbyname(socket.gethostname())
    except:
        return "Unknown"

def send_to_webhook(message):
    try:
        payload = {"content": message}
        headers = {"Content-Type": "application/json"}
        response = requests.post(WEBHOOK_URL, json=payload, headers=headers)
        return response.status_code == 204
    except Exception as e:
        print(f"Webhook error: {e}")
        return False

def log_event(event_type, username, ip, additional_info=""):
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    message = (
        f"**{event_type}** - {timestamp}\n"
        f"👤 User: `{username}`\n"
        f"🌐 IP: `{ip}`\n"
    )
    if additional_info:
        message += f"📝 Info: {additional_info}\n"
    
    send_to_webhook(message)
    with open("activity_log.txt", "a") as log_file:
        log_file.write(f"{timestamp} - {event_type} - {username} - {ip} - {additional_info}\n")

# ============== SECURITY FUNCTIONS ==============
def hash_password(password):
    salt = os.urandom(32)
    key = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100000)
    return (salt + key).hex()

def verify_password(stored_hash, password):
    try:
        stored_bytes = bytes.fromhex(stored_hash)
        salt = stored_bytes[:32]
        key = stored_bytes[32:]
        new_key = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100000)
        return key == new_key
    except:
        return False

def is_blacklisted(username, ip):
    if not os.path.exists(BLACKLIST_FILE):
        return False
    
    with open(BLACKLIST_FILE, 'r') as f:
        blacklist = json.load(f)
    
    return username in blacklist.get("usernames", []) or ip in blacklist.get("ips", [])

def add_to_blacklist(username=None, ip=None):
    blacklist = {"usernames": [], "ips": []}
    if os.path.exists(BLACKLIST_FILE):
        with open(BLACKLIST_FILE, 'r') as f:
            blacklist = json.load(f)
    
    if username and username not in blacklist["usernames"]:
        blacklist["usernames"].append(username)
    if ip and ip not in blacklist["ips"]:
        blacklist["ips"].append(ip)
    
    with open(BLACKLIST_FILE, 'w') as f:
        json.dump(blacklist, f, indent=2)

# ============== LICENSE FUNCTIONS ==============
def generate_license_key(tier):
    return {
        "key": f"{secrets.token_hex(4).upper()}-{secrets.token_hex(4).upper()}",
        "tier": tier,
        "generated_at": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        "expires_at": (datetime.now() + timedelta(days=365)).strftime('%Y-%m-%d'),
        "status": "active",
        "claimed_by": None
    }

def verify_license_key(key):
    if not os.path.exists(LICENSE_KEYS_FILE):
        return False
    
    with open(LICENSE_KEYS_FILE, 'r') as f:
        licenses = json.load(f)
    
    for license in licenses:
        if license["key"] == key and license["status"] == "active":
            if datetime.strptime(license["expires_at"], '%Y-%m-%d') > datetime.now():
                return license
    return False

def claim_license_key(key, username):
    with open(LICENSE_KEYS_FILE, 'r+') as f:
        licenses = json.load(f)
        for license in licenses:
            if license["key"] == key and license["status"] == "active":
                license["claimed_by"] = username
                license["claimed_at"] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                f.seek(0)
                json.dump(licenses, f, indent=2)
                return license
    return False

# ============== STAFF FUNCTIONS ==============
def staff_login():
    if not os.path.exists(STAFF_CREDENTIALS_FILE):
        with open(STAFF_CREDENTIALS_FILE, 'w') as f:
            json.dump({
                "1": {
                    "username": "admin",
                    "password_hash": hash_password("admin123"),
                    "role": "admin"
                }
            }, f)
    
    while True:
        clear_screen()
        print_header("STAFF LOGIN")
        
        username = input("Username: ").strip()
        password = get_password_input("Password: ")
        ip = get_ip_address()
        
        if is_blacklisted(username, ip):
            print_error("This account or IP has been banned")
            time.sleep(2)
            return None
        
        with open(STAFF_CREDENTIALS_FILE, 'r') as f:
            staff_db = json.load(f)
        
        for staff_id, data in staff_db.items():
            if data["username"] == username and verify_password(data["password_hash"], password):
                log_event("STAFF LOGIN", username, ip)
                print_success("Login successful!")
                time.sleep(1)
                return staff_id
        
        log_event("FAILED STAFF LOGIN", username, ip)
        print_error("Invalid credentials")
        time.sleep(1)

def staff_generate_license_keys(staff_id):
    ip = get_ip_address()
    while True:
        clear_screen()
        print_header("GENERATE LICENSE KEYS")
        print("1. Free Tier (1K cards, 1h cooldown)")
        print("2. Standard Tier (All cards, 5m cooldown)")
        print("3. Premium Tier (All cards, no cooldown)")
        print("Q. Return to menu")
        
        choice = input("\nSelect tier (1-3) or Q: ").strip().upper()
        
        if choice == 'Q':
            return
        
        tier_map = {'1': 'free', '2': 'standard', '3': 'premium'}
        if choice not in tier_map:
            print_error("Invalid selection")
            time.sleep(1)
            continue
            
        tier = tier_map[choice]
        try:
            quantity = int(input(f"How many {TIERS[tier]['display']} keys to generate? (1-100): "))
            if not 1 <= quantity <= 100:
                print_error("Quantity must be 1-100")
                time.sleep(1)
                continue
                
            # Generate and save keys
            keys = []
            existing = []
            if os.path.exists(LICENSE_KEYS_FILE):
                with open(LICENSE_KEYS_FILE, 'r') as f:
                    existing = json.load(f)
            
            for _ in range(quantity):
                key_data = generate_license_key(tier)
                key_data["generated_by"] = staff_id
                keys.append(key_data)
            
            with open(LICENSE_KEYS_FILE, 'w') as f:
                json.dump(existing + keys, f, indent=2)
            
            # Log and show results
            log_event("LICENSE KEYS GENERATED", staff_id, ip, 
                     f"Generated {quantity} {TIERS[tier]['display']} keys")
            
            clear_screen()
            print_success(f"Generated {quantity} {TIERS[tier]['display']} keys:")
            for key in keys:
                print(f"\nKey: {key['key']}")
                print(f"Tier: {key['tier']}")
                print(f"Expires: {key['expires_at']}")
            
            input("\nPress Enter to continue...")
            
        except ValueError:
            print_error("Please enter a valid number")
            time.sleep(1)

def staff_ban_account(staff_id):
    ip = get_ip_address()
    clear_screen()
    print_header("BAN ACCOUNT")
    
    username = input("Enter username to ban: ").strip()
    ip_to_ban = input("Enter IP to ban (leave blank for username only): ").strip()
    
    if not username and not ip_to_ban:
        print_error("Must provide username or IP")
        time.sleep(1)
        return
    
    add_to_blacklist(username if username else None, ip_to_ban if ip_to_ban else None)
    log_event("ACCOUNT BANNED", staff_id, ip, 
             f"Banned username: {username if username else 'N/A'}, IP: {ip_to_ban if ip_to_ban else 'N/A'}")
    print_success("Account banned successfully")
    time.sleep(1)

def view_license_stats():
    try:
        with open(LICENSE_KEYS_FILE, 'r') as f:
            licenses = json.load(f)
        
        stats = {
            "total": len(licenses),
            "free": 0,
            "standard": 0,
            "premium": 0,
            "active": 0,
            "expired": 0,
            "claimed": 0
        }
        
        for license in licenses:
            stats[license["tier"]] += 1
            if datetime.strptime(license["expires_at"], '%Y-%m-%d') > datetime.now():
                stats["active"] += 1
            else:
                stats["expired"] += 1
            if license["claimed_by"]:
                stats["claimed"] += 1
        
        clear_screen()
        print_header("LICENSE STATISTICS")
        print(f"Total Keys: {stats['total']}")
        print(f"Active Keys: {stats['active']}")
        print(f"Expired Keys: {stats['expired']}")
        print(f"Claimed Keys: {stats['claimed']}")
        print("\nBy Tier:")
        print(f"- Free: {stats['free']}")
        print(f"- Standard: {stats['standard']}")
        print(f"- Premium: {stats['premium']}")
        
        input("\nPress Enter to continue...")
    except Exception as e:
        print_error(f"Error loading statistics: {str(e)}")
        time.sleep(1)

def staff_menu(staff_id):
    ip = get_ip_address()
    log_event("STAFF MENU ACCESS", staff_id, ip)
    
    while True:
        clear_screen()
        print_header("STAFF MENU")
        print(f"Logged in as: {staff_id}")
        print("\n1. Generate License Keys")
        print("2. Ban Account")
        print("3. View License Statistics")
        print("4. Logout")
        
        choice = input("\nSelect option: ").strip()
        
        if choice == '1':
            staff_generate_license_keys(staff_id)
        elif choice == '2':
            staff_ban_account(staff_id)
        elif choice == '3':
            view_license_stats()
        elif choice == '4':
            log_event("STAFF LOGOUT", staff_id, ip)
            break
        else:
            print_error("Invalid option")
            time.sleep(1)

# ============== USER FUNCTIONS ==============
def register_user():
    ip = get_ip_address()
    clear_screen()
    print_header("REGISTRATION")
    
    if is_blacklisted("", ip):
        print_error("Your IP address has been banned")
        log_event("BLOCKED REGISTRATION ATTEMPT", "UNKNOWN", ip, "IP is blacklisted")
        time.sleep(2)
        return None
    
    username = input("Username: ").strip()
    if is_blacklisted(username, ""):
        print_error("This username has been banned")
        log_event("BLOCKED REGISTRATION ATTEMPT", username, ip, "Username is blacklisted")
        time.sleep(2)
        return None
    
    password = get_password_input("Password (min 8 chars): ")
    if len(password) < 8:
        print_error("Password must be at least 8 characters")
        time.sleep(1)
        return None
    
    license_key = input("License Key (XXXX-XXXX format): ").strip().upper()
    license_info = verify_license_key(license_key)
    if not license_info:
        print_error("Invalid or expired license key")
        log_event("FAILED REGISTRATION", username, ip, "Invalid license key")
        time.sleep(1)
        return None
    
    # Check if username exists
    users = {}
    if os.path.exists(USER_CREDENTIALS_FILE):
        with open(USER_CREDENTIALS_FILE, 'r') as f:
            users = json.load(f)
    
    if username in users:
        print_error("Username already exists")
        time.sleep(1)
        return None
    
    # Claim the license key
    claimed_license = claim_license_key(license_key, username)
    if not claimed_license:
        print_error("License key already claimed")
        time.sleep(1)
        return None
    
    # Create user account
    users[username] = {
        "password_hash": hash_password(password),
        "license_key": license_key,
        "license_tier": claimed_license["tier"],
        "registered_at": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        "ip_address": ip
    }
    
    with open(USER_CREDENTIALS_FILE, 'w') as f:
        json.dump(users, f, indent=2)
    
    log_event("NEW REGISTRATION", username, ip, 
             f"License Tier: {claimed_license['tier']}")
    print_success("Registration successful!")
    time.sleep(1)
    return username

def user_login():
    ip = get_ip_address()
    clear_screen()
    print_header("USER LOGIN")
    
    if is_blacklisted("", ip):
        print_error("Your IP address has been banned")
        log_event("BLOCKED LOGIN ATTEMPT", "UNKNOWN", ip, "IP is blacklisted")
        time.sleep(2)
        return None
    
    username = input("Username: ").strip()
    if is_blacklisted(username, ""):
        print_error("This account has been banned")
        log_event("BLOCKED LOGIN ATTEMPT", username, ip, "Username is blacklisted")
        time.sleep(2)
        return None
    
    password = get_password_input("Password: ")
    
    users = {}
    if os.path.exists(USER_CREDENTIALS_FILE):
        with open(USER_CREDENTIALS_FILE, 'r') as f:
            users = json.load(f)
    
    if username not in users:
        log_event("FAILED LOGIN", username, ip, "Username not found")
        print_error("Invalid credentials")
        time.sleep(1)
        return None
    
    if not verify_password(users[username]["password_hash"], password):
        log_event("FAILED LOGIN", username, ip, "Incorrect password")
        print_error("Invalid credentials")
        time.sleep(1)
        return None
    
    log_event("USER LOGIN", username, ip)
    print_success("Login successful!")
    time.sleep(1)
    return username

def generate_card(username):
    ip = get_ip_address()
    users = {}
    with open(USER_CREDENTIALS_FILE, 'r') as f:
        users = json.load(f)
    
    user_data = users.get(username, {})
    if not user_data:
        print_error("User data not found")
        time.sleep(1)
        return
    
    license_key = user_data.get("license_key", "")
    if not license_key:
        print_error("No license key assigned")
        time.sleep(1)
        return
    
    license_info = verify_license_key(license_key)
    if not license_info:
        print_error("Invalid or expired license key")
        time.sleep(1)
        return
    
    tier = license_info["tier"]
    tier_info = TIERS[tier]
    
    # Check cooldown
    last_request = get_last_card_request(username)
    if last_request:
        elapsed = (datetime.now() - datetime.strptime(last_request["timestamp"], '%Y-%m-%d %H:%M:%S')).total_seconds()
        if elapsed < tier_info["cooldown"]:
            remaining = tier_info["cooldown"] - elapsed
            print_error(f"Please wait {int(remaining//60)} minutes before generating another card")
            time.sleep(2)
            return
    
    # Show available card options
    clear_screen()
    print_header("SELECT CARD TYPE")
    print(f"Your License: {tier_info['display']}")
    for code, card in CARD_TYPES.items():
        if card["value"] <= tier_info["max_balance"]:
            print(f"{code}. {card['name']}")
    
    choice = input("\nSelect card type: ").strip()
    if choice not in CARD_TYPES or CARD_TYPES[choice]["value"] > tier_info["max_balance"]:
        print_error("Invalid selection or not allowed for your tier")
        time.sleep(1)
        return
    
    # Generate card
    card_code = f"{secrets.token_hex(4).upper()}-{secrets.token_hex(4).upper()}"
    card_data = {
        "user_id": username,
        "license_key": license_key,
        "card_type": CARD_TYPES[choice]["name"],
        "card_value": CARD_TYPES[choice]["value"],
        "card_code": card_code,
        "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        "ip_address": ip
    }
    
    # Save request
    requests = []
    if os.path.exists(CARD_REQUESTS_FILE):
        with open(CARD_REQUESTS_FILE, 'r') as f:
            requests = json.load(f)
    
    requests.append(card_data)
    with open(CARD_REQUESTS_FILE, 'w') as f:
        json.dump(requests, f, indent=2)
    
    # Log and show result
    log_event("CARD GENERATED", username, ip, 
             f"Card: {CARD_TYPES[choice]['name']}, Code: {card_code}")
    
    clear_screen()
    print_header("CARD GENERATED")
    print("Please make a ticket and send this code to claim your card:")
    print(f"\n=== CARD CODE ===\n{card_code}\n=================")
    print(f"\nCard Type: {CARD_TYPES[choice]['name']}")
    print(f"Value: ${CARD_TYPES[choice]['value']:,}")
    
    input("\nPress Enter to return to menu...")

def get_last_card_request(username):
    if not os.path.exists(CARD_REQUESTS_FILE):
        return None
    
    with open(CARD_REQUESTS_FILE, 'r') as f:
        requests = json.load(f)
    
    user_requests = [r for r in requests if r["user_id"] == username]
    if not user_requests:
        return None
    
    return sorted(user_requests, key=lambda x: x["timestamp"], reverse=True)[0]

def user_menu(username):
    ip = get_ip_address()
    users = {}
    with open(USER_CREDENTIALS_FILE, 'r') as f:
        users = json.load(f)
    
    user_data = users.get(username, {})
    if not user_data:
        print_error("User data not found")
        time.sleep(1)
        return
    
    while True:
        clear_screen()
        print_header(f"WELCOME {username.upper()}")
        print(f"License: {TIERS[user_data.get('license_tier', '')]['display']}")
        print("\n1. Generate Gift Card")
        print("2. Logout")
        
        choice = input("\nSelect option: ").strip()
        
        if choice == '1':
            generate_card(username)
        elif choice == '2':
            log_event("USER LOGOUT", username, ip)
            break
        else:
            print_error("Invalid option")
            time.sleep(1)

# ============== MAIN PROGRAM ==============
def initialize_system():
    os.makedirs(EXPORT_DIR, exist_ok=True)
    
    # Initialize files with empty structures if they don't exist
    files = {
        LICENSE_KEYS_FILE: [],
        STAFF_CREDENTIALS_FILE: {
            "1": {
                "username": "admin",
                "password_hash": hash_password("admin123"),
                "role": "admin",
                "created_at": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
        },
        USER_CREDENTIALS_FILE: {},
        BLACKLIST_FILE: {"usernames": [], "ips": []},
        CARD_REQUESTS_FILE: []
    }
    
    for file_path, default_content in files.items():
        if not os.path.exists(file_path):
            with open(file_path, 'w') as f:
                json.dump(default_content, f, indent=2)

def main():
    show_welcome_screen()
    clear_screen()
    initialize_system()
    ip = get_ip_address()
    
    while True:
        clear_screen()
        print_header("MAIN MENU")
        print("1. Register")
        print("2. Login")
        print("3. Staff Login")
        print("4. Exit")
        
        choice = input("\nSelect option: ").strip()
        
        if choice == '1':
            username = register_user()
            if username:
                user_menu(username)
        elif choice == '2':
            username = user_login()
            if username:
                user_menu(username)
        elif choice == '3':
            staff_id = staff_login()
            if staff_id:
                staff_menu(staff_id)
        elif choice == '4':
            sys.exit(0)
        else:
            print_error("Invalid option")
            time.sleep(1)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nProgram terminated by user")
        sys.exit(0)