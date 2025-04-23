
import os
import shutil
import string

def print_logo():
    print("=" * 50)
    print(" " * 15 + "Cursed Booster")
    print("=" * 50)

def list_drives():
    drives = [f"{d}:\\" for d in string.ascii_uppercase if os.path.exists(f"{d}:\\")]
    for i, drive in enumerate(drives):
        print(f"{i + 1}. {drive}")
    return drives

def get_user_drive(drives):
    while True:
        try:
            choice = int(input("Dota 2 در کدام درایو نصب شده است؟ شماره مربوط به درایو را وارد کن: "))
            if 1 <= choice <= len(drives):
                return drives[choice - 1]
            else:
                print("عدد نامعتبر. دوباره امتحان کن.")
        except ValueError:
            print("لطفاً فقط عدد وارد کن.")

def delete_paths(base_drive):
    relative_paths = [
        r"SteamLibrary\steamapps\common\dota 2 beta\game\dota\maps\backgrounds",
        r"SteamLibrary\steamapps\common\dota 2 beta\game\dota\models\heroes"
    ]

    for rel_path in relative_paths:
        full_path = os.path.join(base_drive, rel_path)
        if os.path.exists(full_path):
            shutil.rmtree(full_path)
            print(f"[✓] مسیر حذف شد: {full_path}")
        else:
            print(f"[!] مسیر پیدا نشد: {full_path}")

if __name__ == "__main__":
    print_logo()
    drives = list_drives()
    selected_drive = get_user_drive(drives)
    delete_paths(selected_drive)
    print("\nهمه مسیرهای مورد نظر بررسی و در صورت وجود حذف شدند.")
