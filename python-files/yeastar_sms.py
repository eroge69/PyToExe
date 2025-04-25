import requests

# Yeastar TG1600 API məlumatları
IP = "192.168.12.77"
USERNAME = "apiuser"
PASSWORD = "@dmin123"

# Göndəriləcək nömrə və mesaj
TO_NUMBER = "+994552101520"
MESSAGE = "Salam, bu Yeastar TG1600 üzərindən test mesajıdır"

def send_sms(ip, username, password, number, message):
    url = f"http://{ip}/cgi-bin/sms_send.cgi"
    payload = {
        "username": username,
        "password": password,
        "port": "1",           # Əgər bir neçə port varsa, uyğun port nömrəsini qeyd edin
        "number": number,
        "message": message,
        "encode": "yes"        # Mesajı UTF-8 kimi kodlayır
    }

    try:
        response = requests.get(url, params=payload, timeout=10)
        if "Message has been sent" in response.text:
            print(f"[OK] Mesaj göndərildi: {number}")
        elif "Login failed" in response.text:
            print("[Xəta] Login uğursuz oldu. İstifadəçi adı və şifrəni yoxlayın.")
        else:
            print(f"[Xəta] Cavab: {response.text}")
    except requests.exceptions.RequestException as e:
        print(f"[Xəta] Sorğu zamanı problem yarandı: {e}")

# SMS göndər
send_sms(IP, USERNAME, PASSWORD, TO_NUMBER, MESSAGE)
