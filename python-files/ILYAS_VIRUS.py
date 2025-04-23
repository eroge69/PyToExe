import time
import random
import sys

def virus():
    print("Initializing Ilyas.exe...")
    time.sleep(2)

    print("Scanning system directories...")
    time.sleep(5)

    print("Locating sensetive data...")
    time.sleep(2)

    print("Establishing connection to darknet...")
    time.sleep(3)

    print("WARNING: SYSTEM COMPROMISED")
    time.sleep(1)

    files = [
        "etc/password",
        "Windows/avcodec-51.dll",
        "var/log/syslog",
        "Windows/system32/040A/rusb3co.dll.mui"
    ]

    for file in files:
        print("[!] Deleting " + file + "...")
        time.sleep(random.uniform(0.3, 1.2))
        print("[!] Successfully deleted " + file)
        
    print("\nCRITICAL ERROR: BOOT SECTOR CORRUPTED")
    time.sleep(2)

    print("\nEncrypting files with RSA-409...")
    for i in range(1, 101):
          time.sleep(0.1)
          sys.stdout.write("\rProgress: " + str(i) + "%   ")
          sys.stdout.flush()

    print("\n\nAll YOUR FILES HAVE BEEN ENCRYPTED!")
    print("Send 0.5 BTC to +79501749009 (T-Bank) to restore access.")
    time.sleep(3)

    for _ in range(15):
        print("! ! ! FATAL ERROR: MEMORY CORRUPTION ! ! !")
        time.sleep(0.2)

    print("Ilyas.exe completed its task. Self-destructing...")
    time.sleep(3)
    print("[!] FATAL ERROR: 4001282. Your PC ran into a problem and needs to restart. We're just collecting some error info, and then we'll restart for you")
    for i in range(1, 101):
          time.sleep(5)
          sys.stdout.write("\rProgress: " + str(i) + "%   ")
          sys.stdout.flush()      


if __name__ == "__main__":
    virus()
