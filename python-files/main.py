import random
import tkinter as tk
from tkinter import messagebox


def subtraction_training():
    num1 = random.randint(1, 100)
    num2 = random.randint(1, 100)
    if num1 < num2:
        num1, num2 = num2, num1
    correct_result = num1 - num2
    return num1, num2, correct_result


def division_training():
    num1 = random.randint(1, 10)
    num2 = random.randint(1, 10)
    divisible_number = num1 * num2
    correct_result = divisible_number // num1  # Используем целочисленное деление
    return divisible_number, num1, correct_result


def addition_training():
    num1 = random.randint(1, 100)
    num2 = random.randint(1, 100)
    correct_result = num1 + num2
    return num1, num2, correct_result


def multiplication_training():
    num1 = random.randint(1, 10)
    num2 = random.randint(1, 10)
    correct_result = num1 * num2
    return num1, num2, correct_result


def square_training():
    num = random.randint(1, 20)
    correct_result = num ** 2  # Fixed exponentiation operator
    return num, correct_result


def sqrt_training():
    num = random.randint(1, 400)  # Для корней выбираем числа до 400
    correct_result = int(num ** 0.5)  # Находим целый корень
    return num, correct_result


class MathTrainerApp:
    def __init__(self, root):  # Fixed method name from init to __init__
        self.root = root
        self.root.title("Math Trainer")

        self.score = 0
        self.total_questions = 10  # Количество вопросов фиксированное
        self.questions_asked = 0  # Track how many questions have been asked

        self.question_label = tk.Label(root, text="Выберите операцию:")
        self.question_label.pack()

        self.operation_var = tk.StringVar(value="1")

        operations = [("Сложение", "1"), ("Вычитание", "4"),
                      ("Умножение", "2"), ("Деление", "3"),
                      ("Квадрат чисел", "5"), ("Квадратный корень", "6")]

        for text, value in operations:
            tk.Radiobutton(root, text=text, variable=self.operation_var, value=value).pack(anchor=tk.W)

        self.answer_label = tk.Label(root, text="Ваш ответ:")
        self.answer_label.pack()

        self.answer_entry = tk.Entry(root)
        self.answer_entry.pack()

        self.submit_button = tk.Button(root, text="Подтвердить", command=self.submit_answer)
        self.submit_button.pack()

        self.feedback_label = tk.Label(root, text="")
        self.feedback_label.pack()

        self.exit_button = tk.Button(root, text="Выход", command=self.root.quit)  # Кнопка выхода
        self.exit_button.pack()

        # Запускаем тренировку сразу при старте
        self.ask_question()

    def ask_question(self):
        operation = self.operation_var.get()

        if operation == "1":  # Addition
            self.num1, self.num2, self.correct_result = addition_training()
            self.question_label.config(text=f"{self.num1} + {self.num2} = ?")

        elif operation == "4":  # Subtraction
            self.num1, self.num2, self.correct_result = subtraction_training()
            self.question_label.config(text=f"{self.num1} - {self.num2} = ?")

        elif operation == "2":  # Multiplication
            self.num1, self.num2, self.correct_result = multiplication_training()
            self.question_label.config(text=f"{self.num1} * {self.num2} = ?")

        elif operation == "3":  # Division
            divisible_number, self.num1, self.correct_result = division_training()
            self.question_label.config(text=f"{divisible_number} / {self.num1} = ?")

        elif operation == "5":  # Square
            self.num, self.correct_result = square_training()
            self.question_label.config(text=f"Квадрат числа {self.num} = ?")

        elif operation == "6":  # Square Root
            self.num, self.correct_result = sqrt_training()
            self.question_label.config(text=f"Корень числа {self.num} = ?")

    def submit_answer(self):
        try:
            user_response = int(self.answer_entry.get())
            self.questions_asked += 1
            
            if user_response == self.correct_result:
                self.score += 1
                self.feedback_label.config(text="Все верно!")
            else:
                self.feedback_label.config(text=f"Неправильный ответ! Правильный: {self.correct_result}.")

            if self.questions_asked < self.total_questions:
                self.ask_question()
                self.answer_entry.delete(0, tk.END)  # Очищаем поле ввода
            else:
                final_score = (self.score / self.total_questions) * 100
                messagebox.showinfo("Итог", f"Ваша оценка: {final_score:.2f}%")
                self.root.quit()  # Закрываем приложение после завершения
        except ValueError:
            messagebox.showerror("Ошибка", "Пожалуйста, введите корректное число.")


if __name__ == "__main__":  # Fixed syntax
    root = tk.Tk()
    app = MathTrainerApp(root)
    root.mainloop()