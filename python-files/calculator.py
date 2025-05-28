import math as m

while True:
    num1 = float((input("number")))
    while True:
        do = input("type one: +,-,*,**(power),/,sqrt,round.")

        if do not in ("sqrt","round"):
            num2 = float((input("number")))

        if do == "+":
            print("answer:", num1 + num2)
            num1 = num1 + num2

        elif do == "-":
            print("answer:", num1 - num2)
            num1 = num1 - num2

        elif do == "round":
            print("answer:", round(num1))
            num1 = round(num1)

        elif do == "*":
            print("answer:", num1 * num2)
            num1 = num1 * num2

        elif do == "**":
            print("answer:", num1 ** num2)
            num1 = num1 ** num2

        elif do == "/":
            if num2 == 0:
                print("Error: division by zero")
                continue
            else:
                print("answer:", num1 / num2)
                num1 = num1 / num2

        elif do == "sqrt":
            print("answer:", m.sqrt(num1))
