import os
import re
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import struct
import csv
import random
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_gigachat.chat_models import GigaChat

class Answer:
    def __init__(self, text=""):
        self.text = text
    
    @classmethod
    def from_binary(cls, file):
        length = struct.unpack('<i', file.read(4))[0]
        text = file.read(length * 2).decode('utf-16le')
        return cls(text)
    
    def to_binary(self, file):
        text_bytes = self.text.encode('utf-16le')
        file.write(struct.pack('<i', len(self.text)))
        file.write(text_bytes)

class Question:
    MAX_ANSWERS = 4
    
    def __init__(self, text="", correct_answer=0):
        self.text = text
        self.correct_answer = correct_answer
        self.answers = [Answer() for _ in range(self.MAX_ANSWERS)]
    
    @classmethod
    def from_binary(cls, file):
        correct_answer = struct.unpack('<B', file.read(1))[0]
        length = struct.unpack('<i', file.read(4))[0]
        text = file.read(length * 2).decode('utf-16le')
        question = cls(text, correct_answer)
        
        answers_count = struct.unpack('<i', file.read(4))[0]
        for i in range(min(answers_count, cls.MAX_ANSWERS)):
            question.answers[i] = Answer.from_binary(file)
        
        return question
    
    def to_binary(self, file):
        file.write(struct.pack('<B', self.correct_answer))
        text_bytes = self.text.encode('utf-16le')
        file.write(struct.pack('<i', len(self.text)))
        file.write(text_bytes)
        file.write(struct.pack('<i', len(self.answers)))
        for answer in self.answers:
            answer.to_binary(file)

class ContestFile:
    def __init__(self, filename=None):
        self.questions = []
        if filename:
            self.load(filename)
    
    def load(self, filename):
        try:
            if filename.endswith('.data'):
                self.load_binary(filename)
            elif filename.endswith('.csv'):
                self.load_csv(filename)
            else:
                messagebox.showerror("Ошибка", "Неподдерживаемый формат файла")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить файл: {filename}\n{str(e)}")
    
    def load_binary(self, filename):
        with open(filename, 'rb') as file:
            questions_count = struct.unpack('<i', file.read(4))[0]
            for _ in range(questions_count):
                self.questions.append(Question.from_binary(file))
    
    def load_csv(self, filename):
        with open(filename, 'r', encoding='utf-8') as file:
            reader = csv.reader(file, delimiter=';')
            for row in reader:
                if len(row) >= 6:
                    question = Question(row[0], int(row[5]))
                    for i in range(4):
                        if i+1 < len(row):
                            question.answers[i].text = row[i+1]
                    self.questions.append(question)
    
    def save(self, filename):
        try:
            if filename.endswith('.data'):
                self.save_binary(filename)
            elif filename.endswith('.csv'):
                self.save_csv(filename)
            else:
                messagebox.showerror("Ошибка", "Неподдерживаемый формат файла")
                return False
            return True
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить файл: {filename}\n{str(e)}")
            return False
    
    def save_binary(self, filename):
        with open(filename, 'wb') as file:
            file.write(struct.pack('<i', len(self.questions)))
            for question in self.questions:
                question.to_binary(file)
    
    def save_csv(self, filename):
        with open(filename, 'w', encoding='utf-8', newline='') as file:
            writer = csv.writer(file, delimiter=';')
            for question in self.questions:
                row = [question.text]
                row.extend([answer.text for answer in question.answers])
                row.append(question.correct_answer)
                writer.writerow(row)

