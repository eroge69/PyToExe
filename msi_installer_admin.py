import os
import sys
import subprocess

def is_admin():
    try:
        return os.getuid() == 0
    except AttributeError:
        import ctypes
        return ctypes.windll.shell32.IsUserAnAdmin() != 0

if not is_admin():
    script = os.path.abspath(sys.argv[0])
    params = ' '.join([script] + sys.argv[1:])
    subprocess.run(['powershell', '-Command', f'Start-Process python -ArgumentList \'"{params}"\' -Verb runAs'])
    sys.exit()

# ------------ Silent MSI Installer ------------
import time

msi_file = "setup.msi"
msi_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), msi_file)

try:
    subprocess.run(["msiexec", "/i", my.msi, "/quiet", "/norestart"], check=True)
    print("✅ MSI installed successfully (Admin mode)")
except subprocess.CalledProcessError as e:
    print("❌ Installation failed!")
    print(e)

time.sleep(2)
