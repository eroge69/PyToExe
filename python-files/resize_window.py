import pyautogui
import pygetwindow as gw
import time

# Disable the fail-safe (use with caution)
pyautogui.FAILSAFE = False

# Function to click and drag to resize the window
def click_and_drag_to_resize(window_title, click_x, click_y, drag_x, drag_y):
    try:
        # Send Win + Right Arrow to snap the current window to the right
        print("Sending Win + Right Arrow...")
        pyautogui.hotkey('win', 'right')
        time.sleep(0.5)  # Small delay to let the window move

        # Get the window by title
        window = gw.getWindowsWithTitle(window_title)[0]

        # Ensure the window is not minimized and is activated
        if window.isMinimized:
            print("Restoring window...")
            window.restore()
        print("Activating window...")
        window.activate()

        # Get the window's position and size
        window_left, window_top, window_width, window_height = window.left, window.top, window.width, window.height
        print(f"Window position: ({window_left}, {window_top}), size: ({window_width}, {window_height})")

        # Adjust the click and drag positions relative to the window's top-left corner
        click_target_x = window_left + click_x
        click_target_y = window_top + click_y
        drag_target_x = window_left + drag_x
        drag_target_y = window_top + drag_y

        # Print the adjusted positions for debugging
        print(f"Adjusted click position: ({click_target_x}, {click_target_y})")
        print(f"Adjusted drag position: ({drag_target_x}, {drag_target_y})")

        # Ensure the calculated positions are within screen bounds
        screen_width, screen_height = pyautogui.size()
        if (click_target_x > screen_width or click_target_y > screen_height or
            drag_target_x > screen_width or drag_target_y > screen_height):
            print("Calculated positions are out of screen bounds!")
            return

        # Move the mouse to the click position on the window's border (for resizing)
        print(f"Moving mouse to click position...")
        pyautogui.moveTo(click_target_x, click_target_y)

        # Hold down the left mouse button
        pyautogui.mouseDown()
        print(f"Mouse clicked and held at ({click_target_x}, {click_target_y}) on window border.")

        # Drag the mouse to the new target position to resize the window
        pyautogui.moveTo(drag_target_x, drag_target_y)
        print(f"Mouse dragged to ({drag_target_x}, {drag_target_y}) for resizing.")

        # Release the mouse button to complete the resize action
        pyautogui.mouseUp()
        print(f"Mouse button released at ({drag_target_x}, {drag_target_y}) to finish resizing.")

    except IndexError:
        print(f"Window titled '{window_title}' not found.")
    except Exception as e:
        print(f"An error occurred: {e}")

# Adjusted positions: click at (7, 229) and drag to (-429, 263)
click_and_drag_to_resize("Remote Desktop Connection", 7, 229, -429, 263)

# Optional: Wait for a second to observe the action
time.sleep(1)