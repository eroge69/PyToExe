def add(a, b):
    return a + b

def subtract(a, b):
    return a - b

def multiply(a, b):
    return a * b

def divide(a, b):
    try:
        return a / b
    except ZeroDivisionError:
        print("float division by zero")
        return None

def power(a, b):
    return a ** b

def remainder(a, b):
    try:
        return a % b
    except ZeroDivisionError:
        print("float division by zero")
        return None

def select_op(choice, a, b):
    if choice == '+':
        return add(a, b)
    elif choice == '-':
        return subtract(a, b)
    elif choice == '*':
        return multiply(a, b)
    elif choice == '/':
        return divide(a, b)
    elif choice == '^':
        return power(a, b)
    elif choice == '%':
        return remainder(a, b)
    else:
        print("Unrecognized operation")
        return None

def calculator():
    while True:
        print("Select operation.")
        print("1.Add      : +")
        print("2.Subtract : -")
        print("3.Multiply : *")
        print("4.Divide   : /")
        print("5.Power    : ^")
        print("6.Remainder: %")
        print("7.Terminate: #")
        print("8.Reset    : $")
        choice = input("Enter choice(+,-,*,/,^,%,#,$):")
        if choice == '#':
            print("Done. Terminating")
            break
        elif choice == '$':
            continue
        elif choice not in ['+', '-', '*', '/', '^', '%']:
            print("Unrecognized operation")
            continue

        # Get first operand
        while True:
            a = input("Enter first number:")
            if a == '$':
                break
            try:
                a = float(a)
                break
            except ValueError:
                print("Not a valid number,please enter again")
        if a == '$':
            continue

        # Get second operand
        while True:
            b = input("Enter second number:")
            if b == '$':
                break
            try:
                b = float(b)
                break
            except ValueError:
                print("Not a valid number,please enter again")
        if b == '$':
            continue

        # Division by zero message must come before result
        if (choice == '/' or choice == '%') and b == 0.0:
            print("float division by zero")
            result = None
        else:
            result = select_op(choice, a, b)
        print(f"{a} {choice} {b} = {result}")

# Run the calculator
calculator()
