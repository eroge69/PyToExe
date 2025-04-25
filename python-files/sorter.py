import os
import time
import pyfiglet
from colorama import Fore, Back, Style, init

# Initialize colorama
init(autoreset=True)

# Define colors
blue = Fore.BLUE
black = Back.BLACK
white = Fore.WHITE

# Function to simulate typing animation for each letter in the title
def type_writer(text, delay=0.001):  # Super fast typing by reducing the delay to 0.001 seconds
    for char in text:
        print(blue + char, end='', flush=True)  # Print incrementally
        time.sleep(delay)
    print()  # Move to the next line after finishing

# Function to print the big title in the center
def print_big_title():
    title = "VALTRIX"
    
    # Clear the screen before starting
    os.system('cls' if os.name == 'nt' else 'clear')

    # Create a big title using pyfiglet (larger font)
    big_title = pyfiglet.figlet_format(title, font="big")  # Using "big" font for larger text
    
    # Center the title (number of spaces before the title to center it on the screen)
    screen_width = os.get_terminal_size().columns
    title_lines = big_title.splitlines()
    
    # Print the title with typing animation
    for line in title_lines:
        centered_line = line.center(screen_width)
        type_writer(centered_line, delay=0.001)  # Super fast typing

# Function to print "discord.gg/valtrix" at the bottom
def print_discord_link():
    screen_width = os.get_terminal_size().columns
    discord_link = "Made by discord.gg/valtrix"
    
    # Center the discord link at the bottom
    print(f"{blue}{discord_link.center(screen_width)}")
    time.sleep(1)

# Function to print the header (main menu)
def print_header():
    print(f"{blue}{Style.BRIGHT}")
    print(f"{blue}")
    print("" * 50)

# Function to process logs
def process_logs():
    log_folder = "logs"
    keywords_file = "keywords.txt"
    output_dir = "combos"
    os.makedirs(output_dir, exist_ok=True)

    # Load keywords
    with open(keywords_file, "r", encoding="utf-8") as kf:
        keywords = [line.strip().lower() for line in kf if line.strip()]

    # Pattern: url📧pass
    combo_pattern = re.compile(r'([^:]+):([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}):([^\s]+)')

    # Track seen combos (optional)
    seen_combos = set()

    # Counter for logging progress
    processed_lines = 0
    matches_found = 0

    # Loop through all log files
    for filename in os.listdir(log_folder):
        if not filename.endswith(".txt"):
            continue

        filepath = os.path.join(log_folder, filename)
        try:
            with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
                for line in f:
                    processed_lines += 1
                    match = combo_pattern.search(line)
                    if match:
                        url, email, password = match.groups()
                        combo = f"{email}:{password}"
                        for keyword in keywords:
                            if keyword in url.lower():
                                if combo not in seen_combos:
                                    seen_combos.add(combo)
                                    output_path = os.path.join(output_dir, f"{keyword}.txt")
                                    with open(output_path, "a", encoding="utf-8") as out_f:
                                        out_f.write(combo + "\n")
                                    matches_found += 1
                                    if matches_found % 10 == 0:
                                        print(f"{blue}✅ {matches_found} matches saved so far...")

                    if processed_lines % 1000 == 0:
                        print(f"{blue}📈 Processed {processed_lines} lines...")

        except Exception as e:
            print(f"{red}❌ Error processing {filepath}: {e}")

    print(f"\n{blue}🎉 Done! Total lines: {processed_lines} | Total matches: {matches_found}")

# Menu
def display_menu():
    print_header()
    print(f"{blue}[1] Start Processing")
    print(f"{blue}[2] Exit")

def handle_user_input():
    while True:
        choice = input(f"{blue}Choice Chosen: ")
        if choice == "1":
            print(f"{blue}Processing started...\n")
            process_logs()
        elif choice == "2":
            print(f"{blue}Exiting program...")
            break
        else:
            print(f"{blue}Invalid choice, try again.")

# Run the interface
print_big_title()  # Print the title with typing animation and centered
print_discord_link()  # Display discord link under the title
time.sleep(1)  # Short delay before showing the menu
display_menu()
handle_user_input()
