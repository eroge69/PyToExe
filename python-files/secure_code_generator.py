import hashlib
import base64
import random
import string

# Secret key for encoding/decoding (keep this private!)
SECRET_KEY = "MySuperSecretKey2025"

# Generate a secure-looking code
def generate_code(client, brand, category, country):
    raw_data = f"{client}:{brand}:{category}:{country}:{SECRET_KEY}"
    hashed = hashlib.sha256(raw_data.encode()).digest()
    encoded = base64.b32encode(hashed).decode('utf-8')
    # Remove padding and keep alphanumeric only
    code = ''.join(filter(str.isalnum, encoded))[:16].upper()
    return code

# Decode function (mock) for your support team
def verify_code(code, client, brand, category, country):
    expected_code = generate_code(client, brand, category, country)
    return expected_code == code

# Main CLI loop
def main():
    print("\n🔐 Secure Code Generator - Internal Tool")
    while True:
        print("\n--- Generate New Code ---")
        client = input("Client Name: ").strip()
        brand = input("Brand Name: ").strip()
        category = input("Category: ").strip()
        country = input("Country: ").strip()

        code = generate_code(client, brand, category, country)
        print(f"\n✅ Generated Code: {code}")

        check = input("\nDo you want to verify this code now? (y/n): ").strip().lower()
        if check == 'y':
            vclient = input("Client Name: ").strip()
            vbrand = input("Brand Name: ").strip()
            vcategory = input("Category: ").strip()
            vcountry = input("Country: ").strip()
            if verify_code(code, vclient, vbrand, vcategory, vcountry):
                print("\n✅ Code verification successful.")
            else:
                print("\n❌ Code verification failed.")

        again = input("\nGenerate another code? (y/n): ").strip().lower()
        if again != 'y':
            break

if __name__ == "__main__":
    main()
