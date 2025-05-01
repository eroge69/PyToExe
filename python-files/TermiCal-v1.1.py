#Import Things
import math
import time
import random as ran

ver = "[V1.1]"
#Mathematical values
pi = 3.141592653589793
# Printing
print("  ______")
print(" | |__| | ___                _       ")
print(" |  ()  |  |  _  ._ ._ _  o /   _. | ")
print(" |______|  | (/_ |  | | | | \_ (_| | ")
print(ver + " Created by Junior Emmanuel Marquez Paulino")
print("If you don't know how this works, type 'Help'")

# Main Vars
err1 = "Error: invalid command"
err2 = "Error: invalid entry [err430]"

# Main Center
while True:
    select = input("Command? ")

    if select == "dir":
        print("{Basic Operations}")
        print("  Addition (add)")
        print("  Subtraction (sub)")
        print("  Multiplication (mul)")
        print("  Division (div)")
        print("  Power (pow)")
        print("  Square Root (squ)")
        print("{Advanced Operations}")
        print("  Simple Rule of 3 (ru3)")
        print("  Interest Simple (intS)")
        print("  Interest Compound (intC)")
        print("  Pitagorean Theorem (pth)")
        print("  Linear Algebraic Equation (LAE)")
        print("  Inflation (inf)")
        print("{Other}")
        print("  Help")
        print("  Credits")
        print("  ChangeLog")
        print("  Notes")
        print("  Exit")

    #Help
    elif select == "Help":
        print("To see the available options type 'dir',")
        print("and to select the topic you want to")
        print("calculate, type the abbrebialty to the")
        print("right of each topic.")

    #Credits
    elif select == "Credits":
        print("Program created by Junior Emmanuel Marquez Paulino")
        print("Art from ASCII Art Archive")
        print("Special Thanks to Giselle, Marlun and you for using the program :)")

    #ChangeLog
    elif select == "ChangeLog":
        print("ChangeLog T.C. v1.1")
        print("Linear Algebraic Equation added")
        print("Simple Rule of 3 added")
        print("Pitagorean Theorem added")
        print("Randomizer added")
        print("Someone named ###### added")

    #Notes
    elif select == "Notes":
        print("[(Notes)]")
        print("I'm having trouble with operations involving fractions,")
        print("but I'm going to try to solve that problem. [-Junior Emm.-]")
        
    #Addition
    elif select == "add":
        while True:
            num1 = input("Insert the first addend (or 'back' to return): ")
            if num1 == "back":
                break
            num2 = input("Insert the second addend (or 'back' to return): ")
            if num2 == "back":
                break

            try:
                n1 = float(num1)
                n2 = float(num2)
                result = n1 + n2
                print("Addition: ", result)
            except ValueError:
                print(err2)
                break
                
    #Subtraction
    elif select == "sub":
        while True:
            num1 = input("Insert the minuend (or 'back' to return): ")
            if num1 == "back":
                break
            num2 = input("Insert the subtrahend (or 'back' to return): ")
            if num2 == "back":
                break

            try:
                n1 = float(num1)
                n2 = float(num2)
                result = n1 - n2
                print("Difference: ", result)
            except ValueError:
                print(err2)
                break
                
    #Multiplication
    elif select == "mul":
        while True:
            num1 = input("Insert the Multiplying (or 'back' to return): ")
            if num1 == "back":
                break
            num2 = input("Insert the Multiplier (or 'back' to return): ")
            if num2 == "back":
                break

            try:
                n1 = float(num1)
                n2 = float(num2)
                result = n1 * n2
                print("Product: ", result)
            except ValueError:
                print(err2)
                break

    #Division
    elif select == "div":
        while True:
            num1 = input("Insert the Dividend (or 'back' to return): ")
            if num1 == "back":
                break
            num2 = input("Insert the Divider (or 'back' to return): ")
            if num2 == "back":
                break

            try:
                n1 = float(num1)
                n2 = float(num2)
                result1 = n1 / n2
                ex1 = math.floor(result1)
                ex2 = ex1 * n2
                result2 = n1 - ex2
                print("Quotient: ", result1)
                print("Residue: ", result2)
            except ValueError:
                print(err2)
                break

    #Power
    elif select == "pow":
        while True:
            num1 = input("Insert the Base (or 'back' to return): ")
            if num1 == "back":
                break
            num2 = input("Insert the Exponent (or 'back' to return): ")
            if num2 == "back":
                break

            try:
                n1 = float(num1)
                n2 = float(num2)
                result = n1 ** n2
                print("Power: ", result)
            except ValueError:
                print(err2)
                break

    #Square Root
    elif select == "squ":
        while True:
            num1 = input("Insert the Rooting (or 'back' to return): ")
            if num1 == "back":
                break

            try:
                n1 = float(num1)
                result = n1 ** 0.5
                print("Root: ", result)
            except ValueError:
                print(err2)
                break

    #Simple Rule of 3
    elif select == "ru3":
        while True:
            num1 = input("Insert the first data (or 'back' to return): ")
            if num1 == "back":
                break
            num2 = input("Insert the second data (or 'back' to return): ")
            if num2 == "back":
                break
            num3 = input("Insert the third data (or 'back' to return): ")
            if num3 == "back":
                break

            try:
                n1 = float(num1)
                n2 = float(num2)
                n3 = float(num3)
                result = n1 * n2 / n3
                print("Result: ", result)
            except ValueError:
                print(err2)
                break

    #Interest Simple
    elif select == "intS":
        while True:
               num1 = input("Insert the Initial Capital (or 'back' to return): ")
               if num1.lower() == "back":
                   break

               num2 = input("Insert the Interest Rate (or 'back' to return): ")
               if num2.lower() == "back":
                   break

               num3 = input("Insert the number of years (or 'back' to return): ")
               if num3.lower() == "back":
                  break

               try:
                   n1 = float(num1)
                   n2 = float(num2)
                   n3 = float(num3)
                   result = n1 * (n2 / 100) * n3
                   print("Simple Interest: ".format(result))
               except ValueError:
                   print(err2)


    #Interest Compound
    elif select == "intC":
        while True:
            num1 = input("Insert the Initial Capital (or 'back' to return): ")
            if num1 == "back":
                break
            num2 =input("Insert the Interest Rate (or 'back' to return): ")
            if num2 == "back":
                break
            num3 = input("Insert the number of years (or 'back' to return): ")
            if num3 == "back":
                break

            try:
                n1 = float(num1)
                n2 = float(num2)
                n3 = float(num3)
                result = n1 + (n2 / 100) ** n3 * n1
                print("Interest C.: ", result)
            except ValueError:
                print(err2)
                break
            
    #Pitagorean Theorem
    elif select == "pth":
        while True:
            print("{Chosse}")
            print("  Find Hypotenuse")
            print("  Search Cateto")
            print("<- back ")
            sl1 = input("Command? ")

            if sl1 == "Find Hypotenuse":
                while True:
                    num1 = input("Insert the first Cateto (or 'back' to return): ")
                    if num1 == "back":
                        break
                    num2 = input("Insert the second Cateto (or 'back' to return): ")
                    if num2 == "back":
                        break

                    try:
                        n1 = float(num1)
                        n2 = float(num2)
                        result = (n1 ** 2) + (n2 ** 2) ** 0.5
                        print("Hypotenuse: ",  result)
                    except ValueError:
                        print(err2)
                        break

            elif sl1 == "Search Cateto":
                while True:
                    num1 = input("Insert the Cateto (or 'back' to return): ")
                    if num1 == "back":
                        break
                    num2 = input("Insert the Hypotenuse (or 'back' to return): ")
                    if num2 == "back":
                        break

                    try:
                        n1 = float(num1)
                        n2 = float(num2)
                        result = (n2 ** 2) - (n1 ** 2) ** 0.5
                        print("Cateto: ", result)
                    except ValueError:
                        print(err2)
                        break

            elif sl1 == "back":
                break

            else:
                print(err1)

    #Inflation
    elif select == "inf":
        while True:
            num1 = input("Insert the Initial Value (or 'back' to return): ")
            if num1 == "back":
                break
            num2 =input("Insert the Inflation Rate (or 'back' to return): ")
            if num2 == "back":
                break
            num3 = input("Insert the number of years (or 'back' to return): ")
            if num3 == "back":
                break

            try:
                n1 = float(num1)
                n2 = float(num2)
                n3 = float(num3)
                ex1 = n1 * (n2 / 100) * n3 + n1
                result = round(ex1)
                print("Adjusted Value: ", result)
            except ValueError:
                print(err2)
                break

    #Linear Algebraic Equation
    elif select == "LAE":
        while True:
            num1 = input("Insert the Input Value (or 'back' to return): ")
            if num1 == "back":
                break
            num2 =input("Insert the Earring (or 'back' to return): ")
            if num2 == "back":
                break
            num3 = input("Insert the Intersection (or 'back' to return): ")
            if num3 == "back":
                break

            try:
                n1 = float(num1)
                n2 = float(num2)
                n3 = float(num3)
                result = n1 * n2 + n3
                print("Result: ", result)
            except ValueError:
                print(err2)
                break

    elif select == "That Someone":
        print("What Someone?, ahh... yeah, Giygas?")
        print("He is a very quiet man, do you want to meet him?")
        while True:
            sl2 = input("Command? ")

            if sl2 ==  "no":
                print("see ya")
                exit()

            elif sl2 == "yes":
                print("Ok, go to that door, you'll find it there.")
                print("Going...")
                time.sleep(3)
                print("Opening the door...")
                time.sleep(2)
                print("                                                                     ")
                print("                     ███████████████████████                         ")
                print("              ███████████████        ███████████                     ")
                print("           ████████████████████████████   █████████                  ")
                print("       ████████████             ██████████   ████████                ")
                print("      ███████                          ███████  █████████            ")
                print("     ████                                  █████  ████████           ")
                print("    ██                            █            ███  ████████         ")
                print("                           ███████               ██   ███████        ")
                print("                        ████████████               ██  ███████       ")
                print("                      ██████   ██  ████             ██  ███████      ")
                print("                        ███    ████  ███                 ███████     ")
                print("                         ████████████  █                  ██████     ")
                print("                           █████  ███████                 ███████    ")
                print("                         ████████████████                 ████████   ")
                print("                       ██████    ████████                 ████████   ")
                print("                     ████         ███████                 ████████   ")
                print("                    ███         █   ███                  ███████████ ")
                print("                                   ████                  ████████████")
                print("                                █████                   ████████████ ")
                print("                               ████                    █████████████ ")
                print("                             ███                     ███████████████ ")
                print("                                                   ████████████████  ")
                print("                                                  ████████████████   ")
                print("                                               ██████████████████    ")
                print("                                           █████████████████████     ")
                print("                         █████████████████████████████████████       ")
                print("                           ████████████████████████████████          ")
                print("                              █████████████████████████              ")
                print("                                  █████████████████                  ")
                print("                                                                     ")
                time.sleep(3)
                print("Hello...")
                time.sleep(3)
                print("It's time to begin your secret adventure...")
                time.sleep(3)
                print("Take this")
                time.sleep(0.5)
                while True:
                    print("[SyntaxError]")

    elif select == "Exit":
        print("Closing...")
        time.sleep(3)
        print("Closed")
        exit()

    else:
        print(err1)