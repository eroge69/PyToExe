import sys
import time
import random
from random import randint
import os
import platform

BadLuckMitigation = 0
gateKey = False #key to the gate
lantern = False #lantern to light the cave
questComplete = False #quest completion
questFailed = False #quest failure
questIncomplete = False #quest incomplete
hermitMet = False #hermit meeting
gateBeen = False #gate visit
cabinBeen = False #cabin visit
forestBeen = False #forest visit

a, b = random.sample(range(1, 101), 2) #random numbers for math questions

riddles = [
    "Hermit: 'What has to be broken before you can use it?'",
    "Hermit: 'I speak without a mouth and hear without ears. I have nobody, but I come alive with the wind. What am I?'", #additional feature, may include in a later version
    "Hermit: 'I’m tall when I’m young, and I’m short when I’m old. What am I?'",
    "Hermit: 'What can you break, even if you never pick it up or touch it?'",
    "Hermit: 'What is always in front of you but can’t be seen?'"
]

answers = [
    "egg",
    "echo",
    "candle",
    "promise",
    "future"
]

def print_random_riddle():
    typewriter(random.choice(riddles)) #choose a random riddle
   
def typewriter(message):
    for char in message:
        sys.stdout.write(char)
        sys.stdout.flush()
        time.sleep(0.02)
    print()

def clear_screen(): #clears the screen
    if platform.system() == "Windows": 
        os.system("cls")
    else:
        os.system("clear")
       
def s(): #short sleep
    time.sleep(1)
   
def l(): #long sleep
    time.sleep(2.5)  

class LuckSystem: #lucks system for random events or rng mechanics
    @staticmethod   
    def rng(): 
        return randint(1,10)

def menu(): #main menu
    clear_screen()
    typewriter("Welcome to Textventure")
    typewriter("|| Main Menu ||")
    typewriter("   [1] Play")
    typewriter("   [2] Settings")
    typewriter("   [3] Exit")
    choice = input("> ").strip()
    if choice == '1':
        typewriter("Starting game...")
        cabin()
    elif choice == '2':
        typewriter("Opening settings...")
        settings()
    elif choice == '3':
        typewriter("Exiting...")
        exit()
    else:
        typewriter("Invalid choice. Please try again.")
        menu()

def settings(): #settings menu
    clear_screen()
    typewriter("Settings Menu (Decoration)")
    typewriter("[1] Sound")
    typewriter("[2] Graphics")
    typewriter("[3] Back to Main Menu")
    choice = input("> ")
    if choice == '1':
        typewriter("Adjusting sound settings...")
        typewriter("Returning to menu...")
        menu()
    elif choice == '2':
        typewriter("Adjusting graphics settings...")
        typewriter("Returning to menu...")
        menu()
    elif choice == '3':
        typewriter("Returning to menu...")
        menu()
    else:
        typewriter("Invalid choice. Please try again.")
        settings()

def cabin(): #cabin scene
    global forestBeen
    if forestBeen == True: #visited forest already
        clear_screen()
        typewriter("You enter the dimly lit room.")
        typewriter("You can see a window infront of you.")
        typewriter("You can see a table to the left of you.")   #completed dialogue checks and choices.
        typewriter("What do you want to do?")
        typewriter("[1] Go back outside")
        typewriter("[2] Look out the window")
        typewriter("[3] Inspect the table")
        cabinChoice()    
    else: #brand new play
        clear_screen()
        typewriter("You have awoken inside of a dimly lit room.")
        typewriter("You can see a door to your left.")
        typewriter("You can see a window to your right.")
        typewriter("You can see a table in front of you.")
        typewriter("What do you want to do?")
        typewriter("[1] Open the door")
        typewriter("[2] Look out the window")
        typewriter("[3] Inspect the table")
        cabinChoice()
   