class GigaChatAPI:
    def __init__(self):
        self.credentials = ""
        self.giga = None
    
    def set_credentials(self, credentials):
        self.credentials = credentials
        if credentials:
            self.giga = GigaChat(
                credentials=credentials,
                verify_ssl_certs=False,
                model='GigaChat-Max'
            )
        else:
            self.giga = None
    
    def generate_questions(self, topic, count=5, existing_questions=None):
        if not self.giga:
            messagebox.showerror("Ошибка", "Не установлены учетные данные GigaChat")
            return []

        if existing_questions is None:
            existing_questions = []

        questions = []
        attempts = 0
        max_attempts = 5
        
        while len(questions) < count and attempts < max_attempts:
            prompt = f"""Сгенерируй {count - len(questions)} уникальных вопросов по теме "{topic}". Требования:
1. Конкретный вопрос
2. Ровно 4 варианта ответа (A-D)
3. Указание правильного ответа
4. Не повторять: {[q['question'][:30] + '...' for q in existing_questions][:3]}

Формат:
Вопрос: [Вопрос?]
A) [Вариант A]
B) [Вариант B]
C) [Вариант C]
D) [Вариант D]
Ответ: [A-D]"""

            try:
                messages = [
                    SystemMessage(content="Ты профессиональный составитель викторин."),
                    HumanMessage(content=prompt)
                ]
                response = self.giga.invoke(messages)
                new_questions = self.parse_questions(response.content, count - len(questions), topic)
                
                existing_texts = {q['question'].lower() for q in existing_questions + questions}
                for q in new_questions:
                    if q['question'].lower() not in existing_texts:
                        questions.append(q)
                        existing_texts.add(q['question'].lower())
                
                attempts += 1
                
            except Exception as e:
                messagebox.showerror("Ошибка", f"Ошибка генерации: {str(e)}")
                break

        return questions[:count]

    def parse_questions(self, text, expected_count, topic):
        questions = []
        current = {"question": "", "answers": [], "correct": 0}
        
        for line in text.split('\n'):
            line = line.strip()
            
            if not line or line.startswith(("#", "//")):
                continue
                
            if re.match(r'^(вопрос:|q:|[0-9]+[.)])', line, re.IGNORECASE):
                if current["question"] and len(current["answers"]) == 4:
                    questions.append(current)
                    if len(questions) >= expected_count:
                        break
                    current = {"question": "", "answers": [], "correct": 0}
                
                question_text = re.split(r'[:)]', line, maxsplit=1)[-1].strip()
                if question_text and not question_text.startswith(("[", "пример")):
                    current["question"] = question_text
            
            elif re.match(r'^[A-D][).]', line, re.IGNORECASE):
                answer_text = line[2:].strip()
                if answer_text and not answer_text.startswith(("[", "вариант")):
                    idx = ord(line[0].upper()) - ord('A')
                    while len(current["answers"]) <= idx:
                        current["answers"].append("")
                    current["answers"][idx] = answer_text
            
            elif re.match(r'^(ответ|правильный ответ?)\s*[:]', line, re.IGNORECASE):
                ans = re.sub(r'.*([A-D]).*', r'\1', line.upper())
                if ans in ("A", "B", "C", "D"):
                    current["correct"] = ord(ans) - ord('A')
        
        if current["question"] and len(current["answers"]) == 4:
            questions.append(current)
        
        return questions

