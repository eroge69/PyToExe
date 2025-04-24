import requests
import random
import time
import json
import os
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.common.proxy import Proxy, ProxyType
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Load config
with open("config.json") as f:
    config = json.load(f)

def load_proxies():
    if os.path.exists(config["proxy_list_path"]):
        with open(config["proxy_list_path"]) as f:
            return [line.strip() for line in f if line.strip()]
    return []

def setup_driver(proxy=None, user_agent=None):
    options = uc.ChromeOptions()
    if proxy:
        options.add_argument(f'--proxy-server={proxy}')
    if user_agent:
        options.add_argument(f'user-agent={user_agent}')
    
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_argument("--disable-infobars")
    options.add_argument("--disable-web-security")
    options.add_argument("--disable-site-isolation-trials")
    options.add_argument("--disable-webrtc")
    options.add_argument("--disable-extensions")

    driver = uc.Chrome(options=options)
    return driver

def simulate_typing(element, text):
    for char in text:
        element.send_keys(char)
        time.sleep(random.uniform(0.1, 0.3))

def solve_captcha(sitekey, url, api_key):
    print("[+] Solving CAPTCHA...")
    captcha_payload = {
        "key": api_key,
        "method": "userrecaptcha",
        "googlekey": sitekey,
        "pageurl": url,
        "json": 1
    }
    resp = requests.post("http://2captcha.com/in.php", data=captcha_payload).json()
    if resp.get("status") == 1:
        request_id = resp.get("request")
        fetch_url = f"http://2captcha.com/res.php?key={api_key}&action=get&id={request_id}&json=1"
        for _ in range(20):
            result = requests.get(fetch_url).json()
            if result.get("status") == 1:
                print("[+] CAPTCHA Solved!")
                return result.get("request")
            time.sleep(5)
    return None

def send_telegram_alert(message):
    token = config["telegram_bot_token"]
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    data = {
        "chat_id": "@your_channel_or_user_id",  # এখানে তোমার Chat ID বা Channel ID বসাও
        "text": message
    }
    requests.post(url, data=data)

def main():
    proxies = load_proxies()
    proxy = random.choice(proxies) if proxies else None

    user_agents = [
        "Mozilla/5.0 (Linux; Android 10)", 
        "Mozilla/5.0 (iPhone; CPU iPhone OS 13_2_3)", 
        "Mozilla/5.0 (Windows NT 10.0)"
    ]
    ua = random.choice(user_agents)

    driver = setup_driver(proxy=proxy, user_agent=ua)
    driver.get(config["target_url"])
    time.sleep(random.randint(*config["signup_delay_range"]))

    try:
        # ফর্ম ফিল্ড ফিল করা
        driver.find_element(By.NAME, config["form_fields"]["first_name"]).send_keys("John")
        driver.find_element(By.NAME, config["form_fields"]["last_name"]).send_keys("Doe")
        driver.find_element(By.NAME, config["form_fields"]["email"]).send_keys(f"john{random.randint(1000,9999)}@gmail.com")
        driver.find_element(By.NAME, config["form_fields"]["address"]).send_keys("123 Fake Street")
        driver.find_element(By.NAME, config["form_fields"]["region"]).send_keys("California")
        driver.find_element(By.NAME, config["form_fields"]["city"]).send_keys("Los Angeles")
        driver.find_element(By.NAME, config["form_fields"]["phone"]).send_keys("5551234567")

        # CAPTCHA Solve যদি থাকে
        # sitekey = "SITE_KEY_HERE"
        # token = solve_captcha(sitekey, config["target_url"], config["2captcha_api_key"])
        # CAPTCHA token ইনজেক্ট করো এখানে যদি দরকার হয়

        driver.find_element(By.XPATH, "//button").click()
        send_telegram_alert("Signup submitted successfully!")

    except Exception as e:
        print("[!] Error during signup:", e)
        send_telegram_alert(f"Signup failed: {e}")
    finally:
        driver.quit()

if __name__ == "__main__":
    main()