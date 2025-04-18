import time
import random
import os
from colorama import Fore, Style, init

# Инициализация colorama для работы с цветами в консоли
init()

def generate_fake_password():
    """Генерирует случайный "фейковый" пароль."""
    words = ["hello", "rose", "sun", "moon", "sky", "water", "fire", "earth", "wind", "stone", "tree", "bird", "fish", "cat", "dog", "house", "book", "light", "dark", "blue", "red", "green"]
    numbers = random.randint(0, 99)  # Случайное число для добавления в конец
    return f"{random.choice(words)}{random.choice(words)}{numbers}"

def load_target_password(config_file="config.cfg"):
    """Загружает целевой пароль из файла конфигурации."""
    try:
        with open(config_file, "r") as f:
            for line in f:
                if line.startswith("password="):
                    return line.split("=")[1].strip()
        return None  # Если пароль не найден в файле
    except FileNotFoundError:
        print(f"{Fore.RED}Error: Config file '{config_file}' not found.{Style.RESET_ALL}")
        return None
    except Exception as e:
        print(f"{Fore.RED}Error reading config file: {e}{Style.RESET_ALL}")
        return None

def simulate_bruteforce(target_password, nickname):
    """Симулирует процесс брутфорса с фейковыми паролями."""
    attempts = 0
    max_invalid_attempts = random.randint(30, 50)

    while True:
        attempts += 1
        password = generate_fake_password()

        if password == target_password:
            print(f"{Fore.GREEN}[VALID] {nickname}:{password}{Style.RESET_ALL}")
            break  # Пароль найден, выходим из цикла
        else:
            print(f"{Fore.RED}[INVALID] {password}{Style.RESET_ALL}")
            time.sleep(random.uniform(0.5, 2.0))  # Увеличена задержка (0.5 - 2 секунды)

        if attempts > max_invalid_attempts:
            print(f"{Fore.GREEN}[VALID] {nickname}:{target_password}{Style.RESET_ALL}") #  как будто нашли пароль
            break


# --- Main ---
if __name__ == "__main__":
    # Вывод сообщения в начале
    print(f"{Fore.CYAN}------------([ Retract Proprietary Security Bypass ])------------{Style.RESET_ALL}")

    # 1. Проверка наличия config.cfg и его создание, если его нет.
    config_file = "config.cfg"
    if not os.path.exists(config_file):
        print(f"{Fore.YELLOW}Creating default config file '{config_file}'.  Please edit it!{Style.RESET_ALL}")
        with open(config_file, "w") as f:
            f.write("password=MySecretPassword\n")  # Записываем туда строку с дефолтным паролем
        print("Please edit 'config.cfg' with the password you want to 'crack'.")
        exit()  # и завершаем скрипт чтобы пользователь его отредактировал.

    # 2. Загрузка целевого пароля из файла
    target_password = load_target_password(config_file)

    # 3. Получение никнейма от пользователя
    nickname = input("Enter the nickname: ")

    if target_password:
        print("Starting brute-force simulation...")
        simulate_bruteforce(target_password, nickname)
        print("Brute-force simulation finished.")
    else:
        print("Failed to load target password.  Check the config file.")
