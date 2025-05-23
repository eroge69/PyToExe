import time
import os

def clear_screen():
    """Clear the terminal screen"""
    os.system('cls' if os.name == 'nt' else 'clear')

def countdown(seconds):
    """Display countdown timer"""
    for i in range(seconds, 0, -1):
        print(f"Wait {i} seconds...", end='\r', flush=True)
        time.sleep(1)
    print(" " * 20, end='\r')

def display_menu(puzzles):
    """Display the main menu with puzzle status"""
    clear_screen()
    print("=== ESCAPE ROOM DIGITAL TERMINAL ===")
    print("Navigate between puzzles and enter your solutions.\n")
    
    print("PUZZLE STATUS:")
    for i, puzzle in enumerate(puzzles, 1):
        status = "✓ SOLVED" if puzzle['solved'] else "✗ UNSOLVED"
        print(f"{i}. {puzzle['name']} - {status}")
    
    print("\nCOMMANDS:")
    print("• Enter 1-4 to select a puzzle")
    print("• Enter 'q' to quit")

def attempt_puzzle(puzzle):
    """Handle puzzle attempt with cooldown on wrong answer"""
    clear_screen()
    print(f"=== {puzzle['name'].upper()} ===")
    print(f"Status: {'SOLVED' if puzzle['solved'] else 'UNSOLVED'}")
    
    if puzzle['solved']:
        print("✓ This puzzle has already been solved!")
        input("\nPress Enter to return to menu...")
        return
    
    print(f"\n{puzzle['prompt']}")
    user_input = input("> ").strip().upper()
    
    if user_input == puzzle['answer'].upper():
        puzzle['solved'] = True
        print("✓ Correct! Puzzle solved!")
        input("\nPress Enter to return to menu...")
    else:
        print("✗ Incorrect answer.")
        print("Please wait before trying again...")
        countdown(15)
        input("Press Enter to return to menu...")

def main():
    puzzles = [
        {
            "name": "Stokjes",
            "prompt": "Enter your answer (lowercase if applicable):",
            "answer": "agent",
            "solved": False
        },
        {
            "name": "Tijdschriften",
            "prompt": "Enter your answer (lowercase if applicable):",
            "answer": "decrypt",
            "solved": False
        },
        {
            "name": "Blaadjes",
            "prompt": "Enter your answer (lowercase if applicable)",
            "answer": "011100",
            "solved": False
        },
    ]
    
    while True:
        display_menu(puzzles)
        
        if all(puzzle['solved'] for puzzle in puzzles):
            clear_screen()
            print("🎉 CONGRATULATIONS! 🎉")
            print("You have solved all puzzles and escaped!")
            print("Go to: https://llumora.onrender.com/invitations/c7c9a9bb-1b14-4aa5-b224-8ae4d04a7b40?token=ZMWQHE")
            input("\nPress Enter to exit...")
            break
        
        print()
        user_input = input("Enter your choice: ").strip().lower()
        
        if user_input == 'q':
            print("Goodbye!")
            break
        elif user_input in ['1', '2', '3', '4']:
            puzzle_index = int(user_input) - 1
            attempt_puzzle(puzzles[puzzle_index])
        else:
            print("Invalid input. Please enter 1-4 or 'q'.")
            time.sleep(1)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nGoodbye!")
    except Exception as e:
        print(f"\nAn error occurred: {e}")
        input("Press Enter to exit...")