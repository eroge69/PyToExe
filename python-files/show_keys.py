
import os
import sys
import winreg
from ctypes import windll, create_string_buffer

def decode_product_key(digital_product_id):
    key_chars = "BCDFGHJKMPQRTVWXY2346789"
    key = ''
    is_win8_or_later = digital_product_id[66] // 6 & 1
    key_offset = 52

    if is_win8_or_later:
        return "Key not decodable (Windows 8+ with encrypted key)"

    decoded_chars = []
    for i in range(25):
        current = 0
        for j in range(14, -1, -1):
            current = current * 256
            current += digital_product_id[j + key_offset]
            digital_product_id[j + key_offset] = current // 24
            current = current % 24
        decoded_chars.insert(0, key_chars[current])

    for i in range(5, 25, 6):
        decoded_chars.insert(i, '-')
    return ''.join(decoded_chars)

def get_windows_key():
    try:
        key_path = r"SOFTWARE\Microsoft\Windows NT\CurrentVersion"
        reg_key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, key_path)
        value, _ = winreg.QueryValueEx(reg_key, "DigitalProductId")
        return decode_product_key(bytearray(value))
    except Exception as e:
        return f"Error retrieving Windows key: {e}"

def get_office_keys():
    office_versions = ["16.0", "15.0", "14.0", "12.0"]
    base_path = r"SOFTWARE\Microsoft\Office\{0}\Registration"
    results = []
    for version in office_versions:
        try:
            path = base_path.format(version)
            reg_key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, path)
            i = 0
            while True:
                try:
                    subkey_name = winreg.EnumKey(reg_key, i)
                    subkey = winreg.OpenKey(reg_key, subkey_name)
                    product_name, _ = winreg.QueryValueEx(subkey, "ProductName")
                    pid, _ = winreg.QueryValueEx(subkey, "PID")
                    results.append((product_name, pid))
                    i += 1
                except OSError:
                    break
        except FileNotFoundError:
            continue
    return results

def main():
    print("Windows Product Key:")
    print("--------------------")
    print(get_windows_key())
    print("\nOffice Product Info:")
    print("---------------------")
    office_keys = get_office_keys()
    if not office_keys:
        print("No Office keys found")
    else:
        for product, pid in office_keys:
            print(f"{product} - {pid}")

    input("\nPress Enter to exit...")

if __name__ == "__main__":
    main()
