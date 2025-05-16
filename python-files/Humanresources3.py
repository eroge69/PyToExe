import subprocess
import time
import os
import sys
import psutil

# Configuration
NUM_WINDOWS = 200
BATCH_SIZE = 20
BATCH_DELAY = 6  # Seconds between batches
WINDOW_DELAY = 0.4  # Delay per window
URL = "about:blank"  # Lightweight page
CHROME_PATH = r"C:\Program Files\Google\Chrome\Application\chrome.exe"  # Adjust if needed

def close_chrome():
    print("Closing all Chrome instances...")
    try:
        chrome_count = 0
        for proc in psutil.process_iter(['name']):
            if proc.info['name'] and proc.info['name'].lower() == 'chrome.exe':
                try:
                    proc.terminate()
                    proc.wait(timeout=3)
                    chrome_count += 1
                except Exception as e:
                    print(f"Error closing Chrome process {proc.pid}: {e}")
        print(f"Closed {chrome_count} Chrome instance(s).")
    except Exception as e:
        print(f"Error during Chrome closure: {e}")

def open_chrome_windows():
    if not os.path.exists(CHROME_PATH):
        print(f"Error: Chrome not found at '{CHROME_PATH}'.")
        sys.exit(1)

    try:
        result = subprocess.run([CHROME_PATH, "--version"], capture_output=True, text=True, check=True)
        print(f"Chrome version: {result.stdout.strip()}")
    except Exception as e:
        print(f"Error: Cannot run Chrome: {e}")
        sys.exit(1)

    print(f"\n=== Chrome Window Stress Test ===")
    print(f"Chrome Path: {CHROME_PATH}")
    print(f"Plan: Open {NUM_WINDOWS} Chrome windows in batches of {BATCH_SIZE}, close, and repeat.")
    print("WARNING: This may CRASH your system or use 10-30 GB of RAM!")
    print("Monitor CPU, RAM, and temps. Press Ctrl+C to stop.")
    print("============================\n")

    cycle_count = 0
    while True:
        cycle_count += 1
        print(f"\n--- Cycle {cycle_count}: Opening {NUM_WINDOWS} windows ---")
        windows_opened = 0
        chrome_processes = []

        try:
            close_chrome()
            time.sleep(2)

            while windows_opened < NUM_WINDOWS:
                for _ in range(min(BATCH_SIZE, NUM_WINDOWS - windows_opened)):
                    try:
                        process = subprocess.Popen(
                            [CHROME_PATH, "--new-window", URL],
                            stdout=subprocess.DEVNULL,
                            stderr=subprocess.DEVNULL,
                            creationflags=subprocess.CREATE_NO_WINDOW
                        )
                        chrome_processes.append(process)
                        windows_opened += 1
                        print(f"Opened window {windows_opened}/{NUM_WINDOWS}")
                        time.sleep(WINDOW_DELAY)
                    except Exception as e:
                        print(f"Error opening window {windows_opened + 1}: {e}")
                        time.sleep(1)

                if windows_opened < NUM_WINDOWS:
                    print(f"Waiting {BATCH_DELAY} seconds before next batch...")
                    time.sleep(BATCH_DELAY)

            print(f"Finished opening {NUM_WINDOWS} windows. Waiting 10 seconds...")
            time.sleep(10)

        except Exception as e:
            print(f"Error in cycle {cycle_count}: {e}")

        print("Closing Chrome windows...")
        close_chrome()
        print("Waiting 5 seconds before next cycle...")
        time.sleep(5)

if __name__ == "__main__":
    try:
        open_chrome_windows()
    except KeyboardInterrupt:
        print("\nStopped by user. Closing Chrome...")
        close_chrome()
        print("Script terminated.")
    except Exception as e:
        print(f"\nFatal error: {e}")
        close_chrome()
        print("Script terminated.")
