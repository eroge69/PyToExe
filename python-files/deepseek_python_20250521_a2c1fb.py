import sys
import json
import os
import time
from datetime import timedelta
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QLabel, QPushButton, QRadioButton, QCheckBox, QGroupBox,
                             QLineEdit, QTextEdit, QSpinBox, QMessageBox, QListWidget,
                             QTabWidget, QTimeEdit)
from PyQt5.QtCore import Qt, QTimer


class Question:
    def __init__(self, text="", answers=None, is_multiple_choice=False):
        self.text = text
        self.answers = answers if answers else []
        self.is_multiple_choice = is_multiple_choice

    def to_dict(self):
        return {
            "text": self.text,
            "answers": self.answers,
            "is_multiple_choice": self.is_multiple_choice
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            text=data["text"],
            answers=data["answers"],
            is_multiple_choice=data["is_multiple_choice"]
        )


class TestApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.questions = []
        self.current_question_index = 0
        self.correct_answers = 0
        self.test_start_time = None
        self.test_end_time = None
        self.user_answers = []
        
        self.init_ui()
        self.load_questions()
        
    def init_ui(self):
        self.setWindowTitle("Тестирование")
        self.setGeometry(100, 100, 800, 600)
        
        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)
        
        # Вкладка прохождения теста
        self.test_tab = QWidget()
        self.test_layout = QVBoxLayout()
        
        self.question_label = QLabel("Вопрос будет здесь")
        self.question_label.setWordWrap(True)
        self.test_layout.addWidget(self.question_label)
        
        self.answers_group = QGroupBox("Ответы")
        self.answers_layout = QVBoxLayout()
        self.answers_group.setLayout(self.answers_layout)
        self.test_layout.addWidget(self.answers_group)
        
        self.timer_label = QLabel("Затраченное время: 00:00:00")
        self.test_layout.addWidget(self.timer_label)
        
        self.navigation_layout = QHBoxLayout()
        self.prev_button = QPushButton("Назад")
        self.prev_button.clicked.connect(self.prev_question)
        self.navigation_layout.addWidget(self.prev_button)
        
        self.next_button = QPushButton("Вперед")
        self.next_button.clicked.connect(self.next_question)
        self.navigation_layout.addWidget(self.next_button)
        
        self.finish_button = QPushButton("Завершить тест")
        self.finish_button.clicked.connect(self.finish_test)
        self.navigation_layout.addWidget(self.finish_button)
        
        self.test_layout.addLayout(self.navigation_layout)
        self.test_tab.setLayout(self.test_layout)
        self.tabs.addTab(self.test_tab, "Тест")
        
        # Вкладка редактирования вопросов
        self.edit_tab = QWidget()
        self.edit_layout = QVBoxLayout()
        
        self.questions_list = QListWidget()
        self.questions_list.itemClicked.connect(self.load_question_for_edit)
        self.edit_layout.addWidget(self.questions_list)
        
        self.question_edit = QTextEdit()
        self.question_edit.setPlaceholderText("Введите текст вопроса")
        self.edit_layout.addWidget(self.question_edit)
        
        self.multiple_choice_check = QCheckBox("Множественный выбор (несколько правильных ответов)")
        self.edit_layout.addWidget(self.multiple_choice_check)
        
        self.answers_edit_layout = QVBoxLayout()
        self.edit_layout.addLayout(self.answers_edit_layout)
        
        self.add_answer_button = QPushButton("Добавить ответ")
        self.add_answer_button.clicked.connect(self.add_answer_for_edit)
        self.edit_layout.addWidget(self.add_answer_button)
        
        self.buttons_layout = QHBoxLayout()
        self.save_question_button = QPushButton("Сохранить вопрос")
        self.save_question_button.clicked.connect(self.save_question)
        self.buttons_layout.addWidget(self.save_question_button)
        
        self.add_question_button = QPushButton("Добавить вопрос")
        self.add_question_button.clicked.connect(self.add_new_question)
        self.buttons_layout.addWidget(self.add_question_button)
        
        self.delete_question_button = QPushButton("Удалить вопрос")
        self.delete_question_button.clicked.connect(self.delete_question)
        self.buttons_layout.addWidget(self.delete_question_button)
        
        self.edit_layout.addLayout(self.buttons_layout)
        self.edit_tab.setLayout(self.edit_layout)
        self.tabs.addTab(self.edit_tab, "Редактирование")
        
        # Таймер для отображения времени
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_timer)
        self.timer.start(1000)
        
        self.update_question_display()
        self.update_questions_list()
    
    def add_answer_for_edit(self):
        answer_widget = QWidget()
        answer_layout = QHBoxLayout()
        
        answer_text = QLineEdit()
        answer_text.setPlaceholderText("Текст ответа")
        answer_layout.addWidget(answer_text)
        
        is_correct = QCheckBox("Правильный")
        answer_layout.addWidget(is_correct)
        
        remove_button = QPushButton("Удалить")
        remove_button.clicked.connect(lambda: self.remove_answer_widget(answer_widget))
        answer_layout.addWidget(remove_button)
        
        answer_widget.setLayout(answer_layout)
        self.answers_edit_layout.addWidget(answer_widget)
    
    def remove_answer_widget(self, widget):
        self.answers_edit_layout.removeWidget(widget)
        widget.deleteLater()
    
    def load_question_for_edit(self, item):
        index = self.questions_list.row(item)
        if 0 <= index < len(self.questions):
            question = self.questions[index]
            self.question_edit.setPlainText(question.text)
            self.multiple_choice_check.setChecked(question.is_multiple_choice)
            
            # Очищаем предыдущие ответы
            while self.answers_edit_layout.count():
                child = self.answers_edit_layout.takeAt(0)
                if child.widget():
                    child.widget().deleteLater()
            
            # Добавляем ответы для редактирования
            for answer in question.answers:
                self.add_answer_for_edit()
                last_index = self.answers_edit_layout.count() - 1
                answer_widget = self.answers_edit_layout.itemAt(last_index).widget()
                answer_text = answer_widget.layout().itemAt(0).widget()
                is_correct = answer_widget.layout().itemAt(1).widget()
                
                answer_text.setText(answer["text"])
                is_correct.setChecked(answer["is_correct"])
    
    def save_question(self):
        current_index = self.questions_list.currentRow()
        if current_index == -1:
            return
        
        question_text = self.question_edit.toPlainText().strip()
        if not question_text:
            QMessageBox.warning(self, "Ошибка", "Текст вопроса не может быть пустым")
            return
        
        # Собираем ответы
        answers = []
        for i in range(self.answers_edit_layout.count()):
            answer_widget = self.answers_edit_layout.itemAt(i).widget()
            answer_text = answer_widget.layout().itemAt(0).widget().text().strip()
            is_correct = answer_widget.layout().itemAt(1).widget().isChecked()
            
            if answer_text:
                answers.append({
                    "text": answer_text,
                    "is_correct": is_correct
                })
        
        if not answers:
            QMessageBox.warning(self, "Ошибка", "Добавьте хотя бы один ответ")
            return
        
        # Проверяем, есть ли хотя бы один правильный ответ
        has_correct = any(answer["is_correct"] for answer in answers)
        if not has_correct:
            QMessageBox.warning(self, "Ошибка", "Должен быть хотя бы один правильный ответ")
            return
        
        # Обновляем вопрос
        question = Question(
            text=question_text,
            answers=answers,
            is_multiple_choice=self.multiple_choice_check.isChecked()
        )
        
        self.questions[current_index] = question
        self.save_questions()
        self.update_questions_list()
        QMessageBox.information(self, "Сохранено", "Вопрос успешно сохранен")
    
    def add_new_question(self):
        self.questions.append(Question("Новый вопрос", [{"text": "Правильный ответ", "is_correct": True}], False))
        self.save_questions()
        self.update_questions_list()
        self.questions_list.setCurrentRow(len(self.questions) - 1)
        self.load_question_for_edit(self.questions_list.currentItem())
    
    def delete_question(self):
        current_index = self.questions_list.currentRow()
        if current_index == -1:
            return
        
        reply = QMessageBox.question(
            self, "Удаление вопроса",
            "Вы уверены, что хотите удалить этот вопрос?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            del self.questions[current_index]
            self.save_questions()
            self.update_questions_list()
    
    def update_questions_list(self):
        self.questions_list.clear()
        for i, question in enumerate(self.questions, 1):
            self.questions_list.addItem(f"{i}. {question.text[:50]}...")
    
    def load_questions(self):
        if os.path.exists("questions.json"):
            try:
                with open("questions.json", "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.questions = [Question.from_dict(item) for item in data]
            except:
                self.questions = []
        else:
            self.questions = [
                Question(
                    "Пример вопроса с одним правильным ответом",
                    [
                        {"text": "Правильный ответ", "is_correct": True},
                        {"text": "Неправильный ответ", "is_correct": False},
                        {"text": "Еще один неправильный ответ", "is_correct": False}
                    ],
                    False
                ),
                Question(
                    "Пример вопроса с несколькими правильными ответами",
                    [
                        {"text": "Правильный ответ 1", "is_correct": True},
                        {"text": "Правильный ответ 2", "is_correct": True},
                        {"text": "Неправильный ответ", "is_correct": False}
                    ],
                    True
                )
            ]
            self.save_questions()
    
    def save_questions(self):
        with open("questions.json", "w", encoding="utf-8") as f:
            json.dump([q.to_dict() for q in self.questions], f, ensure_ascii=False, indent=2)
    
    def start_test(self):
        if not self.questions:
            QMessageBox.warning(self, "Ошибка", "Нет вопросов для тестирования")
            return
        
        self.current_question_index = 0
        self.correct_answers = 0
        self.user_answers = [None] * len(self.questions)
        self.test_start_time = time.time()
        self.test_end_time = None
        self.tabs.setCurrentIndex(0)
        self.update_question_display()
    
    def update_question_display(self):
        if not self.questions:
            self.question_label.setText("Нет вопросов для отображения")
            return
        
        question = self.questions[self.current_question_index]
        self.question_label.setText(f"Вопрос {self.current_question_index + 1} из {len(self.questions)}:\n{question.text}")
        
        # Очищаем предыдущие ответы
        while self.answers_layout.count():
            child = self.answers_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        
        # Добавляем новые ответы
        if question.is_multiple_choice:
            for i, answer in enumerate(question.answers):
                checkbox = QCheckBox(answer["text"])
                if self.user_answers[self.current_question_index] is not None and i in self.user_answers[self.current_question_index]:
                    checkbox.setChecked(True)
                self.answers_layout.addWidget(checkbox)
        else:
            for i, answer in enumerate(question.answers):
                radio = QRadioButton(answer["text"])
                if self.user_answers[self.current_question_index] is not None and i == self.user_answers[self.current_question_index][0]:
                    radio.setChecked(True)
                self.answers_layout.addWidget(radio)
        
        # Обновляем кнопки навигации
        self.prev_button.setEnabled(self.current_question_index > 0)
        self.next_button.setEnabled(self.current_question_index < len(self.questions) - 1)
    
    def save_current_answer(self):
        if not self.questions or self.current_question_index >= len(self.questions):
            return
        
        question = self.questions[self.current_question_index]
        selected = []
        
        if question.is_multiple_choice:
            for i in range(self.answers_layout.count()):
                checkbox = self.answers_layout.itemAt(i).widget()
                if checkbox.isChecked():
                    selected.append(i)
        else:
            for i in range(self.answers_layout.count()):
                radio = self.answers_layout.itemAt(i).widget()
                if radio.isChecked():
                    selected.append(i)
                    break
        
        self.user_answers[self.current_question_index] = selected if selected else None
    
    def prev_question(self):
        self.save_current_answer()
        self.current_question_index -= 1
        self.update_question_display()
    
    def next_question(self):
        self.save_current_answer()
        self.current_question_index += 1
        self.update_question_display()
    
    def finish_test(self):
        self.save_current_answer()
        self.test_end_time = time.time()
        
        # Подсчет правильных ответов
        self.correct_answers = 0
        for i, question in enumerate(self.questions):
            user_answer = self.user_answers[i]
            if user_answer is None:
                continue
            
            correct_answers = [j for j, answer in enumerate(question.answers) if answer["is_correct"]]
            
            if question.is_multiple_choice:
                if set(user_answer) == set(correct_answers):
                    self.correct_answers += 1
            else:
                if len(user_answer) == 1 and user_answer[0] in correct_answers:
                    self.correct_answers += 1
        
        # Вывод статистики
        time_spent = self.test_end_time - self.test_start_time
        time_str = str(timedelta(seconds=int(time_spent)))
        percentage = (self.correct_answers / len(self.questions)) * 100 if self.questions else 0
        
        QMessageBox.information(
            self, "Результаты теста",
            f"Тест завершен!\n\n"
            f"Правильных ответов: {self.correct_answers} из {len(self.questions)}\n"
            f"Процент правильных ответов: {percentage:.1f}%\n"
            f"Затраченное время: {time_str}"
        )
    
    def update_timer(self):
        if self.test_start_time and not self.test_end_time:
            time_spent = time.time() - self.test_start_time
            time_str = str(timedelta(seconds=int(time_spent)))
            self.timer_label.setText(f"Затраченное время: {time_str}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TestApp()
    window.show()
    sys.exit(app.exec_())