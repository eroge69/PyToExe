
import sqlite3
import win32crypt
import json
import os

def get_encrypted_key():
    # User se key input lena
    key = input("Apni encrypted key yahan daalein (For demo, koi bhi string): ")
    return key

def decrypt_cookie(encrypted_value):
    try:
        # Windows DPAPI se decrypt karne ki koshish
        decrypted = win32crypt.CryptUnprotectData(encrypted_value, None, None, None, 0)[1]
        return decrypted.decode('utf-8')
    except Exception as e:
        return None

def cookies_to_json(cookie_path, output_path):
    if not os.path.exists(cookie_path):
        print(f"Cookies file nahi mili: {cookie_path}")
        return

    conn = sqlite3.connect(cookie_path)
    cursor = conn.cursor()
    cursor.execute("SELECT host_key, name, encrypted_value FROM cookies")

    cookies_list = []

    for host_key, name, encrypted_value in cursor.fetchall():
        decrypted_value = decrypt_cookie(encrypted_value)
        if decrypted_value is None:
            decrypted_value = ""
        cookies_list.append({
            "host": host_key,
            "name": name,
            "value": decrypted_value
        })

    conn.close()

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(cookies_list, f, indent=4, ensure_ascii=False)
    print(f"Cookies JSON file ban gayi: {output_path}")

def main():
    # Step 1: Encrypted key mangna (demo purpose)
    key = get_encrypted_key()

    # Step 2: Agar key kuch bhi ho, proceed kar rahe hain (aap yahan validation add kar sakte hain)
    if not key:
        print("Key required hai.")
        return

    # Step 3: Cookies file ka path daalein (default path for Chrome on Windows)
    user = os.getlogin()
    cookie_path = fr"C:\Users\{user}\AppData\Local\Google\Chrome\User Data\Default\Cookies"
    output_path = "cookies_output.json"

    # Step 4: Cookies ko JSON mein convert karna
    cookies_to_json(cookie_path, output_path)

if __name__ == "__main__":
    main()
