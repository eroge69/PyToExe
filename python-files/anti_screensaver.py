
import pyautogui
import time

def prevent_screensaver(interval_seconds=60):
    print("Starte Mausbewegung zum Verhindern des Bildschirmschoners (Strg+C zum Beenden)...")
    while True:
        x, y = pyautogui.position()
        pyautogui.moveTo(x + 1, y)
        pyautogui.moveTo(x, y)
        time.sleep(interval_seconds)

if __name__ == "__main__":
    prevent_screensaver(60)
