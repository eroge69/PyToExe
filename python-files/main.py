import os
import subprocess
import shutil
import sys
import winreg
from colorama import init, Fore

# Initialize colorama for colored output
delete_marker = Fore.GREEN + "[ DELETE ]: "
init(autoreset=True)

# 🚨 ขอคีย์จากผู้ใช้ก่อนเริ่มทำงาน
key_input = input(Fore.YELLOW + "[ PLEASE ENTER KEY ] : ")

if key_input.strip() == "BXUN":
    print(Fore.LIGHTGREEN_EX + "The key is correct.")
else:
    print(Fore.RED + "Wrong key!")
    sys.exit(1)  # จบโปรแกรมทันที

def delete_with_log(path):
    """
    Delete a file or directory at the specified path and log the action.
    """
    if os.path.exists(path):
        try:
            if os.path.isfile(path):
                os.remove(path)
            else:
                shutil.rmtree(path, ignore_errors=True)
            print(delete_marker + path)
        except Exception as e:
            print(f"Failed to delete {path}: {e}")

def delete_registry_key(root, sub_key):
    """
    Delete a registry key and its subkeys, and log the action.
    """
    try:
        with winreg.OpenKey(root, sub_key, 0, winreg.KEY_ALL_ACCESS) as key:
            # Delete all subkeys first
            while True:
                try:
                    subkey_name = winreg.EnumKey(key, 0)
                    winreg.DeleteKey(key, subkey_name)
                    print(delete_marker + f"{sub_key}\\{subkey_name}")
                except OSError:
                    break
        # Delete the main key
        winreg.DeleteKey(root, sub_key)
        print(delete_marker + f"{sub_key}")
    except FileNotFoundError:
        print(f"{sub_key} not found (already clean)")
    except Exception as e:
        print(f"Failed to delete {sub_key}: {e}")

# 1️⃣ Clear Recycle Bin
subprocess.call('PowerShell.exe Clear-RecycleBin -Force', shell=True)
print(delete_marker + "Recycle Bin")

# 2️⃣ Clear Temp directories (both user and system-wide)
delete_with_log(os.environ['TEMP'])
delete_with_log(r'C:\Windows\Temp')

# 3️⃣ Clear Recent Files
delete_with_log(os.path.join(os.environ['APPDATA'], 'Microsoft\\Windows\\Recent'))

# 4️⃣ Clear Run History
try:
    with winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                        r'Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\RunMRU',
                        0, winreg.KEY_ALL_ACCESS):
        winreg.DeleteKey(winreg.HKEY_CURRENT_USER,
                         r'Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\RunMRU')
    print(delete_marker + "Run History")
except Exception as e:
    print(f"Failed to clear Run History: {e}")

# ✅ เพิ่มเติม: Clear Registry keys ตามลิสต์
registry_tasks = [
    # AppCompatFlags
    (winreg.HKEY_CURRENT_USER, r'Software\Microsoft\Windows\CurrentVersion\AppCompatFlags\Compatibility Assistant\Store'),
    (winreg.HKEY_CURRENT_USER, r'Software\Microsoft\Windows\CurrentVersion\AppCompatFlags\Compatibility Assistant\Persisted'),
    # MuiCache
    (winreg.HKEY_CURRENT_USER, r'Software\Classes\Local Settings\Software\Microsoft\Windows\Shell\MuiCache'),
    # RunMRU (ซ้ำ เพื่อความชัวร์)
    (winreg.HKEY_CURRENT_USER, r'Software\Microsoft\Windows\CurrentVersion\Explorer\RunMRU'),
    # ComDlg32
    (winreg.HKEY_CURRENT_USER, r'Software\Microsoft\Windows\CurrentVersion\Explorer\ComDlg32'),
    # FeatureUsage\AppSwitched
    (winreg.HKEY_CURRENT_USER, r'Software\Microsoft\Windows\CurrentVersion\Explorer\FeatureUsage\AppSwitched'),
    # FeatureUsage\ShowJumpView
    (winreg.HKEY_CURRENT_USER, r'Software\Microsoft\Windows\CurrentVersion\Explorer\FeatureUsage\ShowJumpView'),
    # FileExts
    (winreg.HKEY_CURRENT_USER, r'Software\Microsoft\Windows\CurrentVersion\Explorer\FileExts'),
    # TypedPaths
    (winreg.HKEY_CURRENT_USER, r'Software\Microsoft\Windows\CurrentVersion\Explorer\TypedPaths'),
    # RecentApps
    (winreg.HKEY_CURRENT_USER, r'Software\Microsoft\Windows\CurrentVersion\Search\RecentApps'),
    # MountPoints2
    (winreg.HKEY_CURRENT_USER, r'Software\Microsoft\Windows\CurrentVersion\Explorer\MountPoints2'),
    # RecentDocs
    (winreg.HKEY_CURRENT_USER, r'Software\Microsoft\Windows\CurrentVersion\Explorer\RecentDocs'),
    # BAM/DAM (HKEY_LOCAL_MACHINE)
    (winreg.HKEY_LOCAL_MACHINE, r'SYSTEM\CurrentControlSet\Services\bam\UserSettings'),
]

for root, key in registry_tasks:
    delete_registry_key(root, key)

# 5️⃣ Clear Open/Save dialog history
delete_with_log(os.path.join(os.environ['APPDATA'], 'Microsoft\\Windows\\Recent'))

# 6️⃣ Clear Prefetch Files
delete_with_log(r'C:\Windows\\Prefetch')

# 7️⃣ Flush DNS Cache
subprocess.call('ipconfig /flushdns', shell=True)
print(delete_marker + "DNS Cache")

# 8️⃣ Clear all Event Logs
logs = subprocess.check_output('wevtutil el', shell=True).decode(errors='ignore').splitlines()
for log in logs:
    try:
        subprocess.call(f'wevtutil cl "{log}"', shell=True)
        print(delete_marker + log)
    except Exception as e:
        print(f"Failed to clear log {log}: {e}")

# 9️⃣ Clear Windows Search Index history
delete_with_log(os.path.join(os.environ['LOCALAPPDATA'],
                             r'Microsoft\\Windows\\Search\\Data\\Applications\\Windows'))

# 🔟 Clear Windows Error Reporting (crash reports)
delete_with_log(r'C:\ProgramData\\Microsoft\\Windows\\WER')

# 11️⃣ Reminder to securely wipe free space
print(Fore.YELLOW + "\n⚠️ คำแนะนำ: หลังจากลบแล้ว แนะนำรันคำสั่งนี้ใน CMD เพื่อเขียนทับพื้นที่ว่าง:")
print(Fore.CYAN + "cipher /w:C")
print(Fore.YELLOW + "(หรือเปลี่ยน C: เป็นไดรฟ์ที่คุณเคยเก็บไฟล์)")
print(Fore.GREEN + "\n✅ เคลียร์เรียบร้อยแล้ว!")
