import tkinter as tk
from tkinter import messagebox
import os
import time

# Path to the RivaTuner Statistics Server config directory
RTSS_CONFIG_PATH = r"C:\Program Files (x86)\RivaTuner Statistics Server\Profiles"
RTSS_PROFILE_FILE = "your_game_name.cfg"  # Replace with your actual game profile name.

# Check if the RTSS config path exists
if not os.path.exists(RTSS_CONFIG_PATH):
    print(f"Error: RTSS configuration path '{RTSS_CONFIG_PATH}' does not exist.")
    exit()

def set_fps_limit(fps: int):
    """
    Set the FPS limit by modifying the RTSS profile file.
    """
    profile_file_path = os.path.join(RTSS_CONFIG_PATH, RTSS_PROFILE_FILE)
    
    if not os.path.exists(profile_file_path):
        messagebox.showerror("Error", f"Profile file '{profile_file_path}' does not exist.")
        return

    with open(profile_file_path, 'r') as file:
        lines = file.readlines()

    # Look for the line that controls the FPS limit in the profile file
    found_fps_limit = False
    for i, line in enumerate(lines):
        if "Framerate" in line:  # Find the FPS setting line
            lines[i] = f"Framerate = {fps}\n"
            found_fps_limit = True
            break
    
    if not found_fps_limit:
        messagebox.showerror("Error", "FPS limit setting not found in the profile.")
        return

    # Write the updated lines back to the file
    with open(profile_file_path, 'w') as file:
        file.writelines(lines)

    messagebox.showinfo("Success", f"FPS limit set to {fps}.")

def unlock_fps():
    """
    Unlock FPS by removing the FPS limit from the RTSS profile file.
    """
    profile_file_path = os.path.join(RTSS_CONFIG_PATH, RTSS_PROFILE_FILE)
    
    if not os.path.exists(profile_file_path):
        messagebox.showerror("Error", f"Profile file '{profile_file_path}' does not exist.")
        return

    with open(profile_file_path, 'r') as file:
        lines = file.readlines()

    # Look for the line that controls the FPS limit in the profile file
    found_fps_limit = False
    for i, line in enumerate(lines):
        if "Framerate" in line:  # Find the FPS setting line
            lines[i] = "Framerate = 0\n"  # 0 means no FPS limit in RTSS
            found_fps_limit = True
            break

    if not found_fps_limit:
        messagebox.showerror("Error", "FPS limit setting not found in the profile.")
        return

    # Write the updated lines back to the file
    with open(profile_file_path, 'w') as file:
        file.writelines(lines)

    messagebox.showinfo("Success", "FPS unlocked.")

def create_gui():
    """
    Create the Tkinter GUI for setting FPS limit and unlocking FPS.
    """
    root = tk.Tk()
    root.title("FPS Limiter Control")

    # Set the window size
    root.geometry("300x150")

    # Add a label
    label = tk.Label(root, text="Control FPS for Your Game", font=("Arial", 14))
    label.pack(pady=10)

    # Button to set FPS to 35
    set_fps_button = tk.Button(root, text="Set FPS to 35", width=20, command=lambda: set_fps_limit(35))
    set_fps_button.pack(pady=10)

    # Button to unlock FPS
    unlock_fps_button = tk.Button(root, text="Unlock FPS", width=20, command=unlock_fps)
    unlock_fps_button.pack(pady=10)

    # Start the Tkinter main loop
    root.mainloop()

if __name__ == "__main__":
    create_gui()
