import random

# Russian Roulette Game

number = random.randint(1, 10)
guess = None

while True:
    guess = input("Guess a number between 1 and 10: ")
    
    if not guess.isdigit():
        print("Please enter a valid number.")
        continue
    
    guess = int(guess)

    if guess < 1 or guess > 10:
        print("Number must be between 1 and 10. Try again.")
    else:
        break 

if guess == number:
    print("You won!")
else:
    print("You lose! The correct number was:", number)