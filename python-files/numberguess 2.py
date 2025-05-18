import random

def play_game():
    num_guesses = 0
    secret_number = random.randint(1, 100)
    print("\nWelcome to the Guess the Number game!")

    while True:
        try:
            guess = int(input("Guess the number (between 1 and 100): "))
            num_guesses += 1

            if guess < secret_number:
                print("Too low! Try guessing higher.")
            elif guess > secret_number:
                print("Too high! Try guessing lower.")
            else:
                print(f"🎉 Congratulations! You guessed the number {secret_number} in {num_guesses} guesses.")
                print("Thanks for playing!")
                break
        except ValueError:
            print("Please enter a valid number.")

# Main loop to allow replaying
while True:
    play_game()
    choice = input("\nDo you want to play again? (yes/no): ").strip().lower()
    if choice not in ["yes", "y"]:
        print("Goodbye! 👋")
        break
