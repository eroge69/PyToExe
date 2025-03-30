import os
import time
import pyautogui

def press_key(key, delay=1):
    """Tugmani bosish va kutish"""
    pyautogui.press(key)
    time.sleep(delay)

# YouTube video URL
YOUTUBE_URL = "https://www.youtube.com/watch?v=UCqYSQV4Kys&autoplay=1&loop=1"

def start_chrome():
    """Chrome'ni ishga tushirish va sozlash"""
    chrome_path = "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe"
    os.system(f'start "" "{chrome_path}" --mute-audio --app="{YOUTUBE_URL}"')
    time.sleep(10)  # Yuklanish uchun kutish

def restart_video():
    """Videoni faqat tugagandan keyin qayta boshlash"""
    pyautogui.hotkey("ctrl", "r")  # Sahifani yangilash
    time.sleep(10)  # Qayta yuklanish uchun kutish

def main():
    start_chrome()
    while True:
        time.sleep(180)  # Har 3 daqiqada tekshirish (videoning taxminiy uzunligi)
        restart_video()  # Videoni qayta boshlash

if __name__ == "__main__":
    main()
