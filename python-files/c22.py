import time
import random
import string
import getpass
import os

def login():
    print("\n\033[0m\033[38;5;16;48;5;208m Logowanie ".ljust(50) + "\033[0m")

    print("\033[38;5;16;48;5;208mPodaj login: \033[0m", end="")
    username = input()

    print("\033[38;5;16;48;5;208mPodaj hasło: \033[0m", end="")
    password = getpass.getpass('')

    if username == "silent" and password == "old":
        print("\033[32mZalogowano pomyślnie!\033[0m")
        return True
    else:
        print("\033[31mNiepoprawny login lub hasło!\033[0m")
        return False

def paste_ip():
    ip = input("\nPodaj adres IP: ")
    print(f"Adres IP {ip} został zapisany.")

def spam_text(text, times, wait_time=0):
    print("\nSpamowanie tekstem...")
    for _ in range(times):
        print(text)
        time.sleep(0.1)

    if wait_time > 0:
        print(f"\nOdczekuję {wait_time} sekund...")
        time.sleep(wait_time)

def generate_random_id(length=8):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

def generate_random_ip():
    return ".".join(str(random.randint(0, 255)) for _ in range(4))

def create_data(file_path):
    with open(file_path, "w") as f:
        data = "\n".join(generate_random_id() for _ in range(100))
        f.write(data)
    print(f"\nDane zapisane do: {file_path}")

def create_new_folder(path):
    if not os.path.exists(path):
        os.makedirs(path)
        print(f"Utworzono folder: {path}")
    else:
        print(f"Folder {path} już istnieje.")

def display_shutdown_message():
    print("\nSpamuję przed zamknięciem...")
    for _ in range(2000):
        print("SILENT.OLD")
        time.sleep(0.05)  # szybciej niż standardowe 0.1

    print("\n" + "="*30)
    print("SILENT.OLD".center(30))
    print("="*30)

def main():
    cooldown_time = 35
    last_spam_time = 0

    # Logowanie
    while not login():
        pass

    # IP input
    paste_ip()

    # Folder dox
    pobrane_folder = os.path.expanduser("~/Pobrane")
    dox_folder = os.path.join(pobrane_folder, "dox")
    create_new_folder(dox_folder)

    while True:
        current_time = time.time()
        if current_time - last_spam_time < cooldown_time:
            remaining = cooldown_time - int(current_time - last_spam_time)
            print(f"Pozostało {remaining} sekund do końca cooldownu.")
            time.sleep(1)
            continue

        # Spam ASCII
        text1 = "⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣀⣴⠾⣿⡇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⡿⠻⢶⣄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀"
        spam_text(text1, 30)

        spam_text("", 0, wait_time=20)

        text2 = r"""___            _     _       
 |  _ \  _____  _| |__ (_)_ __  
 | | | |/ _ \ \/ / '_ \| | '_ \ 
 | |_| | (_) >  <| |_) | | | | |
 |____/ \___/_/\_\_.__/|_|_| |_|"""
        spam_text(text2, 20)

        # 1000 losowych ID
        print("\nSILENT.OLD")
        for _ in range(1000):
            print(generate_random_id())

        # 1000 losowych IP
        print("\nLosowe IP:")
        for _ in range(1000):
            print(generate_random_ip())

        # Zapis danych
        last_spam_time = time.time()
        data_file = os.path.join(dox_folder, "data.txt")
        create_data(data_file)

        print(f"\nCooldown aktywowany. Musisz poczekać {cooldown_time} sekund.")
        time.sleep(cooldown_time)

        print("\n1. Kontynuuj\n2. Wyjście")
        choice = input("Wybierz opcję: ")
        if choice == "2":
            display_shutdown_message()
            break

if __name__ == "__main__":
    main()
