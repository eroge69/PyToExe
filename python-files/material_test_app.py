
import tkinter as tk
from tkinter import messagebox

questions = [{"question": "Диаметр отпечатка измеряют при определении твердости методом:", "options": ["а) Бринелля", "б) Виккерса", "в) Роквелла алмазным конусом", "г) Роквелла шариком"], "answer": 0}, {"question": "Способность материала сопротивляться внедрению в него другого более твердого тела — это:", "options": ["а) прочность", "б) упругость", "в) пластичность", "г) твердость"], "answer": 3}, {"question": "Твердость металла, измеренная по методу Роквелла с алмазным конусом, обозначается:", "options": ["а) НВ", "б) НУ", "в) НКВ", "г) ИКС"], "answer": 3}]

class QuizApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Материаловедение | Тест")
        self.score = 0
        self.q_index = 0

        self.question_label = tk.Label(root, text="", wraplength=600, justify="left", font=("Arial", 14))
        self.question_label.pack(pady=20)

        self.var = tk.IntVar()
        self.option_buttons = []
        for i in range(4):
            b = tk.Radiobutton(root, text="", variable=self.var, value=i, font=("Arial", 12))
            b.pack(anchor="w")
            self.option_buttons.append(b)

        self.feedback_label = tk.Label(root, text="", font=("Arial", 12, "italic"))
        self.feedback_label.pack(pady=5)

        self.next_button = tk.Button(root, text="Ответить", command=self.check_answer)
        self.next_button.pack(pady=20)

        self.display_question()

    def display_question(self):
        q = questions[self.q_index]
        self.question_label.config(text=f"Вопрос {self.q_index + 1}: " + q['question'])
        for i, option in enumerate(q['options']):
            self.option_buttons[i].config(text=option)
        self.var.set(-1)
        self.feedback_label.config(text="")
        self.next_button.config(text="Ответить", command=self.check_answer)

    def check_answer(self):
        selected = self.var.get()
        correct = questions[self.q_index]['answer']
        if selected == correct:
            self.score += 1
            self.feedback_label.config(text="Верно!", fg="green")
        else:
            correct_text = questions[self.q_index]['options'][correct]
            self.feedback_label.config(text=f"Неверно. Правильный ответ: {correct_text}", fg="red")
        self.next_button.config(text="Далее", command=self.next_question)

    def next_question(self):
        self.q_index += 1
        if self.q_index < len(questions):
            self.display_question()
        else:
            self.finish_quiz()

    def finish_quiz(self):
        percent = int((self.score / len(questions)) * 100)
        if percent >= 80:
            grade = "Отлично"
        elif percent >= 70:
            grade = "Хорошо"
        elif percent >= 60:
            grade = "Удовлетворительно"
        else:
            grade = "Неудовлетворительно"
        messagebox.showinfo("Результат", f"Вы ответили правильно на {self.score} из {len(questions)} вопросов ({percent}%)\nОценка: {grade}")
        self.root.quit()

root = tk.Tk()
app = QuizApp(root)
root.mainloop()
