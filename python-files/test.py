import tkinter as tk
from tkinter import messagebox, simpledialog
from tkinter import ttk

class QuizApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Тест по Python и Pascal")
        self.root.geometry("1250x600")
        self.root.configure(bg='#B0E0E6')
        self.root.resizable(False, False)

        self.questions = [
            {
                "type": "text",
                "question": "1. Как называется функция, используемая для вывода информации на экран в Python?",
                "answer": "print"
            },
            {
                "type": "text",
                "question": "2. Какой оператор используется для присваивания значения переменной?",
                "answer": "="
            },
            {
                "type": "multiple_choice",
                "question": "3. Какие из перечисленных типов данных являются изменяемыми (mutable) в Python? (Выберите все подходящие варианты)",
                "options": ["int", "list", "tuple", "dict", "str"],
                "correct_indices": [1, 3]
            },
            {
                "type": "multiple_choice",
                "question": "4. Какие из перечисленных ключевых слов используются для создания циклов в Python? (Выберите все подходящие варианты)",
                "options": ["if", "for", "while", "else", "loop"],
                "correct_indices": [1, 2]
            },
            {
                "type": "multiple_choice",
                "question": "5. Какие из перечисленных символов используются для комментирования кода в Python? (Выберите все подходящие варианты)",
                "options": ["//", "/* */", "#", "--", "''' '''"],
                "correct_indices": [2, 4]
            },
            {
                "type": "single_choice",  # Изменено на single_choice
                "question": "6. Как открыть файл в режиме чтения?",
                "options": ["open(\"file.txt\", \"r\")", "open(\"file.txt\", \"read\")", "open(\"file.txt\", \"w\")", "open(\"file.txt\", \"a\")"],
                "correct_index": 0
            },
            {
                "type": "single_choice",  # Изменено на single_choice
                "question": "7. Какой метод удаляет элемент из списка по значению?",
                "options": [".pop()", ".remove()", ".delete()", ".clear()"],
                "correct_index": 1
            },
            {
                "type": "single_choice",  # Изменено на single_choice
                "question": "8. Какой оператор вывода в Pascal?",
                "options": ["print()", "writeln()", "echo()", "output()"],
                "correct_index": 1
            },
            {
                "type": "single_choice",  # Изменено на single_choice
                "question": "9. Как объявить переменную в Pascal?",
                "options": ["var x = 10;", "int x := 10;", "x: integer = 10;", "var x: integer;"],
                "correct_index": 3
            },
            {
                "type": "single_choice",  # Изменено на single_choice
                "question": "10. Как записать условие if в Pascal?",
                "options": ["if (x > 10) then", "if x > 10:", "if {x > 10} then", "when x > 10 then"],
                "correct_index": 0
            },
            {
                "type": "single_choice",  # Изменено на single_choice
                "question": "11. Какой цикл есть в Pascal, но отсутствует в Python?",
                "options": ["for", "while", "repeat ... until", "loop"],
                "correct_index": 2
            },
            {
                "type": "single_choice",  # Изменено на single_choice
                "question": "12. Как объявить массив в Pascal?",
                "options": ["array [1..10] of integer;", "list = [1, 2, 3]", "int arr[10];", "array (1 to 10) as integer"],
                "correct_index": 0
            },
            {
                "type": "single_choice",  # Изменено на single_choice
                "question": "13. Какой оператор используется для ввода данных?",
                "options": ["input()", "readln()", "scan()", "get()"],
                "correct_index": 1
            },
            {
                "type": "single_choice",  # Изменено на single_choice
                "question": "14. Как завершить программу в Pascal?",
                "options": ["exit", "end.", "stop", "break"],
                "correct_index": 1
            },
            {
                "type": "single_choice",  # Изменено на single_choice
                "question": "15. Как записать комментарий в Pascal?",
                "options": ["# Комментарий", "// Комментарий", "/* Комментарий */", "-- Комментарий"],
                "correct_index": 1
            }
        ]

        self.current_question = 0
        self.score = 0
        self.user_answers = [None] * len(self.questions)
        self.time_left = 6 * 60  # 6 минут в секундах
        self.timer_running = False

        self.create_widgets()
        self.show_welcome_frame()

    def create_widgets(self):
        self.welcome_frame = tk.Frame(self.root, bg='#B0E0E6')
        self.welcome_frame.pack(fill="both", expand=True)

        self.quiz_frame = tk.Frame(self.root, bg='#B0E0E6')

        self.create_welcome_widgets()
        self.create_quiz_widgets()

    def create_welcome_widgets(self):
        self.welcome_label = tk.Label(
            self.welcome_frame,
            text="Добро пожаловать на тест по языку Python и Pascal!\n\n"
                 "Вам предстоит ответить на 15 вопросов разного типа.\n"
                 "На выполнение теста отводится 15 минут.\n"
                 "Пожалуйста, внимательно читайте вопросы и отвечайте обдуманно.\n\n"
                 "Ваш результат будет представлен в виде процентного соотношения правильных ответов.\n\nУдачи!",
            font=("Arial", 20),
            justify="center",
            bg='#B0E0E6'
        )
        self.welcome_label.pack(pady=50)

        self.start_button = tk.Button(
            self.welcome_frame,
            text="Начать тест",
            command=self.start_test,
            bg='#4CAF50',
            fg='white',
            font=('Arial', 20),
            relief=tk.RAISED,
            border=3
        )
        self.start_button.pack(pady=20)

    def create_quiz_widgets(self):
        self.timer_label = tk.Label(
            self.quiz_frame,
            text="Осталось времени: 6:00",
            font=("Arial", 24, "bold"),
            bg='#B0E0E6'
        )
        self.timer_label.pack(pady=10)

        self.question_label = tk.Label(
            self.quiz_frame,
            text="",
            font=("Arial", 20),
            wraplength=700,
            justify="center",
            bg='#B0E0E6'
        )
        self.question_label.pack(pady=20)

        self.answer_frame = tk.Frame(self.quiz_frame, bg='#B0E0E6')
        self.answer_frame.pack()

        self.answer_widgets = []

        self.nav_frame = tk.Frame(self.quiz_frame, bg='#B0E0E6')
        self.nav_frame.pack(pady=20)

        self.prev_button = tk.Button(
            self.nav_frame,
            text="Назад",
            command=self.prev_question,
            state=tk.DISABLED,
            bg='#59E900',
            fg='black',
            font=('Arial', 20),
            relief=tk.RAISED,
            border=3
        )
        self.prev_button.pack(side=tk.LEFT, padx=10)

        self.next_button = tk.Button(
            self.nav_frame,
            text="Вперед",
            command=self.next_question,
            bg="#59E900",
            fg='black',
            font=('Arial', 20),
            relief=tk.RAISED,
            border=3
        )
        self.next_button.pack(side=tk.LEFT, padx=10)

        self.progress_label = tk.Label(
            self.quiz_frame,
            text="",
            font=("Arial", 20),
            bg='#B0E0E6'
        )
        self.progress_label.pack(pady=10)

    def show_welcome_frame(self):
        self.quiz_frame.pack_forget()
        self.welcome_frame.pack(fill="both", expand=True)

    def show_quiz_frame(self):
        self.welcome_frame.pack_forget()
        self.quiz_frame.pack(fill="both", expand=True)

    def start_test(self):
        self.show_quiz_frame()
        self.time_left = 6 * 60
        self.timer_running = True
        self.update_timer()
        self.show_question()

    def update_timer(self):
        if self.timer_running:
            minutes = self.time_left // 60
            seconds = self.time_left % 60
            self.timer_label.config(text=f"Осталось времени: {minutes:02d}:{seconds:02d}")

            if self.time_left <= 60:
                self.timer_label.config(fg='red')
            else:
                self.timer_label.config(fg='black')

            if self.time_left > 0:
                self.time_left -= 1
                self.root.after(1000, self.update_timer)
            else:
                self.finish_quiz()

    def show_question(self):
        # Clear any existing answer widgets
        for widget in self.answer_widgets:
            widget.destroy()
        self.answer_widgets = []

        question_data = self.questions[self.current_question]
        self.question_label.config(text=question_data["question"])

        if question_data["type"] == "text":
            self.show_text_input(question_data)
        elif question_data["type"] == "multiple_choice":
            self.show_multiple_choice(question_data)
        elif question_data["type"] == "single_choice":
            self.show_single_choice(question_data)

        self.progress_label.config(text=f"Вопрос {self.current_question + 1} из {len(self.questions)}")
        self.update_button_states()

    def show_text_input(self, question_data):
        self.answer_entry = tk.Entry(self.answer_frame, font=("Arial", 20))
        self.answer_entry.pack(pady=10)
        self.answer_widgets.append(self.answer_entry)

        if self.user_answers[self.current_question] is not None:
            self.answer_entry.insert(0, self.user_answers[self.current_question])

    def show_multiple_choice(self, question_data):
        self.choice_vars = [tk.BooleanVar() for _ in range(len(question_data["options"]))]
        for i, option in enumerate(question_data["options"]):
            cb = tk.Checkbutton(
                self.answer_frame,
                text=option,
                variable=self.choice_vars[i],
                font=("Arial", 20),
                bg='#B0E0E6',
                selectcolor='#B0E0E6'
            )
            cb.pack(anchor="w", padx=200, pady=5)
            self.answer_widgets.append(cb)

        if self.user_answers[self.current_question] is not None:
            for i, val in enumerate(self.user_answers[self.current_question]):
                self.choice_vars[i].set(val)

    def show_single_choice(self, question_data):
        self.radio_var = tk.IntVar()
        self.radio_buttons = []
        for i, option in enumerate(question_data["options"]):
            rb = tk.Radiobutton(
                self.answer_frame,
                text=option,
                variable=self.radio_var,
                value=i,
                font=("Arial", 20),
                bg='#B0E0E6',
                selectcolor='#B0E0E6'
            )
            rb.pack(anchor="w", padx=200, pady=5)
            self.radio_buttons.append(rb)
            self.answer_widgets.append(rb)

        if self.user_answers[self.current_question] is not None:
            self.radio_var.set(self.user_answers[self.current_question])
        else:
            self.radio_var.set(-1)

    def get_user_answer(self):
        question_data = self.questions[self.current_question]
        if question_data["type"] == "text":
            return self.answer_entry.get().strip().lower()
        elif question_data["type"] == "multiple_choice":
            return [var.get() for var in self.choice_vars]
        elif question_data["type"] == "single_choice":
            return self.radio_var.get()

    def next_question(self):
        user_answer = self.get_user_answer()

        if user_answer is None or (isinstance(user_answer, str) and not user_answer) or (isinstance(user_answer, int) and user_answer == -1):
            messagebox.showwarning("Ответ не введен", "Пожалуйста, введите ответ.")
            return

        self.user_answers[self.current_question] = user_answer
        self.current_question += 1

        if self.current_question < len(self.questions):
            self.show_question()
        else:
            self.finish_quiz()

    def prev_question(self):
        self.current_question -= 1
        self.show_question()

    def update_button_states(self):
        self.prev_button.config(state=tk.NORMAL if self.current_question > 0 else tk.DISABLED)
        self.next_button.config(text="Завершить" if self.current_question == len(self.questions) - 1 else "Вперед")

    def finish_quiz(self):
        self.timer_running = False
        self.calculate_score()

        result = f"Правильных ответов: {self.score} из {len(self.questions)}\n"
        result += f"Процент правильных ответов: {self.score / len(self.questions) * 100:.1f}%"

        # Модифицированный messagebox
        if messagebox.showinfo("Результаты теста", result) == "ok":  # Закрываем окно
            self.root.destroy()

    def calculate_score(self):
        self.score = 0
        for i, question in enumerate(self.questions):
            if question["type"] == "text":
                correct_answer = question["answer"].lower()
                if self.user_answers[i] == correct_answer:
                    self.score += 1
            elif question["type"] == "multiple_choice":
                correct_indices = question["correct_indices"]
                user_choices = self.user_answers[i]
                correct_selections = [question["options"][index] for index in correct_indices]

                selected_options = [question["options"][j] for j, selected in enumerate(user_choices) if selected]

                if set(selected_options) == set(correct_selections):
                    self.score += 1
            elif question["type"] == "single_choice":
                if self.user_answers[i] == question["correct_index"]:
                    self.score += 1


def main():
    root = tk.Tk()
    QuizApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()