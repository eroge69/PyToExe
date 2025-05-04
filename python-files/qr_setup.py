
import os
import subprocess
import sys
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from time import sleep

# Gerekli pip modülünü yükle
def install_package(package):
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])

try:
    from selenium import webdriver
except ImportError:
    print("[!] selenium yüklü değil. Kuruluyor...")
    install_package("selenium")

# Session klasörü oluştur
SESSIONS_DIR = "sessions"
os.makedirs(SESSIONS_DIR, exist_ok=True)

# Kaç tane profil olduğunu kontrol et
existing = [d for d in os.listdir(SESSIONS_DIR) if os.path.isdir(os.path.join(SESSIONS_DIR, d))]
new_profile_id = len(existing) + 1
new_profile_path = os.path.join(SESSIONS_DIR, f"profile_{new_profile_id}")

print(f"[+] Yeni profil oluşturuluyor: {new_profile_path}")

# Chrome options ayarları
options = Options()
options.add_argument(f"--user-data-dir={new_profile_path}")
options.add_argument("--profile-directory=Default")
options.add_argument("--disable-extensions")
options.add_argument("--start-maximized")

# Chrome driver çalıştır
driver = webdriver.Chrome(options=options)
driver.get("https://web.whatsapp.com")

print("\n[!] Lütfen QR kodu tarat ve giriş yap.")
sleep(30)  # User needs time to scan the QR code
driver.quit()