def cabinChoice(): #cabin choices
    global gateKey 
    global forestBeen
    if forestBeen == True: #visited forest already
        choice = input("> ").strip()
        if choice == '1' and gateKey == False: #if the player has not found the key
            typewriter("You walk back out the cabin, as empty handed and unenlightened as when you stepped in.")
            l()
            forest()
        elif choice == '1' and gateKey == True: #if the player has found the key
            typewriter("You walk back out the cabin")
            l()
            forest()
        elif choice == '2':
            typewriter("Like before, you can't see much out as it's dark.")
            l()
            cabinChoice()
        elif choice == '3':
            if gateKey == True: #if the player has already found the key
                typewriter("The table is empty.")
                l()
            else:
                typewriter("You inspect the table and find a mysterious key")
                typewriter("You should've looked here before, you tell yourself.")
                l()
                gateKey = True
                cabinChoice()
        elif choice not in '1' or '2' or '3':
            typewriter("Invalid choice. Please try again.")
            l()
            cabinChoice()
    else:
        choice = input("> ")
        if choice == '1':
            typewriter("You open the door and walk outside")
            l()
            forest()
        elif choice == '2':
            typewriter("You look out the window, you can't see much as it's dark out")
            l()
            cabinChoice()
        elif choice == '3':
            typewriter("You inspect the table and find a mysterious key")
            gateKey = True
            l()
            cabinChoice()
        else:
            typewriter("Invalid choice. Please try again.")
            l()
            cabinChoice()
   
def forest(): #forest scene
    global forestBeen
    global questComplete
    forestBeen = True 
    if questFailed == True or questComplete == True: #completed or failed quest
        clear_screen()
        typewriter("You no longer see the Hermit beside the tree.")
        typewriter("You see a path further into the forest.")
        typewriter("You see the path back to the cabin")
        typewriter("What do you want to do?")
        typewriter("[1] Travel deeper into the forest")
        typewriter("[2] Go back to the cabin")
        forestChoice()
    elif gateBeen == True and hermitMet == True: #already met hermit and visited the gate
        clear_screen()
        typewriter("You walk away from the Hermit")
        typewriter("The winding path into the forest stares at you.")
        typewriter("What do you want to do?")
        typewriter("[1] Talk to the man again")
        typewriter("[2] Travel deeper into the forest")
        typewriter("[3] Go back to the cabin")
        forestChoice()
    else: #first time meeting the hermit
        clear_screen()
        typewriter("You see a man standing beside a tree, He looks up and smiles at you.")
        typewriter("You see a path further into the forest")
        typewriter("What do you want to do?")
        typewriter("[1] Talk to the man")
        typewriter("[2] Travel deeper into the forest")
        typewriter("[3] Go back to the cabin")
        forestChoice()

       
    if questFailed == True or questComplete == True: #completed or failed quest
        clear_screen()
        typewriter("You no longer see the Hermit beside the tree.")
        typewriter("You see a path further into the forest.")
        typewriter("You see the path back to the cabin")
        typewriter("What do you want to do?")
        typewriter("[1] Travel deeper into the forest")
        typewriter("[2] Go back to the cabin")
        forestChoice()
    elif gateBeen == False and hermitMet == True: #already met hermit and visited the gate
        clear_screen()
        typewriter("You walk away from the Hermit")
        typewriter("The winding path into the forest stares at you.")
        typewriter("What do you want to do?")
        typewriter("[1] Talk to the man again")
        typewriter("[2] Travel deeper into the forest")
        typewriter("[3] Go back to the cabin")
        forestChoice()
    else: #first time meeting the hermit
        clear_screen()
        typewriter("You see a man standing beside a tree, He looks up and smiles at you.")
        typewriter("You see a path further into the forest")
        typewriter("What do you want to do?")
        typewriter("[1] Talk to the man")
        typewriter("[2] Travel deeper into the forest")
        typewriter("[3] Go back to the cabin")
        forestChoice()

   
   
   
def forestChoice(): #forest choices
    choice = input("> ").strip() 
    if questFailed or questComplete:   # Already completed or failed quest
        if choice == '1':
            typewriter("You travel deeper into the forest")
            l()
            lockedGate()
        elif choice == '2':
            typewriter("You go back to the cabin")
            l()
            cabin()
        else:
            typewriter("Invalid choice. Please try again.")
            l()
            forestChoice()
    elif hermitMet:     # Already met Hermit but quest not yet finished
        if choice == '1':
            typewriter("You approach the Hermit again")
            l()
            hermit()
        elif choice == '2':
            typewriter("You travel deeper into the forest")
            l()
            lockedGate()
        elif choice == '3':
            typewriter("You go back to the cabin")
            l()
            cabin()
        else:
            typewriter("Invalid choice. Please try again.")
            l()
            forestChoice()
    else:     # First-time encounter
        if choice == '1':
            typewriter("You approach the man and he introduces himself as a Hermit...")
            l()
            hermit()
        elif choice == '2':
            typewriter("You travel deeper into the forest and discover a locked gate")
            l()
            lockedGate()
        elif choice == '3':
            typewriter("You go back to the cabin")
            l()
            cabin()
        else:
            typewriter("Invalid choice. Please try again.")
            l()
            forestChoice()


