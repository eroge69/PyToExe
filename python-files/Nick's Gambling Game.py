turn = 0
roundscore = 0
bankscore = 0

botTurn = 0
botRoundscore = 0
botBankscore = 0

import sys
import time
#Main menu
def mainmenu():
    import os
    print(f"""         -Scam!-
    \__--_----_--__/
    
a) Start
b) How to Play
c) Quit
    """)
    
    while True:
        choice = (input("> "))
        if choice == "a":
            os.system('cls')
            turnComplete()
        
        elif choice == "b":
            os.system('cls')
            howtoplay()
    
        elif choice == "c":
            os.system('cls')
            print("\nbye i guess")
            time.sleep(3)
            sys.exit()
        
        else:
            print("\nInvalid Choice!\n")

def howtoplay():
    import os
    print("""
Be the first the roll 100! Be careful, if you roll a 1, you lose all your money. 
          You can save money from being lost by banking it!
    """)

    while True:
        choice = input("> Return ")
        if choice == "":
            os.system('cls')
            mainmenu()
        else:
            print("\nInvalid Choice!\n")

# Player
import os
def choose():
    global bankscore
    global roundscore
    import random
    choice = input("Would you like to roll or bank? ")
    
    if choice == "roll":
        os.system('cls')
        diceroll = random.randint(1, 6)
        if diceroll > 1:
            roundscore = roundscore + diceroll
            print(f"\nYou rolled a {diceroll}!\n")
            round()
            
        elif diceroll == 1:
            roundscore = 0
            print(f"\nYou rolled a 1! Your score has been reset to 0.\n\n {random_bot_name}'s Turn.\n")
            time.sleep(2)
            botplay()
            
        
    elif choice == "bank":
        bankscore = bankscore + roundscore
        roundscore = 0
        print(f"\nYour score is {bankscore}. {random_bot_name}'s turn.")
        time.sleep(2)
        os.system('cls')
        botplay()

    else:
        print("\nInvalid Choice!")
        choose()
    

def round():
    global roundscore
    print(f"This round you have: {roundscore}")
    choose()


def turnComplete():
    os.system('cls')
    global turn
    global bankscore
    
    turn = turn + 1
    print(f"Turn: {turn}")
    print(f"Your Current Score is: {bankscore}")
    print(f"{random_bot_name}'s Current Score is {botBankscore}")
    choose()



# Computer
import random
def generate_random_name(name_list):
    return random.choice(name_list)

if __name__== "__main__":
    bot_names = ["Nick","Lewis","Raiden","Sai","Seth"]
    random_bot_name=generate_random_name(bot_names)


def botplay():
    global botTurn
    global botRoundscore
    global botBankscore
    global roundscore
    botTurn = botTurn + 1
    import random
    
    while True:
        diceroll = random.randint(1, 6)
        if diceroll > 1:
            print(f"{random_bot_name} is rolling...")
            time.sleep(2)
            os.system('cls')
            print(f"\n{random_bot_name} rolls a {diceroll}.\n{random_bot_name}'s score this round is {botRoundscore}. \n")
            botRoundscore = botRoundscore + diceroll
            if botRoundscore > 15:
                botBankscore = botBankscore + botRoundscore
                botRoundscore = 0
                roundscore = 0
                print(f"{random_bot_name} banked their score. {random_bot_name}'s score is {botBankscore}\n")
                evaluate()

  
        elif diceroll == 1:
            print(f"{random_bot_name} is rolling...")
            time.sleep(2)
            print(f"\n{random_bot_name} rolled a 1. End of turn.\n{random_bot_name}'s score is {botBankscore}.\n")
            time.sleep(2)
            evaluate()
            

# Score Evaluation
def evaluate():
    global turn
    global botTurn
    
    if bankscore >= 100 and bankscore > botBankscore:
        print(f"\nCongratulations! You won on turn {turn}!\nYour score: {bankscore}\n{random_bot_name}'s score: {botBankscore}")
        exit()
        
    elif botBankscore >= 100 and botBankscore > bankscore:
        print(f"Good Try. {random_bot_name} won on turn {botTurn}.\nYour score: {bankscore}\n{random_bot_name}'s score: {botBankscore}")
        exit()
        
    else:
        turnComplete()


# Starts Game
mainmenu()