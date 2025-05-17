
import keyboard
import threading
import time

running = False
key_to_press = None

def auto_press():
    global running, key_to_press
    while True:
        if running and key_to_press:
            keyboard.press_and_release(key_to_press)
            time.sleep(0.05)  # delay 50ms

def on_key_event(e):
    global running, key_to_press
    if e.name in ['e', 'y', 'f'] and not running:
        key_to_press = e.name
        running = True
        print(f"Tự động nhấn '{key_to_press.upper()}' bắt đầu.")
    elif e.name == 'space':
        if running:
            print(f"Dừng tự động nhấn '{key_to_press.upper()}'.")
        running = False
        key_to_press = None

if __name__ == "__main__":
    print("Nhấn E, Y hoặc F để bắt đầu tự động nhấn. Nhấn Space để dừng.")
    threading.Thread(target=auto_press, daemon=True).start()
    keyboard.on_press(on_key_event)
    keyboard.wait()  # chạy vô hạn
