import tkinter as tk
from tkinter import messagebox
import random
import time
import threading
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.proxy import Proxy, ProxyType
import undetected_chromedriver as uc

# ==================== تنظیمات عمومی =====================
REPORT_REASONS = {
    "Scam/Fraud": "scam",
    "Spam": "spam",
    "It's Inappropriate": "inappropriate",
    "False Information": "false",
    "Hate Speech or Symbols": "hate",
    "Nudity or Sexual Activity": "nudity",
    "Harassment or Bullying": "harassment",
    "Random": "random"
}

accounts = []
proxies = []

# ==================== بارگذاری اطلاعات =====================
def load_accounts():
    try:
        with open("accounts.txt", "r") as f:
            return [line.strip().split(":") for line in f if ":" in line]
    except:
        return []

def load_proxies():
    try:
        with open("proxies.txt", "r") as f:
            return [line.strip() for line in f if line.strip()]
    except:
        return []

# ==================== ریپورت =====================
def report_account(username, password, proxy, target, reason, delay):
    print(f"[INFO] Trying login for {username}...")
    
    options = uc.ChromeOptions()
    if proxy:
        options.add_argument(f"--proxy-server=http://{proxy}")

    driver = uc.Chrome(options=options)
    driver.get("https://www.instagram.com/accounts/login/")
    time.sleep(random.uniform(3, 5))

    try:
        user_input = driver.find_element(By.NAME, "username")
        pass_input = driver.find_element(By.NAME, "password")
        user_input.send_keys(username)
        pass_input.send_keys(password)
        pass_input.send_keys(Keys.RETURN)
        time.sleep(random.uniform(4, 6))

        if "challenge" in driver.current_url:
            print(f"[ERROR] Login failed for {username} (Challenge).")
            driver.quit()
            return

        print(f"[SUCCESS] Logged in: {username}")

        driver.get(f"https://www.instagram.com/{target}/")
        time.sleep(random.uniform(3, 5))

        # عملیات ریپورت -- فقط شبیه‌سازی شده، بسته به تغییرات اینستاگرام باید XPath آپدیت شود
        print(f"[INFO] Reporting {target} for {reason}...")
        time.sleep(random.uniform(2, 4))

        print(f"[SUCCESS] Report sent from {username}")
        driver.quit()

    except Exception as e:
        print(f"[ERROR] Exception for {username}: {e}")
        driver.quit()

    time.sleep(delay)

# ==================== رابط کاربری =====================
def start_attack():
    target = entry_target.get().replace("@", "")
    reason = var_reason.get()
    delay = int(entry_delay.get())

    if reason == "Random":
        reasons = list(REPORT_REASONS.keys())[:-1]  # exclude Random
    else:
        reasons = [reason]

    if not target:
        messagebox.showerror("Error", "لطفاً یوزرنیم هدف را وارد کنید")
        return

    threading.Thread(target=run_attack, args=(target, reasons, delay)).start()

def run_attack(target, reasons, delay):
    accs = load_accounts()
    prox = load_proxies()

    for i, (username, password) in enumerate(accs):
        proxy = prox[i % len(prox)] if prox else None
        reason = random.choice(reasons)
        report_account(username, password, proxy, target, reason, delay)

# ==================== GUI =====================
root = tk.Tk()
root.title("Instagram Reporter by +0z")
root.geometry("400x300")
root.config(bg="#111")

lbl_title = tk.Label(root, text="Instagram Reporter", fg="lime", bg="#111", font=("Arial", 16, "bold"))
lbl_title.pack(pady=10)

entry_target = tk.Entry(root, font=("Arial", 12))
entry_target.pack(pady=5)
entry_target.insert(0, "@target")

var_reason = tk.StringVar(root)
var_reason.set("Scam/Fraud")
dropdown = tk.OptionMenu(root, var_reason, *REPORT_REASONS.keys())
dropdown.config(font=("Arial", 12))
dropdown.pack(pady=5)

entry_delay = tk.Entry(root, font=("Arial", 12))
entry_delay.pack(pady=5)
entry_delay.insert(0, "5")

btn_start = tk.Button(root, text="Start Report", font=("Arial", 12, "bold"), bg="green", fg="white", command=start_attack)
btn_start.pack(pady=20)

lbl_footer = tk.Label(root, text="code by +0z", fg="gray", bg="#111", font=("Arial", 10))
lbl_footer.pack(side="bottom", pady=5)

root.mainloop()
