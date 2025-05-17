import subprocess
import time

def open_notepad_multiple_times(num_times=3):
    """Opens Notepad the specified number of times on Windows."""
    if num_times <= 0:
        print("Number of times to open Notepad should be greater than 0.")
        return

    try:
        for i in range(num_times):
            subprocess.Popen(['notepad.exe'])
            print(f"Opened Notepad instance {i+1}")
            time.sleep(0.5) 

    except FileNotFoundError:
        print("Error: notepad.exe not found. Make sure it's in your system's PATH.")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    open_notepad_multiple_times()
