
import cv2
import numpy as np
import pyautogui
import time

# إعدادات
attack_key = 'f1'     # زر هجوم مهارة السكتر (تعديله حسب مكان المهارة)
loot_key = 'x'        # زر مخصص للوت (تقدر تعدله)
screenshot_region = None  # كامل الشاشة

# اللون المستهدف - لون دم الوحوش
lower_red = np.array([0, 0, 180])
upper_red = np.array([80, 80, 255])

def find_enemy_locations():
    screenshot = pyautogui.screenshot(region=screenshot_region)
    frame = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)

    mask = cv2.inRange(frame, lower_red, upper_red)
    contours, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    targets = []
    for c in contours:
        if cv2.contourArea(c) > 50:
            M = cv2.moments(c)
            if M["m00"] != 0:
                cx = int(M["m10"] / M["m00"])
                cy = int(M["m01"] / M["m00"])
                targets.append((cx, cy))

    return targets

def move_and_attack_all(targets):
    screen_w, screen_h = pyautogui.size()
    center_x, center_y = screen_w // 2, screen_h // 2

    # تحريك بسيط نحو أول هدف
    if targets:
        x, y = targets[0]
        dx = x - center_x
        dy = y - center_y

        if abs(dx) > 10:
            pyautogui.keyDown('right' if dx > 0 else 'left')
            time.sleep(0.1)
            pyautogui.keyUp('right' if dx > 0 else 'left')
        if abs(dy) > 10:
            pyautogui.keyDown('down' if dy > 0 else 'up')
            time.sleep(0.1)
            pyautogui.keyUp('down' if dy > 0 else 'up')

    # تنفيذ ضربة سكتر لكل الوحوش الظاهرة
    pyautogui.press(attack_key)

    # لوت
    pyautogui.press(loot_key)

print("Scatter Bot started. Press Ctrl+C to stop.")

try:
    while True:
        enemies = find_enemy_locations()
        if enemies:
            move_and_attack_all(enemies)
        time.sleep(0.3)
except KeyboardInterrupt:
    print("Bot stopped.")
