import pyautogui
import random
import time
import keyboard
import sys

# Configuration
MAX_ALLOWED_Y = 800
CHECK_INTERVAL = 0.01  # seconds
KILL_SWITCH_KEY = 'f12'

def main():
    # Get screen dimensions
    screen_width, screen_height = pyautogui.size()
    
    print(f"Mouse Y-coordinate limiter active (max Y = {MAX_ALLOWED_Y})")
    print(f"Press {KILL_SWITCH_KEY.upper()} to exit...")
    
    try:
        while True:
            # Check for kill switch
            if keyboard.is_pressed(KILL_SWITCH_KEY):
                print("Kill switch activated - exiting...")
                sys.exit(0)
                
            # Get current mouse position
            current_x, current_y = pyautogui.position()
            
            # Check if Y exceeds the limit
            if current_y > MAX_ALLOWED_Y:
                # Generate new random coordinates (Y ≤ MAX_ALLOWED_Y)
                new_x = random.randint(0, screen_width)
                new_y = random.randint(0, MAX_ALLOWED_Y)
                
                # Move mouse to new position
                pyautogui.moveTo(new_x, new_y)
                print(f"Corrected position from ({current_x}, {current_y}) to ({new_x}, {new_y})")
            
            time.sleep(CHECK_INTERVAL)
            
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()