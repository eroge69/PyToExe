import os
import random
import time
import sys

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def fake_binary_stream(duration=5):
    end_time = time.time() + duration
    while time.time() < end_time:
        line = ''.join(random.choice(['0', '1']) for _ in range(100))
        print(line)
        time.sleep(0.05)

def fake_virus():
    clear_screen()
    print("Booting up...")
    time.sleep(2)

    # Display random 0s and 1s
    fake_binary_stream(duration=5)

    clear_screen()
    print("⚠️ VIRUS DETECTED! SYSTEM FAILURE IMMINENT ⚠️")
    time.sleep(2)

    # Black screen
    clear_screen()
    print("\033[30m" + " " * 10000)  # Fill with black text
    time.sleep(2)

    # "Just joking!"
    clear_screen()
    print("\033[92mJUST JOKING! 😂 Your system is safe. 😎")
    time.sleep(5)

    # Reset text color
    print("\033[0m")
    sys.exit()

if __name__ == "__main__":
    fake_virus()