def lockedGate(): #locked gate scene
    global gateKey
    global gateBeen
    gateBeen = True
    clear_screen()
    typewriter("You approach the locked gate.")
    if gateKey == True: #if the player has found the key
        typewriter("You remember the mysterious key you picked up from the table in the cabin.")
        typewriter("You unlock the gate")
        typewriter("What do you want to do?")
        typewriter("[1] Carry on through the gate?")
        typewriter("[2] Go back to through the forest.")
        choice = input("> ").strip()
        if choice == '1':
            clear_screen()
            typewriter("You carry on through the gate and walk for a time")
            l()
            cave()
        elif choice == '2':
            clear_screen()
            typewriter("You decide you aren't ready for what lies ahead the gate and head back through the forest.")
            l()
            forest()
    elif gateKey == False: #if the player has not found the key
        typewriter("You rattle the gate back and forth to no avail.")
        typewriter("You do however notice a small keyhole in the gate.")
        typewriter("Perhaps there is a key for this somewhere, you tell yourself.")
        typewriter("You decide to walk back through the forest")
        l()
        forest()
             
def cave(): #cave scene
    clear_screen()
    typewriter("After what seems to have been a millenia, you find yourself standing infront of the large cave opening.")
    typewriter("The sounds you hear are ungodly. You take a step back.")
    typewriter("Sweat drips down your face...")
    typewriter("What do you want to do?")
    typewriter("[1] Enter the Cave")
    typewriter("[2] Go back through the Forest")
    typewriter("[3] Quit the Game...")
    caveChoice()

def lanternOut(): #lantern out scene
    clear_screen()
    typewriter("You wait a while to gather your bearings before re-lighting the lantern.")
    typewriter("You venture back into the cave")
    l()
    caveDeeper()

def caveChoice(): #cave choices
    global lantern
    choice = input("> ").strip()
    if choice == '1' and lantern == False: #if the player has not found the lantern
        typewriter("You think the cave is too dark and go back through the forest..")
        typewriter("Maybe you can find a light source to use in the cave..")
        l()
        forest()
    elif choice == '1' and lantern == True: #if the player has found the lantern
        typewriter("You take a deep breath..and carefully venture into the cave..")
        l()
        caveDeeper()
    elif choice == '2':
        typewriter("You think you're not ready for the cave just yet and decide to go back through the forest.")
        l()
        forest()
    elif choice == '3':
        typewriter("You think about quitting the game...")
        typewriter("Game Over! Scaredy Cat Ending.")
        l()
        exit()
    else:
        typewriter("Invalid choice. Please try again.")
        l()
        caveChoice()


def caveDeeper(): #cave deeper scene
    global BadLuckMitigation
    clear_screen()
    typewriter("After some time, you grow tired of the steady, cold breeze of the cave..")
    typewriter("Your lantern begins to flicker madly. You pray it doesn't go out.")
    if LuckSystem.rng() < 3: #implemented luck based on testing reflection
        BadLuckMitigation += 1
        typewriter("The gods have answered your prayers and your lantern holds on for dear life.")
        typewriter("You see a faint light in the distance. Hope is restored..")
        typewriter("You make your way towards the light")
        l()
        puzzleRoom()
    elif BadLuckMitigation == 3:
        typewriter("The gods have answered your prayers and your lantern holds on for dear life.")
        typewriter("You see a faint light in the distance. Hope is restored..")
        typewriter("You make your way towards the light")
        l()
        puzzleRoom()
    else:
        typewriter("The cave sends out a fierce breeze")
        typewriter("Your lantern gets extinguished")
        typewriter("You run out of the cave")
        l()
        lanternOut()
       
       
