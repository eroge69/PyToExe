import random
import string
import os

def clear():
    os.system("cls" if os.name == "nt" else "clear")

def banner_main():
    clear()
    print("\033[33m" + r"""
 ██▓███   ▄▄▄        ██████   ██████  █     █░ ▒█████   ██▀███  ▓█████▄    ▄▄▄█████▓ ▒█████   ▒█████   ██▓    
▓██░  ██▒▒████▄    ▒██    ▒ ▒██    ▒ ▓█░ █ ░█░▒██▒  ██▒▓██ ▒ ██▒▒██▀ ██▌   ▓  ██▒ ▓▒▒██▒  ██▒▒██▒  ██▒▓██▒    
▓██░ ██▓▒▒██  ▀█▄  ░ ▓██▄   ░ ▓██▄   ▒█░ █ ░█ ▒██░  ██▒▓██ ░▄█ ▒░██   █▌   ▒ ▓██░ ▒░▒██░  ██▒▒██░  ██▒▒██░    
▒██▄█▓▒ ▒░██▄▄▄▄██   ▒   ██▒  ▒   ██▒░█░ █ ░█ ▒██   ██░▒██▀▀█▄  ░▓█▄   ▌   ░ ▓██▓ ░ ▒██   ██░▒██   ██░▒██░    
▒██▒ ░  ░ ▓█   ▓██▒▒██████▒▒▒██████▒▒░░██▒██▓ ░ ████▓▒░░██▓ ▒██▒░▒████▓      ▒██▒ ░ ░ ████▓▒░░ ████▓▒░░██████▒
▒▓▒░ ░  ░ ▒▒   ▓▒█░▒ ▒▓▒ ▒ ░▒ ▒▓▒ ▒ ░░ ▓░▒ ▒  ░ ▒░▒░▒░ ░ ▒▓ ░▒▓░ ▒▒▓  ▒      ▒ ░░   ░ ▒░▒░▒░ ░ ▒░▒░▒░ ░ ▒░▓  ░
░▒ ░       ▒   ▒▒ ░░ ░▒  ░ ░░ ░▒  ░ ░  ▒ ░ ░    ░ ▒ ▒░   ░▒ ░ ▒░ ░ ▒  ▒        ░      ░ ▒ ▒░   ░ ▒ ▒░ ░ ░ ▒  ░
░░         ░   ▒   ░  ░  ░  ░  ░  ░    ░   ░  ░ ░ ░ ▒    ░░   ░  ░ ░  ░      ░      ░ ░ ░ ▒  ░ ░ ░ ▒    ░ ░   
               ░  ░      ░        ░      ░        ░ ░     ░        ░                    ░ ░      ░ ░      ░  ░
                                                                 ░                                            
""" + "\033[0m")
    # Box-style container for options
    print("\033[33m╔═══════════════════════════════════════════════════════════════════╗")
    print("║  [1] Generate Password   [2] Check Password Security   [3] Exit   ║")
    print("╚═══════════════════════════════════════════════════════════════════╝\033[0m\n")

def banner_checker():
    clear()
    print("\033[33m" + r"""
 ▄████▄   ██░ ██ ▓█████  ▄████▄   ██ ▄█▀▓█████  ██▀███  
▒██▀ ▀█  ▓██░ ██▒▓█   ▀ ▒██▀ ▀█   ██▄█▒ ▓█   ▀ ▓██ ▒ ██▒
▒▓█    ▄ ▒██▀▀██░▒███   ▒▓█    ▄ ▓███▄░ ▒███   ▓██ ░▄█ ▒
▒▓▓▄ ▄██▒░▓█ ░██ ▒▓█  ▄ ▒▓▓▄ ▄██▒▓██ █▄ ▒▓█  ▄ ▒██▀▀█▄  
▒ ▓███▀ ░░▓█▒░██▓░▒████▒▒ ▓███▀ ░▒██▒ █▄░▒████▒░██▓ ▒██▒
░ ░▒ ▒  ░ ▒ ░░▒░▒░░ ▒░ ░░ ░▒ ▒  ░▒ ▒▒ ▓▒░░ ▒░ ░░ ▒▓ ░▒▓░
  ░  ▒    ▒ ░▒░ ░ ░ ░  ░  ░  ▒   ░ ░▒ ▒░ ░ ░  ░  ░▒ ░ ▒░
░         ░  ░░ ░   ░   ░        ░ ░░ ░    ░     ░░   ░ 
░ ░       ░  ░  ░   ░  ░░ ░      ░  ░      ░  ░   ░     
░                       ░                               
""" + "\033[97m" + "               PASSWORD CHECKER\n" + "\033[0m")

def generate_password():
    length = input("Enter password length (8-32): ")
    try:
        length = int(length)
        if length < 8 or length > 32:
            raise ValueError
    except:
        print("\n\033[31mInvalid length.\033[0m")
        input("Press Enter to return...")
        return

    chars = string.ascii_letters + string.digits + "!@#$%^&*()"
    password = ''.join(random.choice(chars) for _ in range(length))
    print("\n\033[92mGenerated Password:\033[0m", password)
    input("\nPress Enter to return...")

def check_password_security():
    banner_checker()
    pwd = input("Enter your password: ")
    score = 0
    feedback = []

    if len(pwd) >= 12:
        score += 2
        feedback.append("✓ Good length")
    elif len(pwd) >= 8:
        score += 1
        feedback.append("• Moderate length")
    else:
        feedback.append("✗ Too short")

    if any(c.islower() for c in pwd):
        score += 1
    else:
        feedback.append("✗ Add lowercase letters")

    if any(c.isupper() for c in pwd):
        score += 1
    else:
        feedback.append("✗ Add uppercase letters")

    if any(c.isdigit() for c in pwd):
        score += 1
    else:
        feedback.append("✗ Add numbers")

    if any(c in "!@#$%^&*()" for c in pwd):
        score += 1
    else:
        feedback.append("✗ Add special characters")

    print("\n\033[96mSecurity Score:\033[0m", f"{score}/6")
    print("Feedback:")
    for f in feedback:
        print("  -", f)
    input("\nPress Enter to return...")

# === MAIN LOOP ===
while True:
    banner_main()
    choice = input("Enter your choice ~> ")

    if choice == "1":
        generate_password()
    elif choice == "2":
        check_password_security()
    elif choice == "3":
        print("\nGoodbye!\n")
        break
    else:
        input("\033[31mInvalid option. Press Enter to try again...\033[0m")