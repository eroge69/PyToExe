# user_validator.py

import requests
import os
import json
import uuid
import hashlib
from tqdm import tqdm
from colorama import init, Fore

init(autoreset=True)

LOGIN_FILE = "login.json"
USED_KEYS_FILE = "used_keys.json"

def splash_screen():
    print(Fore.MAGENTA + "\n" + "=" * 60)
    print(Fore.CYAN + "\n██████╗ ███╗   ██╗██╗   ██╗███████╗██╗   ██╗███████╗████████╗")
    print(Fore.CYAN + "██╔══██╗████╗  ██║██║   ██║██╔════╝██║   ██║██╔════╝╚══██╔══╝")
    print(Fore.CYAN + "██████╔╝██╔██╗ ██║██║   ██║███████╗██║   ██║███████╗   ██║")
    print(Fore.CYAN + "██╔═══╝ ██║╚██╗██║██║   ██║╚════██║██║   ██║╚════██║   ██║")
    print(Fore.CYAN + "██║     ██║ ╚████║╚██████╔╝███████║╚██████╔╝███████║   ██║")
    print(Fore.CYAN + "╚═╝     ╚═╝  ╚═══╝  ╚═════╝ ╚══════╝ ╚═════╝ ╚══════╝   ╚═╝")
    print(Fore.CYAN + "                                   Version 1.0.0".center(60))
    print(Fore.YELLOW + "📱 Numverify Phone Validator".center(60))
    print(Fore.CYAN + "=" * 60 + "\n")
    print(Fore.GREEN + "Created by: Mr67iPhone".center(60))
    print(Fore.GREEN + "🔐 Let's go boys!".center(60))
    print(Fore.MAGENTA + "=" * 60 + "\n")

def get_system_id():
    return str(uuid.getnode())

def generate_expected_license(system_id):
    hashed = hashlib.sha256(system_id.encode()).hexdigest()
    return hashed[:16]

def authenticate():
    if os.path.exists(LOGIN_FILE):
        with open(LOGIN_FILE, "r") as file:
            saved_data = json.load(file)

        print(f"{Fore.CYAN}👤 Returning user detected.")
        username = input("Enter your username: ").strip()
        password = input("Enter your password: ").strip()

        if username == saved_data.get("username") and password == saved_data.get("password"):
            print(f"{Fore.GREEN}✅ Login successful!")
            return username, password, saved_data["api_key"]
        else:
            print(f"{Fore.RED}❌ Incorrect credentials.")
            return None, None, None

    print(f"{Fore.CYAN}🔑 First time setup:\n📌 Your System ID is: {get_system_id()}")
    print(f"{Fore.YELLOW}Send this System ID to the admin to receive your license key.\n")

    system_id = get_system_id()
    expected_prefix = generate_expected_license(system_id)

    if not os.path.exists(USED_KEYS_FILE):
        with open(USED_KEYS_FILE, "w") as file:
            json.dump([], file)

    while True:
        license_key = input(f"{Fore.YELLOW}Enter license key provided by admin: ").strip()
        if not license_key.startswith(expected_prefix):
            print(f"{Fore.RED}❌ Invalid license key. It doesn’t match your system.")
            continue

        with open(USED_KEYS_FILE, "r") as file:
            used_keys = json.load(file)

        if license_key in used_keys:
            print(f"{Fore.RED}❌ This license key has already been used!")
            continue

        print(f"{Fore.GREEN}✅ License key verified!")
        break

    username = input("👤 Create your username: ").strip()
    password = input("🔒 Create your password: ").strip()
    api_key = input("🔐 Enter your Numverify API key: ").strip()

    login_data = {
        "username": username,
        "password": password,
        "api_key": api_key
    }

    with open(LOGIN_FILE, "w") as file:
        json.dump(login_data, file)

    used_keys.append(license_key)
    with open(USED_KEYS_FILE, "w") as file:
        json.dump(used_keys, file)

    print(f"{Fore.GREEN}✅ Registration complete!")
    return username, password, api_key

