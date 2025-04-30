import random

def multiplication_quiz():
    score = 0
    total_questions = 10

    for _ in range(total_questions):
        num1 = random.randint(1, 10)
        num2 = random.randint(1, 10)
        correct_answer = num1 * num2

        user_answer = int(input(f"Сколько будет {num1} * {num2}? "))

        if user_answer == correct_answer:
            score += 1
            print("Правильно!")
        else:
            print(f"Неправильно. Правильный ответ: {correct_answer}")

    print(f"Вы правильно ответили на {score} из {total_questions} вопросов.")

def main():
    while True:
        multiplication_quiz()
        continue_quiz = input("Хотите продолжить? (да/нет): ").strip().lower()
        if continue_quiz != 'да':
            break

if __name__ == "__main__":
    main()