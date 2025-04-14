import random

def generate_equation(difficulty):
    if difficulty == "medium":
        operation = random.choice(["+", "-", "*"])
        if operation == "+":
            a, b = random.randint(10, 99), random.randint(10, 99)
        elif operation == "-":
            a, b = random.randint(10, 99), random.randint(10, 99)
        else:  # multiplication
            a, b = random.randint(10, 99), random.randint(1, 9)
    elif difficulty == "hard":
        operation = random.choice(["+", "-", "*"])
        if operation == "+":
            a, b = random.randint(100, 999), random.randint(100, 999)
        elif operation == "-":
            a, b = random.randint(100, 999), random.randint(100, 999)
        else:  # multiplication
            a, b = random.randint(10, 99), random.randint(100, 999)
    else:
        print("Invalid difficulty.")
        return None, None, None

    return a, b, operation

def main():
    print("Welcome to Donya's Math Quiz!")
    difficulty = input("7asa enk zakya enharda? (medium/hard): ").lower()

    while True:
        a, b, op = generate_equation(difficulty)
        if a is None:
            break

        question = f"What is {a} {op} {b}? "
        try:
            user_answer = int(input(question))
        except ValueError:
            print("7oty r2am s7 ya shle7f")
            continue

        correct_answer = eval(f"{a} {op} {b}")

        if user_answer == correct_answer:
            print("✅ aywaaaaaaa b2aaaa!\n")
        else:
            print(f"❌ yaa Looooooser. The correct answer is {correct_answer}.\n")

        play_more = input("3ayza so2al tany? (yes/no): ").lower()
        if play_more != "yes":
            print("Thanks for playing!")
            break

if __name__ == "__main__":
    main()
