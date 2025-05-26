def addition():
    arg1 = int(input("What is your First Argument: "))
    arg2 = int(input("What is your Second Argument: "))
    print("The Answer is ", arg1 + arg2)
    input("Use Enter to Exit")

def Subtraction():
    arg1 = int(input("What is your First Argument: "))
    arg2 = int(input("What is your Second Argument: "))
    print("The Answer is ", arg1 - arg2)
    input("Use Enter to Exit")

def times():
    arg1 = int(input("What is your First Argument: "))
    arg2 = int(input("What is your Second Argument: "))
    print("The Answer is ", arg1 * arg2)
    input("Use Enter to Exit")

def divide():
    arg1 = int(input("What is your First Argument: "))
    arg2 = int(input("What is your Second Argument: "))
    print("The Answer is ", arg1 / arg2)
    input("Use Enter to Exit")

def select(arg):
    if selection == 1:
        addition()
    elif selection == 2:
        Subtraction()
    elif selection == 3:
        times()
    elif selection == 4:
        divide()
    else:
        print("Invalid Value")


print("1: Adition")
print("2: Subtraction")
print("3: Times")
print("4: Division")
selection = int(input("Select Which Operation to use: "))
select(selection)
