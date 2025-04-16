
import subprocess
import winreg

def get_bios_key():
    try:
        result = subprocess.run(
            ["powershell", "-Command", "(Get-CimInstance -ClassName SoftwareLicensingService).OA3xOriginalProductKey"],
            capture_output=True, text=True, shell=True
        )
        key = result.stdout.strip()
        if key:
            return key
        else:
            return "No BIOS key found."
    except Exception as e:
        return f"Error retrieving BIOS key: {e}"

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
    print("📌 Windows Product Key from BIOS:")
    print("---------------------------------")
    print(get_bios_key())

    print("\n📦 Microsoft Office Product Info:")
    print("---------------------------------")
    office_keys = get_office_keys()
    if not office_keys:
        print("No Office keys found.")
    else:
        for product, pid in office_keys:
            print(f"{product} - {pid}")

    input("\nPress Enter to exit...")

if __name__ == "__main__":
    main()
