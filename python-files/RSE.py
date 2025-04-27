import os
import requests
from datetime import datetime
from urllib3.exceptions import InsecureRequestWarning

# Suppress SSL warnings
requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)

# === Firewall details with folder mapping ===
FIREWALLS = {
    "10.1.1.1": "delhi",
    "10.1.1.2": "Nokh",
    "10.2.2.2": "RB01",
    "10.3.3.2": "RB02"
}

USERNAME = "admin"
PASSWORD = "Admin@123"

# === Base directory to store backups ===
BASE_DIR = r"C:\Users\manin\Backup"

def get_api_key(ip):
    """Get API key from firewall"""
    url = f"https://{ip}/api/?type=keygen&user={USERNAME}&password={PASSWORD}"  # Fix the URL here
    response = requests.get(url, verify=False)
    if "<key>" in response.text:
        key = response.text.split("<key>")[1].split("</key>")[0]
        print(f"[+] API Key acquired for {ip}")
        return key
    else:
        raise Exception(f"[-] Failed to retrieve API key from {ip}")

def download_config(ip, folder_name, api_key):
    """Download running config to folder"""
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    folder_path = os.path.join(BASE_DIR, folder_name)
    os.makedirs(folder_path, exist_ok=True)
    file_path = os.path.join(folder_path, f"PA_Backup_{timestamp}.xml")

    url = f"https://{ip}/api/?type=export&category=configuration&key={api_key}"
    print(f"[+] Downloading config from {ip}...")
    response = requests.get(url, verify=False)
    if response.status_code == 200:
        with open(file_path, "wb") as f:
            f.write(response.content)
        print(f"[+] Backup saved: {file_path}")
    else:
        raise Exception(f"[-] Failed to download configuration from {ip}")

def main():
    for ip, folder in FIREWALLS.items():
        try:
            print(f"\n[=] Processing firewall: {ip} -> Folder: {folder}")
            api_key = get_api_key(ip)
            download_config(ip, folder, api_key)
        except Exception as e:
            print(f"[!] Error for {ip}: {e}")

if __name__ == "__main__":
    main()
