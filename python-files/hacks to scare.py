import pyautogui
import random
import time
import tkinter as tk
from tkinter import messagebox
import threading
import os
import platform

# Global variable to track if the user can control the mouse
user_can_control_mouse = False
files_opened = 0

def nudge_mouse():
    """
    Slightly nudges the mouse in a random direction periodically, only if the user has control.
    """
    global user_can_control_mouse
    screen_width, screen_height = pyautogui.size()
    try:
        while True:
            if user_can_control_mouse:
                x_offset = random.randint(-30, 30)
                y_offset = random.randint(-30, 30)
                current_x, current_y = pyautogui.position()
                new_x = max(0, min(current_x + x_offset, screen_width))
                new_y = max(0, min(current_y + y_offset, screen_height))
                pyautogui.move(new_x - current_x, new_y - current_y, duration=0.3)
            time.sleep(random.uniform(5, 10))  # Less frequent nudges
    except Exception as e:
        print(f"Mouse nudging stopped due to error: {e}")

def ghost_click():
    """
    Performs random, brief mouse clicks, only if the user has control.
    """
    global user_can_control_mouse
    screen_width, screen_height = pyautogui.size()
    try:
        while True:
            if user_can_control_mouse:
                x = random.randint(0, screen_width - 1)
                y = random.randint(0, screen_height - 1)
                pyautogui.moveTo(x, y, duration=0.5)  # Move to a random spot first
                pyautogui.click()  # Perform a ghost click
            time.sleep(random.uniform(7, 15))  # Inconsistent timing
    except Exception as e:
        print(f"Ghost clicking stopped due to error: {e}")

def type_random_characters():
    """
    Types random characters into the currently active window, only if the user has control.
    """
    global user_can_control_mouse
    try:
        while True:
            if user_can_control_mouse:
                random_char = chr(random.randint(33, 64))  # Limit to punctuation and symbols
                pyautogui.typewrite(random_char, interval=0.3)
            time.sleep(random.uniform(7, 12))  # Less frequent typing
    except Exception as e:
        print(f"Random typing stopped due to error: {e}")

def volume_fluctuations():
    """
    Randomly adjusts the system volume, only if the user has control.
    """
    global user_can_control_mouse
    try:
        while True:
            if user_can_control_mouse:
                volume_change = random.randint(-5, 5)
                current_volume = pyautogui.getVolume()
                if current_volume is not None:
                    new_volume = max(0, min(1, current_volume + volume_change / 100))
                    pyautogui.setVolume(new_volume)
            time.sleep(random.uniform(8, 16))  # Less frequent changes
    except Exception as e:
        print(f"Volume fluctuations stopped due to error: {e}")

def show_message(message):
    """
    Displays a message in a pop-up window.
    """
    root = tk.Tk()
    root.withdraw()  # Hide the main window
    messagebox.showinfo("Attention!", message)

def crazy_mouse():
    """
    Moves the mouse cursor randomly across the screen.
    """
    screen_width, screen_height = pyautogui.size()

    start_time = time.time()
    try:
        while time.time() - start_time < 5:  # Run for 5 seconds
            # Generate random coordinates
            x = random.randint(0, screen_width - 1)
            y = random.randint(0, screen_height - 1)

            # Move the mouse to the random coordinates
            pyautogui.moveTo(x, y, duration=0.01)  # Faster movement

            # Add a small delay
            time.sleep(0.01)

    except Exception as e:
        print(f"Mouse madness stopped due to error: {e}")

def open_random_files():
    """
    Opens a file explorer window and navigates and opens random files, then unlocks the mouse.
    """
    global user_can_control_mouse, files_opened
    user_can_control_mouse = False  # Disable user control initially

    # Open a file explorer window
    if platform.system() == "Windows":
        os.system("explorer")
    elif platform.system() == "Darwin":  # macOS
        os.system("open .")
    else:
        print("Unsupported operating system.")
        return

    time.sleep(2)  # Give the file explorer time to open into fullscreen mode

    try:
        for _ in range(2):  # Open two files
            # Get current mouse position for smooth movement
            current_x, current_y = pyautogui.position()
            screen_width, screen_height = pyautogui.size()

            # Move to a random location in the file explorer window
            x = random.randint(50, min(500, screen_width - 50))  # Stay within reasonable bounds
            y = random.randint(50, min(400, screen_height - 50))

            # Smoothly move the mouse
            steps = 50  # Number of steps for smooth motion
            for i in range(steps):
                new_x = int(current_x + (x - current_x) * i / steps)
                new_y = int(current_y + (y - current_y) * i / steps)
                pyautogui.moveTo(new_x, new_y, duration=0.02)
            time.sleep(0.5)  # Small pause before click

            pyautogui.doubleClick()  # Open the file
            files_opened += 1
            time.sleep(3)  # Give time for file to open before next action

    except Exception as e:
        print(f"File opening sequence stopped due to error: {e}")
    finally:
        user_can_control_mouse = True  # Re-enable user control

if __name__ == "__main__":
    # First message
    show_message("Hello!")

    # Second message
    show_message("I am your king now.")

    # Third message
    show_message("You don’t agree?")

    # Fourth message
    show_message("Too bad because I can do things like this.")

    crazy_mouse()

    # Fifth message
    show_message("You better not cross the line with me, I can do far worse you know.")

    # Sixth message
    show_message("Now I will live here, goodbye.")

    open_random_files()

    print("Prank complete!")