class ZhuxianQuestEditor:
    def __init__(self, root):
        self.root = root
        self.root.title("Zhuxian Quest Editor (GigaChat)")
        self.root.geometry("1000x800")
        
        self.current_file = None
        self.contest_file = ContestFile()
        self.current_question_index = -1
        self.correct_answer_var = tk.IntVar(value=-1)
        
        self.gigachat = GigaChatAPI()
        
        self.create_menu()
        self.create_widgets()
        self.create_ai_panel()
        self.update_title()
    
    def create_menu(self):
        menubar = tk.Menu(self.root)
        
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Новый", command=self.new_file, accelerator="Ctrl+N")
        file_menu.add_command(label="Открыть", command=self.open_file, accelerator="Ctrl+O")
        file_menu.add_command(label="Сохранить", command=self.save_file, accelerator="Ctrl+S")
        file_menu.add_command(label="Сохранить как", command=self.save_file_as)
        file_menu.add_separator()
        file_menu.add_command(label="Выход", command=self.root.quit)
        
        edit_menu = tk.Menu(menubar, tearoff=0)
        edit_menu.add_command(label="Добавить вопрос", command=self.add_question, accelerator="Ctrl+Q")
        edit_menu.add_command(label="Удалить вопрос", command=self.remove_question)
        
        settings_menu = tk.Menu(menubar, tearoff=0)
        settings_menu.add_command(label="Настройки GigaChat API", command=self.show_settings_dialog)
        
        menubar.add_cascade(label="Файл", menu=file_menu)
        menubar.add_cascade(label="Правка", menu=edit_menu)
        menubar.add_cascade(label="Настройки", menu=settings_menu)
        
        self.root.config(menu=menubar)
        
        self.root.bind("<Control-n>", lambda e: self.new_file())
        self.root.bind("<Control-o>", lambda e: self.open_file())
        self.root.bind("<Control-s>", lambda e: self.save_file())
        self.root.bind("<Control-q>", lambda e: self.add_question())
    
    def show_settings_dialog(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("Настройки GigaChat API")
        dialog.geometry("400x200")
        
        ttk.Label(dialog, text="Ключ авторизации:").pack(pady=(10, 0))
        auth_key_entry = ttk.Entry(dialog, width=40)
        auth_key_entry.pack(pady=5)
        
        if self.gigachat.credentials:
            auth_key_entry.insert(0, self.gigachat.credentials)
        
        def save_settings():
            self.gigachat.set_credentials(auth_key_entry.get())
            dialog.destroy()
            messagebox.showinfo("Настройки", "Учетные данные сохранены!")
        
        ttk.Button(dialog, text="Сохранить", command=save_settings).pack(pady=10)
    
    def create_widgets(self):
        main_pane = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        main_pane.pack(fill=tk.BOTH, expand=True)
        
        left_pane = ttk.PanedWindow(main_pane, orient=tk.VERTICAL)
        main_pane.add(left_pane)
        
        questions_frame = ttk.LabelFrame(left_pane, text="Список вопросов", padding=5)
        left_pane.add(questions_frame)
        
        scrollbar = ttk.Scrollbar(questions_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.questions_listbox = tk.Listbox(
            questions_frame,
            height=15,
            yscrollcommand=scrollbar.set,
            selectbackground="#4a6984",
            selectforeground="#ffffff"
        )
        self.questions_listbox.pack(fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.questions_listbox.yview)
        self.questions_listbox.bind('<<ListboxSelect>>', self.on_question_select)
        
        buttons_frame = ttk.Frame(questions_frame)
        buttons_frame.pack(fill=tk.X, pady=5)
        
        ttk.Button(buttons_frame, text="Добавить", command=self.add_question).pack(side=tk.LEFT, padx=2)
        ttk.Button(buttons_frame, text="Удалить", command=self.remove_question).pack(side=tk.LEFT, padx=2)
        
        right_pane = ttk.PanedWindow(main_pane, orient=tk.VERTICAL)
        main_pane.add(right_pane)
        
        question_frame = ttk.LabelFrame(right_pane, text="Редактор вопроса", padding=5)
        right_pane.add(question_frame)
        
        self.question_text = tk.Text(question_frame, height=5, wrap=tk.WORD)
        self.question_text.pack(fill=tk.X)
        self.question_text.bind("<KeyRelease>", lambda e: self.save_current_question())
        
        answers_frame = ttk.LabelFrame(right_pane, text="Ответы (выберите один правильный)", padding=5)
        right_pane.add(answers_frame)
        
        self.answer_texts = []
        for i in range(Question.MAX_ANSWERS):
            answer_frame = ttk.Frame(answers_frame)
            answer_frame.pack(fill=tk.X, pady=2)
            
            rb = ttk.Radiobutton(
                answer_frame,
                variable=self.correct_answer_var,
                value=i,
                command=lambda v=i: self.set_correct_answer(v)
            )
            rb.pack(side=tk.LEFT, padx=5)
            
            ttk.Label(answer_frame, text=f"{chr(65+i)}.", width=3).pack(side=tk.LEFT)
            
            text = tk.Text(answer_frame, height=2, wrap=tk.WORD)
            text.pack(fill=tk.X, expand=True, padx=5)
            text.bind("<KeyRelease>", lambda e, idx=i: self.save_answer_text(idx))
            self.answer_texts.append(text)
    
    def create_ai_panel(self):
        ai_frame = ttk.LabelFrame(self.root, text="Генератор вопросов GigaChat", padding=5)
        ai_frame.pack(fill=tk.BOTH, padx=5, pady=5)
        
        topic_frame = ttk.Frame(ai_frame)
        topic_frame.pack(fill=tk.X, pady=5)
        ttk.Label(topic_frame, text="Тема вопросов:").pack(side=tk.LEFT)
        self.topic_entry = ttk.Entry(topic_frame)
        self.topic_entry.pack(fill=tk.X, expand=True, padx=5)
        
        count_frame = ttk.Frame(ai_frame)
        count_frame.pack(fill=tk.X, pady=5)
        ttk.Label(count_frame, text="Количество вопросов:").pack(side=tk.LEFT)
        self.questions_count_var = tk.IntVar(value=5)
        ttk.Spinbox(count_frame, from_=1, to=1000, textvariable=self.questions_count_var).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(ai_frame, 
                 text="Добавить вопросы", 
                 command=self.add_ai_questions).pack(pady=5)
        
        self.progress = ttk.Progressbar(ai_frame, orient=tk.HORIZONTAL, mode='determinate')
        self.progress.pack(fill=tk.X, pady=5)
        
        self.status_label = ttk.Label(ai_frame, text="Готов к генерации вопросов")
        self.status_label.pack()
    
    def add_ai_questions(self):
        topic = self.topic_entry.get()
        if not topic:
            messagebox.showerror("Ошибка", "Введите тему вопросов")
            return
        
        if not self.gigachat.credentials:
            messagebox.showerror("Ошибка", "Сначала настройте ключ авторизации")
            self.show_settings_dialog()
            return
        
        try:
            num_questions = self.questions_count_var.get()
            
            self.status_label.config(text="Генерация вопросов...")
            self.progress['value'] = 0
            self.root.update()
            
            existing = [{"question": q.text, "answers": [a.text for a in q.answers]} 
                       for q in self.contest_file.questions]
            
            new_questions_data = self.gigachat.generate_questions(
                topic, 
                num_questions,
                existing_questions=existing
            )
            
            if not new_questions_data:
                self.status_label.config(text="Не удалось сгенерировать вопросы")
                return
            
            added_count = 0
            for q in new_questions_data:
                question = Question(q["question"], q["correct"])
                for i in range(Question.MAX_ANSWERS):
                    if i < len(q["answers"]):
                        question.answers[i].text = q["answers"][i]
                
                self.contest_file.questions.append(question)
                added_count += 1
            
            self.progress['value'] = 100
            self.status_label.config(text=f"Добавлено {added_count} новых вопросов")
            self.update_questions_list()
            
            if self.contest_file.questions:
                self.questions_listbox.selection_set(len(self.contest_file.questions) - 1)
                self.on_question_select(None)
            
            messagebox.showinfo("Готово", f"Успешно добавлено {added_count} вопросов")
            
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка при генерации: {str(e)}")
            self.status_label.config(text="Ошибка генерации")
    
    def on_question_select(self, event):
        if not self.contest_file.questions:
            self.clear_question_editor()
            return
            
        selection = self.questions_listbox.curselection()
        if not selection:
            return
        
        try:
            self.save_current_question()
            
            index = selection[0]
            if index >= len(self.contest_file.questions):
                return
                
            self.current_question_index = index
            question = self.contest_file.questions[index]
            
            self.question_text.delete("1.0", tk.END)
            self.question_text.insert(tk.END, question.text)
            
            for i in range(Question.MAX_ANSWERS):
                self.answer_texts[i].delete("1.0", tk.END)
                if i < len(question.answers):
                    self.answer_texts[i].insert(tk.END, question.answers[i].text)
            
            self.correct_answer_var.set(question.correct_answer)
            self.update_title()
        except Exception as e:
            print(f"Ошибка при выборе вопроса: {e}")
    
    def save_current_question(self):
        if self.current_question_index == -1 or not self.contest_file.questions:
            return
        
        try:
            if self.current_question_index >= len(self.contest_file.questions):
                return
                
            question = self.contest_file.questions[self.current_question_index]
            question.text = self.question_text.get("1.0", tk.END).strip()
            question.correct_answer = self.correct_answer_var.get()
            
            for i in range(Question.MAX_ANSWERS):
                question.answers[i].text = self.answer_texts[i].get("1.0", tk.END).strip()
            
            self.update_questions_list()
        except Exception as e:
            print(f"Ошибка сохранения вопроса: {e}")
    
    def save_answer_text(self, answer_index):
        if self.current_question_index == -1 or not self.contest_file.questions:
            return
        
        try:
            question = self.contest_file.questions[self.current_question_index]
            question.answers[answer_index].text = self.answer_texts[answer_index].get("1.0", tk.END).strip()
            self.update_questions_list()
        except Exception as e:
            print(f"Ошибка сохранения ответа: {e}")
    
    def set_correct_answer(self, answer_index):
        if self.current_question_index != -1 and self.contest_file.questions:
            try:
                self.contest_file.questions[self.current_question_index].correct_answer = answer_index
            except Exception as e:
                print(f"Ошибка установки правильного ответа: {e}")
    
    def new_file(self):
        if self.current_file or len(self.contest_file.questions) > 0:
            if not messagebox.askyesno("Новый файл", "Вы уверены? Все несохраненные изменения будут потеряны."):
                return
        
        self.contest_file = ContestFile()
        self.current_file = None
        self.current_question_index = -1
        self.update_questions_list()
        self.clear_question_editor()
        self.update_title()
    
    def open_file(self):
        filename = filedialog.askopenfilename(
            title="Открыть файл квеста",
            filetypes=[("Файлы квестов", "*.data"), ("CSV файлы", "*.csv"), ("Все файлы", "*.*")]
        )
        if filename:
            if self.current_file or len(self.contest_file.questions) > 0:
                if not messagebox.askyesno("Открыть файл", "Вы уверены? Все несохраненные изменения будут потеряны."):
                    return
            
            self.current_file = filename
            self.contest_file = ContestFile(filename)
            self.current_question_index = -1
            self.update_questions_list()
            if self.contest_file.questions:
                self.questions_listbox.selection_set(0)
                self.on_question_select(None)
            else:
                self.clear_question_editor()
            self.update_title()
    
    def save_file(self):
        if not self.current_file:
            self.save_file_as()
            return
        
        self.save_current_question()
        
        if self.contest_file.save(self.current_file):
            messagebox.showinfo("Сохранение", "Файл успешно сохранен")
            self.update_title()
    
    def save_file_as(self):
        filename = filedialog.asksaveasfilename(
            title="Сохранить файл квеста",
            defaultextension=".data",
            filetypes=[("Файлы квестов", "*.data"), ("CSV файлы", "*.csv"), ("Все файлы", "*.*")]
        )
        if filename:
            self.current_file = filename
            self.save_file()
    
    def add_question(self):
        question = Question("Новый вопрос", 0)
        for i in range(Question.MAX_ANSWERS):
            question.answers[i].text = f"Ответ {chr(65+i)}"
        
        self.contest_file.questions.append(question)
        self.update_questions_list()
        self.questions_listbox.selection_clear(0, tk.END)
        self.questions_listbox.selection_set(tk.END)
        self.on_question_select(None)
    
    def remove_question(self):
        if not self.contest_file.questions:
            return
            
        selection = self.questions_listbox.curselection()
        if not selection:
            messagebox.showwarning("Внимание", "Выберите вопрос для удаления")
            return
            
        if not messagebox.askyesno("Удаление", "Вы уверены, что хотите удалить этот вопрос?"):
            return
        
        index = selection[0]
        if index >= len(self.contest_file.questions):
            return
            
        self.contest_file.questions.pop(index)
        self.update_questions_list()
        
        if len(self.contest_file.questions) == 0:
            self.clear_question_editor()
        else:
            new_index = min(index, len(self.contest_file.questions) - 1)
            self.questions_listbox.selection_set(new_index)
            self.on_question_select(None)
    
    def update_questions_list(self):
        self.questions_listbox.delete(0, tk.END)
        for i, question in enumerate(self.contest_file.questions):
            short_text = question.text[:50] + "..." if len(question.text) > 50 else question.text
            self.questions_listbox.insert(tk.END, f"{i+1}. {short_text}")
    
    def clear_question_editor(self):
        self.current_question_index = -1
        self.question_text.delete("1.0", tk.END)
        self.correct_answer_var.set(-1)
        
        for text in self.answer_texts:
            text.delete("1.0", tk.END)
    
    def update_title(self):
        title = "Zhuxian Quest Editor"
        if self.current_file:
            title += f" - {os.path.basename(self.current_file)}"
            if self.current_question_index != -1 and self.contest_file.questions:
                title += f" (Вопрос {self.current_question_index + 1}/{len(self.contest_file.questions)})"
        self.root.title(title)

if __name__ == "__main__":
    root = tk.Tk()
    app = ZhuxianQuestEditor(root)
    root.mainloop()
