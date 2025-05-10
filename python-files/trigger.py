import os
import time
import math
import threading
import random
from PIL import ImageGrab
from inference_sdk import InferenceHTTPClient

try:
    import win32api
    import win32con
except ImportError:
    win32api = None
    win32con = None


screenshot_interval = 1 / 240  
screenshot_name = "latest_screenshot.png"
api_key = "IUIeX6ZqdYk6kPVZWAAn"
model_id = "fortnite-yolov8-aimbot/2"
screen_width, screen_height = 1920, 1080


aim_key = 'shift'
circle_radius = 200
jitter_amount = 2  
confidence_threshold = 50
sensitivity_multiplier = 2  
chill_factor = 0.3  


print("Loading Roboflow client...")
CLIENT = InferenceHTTPClient(
    api_url="https://serverless.roboflow.com",
    api_key=api_key
)
print("Roboflow client loaded.")


predictions = []
current_target = None


def is_aim_key_pressed():
    """Check if the Shift key is being held down"""
    return win32api.GetAsyncKeyState(0x10) & 0x8000 != 0

def move_mouse_smooth(dx, dy):
    """Move the mouse smoothly and quickly to the given coordinates"""
    try:
        dx = int(dx * sensitivity_multiplier * chill_factor)
        dy = int(dy * sensitivity_multiplier * chill_factor)
        win32api.mouse_event(win32con.MOUSEEVENTF_MOVE, dx, dy, 0, 0)
        print(f"[AIMBOT] Moving by: ({dx}, {dy})")
    except Exception as e:
        print(f"Error in smooth mouse movement: {e}")

def jitter_mouse():
    """Jitter the mouse slightly to ensure hit registration"""
    for _ in range(3):  
        jitter_x = random.randint(-jitter_amount, jitter_amount)
        jitter_y = random.randint(-jitter_amount, jitter_amount)
        move_mouse_smooth(jitter_x, jitter_y)
        time.sleep(0.005)  
    print(f"[AIMBOT] Jittered around the target.")

def click():
    """Simulate a left mouse click"""
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
    time.sleep(0.01)  
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
    print("[TRIGGER BOT] Clicked!")

def take_screenshot():
    bbox = (
        screen_width // 2 - circle_radius,
        screen_height // 2 - circle_radius,
        screen_width // 2 + circle_radius,
        screen_height // 2 + circle_radius
    )
    screenshot = ImageGrab.grab(bbox)
    screenshot.save(screenshot_name)

def detect_objects(image_path):
    try:
        result = CLIENT.infer(image_path, model_id=model_id)
        detections = result.get("predictions", [])
        filtered = [p for p in detections if p['confidence'] * 100 >= confidence_threshold]
        return filtered
    except Exception as e:
        print(f"Detection error: {e}")
        return []

def aim_at_target(target):
    target_x, target_y = target
    current_x, current_y = win32api.GetCursorPos()
    dx = target_x - current_x
    dy = target_y - current_y

    
    move_mouse_smooth(dx, dy)

def detection_loop():
    global predictions
    while True:
        start_time = time.time()
        take_screenshot()
        predictions = detect_objects(screenshot_name)

        if predictions:
            for obj in predictions:
                x = int(obj['x'])
                y = int(obj['y'])
                confidence = obj['confidence'] * 100
                print(f"[DETECTED] {obj['class']} at ({x}, {y}) with confidence {confidence:.1f}%")
        else:
            print("[NO TARGET] No valid detection")

        
        elapsed = time.time() - start_time
        time.sleep(max(0, screenshot_interval - elapsed))

def aimbot_loop():
    global predictions, current_target
    while True:
        if is_aim_key_pressed():
            
            if current_target is None:
                if predictions:
                    current_target = min(predictions, key=lambda p: math.hypot(
                        p['x'] - circle_radius, p['y'] - circle_radius))
                    print(f"[AIMBOT] Locked onto new target: {current_target['class']}")
                    click()

            
            if current_target:
                relative_x = current_target['x']
                relative_y = current_target['y']
                fov_left = (screen_width // 2) - circle_radius
                fov_top = (screen_height // 2) - circle_radius
                target_x = fov_left + relative_x
                target_y = fov_top + relative_y

                print(f"[AIMBOT] Sticking to target at: ({target_x}, {target_y})")
                aim_at_target((int(target_x), int(target_y)))

                
                if not any(
                    abs(p['x'] - relative_x) < 20 and abs(p['y'] - relative_y) < 20 
                    for p in predictions
                ):
                    print("[AIMBOT] Lost target, searching for new one.")
                    current_target = None
            time.sleep(0.001)
        else:
            if current_target:
                print(f"[AIMBOT] Released target: {current_target['class']}")
            current_target = None
            time.sleep(0.01)


print("Starting high-speed, stable aimbot (240 FPS)...")
threading.Thread(target=detection_loop, daemon=True).start()
threading.Thread(target=aimbot_loop, daemon=True).start()

try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("Stopping script.")
