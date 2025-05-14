import pyautogui
import time
import requests
from pynput.mouse import Controller as MouseController
from pynput.keyboard import Controller as KeyboardController

BOT_TOKEN = "YOUR_BOT_TOKEN_HERE"
CHAT_ID = "YOUR_CHAT_ID_HERE"

mouse = MouseController()
keyboard = KeyboardController()

def lock_input():
    print("🚫 Locking keyboard & mouse. Send 'unlock' in Telegram to release.")
    while True:
        try:
            res = requests.get(f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates").json()
            if "result" in res:
                messages = res["result"]
                for msg in messages[::-1]:
                    if str(msg["message"]["chat"]["id"]) == CHAT_ID:
                        text = msg["message"].get("text", "").lower()
                        if "unlock" in text:
                            print("✅ Unlock signal received. Releasing input.")
                            return
            # Keep interfering with input
            mouse.position = (0, 0)
            keyboard.press(' ')
            keyboard.release(' ')
            time.sleep(0.5)
        except Exception as e:
            print("Error:", e)

lock_input()
