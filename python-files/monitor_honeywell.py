import time
import pygetwindow as gw
import pyautogui
import numpy as np
import winsound
import tkinter as tk
from PIL import Image

def find_honeywell_window():
    windows = gw.getWindowsWithTitle('Honeywell')
    if windows:
        return windows[0]
    return None

def capture_screenshot(window):
    window.activate()
    screenshot = pyautogui.screenshot(region=(window.left, window.top, window.width, window.height))
    return screenshot

def detect_yellow(image):
    image = image.convert('HSV')
    np_image = np.array(image)
    h, s, v = np_image[:,:,0], np_image[:,:,1], np_image[:,:,2]
    yellow_mask = ((h >= 20) & (h <= 30)) & (s >= 100) & (v >= 100)
    return np.count_nonzero(yellow_mask) > 0

def main():
    # Δημιουργία παραθύρου για ένδειξη λειτουργίας
    root = tk.Tk()
    root.title("Honeywell Monitor")
    label = tk.Label(root, text="Το πρόγραμμα παρακολουθεί το παράθυρο Honeywell.")
    label.pack()
    root.update()

    previous_yellow_detected = False
    while True:
        window = find_honeywell_window()
        if window:
            screenshot = capture_screenshot(window)
            yellow_detected = detect_yellow(screenshot)
            if yellow_detected and not previous_yellow_detected:
                winsound.Beep(1000, 5000)
            previous_yellow_detected = yellow_detected
        root.update()
        time.sleep(5)

if __name__ == "__main__":
    main()
