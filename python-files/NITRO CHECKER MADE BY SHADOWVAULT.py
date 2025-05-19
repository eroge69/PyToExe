from colorama import Fore, Style, init
import requests
import time
import os

# Initialize colorama
init()

SHADOW_VAULT_LOGO = f"""
{Fore.BLUE} ________  ___  ___  ________  ________  ________  ___       __      
{Fore.BLUE}|\   ____\|\  \|\  \|\   __  \|\   ___ \|\   __  \|\  \     |\  \    
{Fore.BLUE}\ \  \___|\ \  \\\  \ \  \|\  \ \  \_|\ \ \  \|\  \ \  \    \ \  \   
{Fore.BLUE} \ \_____  \ \   __  \ \   __  \ \  \ \\ \ \  \\\  \ \  \  __\ \  \  
{Fore.BLUE}  \|____|\  \ \  \ \  \ \  \ \  \ \  \_\\ \ \  \\\  \ \  \|\__\_\  \ 
{Fore.BLUE}    ____\_\  \ \__\ \__\ \__\ \__\ \_______\ \_______\ \____________\
{Fore.BLUE}   |\_________\|__|\|__|\|__|\|__|\|_______|\|_______|\|____________|
{Fore.BLUE}   \|_________|                                                      
{Fore.BLUE}                                                                     
{Fore.BLUE}                                                                     
{Fore.BLUE} ___      ___ ________  ___  ___  ___   _________                    
{Fore.BLUE}|\  \    /  /|\   __  \|\  \|\  \|\  \ |\___   ___\                  
{Fore.BLUE}\ \  \  /  / | \  \|\  \ \  \\\  \ \  \\|___ \  \_|                  
{Fore.BLUE} \ \  \/  / / \ \   __  \ \  \\\  \ \  \    \ \  \                   
{Fore.BLUE}  \ \    / /   \ \  \ \  \ \  \\\  \ \  \____\ \  \                  
{Fore.BLUE}   \ \__/ /     \ \__\ \__\ \_______\ \_______\ \__\                 
{Fore.BLUE}    \|__|/       \|__|\|__|\|_______|\|_______|\|__|                                                                                  
{Style.RESET_ALL}
"""

def print_colored(text, color):
    print(color + text + Fore.RESET)

def check_nitro_code(code):
    url = f"https://discordapp.com/api/v9/entitlements/gift-codes/{code}?with_application=false&with_subscription_plan=true"
    response = requests.get(url)
    
    if response.status_code == 200:
        return True
    elif response.status_code == 404:
        return False
    else:
        return None

def save_to_file(filename, codes):
    with open(filename, "w") as file:
        for code in codes:
            file.write(code + "\n")
    print_colored(f"[✓] Saved {len(codes)} codes to {filename}", Fore.GREEN)

def load_codes_from_file(filename="codes.txt"):
    if not os.path.exists(filename):
        return None
    
    with open(filename, "r") as file:
        codes = [line.strip() for line in file if line.strip()]
    return codes

def process_codes(codes):
    valid = []
    invalid = []
    unknown = []
    
    for code in codes:
        clean = code.strip()
        print_colored(f"Checking: {clean}...", Fore.CYAN)
        
        result = check_nitro_code(clean)
        
        if result is True:
            print_colored("VALID", Fore.GREEN)
            valid.append(clean)
        elif result is False:
            print_colored("INVALID", Fore.RED)
            invalid.append(clean)
        else:
            print_colored("UNKNOWN (Rate limited or error)", Fore.YELLOW)
            unknown.append(clean)
        
        time.sleep(1)  # Avoid rate limiting
    
    return valid, invalid

def main():
    print(SHADOW_VAULT_LOGO)
    print_colored("Discord Nitro Gift Checker", Fore.MAGENTA)
    
    # Try to load codes from file
    codes = load_codes_from_file()
    
    if codes is None:
        print_colored("No 'codes.txt' found. Enter codes manually (one per line). Type 'done' to start.", Fore.WHITE)
        codes = []
        while True:
            code = input("> ")
            if code.lower() == 'done':
                break
            codes.append(code)
    
    if not codes:
        print_colored("No codes to check!", Fore.YELLOW)
        return
    
    print_colored(f"Checking {len(codes)} codes...", Fore.CYAN)
    valid, invalid = process_codes(codes)
    
    print("\nResults:")
    print_colored(f"Valid: {len(valid)}", Fore.GREEN)
    print_colored(f"Invalid: {len(invalid)}", Fore.RED)
    
    # Save results to files
    if valid:
        save_to_file("valid.txt", valid)
    if invalid:
        save_to_file("invalid.txt", invalid)

if __name__ == "__main__":
    main()
    