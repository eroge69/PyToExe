import os
import shutil
import sqlite3
import csv
import subprocess
from pathlib import Path
import time

import win32crypt
from Cryptodome.Cipher import AES
import json

# ====== NASTAVENIA ======
BROWSERS = {
    "Opera GX": {
        "exe": "opera.exe",
        "base": os.path.join(os.getenv("APPDATA"), "Opera Software", "Opera GX Stable")
    },
    "Chrome": {
        "exe": "chrome.exe",
        "base": os.path.join(os.getenv("LOCALAPPDATA"), "Google", "Chrome", "User Data", "Default")
    },
    "Edge": {
        "exe": "msedge.exe",
        "base": os.path.join(os.getenv("LOCALAPPDATA"), "Microsoft", "Edge", "User Data", "Default")
    },
    "Firefox": {
        "exe": "firefox.exe",
        "base": os.path.join(os.getenv("APPDATA"), "Mozilla", "Firefox", "Profiles")
    }
}

DESKTOP = os.path.join(os.getenv("USERPROFILE"), "Desktop")

# ====== VYPNUTIE PREHLIADAČOV ======
print("🛑 Zatváram prehliadače...")
for browser, data in BROWSERS.items():
    subprocess.call(f"taskkill /F /IM {data['exe']} >nul 2>&1", shell=True)

time.sleep(2)

# ====== FUNKCIE NA DEŠIFROVANIE DPAPI ======
def decrypt_value_dpapi(encrypted_value):
    try:
        if encrypted_value[:3] == b'v10' or encrypted_value[:3] == b'v11':
            iv = encrypted_value[3:15]
            payload = encrypted_value[15:]
            key = win32crypt.CryptUnprotectData(b"")[1]
            cipher = AES.new(key, AES.MODE_GCM, iv)
            decrypted = cipher.decrypt(payload)[:-16]
            return decrypted.decode()
        else:
            return win32crypt.CryptUnprotectData(encrypted_value, None, None, None, 0)[1].decode()
    except:
        return ""

