import os
import tkinter as tk
from tkinter import messagebox
import psutil
import pyautogui
import threading
import time
import subprocess

# Recoil control state
recoil_enabled = False

def boost_fps():
    # Kill common background apps to free system resources
    for proc in psutil.process_iter():
        try:
            if proc.name().lower() in ["onedrive.exe", "discord.exe", "chrome.exe"]:
                proc.kill()
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    os.system("echo FPS Boost Applied.")
    messagebox.showinfo("FPS Boost", "Background tasks cleared to improve FPS.")

def apply_msi_optimizations():
    # Check if MSI software (MSI Center or Dragon Center) is installed
    msi_software_path = "C:\\Program Files\\MSI\\Dragon Center\\DragonCenter.exe"  # Adjust path if using MSI Center
    if os.path.exists(msi_software_path):
        subprocess.run([msi_software_path, "optimize"])  # Run optimization through MSI software
        messagebox.showinfo("MSI Optimizer", "MSI Dragon Center optimizations applied.")
    else:
        messagebox.showwarning("MSI Software Not Found", "MSI Dragon Center or MSI Center not installed.")

def apply_emulator_optimizations():
    # Example: Optimize LDPlayer config file (can be adjusted for other emulators)
    ldplayer_config_path = os.path.expanduser("~\\LDPlayer\\config\\config.ini")
    if os.path.exists(ldplayer_config_path):
        with open(ldplayer_config_path, 'r') as file:
            lines = file.readlines()
        with open(ldplayer_config_path, 'w') as file:
            for line in lines:
                if "fps" in line.lower():
                    file.write("fps=90\n")  # Set FPS to 90
                elif "dpi" in line.lower():
                    file.write("dpi=320\n")  # Adjust DPI setting
                else:
                    file.write(line)
        messagebox.showinfo("Emulator Optimization", "LDPlayer config optimized for better performance.")
    else:
        messagebox.showwarning("File Not Found", "LDPlayer config file not found.")

def enable_recoil_controller():
    global recoil_enabled
    recoil_enabled = True
    def recoil_loop():
        while recoil_enabled:
            if pyautogui.mouseDown(button='left'):
                pyautogui.moveRel(0, 2, duration=0.02)  # Smooth recoil compensation
            time.sleep(0.01)
    threading.Thread(target=recoil_loop, daemon=True).start()
    messagebox.showinfo("Recoil Control", "Recoil control enabled to help maintain aim stability.")

def disable_recoil_controller():
    global recoil_enabled
    recoil_enabled = False
    messagebox.showinfo("Recoil Control", "Recoil control disabled.")

def optimize_sensitivity():
    # Adjust mouse sensitivity via registry (Windows only)
    os.system("reg add \"HKCU\\Control Panel\\Mouse\" /v MouseSensitivity /t REG_SZ /d 12 /f")
    messagebox.showinfo("Sensitivity Optimized", "Mouse sensitivity set for better aim control.")

def provide_headshot_training_tips():
    # Display training tips and focus areas for improving headshots
    training_tips = """
    Headshot Training Tips:
    1. Keep your crosshair at head level while moving.
    2. Practice in the training ground focusing on headshots.
    3. Adjust your mouse sensitivity to your personal preference (not too high or low).
    4. Try to aim ahead of the target if they're moving.
    5. Utilize the best gun for headshots (like M1014 or AK).
    """
    messagebox.showinfo("Headshot Training Tips", training_tips)

def create_gui():
    root = tk.Tk()
    root.title("Free Fire Optimizer Panel")
    root.geometry("500x600")
    root.config(bg="#2f2f2f")  # Background color

    # Title Label
    title_label = tk.Label(root, text="Free Fire Optimizer Panel", font=("Arial", 18, "bold"), fg="#ffcc00", bg="#2f2f2f")
    title_label.pack(pady=20)

    # Styling the buttons
    button_style = {
        "font": ("Arial", 12, "bold"),
        "fg": "white",
        "bg": "#00aaff",
        "activebackground": "#0088cc",
        "relief": "flat",
        "width": 25,
        "height": 2
    }

    # FPS Boost Button
    fps_button = tk.Button(root, text="Boost FPS", command=boost_fps, **button_style)
    fps_button.pack(pady=10)

    # Optimize Emulator Button
    emulator_button = tk.Button(root, text="Optimize Emulator", command=apply_emulator_optimizations, **button_style)
    emulator_button.pack(pady=10)

    # Recoil Control Buttons
    recoil_button = tk.Button(root, text="Enable Recoil Control", command=enable_recoil_controller, **button_style)
    recoil_button.pack(pady=10)

    recoil_off_button = tk.Button(root, text="Disable Recoil Control", command=disable_recoil_controller, **button_style)
    recoil_off_button.pack(pady=10)

    # Sensitivity Optimizer Button
    sensitivity_button = tk.Button(root, text="Optimize Sensitivity", command=optimize_sensitivity, **button_style)
    sensitivity_button.pack(pady=10)

    # MSI Optimizer Button
    msi_button = tk.Button(root, text="Apply MSI Optimizations", command=apply_msi_optimizations, **button_style)
    msi_button.pack(pady=10)

    # Headshot Training Tips Button
    training_tips_button = tk.Button(root, text="Headshot Training Tips", command=provide_headshot_training_tips, **button_style)
    training_tips_button.pack(pady=10)

    # Footer Label
    footer_label = tk.Label(root, text="* Safe & Legal Tool | Emulator Support Only *", fg="gray", bg="#2f2f2f", font=("Arial", 8))
    footer_label.pack(pady=20)

    root.mainloop()

if __name__ == "__main__":
    create_gui()
