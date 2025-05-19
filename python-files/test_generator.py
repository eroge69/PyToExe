import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import sqlite3
import json

class TestGeneratorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Генератор тестов")
        self.root.geometry("800x600")

        try:
            self.conn = sqlite3.connect("test_generator.db")
            self.cursor = self.conn.cursor()
            self.create_tables()
        except sqlite3.Error as e:
            messagebox.showerror("Ошибка", f"Не удалось подключиться к базе данных: {e}")
            self.root.quit()
            return

        self.create_main_interface()

    def create_tables(self):
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS tests (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                subject TEXT NOT NULL
            )""")
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS questions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                test_id INTEGER,
                question_text TEXT NOT NULL,
                correct_answer TEXT NOT NULL,
                FOREIGN KEY (test_id) REFERENCES tests(id)
            )""")
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                test_id INTEGER,
                user_name TEXT,
                score INTEGER,
                date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (test_id) REFERENCES tests(id)
            )""")
        self.conn.commit()

    def create_main_interface(self):
        nav_frame = ttk.Frame(self.root)
        nav_frame.pack(pady=10)

        ttk.Button(nav_frame, text="Список тестов", command=self.show_test_list).pack(side=tk.LEFT, padx=5)
        ttk.Button(nav_frame, text="Добавить тест", command=self.add_test_window).pack(side=tk.LEFT, padx=5)
        ttk.Button(nav_frame, text="Поиск теста", command=self.search_test_window).pack(side=tk.LEFT, padx=5)
        ttk.Button(nav_frame, text="Экспорт тестов", command=self.export_tests).pack(side=tk.LEFT, padx=5)
        ttk.Button(nav_frame, text="Импорт тестов", command=self.import_tests).pack(side=tk.LEFT, padx=5)

        self.main_frame = ttk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        self.show_test_list()

    def clear_frame(self, frame):
        for widget in frame.winfo_children():
            widget.destroy()

    def show_test_list(self):
        self.clear_frame(self.main_frame)
        
        tree_frame = ttk.Frame(self.main_frame)
        tree_frame.pack(fill=tk.BOTH, expand=True)
        
        self.tree = ttk.Treeview(tree_frame, columns=("id", "name", "subject"), show="headings")
        self.tree.heading("id", text="ID")
        self.tree.heading("name", text="Название")
        self.tree.heading("subject", text="Дисциплина")
        self.tree.pack(fill=tk.BOTH, expand=True)

        self.cursor.execute("SELECT * FROM tests")
        for row in self.cursor.fetchall():
            self.tree.insert("", tk.END, values=row)

        btn_frame = ttk.Frame(self.main_frame)
        btn_frame.pack(side=tk.BOTTOM, pady=5)
        ttk.Button(btn_frame, text="Редактировать", command=self.edit_test).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Удалить", command=self.delete_test).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Вопросы", command=self.show_questions).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Пройти тест", command=self.take_test).pack(side=tk.LEFT, padx=5)

    def export_tests(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON files", "*.json")])
        if not file_path:
            return

        try:
            tests = []
            self.cursor.execute("SELECT * FROM tests")
            for test in self.cursor.fetchall():
                test_id, name, subject = test
                self.cursor.execute("SELECT question_text, correct_answer FROM questions WHERE test_id = ?", (test_id,))
                questions = [{"question_text": q[0], "correct_answer": q[1]} for q in self.cursor.fetchall()]
                tests.append({"id": test_id, "name": name, "subject": subject, "questions": questions})

            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(tests, f, ensure_ascii=False, indent=4)
            messagebox.showinfo("Успех", f"Тесты экспортированы в {file_path}")
        except sqlite3.Error as e:
            messagebox.showerror("Ошибка", f"Ошибка базы данных при экспорте: {e}")
        except IOError as e:
            messagebox.showerror("Ошибка", f"Ошибка записи файла: {e}")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Неизвестная ошибка при экспорте: {e}")

    def import_tests(self):
        file_path = filedialog.askopenfilename(filetypes=[("JSON files", "*.json")])
        if not file_path:
            return

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                tests = json.load(f)

            for test in tests:
                self.cursor.execute("INSERT INTO tests (name, subject) VALUES (?, ?)", (test['name'], test['subject']))
                test_id = self.cursor.lastrowid
                for q in test.get('questions', []):
                    self.cursor.execute("INSERT INTO questions (test_id, question_text, correct_answer) VALUES (?, ?, ?)",
                                      (test_id, q['question_text'], q['correct_answer']))
            self.conn.commit()
            messagebox.showinfo("Успех", f"Тесты импортированы из {file_path}")
            self.show_test_list()
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка импорта: {e}")

    def add_test_window(self):
        window = tk.Toplevel(self.root)
        window.title("Добавить тест")
        window.geometry("300x200")

        ttk.Label(window, text="Название:").pack(pady=5)
        name_entry = ttk.Entry(window)
        name_entry.pack(pady=5)

        ttk.Label(window, text="Дисциплина:").pack(pady=5)
        subject_entry = ttk.Entry(window)
        subject_entry.pack(pady=5)

        ttk.Button(window, text="Сохранить", command=lambda: self.save_test(name_entry.get(), subject_entry.get(), window)).pack(pady=10)

    def save_test(self, name, subject, window):
        if not name or not subject:
            messagebox.showerror("Ошибка", "Заполните все поля")
            return
        self.cursor.execute("INSERT INTO tests (name, subject) VALUES (?, ?)", (name, subject))
        self.conn.commit()
        window.destroy()
        self.show_test_list()

    def edit_test(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showerror("Ошибка", "Выберите тест")
            return

        test_id = self.tree.item(selected)["values"][0]
        window = tk.Toplevel(self.root)
        window.title("Редактировать тест")
        window.geometry("300x200")

        self.cursor.execute("SELECT name, subject FROM tests WHERE id = ?", (test_id,))
        result = self.cursor.fetchone()
        if result:
            name, subject = result
            ttk.Label(window, text="Название:").pack(pady=5)
            name_entry = ttk.Entry(window)
            name_entry.insert(0, name)
            name_entry.pack(pady=5)

            ttk.Label(window, text="Дисциплина:").pack(pady=5)
            subject_entry = ttk.Entry(window)
            subject_entry.insert(0, subject)
            subject_entry.pack(pady=5)

            ttk.Button(window, text="Сохранить", command=lambda: self.update_test(test_id, name_entry.get(), subject_entry.get(), window)).pack(pady=10)

    def update_test(self, test_id, name, subject, window):
        if not name or not subject:
            messagebox.showerror("Ошибка", "Заполните все поля")
            return
        self.cursor.execute("UPDATE tests SET name = ?, subject = ? WHERE id = ?", (name, subject, test_id))
        self.conn.commit()
        window.destroy()
        self.show_test_list()

    def delete_test(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showerror("Ошибка", "Выберите тест")
            return

        test_id = self.tree.item(selected)["values"][0]
        if messagebox.askyesno("Подтверждение", "Удалить тест?"):
            self.cursor.execute("DELETE FROM questions WHERE test_id = ?", (test_id,))
            self.cursor.execute("DELETE FROM results WHERE test_id = ?", (test_id,))
            self.cursor.execute("DELETE FROM tests WHERE id = ?", (test_id,))
            self.conn.commit()
            self.show_test_list()

    def show_questions(self, test_id=None):
        if not test_id:
            selected = self.tree.selection()
            if not selected:
                messagebox.showerror("Ошибка", "Выберите тест")
                return
            test_id = self.tree.item(selected)["values"][0]

        self.clear_frame(self.main_frame)
        self.current_test_id = test_id

        q_tree = ttk.Treeview(self.main_frame, columns=("id", "question"), show="headings")
        q_tree.heading("id", text="ID")
        q_tree.heading("question", text="Вопрос")
        q_tree.pack(fill=tk.BOTH, expand=True)

        self.cursor.execute("SELECT id, question_text FROM questions WHERE test_id = ?", (test_id,))
        for row in self.cursor.fetchall():
            q_tree.insert("", tk.END, values=row)

        btn_frame = ttk.Frame(self.main_frame)
        btn_frame.pack(side=tk.BOTTOM, pady=5)
        ttk.Button(btn_frame, text="Добавить вопрос", command=lambda: self.add_question_window(test_id)).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Редактировать", command=lambda: self.edit_question(q_tree, test_id)).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Удалить", command=lambda: self.delete_question(q_tree, test_id)).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Назад", command=self.show_test_list).pack(side=tk.LEFT, padx=5)

    def add_question_window(self, test_id):
        window = tk.Toplevel(self.root)
        window.title("Добавить вопрос")
        window.geometry("400x300")

        ttk.Label(window, text="Текст вопроса:").pack(pady=5)
        question_entry = ttk.Entry(window, width=40)
        question_entry.pack(pady=5)

        ttk.Label(window, text="Правильный ответ:").pack(pady=5)
        answer_entry = ttk.Entry(window, width=40)
        answer_entry.pack(pady=5)

        ttk.Button(window, text="Сохранить", command=lambda: self.save_question(test_id, question_entry.get(), answer_entry.get(), window)).pack(pady=10)

    def save_question(self, test_id, question, answer, window):
        if not question or not answer:
            messagebox.showerror("Ошибка", "Заполните все поля")
            return
        self.cursor.execute("INSERT INTO questions (test_id, question_text, correct_answer) VALUES (?, ?, ?)", 
                          (test_id, question, answer))
        self.conn.commit()
        window.destroy()
        self.show_questions(test_id)

    def edit_question(self, tree, test_id):
        selected = tree.selection()
        if not selected:
            messagebox.showerror("Ошибка", "Выберите вопрос")
            return

        question_id = tree.item(selected)["values"][0]
        window = tk.Toplevel(self.root)
        window.title("Редактировать вопрос")
        window.geometry("400x300")

        self.cursor.execute("SELECT question_text, correct_answer FROM questions WHERE id = ?", (question_id,))
        result = self.cursor.fetchone()
        if result:
            question, answer = result
            ttk.Label(window, text="Текст вопроса:").pack(pady=5)
            question_entry = ttk.Entry(window, width=40)
            question_entry.insert(0, question)
            question_entry.pack(pady=5)

            ttk.Label(window, text="Правильный ответ:").pack(pady=5)
            answer_entry = ttk.Entry(window, width=40)
            answer_entry.insert(0, answer)
            answer_entry.pack(pady=5)

            ttk.Button(window, text="Сохранить", command=lambda: self.update_question(question_id, question_entry.get(), answer_entry.get(), window, test_id)).pack(pady=10)

    def update_question(self, question_id, question, answer, window, test_id):
        if not question or not answer:
            messagebox.showerror("Ошибка", "Заполните все поля")
            return
        self.cursor.execute("UPDATE questions SET question_text = ?, correct_answer = ? WHERE id = ?", 
                          (question, answer, question_id))
        self.conn.commit()
        window.destroy()
        self.show_questions(test_id)

    def delete_question(self, tree, test_id):
        selected = tree.selection()
        if not selected:
            messagebox.showerror("Ошибка", "Выберите вопрос")
            return

        question_id = tree.item(selected)["values"][0]
        if messagebox.askyesno("Подтверждение", "Удалить вопрос?"):
            self.cursor.execute("DELETE FROM questions WHERE id = ?", (question_id,))
            self.conn.commit()
            self.show_questions(test_id)

    def take_test(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showerror("Ошибка", "Выберите тест")
            return

        test_id = self.tree.item(selected)["values"][0]
        self.cursor.execute("SELECT id, question_text, correct_answer FROM questions WHERE test_id = ?", (test_id,))
        self.questions = self.cursor.fetchall()

        if not self.questions:
            messagebox.showinfo("Информация", "В тесте нет вопросов")
            return

        self.clear_frame(self.main_frame)
        self.answers = {}
        self.current_question = 0

        self.question_frame = ttk.Frame(self.main_frame)
        self.question_frame.pack(pady=10, fill=tk.BOTH, expand=True)

        self.question_label = ttk.Label(self.question_frame, text=self.questions[0][1], wraplength=700)
        self.question_label.pack(pady=5)

        self.answer_entry = ttk.Entry(self.question_frame, width=50)
        self.answer_entry.pack(pady=5)

        btn_frame = ttk.Frame(self.main_frame)
        btn_frame.pack(side=tk.BOTTOM, pady=10)
        self.prev_btn = ttk.Button(btn_frame, text="Назад", command=self.prev_question, state=tk.DISABLED)
        self.prev_btn.pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Далее", command=self.next_question).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Завершить", command=self.finish_test).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Отмена", command=self.show_test_list).pack(side=tk.LEFT, padx=5)

    def next_question(self):
        current_id = self.questions[self.current_question][0]
        self.answers[current_id] = self.answer_entry.get()
        
        if self.current_question < len(self.questions) - 1:
            self.current_question += 1
            self.update_question_display()
            self.prev_btn.config(state=tk.NORMAL)

    def prev_question(self):
        current_id = self.questions[self.current_question][0]
        self.answers[current_id] = self.answer_entry.get()
        
        if self.current_question > 0:
            self.current_question -= 1
            self.update_question_display()
            if self.current_question == 0:
                self.prev_btn.config(state=tk.DISABLED)

    def update_question_display(self):
        self.question_label.config(text=self.questions[self.current_question][1])
        self.answer_entry.delete(0, tk.END)
        current_id = self.questions[self.current_question][0]
        if current_id in self.answers:
            self.answer_entry.insert(0, self.answers[current_id])

    def finish_test(self):
        current_id = self.questions[self.current_question][0]
        self.answers[current_id] = self.answer_entry.get()
        
        score = 0
        for q_id, _, correct_answer in self.questions:
            if q_id in self.answers and self.answers[q_id].strip().lower() == correct_answer.strip().lower():
                score += 1

        window = tk.Toplevel(self.root)
        window.title("Результаты")
        window.geometry("300x200")

        ttk.Label(window, text=f"Ваш результат: {score}/{len(self.questions)}").pack(pady=20)
        ttk.Label(window, text="Имя пользователя:").pack()
        name_entry = ttk.Entry(window)
        name_entry.pack(pady=5)

        ttk.Button(window, text="Сохранить", command=lambda: self.save_result(self.questions[0][0], score, name_entry.get(), window)).pack(pady=20)

    def save_result(self, test_id, score, user_name, window):
        if not user_name:
            messagebox.showerror("Ошибка", "Введите имя")
            return
        self.cursor.execute("INSERT INTO results (test_id, user_name, score) VALUES (?, ?, ?)", (test_id, user_name, score))
        self.conn.commit()
        window.destroy()
        self.show_test_list()

    def search_test_window(self):
        window = tk.Toplevel(self.root)
        window.title("Поиск теста")
        window.geometry("300x200")

        ttk.Label(window, text="Название или дисциплина:").pack(pady=5)
        search_entry = ttk.Entry(window)
        search_entry.pack(pady=5)

        ttk.Button(window, text="Поиск", command=lambda: self.search_test(search_entry.get(), window)).pack(pady=10)

    def search_test(self, query, window):
        self.clear_frame(self.main_frame)
        
        tree_frame = ttk.Frame(self.main_frame)
        tree_frame.pack(fill=tk.BOTH, expand=True)
        
        self.tree = ttk.Treeview(tree_frame, columns=("id", "name", "subject"), show="headings")
        self.tree.heading("id", text="ID")
        self.tree.heading("name", text="Название")
        self.tree.heading("subject", text="Дисциплина")
        self.tree.pack(fill=tk.BOTH, expand=True)

        self.cursor.execute("SELECT * FROM tests WHERE name LIKE ? OR subject LIKE ?",
                          (f"%{query}%", f"%{query}%"))
        for row in self.cursor.fetchall():
            self.tree.insert("", tk.END, values=row)

        btn_frame = ttk.Frame(self.main_frame)
        btn_frame.pack(side=tk.BOTTOM, pady=5)
        ttk.Button(btn_frame, text="Редактировать", command=self.edit_test).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Удалить", command=self.delete_test).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Вопросы", command=self.show_questions).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Пройти тест", command=self.take_test).pack(side=tk.LEFT, padx=5)
        
        window.destroy()

def main():
    root = tk.Tk()
    app = TestGeneratorApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()