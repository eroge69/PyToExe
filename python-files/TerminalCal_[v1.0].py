#Import Things
import math

# Title
# Vars
t1 = "_____  ____  ___   _      _   __     __    _    "
t2 = " | |  | |_  | |_) | |\/| | | / /`   / /\  | |   "
t3 = " |_|  |_|__ |_| \ |_|  | |_| \_\_, /_/--\ |_|__ "
ver = "[V1.0]"
# Printing
print("======================================")
print(t1)
print(t2)
print(t3 + ver)
print("======================================")

# Main Vars
err1 = "Error: invalid command"
err2 = "Error: invalid entry [err430]"
err3 = "Error: invalid number [err510]"

# Main Center
while True:
    select = input("Command? ")

    if select == "dir":
        print("{Basic Operations}")
        print("  Addition")
        print("  Subtraction")
        print("  Multiplication")
        print("  Division")
        print("  Power")
        print("  Square Root")
        print("{Advanced Operations}")
        print("  Interest Simple")
        print("  Interest Compound")
        print("  Inflation")
        print("{Other}")
        print("  Credits")
        print("  ChangeLog")

    #Credits
    elif select == "Credits":
        print("Program created by JR-Emm")
        print("Special Thanks to Giselle, Marlun and you for using the program :)")

    #ChangeLog
    elif select == "ChangeLog":
        print("ChangeLog T.C. v1.0")
        print("Nothing New :/")
        
    #Addition
    elif select == "Addition":
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
    elif select == "Subtraction":
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
    elif select == "Multiplication":
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
    elif select == "Division":
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
    elif select == "Power":
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
    elif select == "Square Root":
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
            
    #Interest Simple
    elif select == "Interest Simple":
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
                result = n1 * (n2 / 100) * n3
                print("Interest S.: ", result)
            except ValueError:
                print(err2)
                break

    #Interest Compound
    elif select == "Interest Compound":
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

    #Inflation
    elif select == "Inflation":
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

    else:
        print(err1)
