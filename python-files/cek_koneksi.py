
import requests
import time
from datetime import datetime

while True:
    try:
        response = requests.get("https://www.google.com", timeout=5)
        if 200 <= response.status_code < 400:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] [OK] Koneksi berhasil (kode {response.status_code})")
        else:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] [X] Gagal akses (kode {response.status_code})")
    except Exception as e:
        print(f"[{datetime.now().strftime('%H:%M:%S')}] [X] Gagal akses ({e})")
    time.sleep(10)