# ====== EXPORT COOKIES ======
def export_cookies(browser, db_path):
    if not os.path.exists(db_path):
        print(f"[{browser}] Cookies DB sa nenašla.")
        return
    backup = os.path.join(DESKTOP, f"{browser.replace(' ', '_')}_cookies.db")
    shutil.copyfile(db_path, backup)
    print(f"[{browser}] Cookies DB záloha: {backup}")

    output_csv = os.path.join(DESKTOP, f"{browser.replace(' ', '_')}_cookies.csv")
    try:
        conn = sqlite3.connect(backup)
        cursor = conn.cursor()
        cursor.execute("SELECT host_key, name, path, encrypted_value FROM cookies")

        with open(output_csv, "w", newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(["Host", "Name", "Path", "Value"])
            for host_key, name, path, encrypted_value in cursor.fetchall():
                value = decrypt_value_dpapi(encrypted_value)
                writer.writerow([host_key, name, path, value])
        print(f"[{browser}] Cookies exportované: {output_csv}")
    except Exception as e:
        print(f"[{browser}] Chyba pri cookies: {e}")
    finally:
        conn.close()

# ====== EXPORT HESIEL ======
def export_passwords(browser, login_db_path):
    if not os.path.exists(login_db_path):
        print(f"[{browser}] Login Data DB sa nenašla.")
        return

    backup = os.path.join(DESKTOP, f"{browser.replace(' ', '_')}_passwords.db")
    shutil.copyfile(login_db_path, backup)
    print(f"[{browser}] Login Data záloha: {backup}")

    output_csv = os.path.join(DESKTOP, f"{browser.replace(' ', '_')}_passwords.csv")

    try:
        conn = sqlite3.connect(backup)
        cursor = conn.cursor()
        cursor.execute("SELECT origin_url, username_value, password_value FROM logins")

        with open(output_csv, "w", newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(["URL", "Username", "Password"])
            for url, username, encrypted_password in cursor.fetchall():
                password = decrypt_value_dpapi(encrypted_password)
                writer.writerow([url, username, password])
        print(f"[{browser}] Heslá exportované: {output_csv}")
    except Exception as e:
        print(f"[{browser}] Chyba pri heslách: {e}")
    finally:
        conn.close()

# ====== EXPORT HISTÓRIE ======
def export_history(browser, history_path):
    if not os.path.exists(history_path):
        print(f"[{browser}] History DB sa nenašla.")
        return

    backup = os.path.join(DESKTOP, f"{browser.replace(' ', '_')}_history.db")
    shutil.copyfile(history_path, backup)
    print(f"[{browser}] History DB záloha: {backup}")

    output_csv = os.path.join(DESKTOP, f"{browser.replace(' ', '_')}_history.csv")

    try:
        conn = sqlite3.connect(backup)
        cursor = conn.cursor()
        cursor.execute("SELECT url, title, last_visit_time FROM urls")

        def chrome_time_to_unix(chrome_time):
            # Chrome time is in microseconds since 1601
            return int(chrome_time / 1000000 - 11644473600)

        with open(output_csv, "w", newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(["URL", "Title", "Last Visited (unix)"])
            for url, title, visit_time in cursor.fetchall():
                timestamp = chrome_time_to_unix(visit_time)
                writer.writerow([url, title, timestamp])
        print(f"[{browser}] História exportovaná: {output_csv}")
    except Exception as e:
        print(f"[{browser}] Chyba pri histórii: {e}")
    finally:
        conn.close()

# ====== FIREFOX – cookies a história (iba záloha) ======
def backup_firefox_files():
    base = BROWSERS["Firefox"]["base"]
    if not os.path.exists(base):
        print("[Firefox] Profily sa nenašli.")
        return
    for profile in os.listdir(base):
        profile_path = os.path.join(base, profile)
        for fname in ["cookies.sqlite", "places.sqlite"]:  # places.sqlite obsahuje históriu aj záložky
            full = os.path.join(profile_path, fname)
            if os.path.exists(full):
                dest = os.path.join(DESKTOP, f"Firefox_{profile}_{fname}")
                shutil.copyfile(full, dest)
                print(f"[Firefox] Skopírované: {dest}")

# ====== HLAVNÝ CYKLUS PRE CHROMIUM PREHLIADAČE ======
for browser in ["Opera GX", "Chrome", "Edge"]:
    base = BROWSERS[browser]["base"]
    export_cookies(browser, os.path.join(base, "Network", "Cookies"))
    export_passwords(browser, os.path.join(base, "Login Data"))
    export_history(browser, os.path.join(base, "History"))

# ====== FIREFOX ======
backup_firefox_files()

print("\n✅ Export cookies, hesiel a histórie dokončený. Súbory sú na ploche.")

# ====== EXPORT HESIEL ======
def export_passwords(browser, login_db_path):
    if not os.path.exists(login_db_path):
        print(f"[{browser}] Login Data DB sa nenašla.")
        return

    backup = os.path.join(DESKTOP, f"{browser.replace(' ', '_')}_passwords.db")
    shutil.copyfile(login_db_path, backup)
    print(f"[{browser}] Login Data záloha: {backup}")

    output_csv = os.path.join(DESKTOP, f"{browser.replace(' ', '_')}_passwords.csv")

    try:
        conn = sqlite3.connect(backup)
        cursor = conn.cursor()
        cursor.execute("SELECT origin_url, username_value, password_value FROM logins")

        with open(output_csv, "w", newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(["URL", "Username", "Password"])
            for url, username, encrypted_password in cursor.fetchall():
                password = decrypt_value_dpapi(encrypted_password)
                writer.writerow([url, username, password])
        print(f"[{browser}] Heslá exportované: {output_csv}")
    except Exception as e:
        print(f"[{browser}] Chyba pri heslách: {e}")
    finally:
        conn.close()

# ====== EXPORT HISTÓRIE ======
def export_history(browser, history_path):
    if not os.path.exists(history_path):
        print(f"[{browser}] History DB sa nenašla.")
        return

    backup = os.path.join(DESKTOP, f"{browser.replace(' ', '_')}_history.db")
    shutil.copyfile(history_path, backup)
    print(f"[{browser}] History DB záloha: {backup}")

    output_csv = os.path.join(DESKTOP, f"{browser.replace(' ', '_')}_history.csv")

    try:
        conn = sqlite3.connect(backup)
        cursor = conn.cursor()
        cursor.execute("SELECT url, title, last_visit_time FROM urls")

        def chrome_time_to_unix(chrome_time):
            # Chrome time is in microseconds since 1601
            return int(chrome_time / 1000000 - 11644473600)

        with open(output_csv, "w", newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(["URL", "Title", "Last Visited (unix)"])
            for url, title, visit_time in cursor.fetchall():
                timestamp = chrome_time_to_unix(visit_time)
                writer.writerow([url, title, timestamp])
        print(f"[{browser}] História exportovaná: {output_csv}")
    except Exception as e:
        print(f"[{browser}] Chyba pri histórii: {e}")
    finally:
        conn.close()

# ====== FIREFOX – cookies a história (iba záloha) ======
def backup_firefox_files():
    base = BROWSERS["Firefox"]["base"]
    if not os.path.exists(base):
        print("[Firefox] Profily sa nenašli.")
        return
    for profile in os.listdir(base):
        profile_path = os.path.join(base, profile)
        for fname in ["cookies.sqlite", "places.sqlite"]:  # places.sqlite obsahuje históriu aj záložky
            full = os.path.join(profile_path, fname)
            if os.path.exists(full):
                dest = os.path.join(DESKTOP, f"Firefox_{profile}_{fname}")
                shutil.copyfile(full, dest)
                print(f"[Firefox] Skopírované: {dest}")

# ====== HLAVNÝ CYKLUS PRE CHROMIUM PREHLIADAČE ======
for browser in ["Opera GX", "Chrome", "Edge"]:
    base = BROWSERS[browser]["base"]
    export_cookies(browser, os.path.join(base, "Network", "Cookies"))
    export_passwords(browser, os.path.join(base, "Login Data"))
    export_history(browser, os.path.join(base, "History"))

# ====== FIREFOX ======
backup_firefox_files()

print("\n✅ Export cookies, hesiel a histórie dokončený. Súbory sú na ploche.")
