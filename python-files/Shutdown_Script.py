import os

def shutdown_computer():
    """Shuts down the computer"""
    os.system("shutdown /s /t 1") # For Windows
    # os.system("sudo shutdown -h now") # For Linux/macOS

shutdown_computer()
