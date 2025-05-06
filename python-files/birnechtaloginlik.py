import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time

# --- Barcha login fayllarni olish ---
def get_account_files(folder):
    return [f for f in os.listdir(folder) if f.endswith('.txt') and not f.startswith('xatoliklar_')]

# --- Fayldan login-parollarni o‘qish ---
def load_accounts(filepath):
    accounts = []
    with open(filepath, 'r') as file:
        for line in file:
            if ',' in line:
                username, password = line.strip().split(',', 1)
                accounts.append({'username': username, 'password': password})
    return accounts

# --- WebDriver sozlash ---
options = webdriver.ChromeOptions()
options.add_argument('--window-size=480,640')

driver = webdriver.Chrome(options=options)
driver.implicitly_wait(10)

# --- Sayt manzili ---
url = "https://login.emaktab.uz/login"

# --- Login fayllar joylashgan papka ---
login_folder = "./loginlar"

account_files = get_account_files(login_folder)

for filename in account_files:
    filepath = os.path.join(login_folder, filename)
    accounts = load_accounts(filepath)

    print(f"\n📂 Fayl: {filename} ({len(accounts)} ta login)")

    for account in accounts:
        driver.get(url)
        time.sleep(3)

        print(f">>> Kirilmoqda: {account['username']}")

        try:
            loginxpath = '/html/body/div/div/div/div/div/form/div[2]/div[3]/div[1]/div[1]/label/input'
            driver.find_element(By.XPATH, loginxpath).send_keys(account["username"])

            passwordxpath = '/html/body/div/div/div/div/div/form/div[2]/div[3]/div[2]/div[1]/label/input'
            driver.find_element(By.XPATH, passwordxpath).send_keys(account["password"])

            kirish = '/html/body/div/div/div/div/div/form/div[2]/div[3]/div[4]/div[1]/input'
            driver.find_element(By.XPATH, kirish).click()
            time.sleep(5)

            if "dashboard" in driver.current_url or "profil" in driver.page_source.lower():
                print(f"[✅] Muvaffaqiyatli login: {account['username']}")
                chiqish = '/html/body/div[3]/div/div[1]/div/div[2]/div[3]/div/form'
                driver.find_element(By.XPATH, chiqish).click()
            else:
                print(f"[❌] Login xato: {account['username']}")
                with open(os.path.join(login_folder, f"xatoliklar_{filename}"), "a") as log_file:
                    log_file.write(account["username"] + "\n")

        except Exception as e:
            print(f"[‼️] Xatolik yuz berdi: {account['username']} => {e}")
            with open(os.path.join(login_folder, f"xatoliklar_{filename}"), "a") as log_file:
                log_file.write(account["username"] + "\n")

driver.quit()
print("\n✅ Barcha fayllar tekshirildi.")