def puzzleRoom(): #puzzle room scene
    clear_screen()
    typewriter("You find yourself infront of a large ornate door.")
    typewriter("There are ancient inscriptions etched into the door, with a small stone that emanated the light you saw earlier.")
    typewriter("You run your fingers over the inscriptions")
    typewriter("You are hit with flashbacks of your time here")
    typewriter("Darkness floods your vision.")
    l()
    clear_screen()
    typewriter("A man steps out from the darkness.")
    typewriter("He is carrying a large wooden stick with a small stone atop..similar to the stone in the door.")
    typewriter("He seems somewhat familiar...")
    l()
    if questComplete == True:
        puzzleRoomEasy()
    if questFailed == True:
        puzzleRoomHard()
    if questIncomplete == True:
        puzzleRoomHard()
         
       
def puzzleRoomEasy(): #puzzle room easy scene
    clear_screen()
    l()
    typewriter("Hermit: 'Greetings Adventurer...Its wonderful to see you again.'")
    typewriter("Hermit: 'Because you helped me before, I am only required to ask you one simple question...'")
    typewriter("Hermit: 'Are you ready?'")
    typewriter("You nod your head")
    l()
    clear_screen()
    answer = int(input(f"Hermit: 'What is...{a} + {b}?: '"))
    if answer == a + b:
        typewriter("Correct!")
        l()
        ancientShrine()
    else:
        typewriter("Hermit: 'Come on now..Unfortunatley due to the power of cave you can only answer once more...'")
        answer = int(input(f"Try once more: "))  
        if answer == a + b:
            typewriter("Hermit: 'Well done Adventurer...Awaken...'")
            l()
            ancientShrine()
        else:
            typewriter("Hermit: 'How unfortunate Adventurer...'")
            typewriter("Hermit: 'I had high hopes for you.'")
            typewriter("Your vision starts to fade")
            typewriter("You lose sensation in your body")
            l()
            clear_screen()
            typewriter("Game Over! Dyscalculia Ending.")
            exit()
           
def puzzleRoomHard(): #puzzle room hard scene
    clear_screen()
    l()
    typewriter("Hermit: 'Greetings Adventurer...I am the Hermit.'")
    typewriter("Hermit: 'I remember you declining my request for aid. Therefore to pass you must answer a trivial question.'")
    typewriter("Hermit: 'Are you ready?'")
    typewriter("You nod your head")
    l()
    clear_screen()
    answer = int(input(f"Hermit: 'What is...{a} x {b}?: '"))
    if answer == a * b:
        typewriter("Correct!")
        l()
        ancientShrine()
    else:
        typewriter("Hermit: 'The cave has noted your insolence...'")
        typewriter("Hermit: 'I too have noted your insolence...'")
        typewriter("Hermit: 'You decline aid and struggle with intelligence...'")
        typewriter("Hermit: 'You are banished!'")
        typewriter("Your vision starts to fade")
        typewriter("You lose sensation in your body")
        l()
        l()
        clear_screen()
        typewriter("Game Over! Bad Ending.")
        exit()
       
def ancientShrine(): #ancient shrine scene
    clear_screen()
    typewriter("A single high soprano wakes you up..")
    typewriter("Others joined—altos, tenors, and deep, resonant basses.")
    typewriter("Each voice folding into the next like ripples on a still lake.")
    typewriter("The song wasn't in any mortal tongue..Yet its meaning flowed straight to your heart.")
    l()
    l()
    clear_screen()
    typewriter("You instantly regain the strength to stand...although you don't remember being on the floor.")
    typewriter("You take a glance of the surroundings.")
    typewriter("There stands four tall pillars surrounding a smaller pillar in the center.")
    typewriter("Tapestries and goldleaf furnish the walls of the dimly lit stone room.")
    l()
    l()
    clear_screen()
    typewriter("You approch the center of the pillars.")
    typewriter("A pool of rejuvination stands before you.")
    typewriter("You instinctly drink from the pool")
    typewriter("Vigour flows through your body.")
    l()
    l()
    clear_screen()
    typewriter("Game Over! Adventurers' Ending.")
    l()
    exit()
   
   
