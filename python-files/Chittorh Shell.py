import os
import getpass
import time

stored_txt1 = None
stored_txt2 = None

if os.path.exists("stored_text1.txt"):
    with open("stored_text1.txt") as file:
        stored_txt1 = file.read()

if os.path.exists("stored_text2.txt"):
    with open("stored_text2.txt") as file:
        stored_txt2 = file.read()

R = getpass.getpass("Enter your password:")
if R == "011010":
    print("Access Granted")
    R = None
    del R
else:
    print("Access denied. Wrong passcode!")
    time.sleep(1)
    quit()

while True:
    basic_command = input()
    if basic_command == "start.(CT)":
        
        while True:
            command = input("Chittorh> ")

            if command == "stop.(CT)":
                break

            if command.startswith('store.txt3(') and command.endswith(')'):
                print("NO more text can be stored")
                continue

            if command.startswith('print("') and command.endswith('")'):
                to_print = command[7:-2]
                print(to_print)
                continue

            if command.startswith('store.txt1(') and command.endswith(')'):
                stored_txt1 = command[11:-1]
                with open("stored_text1.txt", "w") as file:
                    file.write(stored_txt1)
                print("Text1 has been Stored Successfully")
                continue

            if command.startswith('prv.txt(1)'):
                if stored_txt1:
                    print("text1:", stored_txt1)
                else:
                    print("No text1 is stored")
                continue

            if command.startswith('store.txt2(') and command.endswith(')'):
                stored_txt2 = command[11:-1]
                with open("stored_text2.txt", "w") as file:
                    file.write(stored_txt2)
                print("Text2 has been Stored Successfully")
                continue

            if command.startswith('prv.txt(2)'):
                if stored_txt2:
                    print("text2:", stored_txt2)
                else:
                    print("No text2 is stored")
                continue

            if command == "clear.txt1()":
                stored_txt1 = None
                with open("stored_text1.txt", "w") as f:
                    pass
                print("Text1 cleared successfully.")
                continue

            if command == "clear.txt2()":
                stored_txt2 = None
                with open("stored_text2.txt", "w") as f:
                    pass
                print("Text2 cleared successfully.")
                continue

            if command == 'open.(calc)':
                def add(x, y): return x + y
                def subtract(x, y): return x - y
                def multiply(x, y): return x * y
                def divide(x, y): return 'infinite' if y == 0 else x / y

                while True:
                    print("\n----- Calculator ----- (Made By Keshav)")
                    print("1. Addition")
                    print("2. Subtraction")
                    print("3. Multiplication")
                    print("4. Division")
                    print("5. Quit")

                    c = input("Please Select (1-5): ").strip()

                    if c in {'1', '2', '3', '4'}:
                        try:
                            x = float(input("First number: "))
                            y = float(input("Second number: "))
                        except ValueError:
                            print("Invalid input. Please enter numeric values.")
                            continue

                        if c == '1':
                            print("Answer:", add(x, y))
                        elif c == '2':
                            print("Answer:", subtract(x, y))
                        elif c == '3':
                            print("Answer:", multiply(x, y))
                        elif c == '4':
                            print("Answer:", divide(x, y))
                    elif c == '5':
                        break
                    else:
                        print("Invalid Choice. Please choose 1-5.")
                continue

            else:
                print("Command can't be identified.")
                continue

    elif basic_command == "stop.(CT)":
        quit()

    else:
        print("Please Enter basic command to run the CT. type help for the list for command")

    if basic_command == "help":
        print("\nBasic Commands:               : These commands help to run the CT")
        print("- start.(CT)                    : It starts the CT (Chittorh Terminal)")
        print("- stop.(CT)                     : It Quits the CT")

        print("\nAvailable CT Commands:")
        print("- store.txt1(<your text>)      : Store text in text1")
        print("- store.txt2(<your text>)      : Store text in text2")
        print("- store.txt3(...)              : Not allowed (disabled)")
        print("- prv.txt(1)                   : View stored text1")
        print("- prv.txt(2)                   : View stored text2")
        print("- clear.txt1()                 : Clear text1")
        print("- clear.txt2()                 : Clear text2")
        print("- print(\"<your message>\")     : Print a custom message")
        print("- open.(calc)                  : Open basic calculator")
        continue