def validate_phone_number(phone_number, api_key):
    phone_number = phone_number.strip().replace(" ", "")
    if not phone_number.startswith("+") or not phone_number[1:].isdigit():
        return {"number": phone_number, "success": False, "error": "Invalid format. Use + followed by country code and number."}

    url = "http://apilayer.net/api/validate"
    params = {
        "access_key": api_key,
        "number": phone_number,
        "format": 1
    }

    try:
        response = requests.get(url, params=params)
        data = response.json()

        if response.status_code != 200 or 'valid' not in data:
            return {"number": phone_number, "success": False, "error": "API error or invalid response."}
        if not data["valid"]:
            return {"number": phone_number, "success": False, "error": "Invalid number."}

        return {
            "number": data["international_format"],
            "success": True,
            "country": data["country_name"],
            "location": data["location"],
            "carrier": data["carrier"] or "Unknown",
            "line_type": data["line_type"]
        }

    except Exception as e:
        return {"number": phone_number, "success": False, "error": str(e)}

def categorize_by_carrier(carrier):
    if not carrier:
        return "others.txt"

    carrier = carrier.lower()
    att_keywords = ["at&t", "att", "cingular", "cricket", "h2o", "straight talk gsm"]
    verizon_keywords = ["verizon", "visible", "xfinity", "total wireless", "straight talk cdma", "cellco"]
    tmobile_keywords = ["t-mobile", "tmobile", "metro", "mint", "ultra mobile", "google fi", "sprint", "t-mobile usa inc"]

    if any(kw in carrier for kw in att_keywords):
        return "att.txt"
    elif any(kw in carrier for kw in verizon_keywords):
        return "verizon.txt"
    elif any(kw in carrier for kw in tmobile_keywords):
        return "tmobile.txt"
    else:
        return "others.txt"

def save_result(filename, content):
    os.makedirs("results", exist_ok=True)
    with open(os.path.join("results", filename), "a") as f:
        f.write(content + "\n")

def main():
    splash_screen()
    username, password, api_key = authenticate()
    if not username:
        return

    print(f"\n{Fore.CYAN}📁 Enter the filename with phone numbers (e.g., leads.txt):")
    filename = input("Filename: ").strip()

    print(f"\n{Fore.CYAN}📌 Choose validation mode:")
    print("1. AT&T only")
    print("2. Verizon only")
    print("3. T-Mobile only")
    print("4. All carriers")
    option = input("Select option (1-4): ").strip()

    try:
        with open(filename, "r") as file:
            numbers = [line.strip() for line in file if line.strip()]

        print(f"\n{Fore.CYAN}🔍 Validating {len(numbers)} phone numbers...\n")

        for number in tqdm(numbers, desc="Progress", unit="number", colour="green"):
            result = validate_phone_number(number, api_key)
            if result["success"]:
                carrier = result['carrier'].lower()
                valid = False

                if option == "1" and any(kw in carrier for kw in ["at&t", "att", "cingular", "cricket", "h2o", "straight talk gsm"]):
                    valid = True
                elif option == "2" and any(kw in carrier for kw in ["verizon", "visible", "xfinity", "total wireless", "straight talk cdma", "cellco"]):
                    valid = True
                elif option == "3" and any(kw in carrier for kw in ["t-mobile", "tmobile", "metro", "mint", "ultra mobile", "google fi", "sprint", "t-mobile usa inc"]):
                    valid = True
                elif option == "4":
                    valid = True

                if valid:
                    line = f"{result['number']} | {result['country']} | {result['carrier']} | {result['line_type']}"
                    save_result(categorize_by_carrier(result['carrier']), line)
                    print(f"{Fore.GREEN}✅ {result['number']} | {Fore.YELLOW}{result['carrier']}")
                else:
                    print(f"{Fore.YELLOW}⚠️  Skipped: {result['number']} is not in selected carrier group.")
            else:
                line = f"{result['number']} | ERROR: {result['error']}"
                save_result("invalid.txt", line)
                print(f"{Fore.RED}❌ {result['number']} | {Fore.YELLOW}ERROR: {result['error']}")

        print(f"\n{Fore.GREEN}✅ Validation complete! Check the 'results' folder.")

    except FileNotFoundError:
        print(f"{Fore.RED}❌ File '{filename}' not found.")
    except Exception as e:
        print(f"{Fore.RED}❌ Error: {str(e)}")

if __name__ == "__main__":
    main()