def hermit(): #hermit scene
    global lantern
    global hermitMet
    clear_screen()
    if hermitMet == False: #first time meeting the hermit
        typewriter("Hermit: 'Hi there! I was wondering when you would wake up.'")
        typewriter("Hermit: 'You've been asleep for a long time.'")
        typewriter("Hermit: 'It's dark out, have this lantern.'")
        typewriter("You received a lantern.")
        lantern = True
        typewriter("Hermit: 'Would you mind helping me with something?'")
        typewriter("[1] Yes")
        typewriter("[2] No")
        typewriter("[3] Stare")
        hermitMet = True
        hermitChoice()
    else:
        typewriter("Hermit: 'Hello again. How are you faring on this night?'")
        typewriter("You stare at him")
        typewriter("Hermit: 'Not much of a talker, eh?'")
        typewriter("Hermit: 'I hate to ask again but would you mind helping me with something?'")
        typewriter("[1] Yes")
        typewriter("[2] No")
        typewriter("[3] Stare")
        hermitChoice()

def hermitChoice(): #hermit choices
    global questIncomplete
    global BadLuckMitigation
    choice = input("> ").strip()
    if choice == '1':
        typewriter("You nod at the Hermit, his face lights up with a smile.")
        l()
        hermitQuest()
    elif choice == '2':
        typewriter("The Hermit nods and waves you goodbye.")
        l()
        questIncomplete = True
        forest()
    elif choice == '3':
        typewriter("The Hermit stares back in an epic staring contest...")
        if LuckSystem.rng() < 3:
            typewriter("You break the stare, losing the staring contest.")
            typewriter("All of a sudden, pressure builds in your head.")
            typewriter("You being to lose consciousness...")
            typewriter("Your head explodes...")
            typewriter("Game Over! Random Ending!.")
            l()
            l()
            exit()
        else:
            typewriter("The Hermit breaks his stare, You win the staring contest.")
            typewriter("You feel sudden relief, like the weight of the world has left your head.")
            typewriter("You don't spend another second thinking what might've happened if you'd have lost.")
            l()
            hermitChoice()
    else:
        typewriter("Invalid choice. Please try again.")
        hermitChoice()

def hermitQuest(): #hermit quest
    global questComplete
    global questFailed
    global questIncomplete
    global hermitMet
    clear_screen()
    typewriter("Hermit: 'Im in a bit of a pickle really, I have this piece of paper..'")
    typewriter("Hermit: 'Im told it's really important but I can't quite figure out what it says'")
    typewriter("Hermit: 'It's in these strange runic symbols..Maybe you can help me?'")
    l()
    clear_screen()
    typewriter("The Hermit hands you a piece of paper and a pen.")
    answer = int(input(f"It reads: 'What is...{a} x {b}?: '"))
    if answer == a * b:
        questComplete = True
        questIncomplete = False
        hermitMet = False
        typewriter("You hand back the piece of paper with the answer written down.")
        typewriter("Hermit: 'I hope this is right, thank you'")
        typewriter("You recieve a warm handshake and some pride.")
        typewriter("The Hermit vanishes infront of your eyes.")
        l()
        forest()    
    else:
        typewriter("You think the answer doesn't look quite right and decide to scribble it out and write another.")
        typewriter("There isn't much space left on the paper, you think one more attempt is enough.")
        typewriter("You read the paper properly once more.")
        l()
        answer = int(input(f"It reads: 'What is...{a} x {b}?: '"))
        if answer == a * b:
            questComplete = True
            questIncomplete = False
            hermitMet = False
            typewriter("You hand back the piece of paper with the answer written down.")
            typewriter("Hermit: 'I hope this is right, thank you'")
            typewriter("You recieve a warm handshake and some pride.")
            typewriter("The Hermit vanishes infront of your eyes.")
            l()
            forest()    
        else:
            questFailed = True
            questIncomplete = False
            hermitMet = False
            typewriter("You are still uncertain with your answer and deem it wrong once more.")
            typewriter("You ruined the Hermits paper.")
            typewriter("You give him back the pen and paper.")
            typewriter("The Hermit looks disappointed.")
            l()
            clear_screen()
            typewriter("Hermit: 'It's okay, You tried your best'")
            l()
            forest()  
       
   

def main(): #main function
    menu()
   
main()
