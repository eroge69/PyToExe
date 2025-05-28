import hashlib
import base64
import json
import os

SECRET_KEY = "MySuperSecretKey2025"
DATA_FILE = "code_data.json"

def generate_code(client, brand, category, country):
    raw_data = f"{client}:{brand}:{category}:{country}:{SECRET_KEY}"
    hashed = hashlib.sha256(raw_data.encode()).digest()
    encoded = base64.b32encode(hashed).decode('utf-8')
    code = ''.join(filter(str.isalnum, encoded))[:16].upper()
    return code

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return {}

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f)

def store_code_info(client, brand, category, country, data):
    code = generate_code(client, brand, category, country)
    data[code] = {
        "Client": client,
        "Brand": brand,
        "Category": category,
        "Country": country
    }
    save_data(data)
    return code

def verify_code(code, data):
    return data.get(code)

def main():
    print("\n🔐 Secure Code Generator - Internal Tool")
    data = load_data()
    
    while True:
        action = input("\nChoose action: [1] Generate code  [2] Verify code  [q] Quit\n> ").strip()
        
        if action == '1':
            client = input("Client Name: ").strip()
            brand = input("Brand Name: ").strip()
            category = input("Category: ").strip()
            country = input("Country: ").strip()

            code = store_code_info(client, brand, category, country, data)
            print(f"\n✅ Generated Code: {code}")

        elif action == '2':
            code = input("Enter Code to Verify: ").strip().upper()
            info = verify_code(code, data)
            if info:
                print("\n✅ Code Verified! Details:")
                for k, v in info.items():
                    print(f" - {k}: {v}")
            else:
                print("\n❌ No client found for this code.")

        elif action.lower() == 'q':
            break

        else:
            print("Invalid choice, please select 1, 2, or q.")

if __name__ == "__main__":
    main()
