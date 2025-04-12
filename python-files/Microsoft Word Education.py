import tkinter as tk
from tkinter import messagebox
import time

# --- Расширенные данные для теории (Microsoft Word) ---
theory_points = [
    "1. Интерфейс Microsoft Word. Обзор главного окна, ленты, вкладок и панелей инструментов. Все команды организованы для быстрого доступа и удобной работы.",
    "2. Создание и редактирование документов. Открытие нового файла, сохранение, использование шаблонов и автосохранение для предотвращения потери данных.",
    "3. Форматирование текста. Работа с шрифтами, размерами, стилями (жирный, курсив, подчёркивание), изменением цвета, межстрочного интервала и выравнивания.",
    "4. Работа с абзацами. Настройка отступов, межстрочного интервала и выравнивания текста. Организация списков, создание многоуровневых маркеров.",
    "5. Вставка объектов. Добавление изображений, таблиц, диаграмм, графики и SmartArt для улучшения визуального представления документа.",
    "6. Использование стилей и тем оформления. Применение встроенных стилей, создание и редактирование собственных стилей для обеспечения единого оформления документа.",
    "7. Рецензирование и совместная работа. Использование комментариев, отслеживания изменений, сравнения версий документа и защита паролем.",
    "8. Работа с таблицами. Создание таблиц, настройка их внешнего вида, объединение ячеек, применение формул для вычислений внутри таблиц.",
    "9. Автоматизация и макросы. Запись макросов для автоматизации рутинных задач, использование встроенных функций и написание VBA-скриптов.",
    "10. Работа с разделами и колонтитулами. Добавление, настройка и изменение колонтитулов для разных разделов документа.",
    "11. Использование гиперссылок и закладок. Создание интерактивных документов с переходами к различным частям текста или внешним ресурсам.",
    "12. Работа с ориентацией страницы и полями. Изменение ориентации, настройка размеров и полей страницы для печатных форматов.",
    "13. Использование инструментов проверки. Автоматическая проверка орфографии и грамматики, использование словарей и настроек автозамены.",
    "14. Настройки печати и предпросмотр. Подготовка документов к печати, настройка параметров страницы и печати, создание PDF-файлов.",
    "15. Расширенные возможности. Интеграция с облачными сервисами, синхронизация документов, использование совместного редактирования в реальном времени."
]

# --- Расширенные данные для практической части ---
practice_tasks = [
    "1. Создайте новый документ в Microsoft Word и напишите короткий абзац, используя разные шрифты и размеры.",
    "2. Отформатируйте текст: выделите заголовок, измените его цвет и выравнивание, примените стиль «Жирный».",
    "3. Вставьте таблицу с данными, настройте её внешний вид: измените цвет ячеек, установите границы и выберите шрифты.",
    "4. Добавьте изображение, настройте его размеры, положение и обтекание текстом.",
    "5. Запишите простой макрос для автоматического форматирования текста и выполните его на примере абзаца.",
    "6. Создайте документ с несколькими разделами, настройте колонтитулы и добавьте номера страниц.",
    "7. Используйте функцию сравнения документов, чтобы увидеть отличия между двумя версиями текста."
]

# --- Расширенный список вопросов для теста ---
test_questions = [
    ("Как называется основная область, где располагается текст документа в Microsoft Word?", 
     ["Рабочая область", "Лента", "Панель инструментов", "Строка состояния"], "Рабочая область"),
     
    ("Какой горячей клавишей можно вызвать меню «Файл»?", 
     ["Ctrl+F", "Alt+F", "Ctrl+S", "Shift+F"], "Alt+F"),
     
    ("Какой элемент позволяет применить единый стиль ко всему документу?", 
     ["Шаблон", "Файл", "Тема", "Обложка"], "Тема"),
     
    ("Какой функционал используется для проверки орфографии в документе?", 
     ["Фильтрация", "Рецензирование", "Правописание", "Форматирование"], "Правописание"),
     
    ("Что позволяет функция «Автосохранение»?", 
     ["Редактировать документ", "Печать документа", "Автоматически сохранять изменения", "Добавлять комментарии"], "Автоматически сохранять изменения"),
     
    ("Как называется область, где отображаются комментарии и правки?", 
     ["Область заметок", "Панель задач", "Область рецензирования", "Лента"], "Область рецензирования"),
     
    ("Какая вкладка содержит инструменты для форматирования текста?", 
     ["Вставка", "Главная", "Макет", "Ссылки"], "Главная"),
     
    ("Какой формат файла сохраняет документы Word с поддержкой макросов?", 
     ["DOC", "DOCX", "DOT", "DOCM"], "DOCM"),
     
    ("Как называется элемент, отвечающий за настройку колонтитулов в документе?", 
     ["Раздел", "Конструктор", "Вид", "Колонтитул"], "Колонтитул"),
     
    ("Какой режим просмотра документа позволяет видеть все элементы страницы, включая отступы и поля?", 
     ["Обычный", "Макет страницы", "Веб-документ", "Структура"], "Макет страницы"),
     
    ("Какая функция позволяет сравнить две версии одного документа?", 
     ["Объединение", "Слияние", "Сравнение", "Рецензирование"], "Сравнение"),
     
    ("Какой из вариантов позволяет быстро применить предустановленный стиль к тексту?", 
     ["Панель быстрого доступа", "Область стилей", "Лента", "Контекстное меню"], "Область стилей")
]

# --- Основной класс приложения ---
class WordTrainerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Обучающе-контролирующая программа по Microsoft Word")
        self.root.geometry("1000x750")
        self.root.configure(bg="#f0f8ff")  # нежный голубой фон
        self.score = 0
        self.current_q = 0
        self.user_answers = []
        
        # Создание верхней панели с текущим временем и названием программы
        self.header_frame = tk.Frame(self.root, bg="#4682b4", height=50)
        self.header_frame.pack(fill=tk.X)
        self.title_label = tk.Label(self.header_frame, text="Обучающая программа по Microsoft Word", 
                                    font=("Helvetica", 18, "bold"), fg="white", bg="#4682b4")
        self.title_label.pack(side=tk.LEFT, padx=20)
        self.time_label = tk.Label(self.header_frame, font=("Helvetica", 14), fg="white", bg="#4682b4")
        self.time_label.pack(side=tk.RIGHT, padx=20)
        self.update_clock()
        
        self.create_main_menu()

    def update_clock(self):
        """Обновление метки с текущим временем каждую секунду."""
        current_time = time.strftime("%H:%M:%S")
        self.time_label.config(text="Время: " + current_time)
        self.root.after(1000, self.update_clock)

    def clear_window(self):
        """Очистка всех виджетов главного окна, кроме верхней панели."""
        for widget in self.root.winfo_children():
            if widget == self.header_frame:
                continue
            widget.destroy()

    def create_main_menu(self):
        """Создание главного меню с переходами в различные разделы."""
        self.clear_window()
        menu_frame = tk.Frame(self.root, bg="#f0f8ff")
        menu_frame.pack(pady=30)
        
        btn_style = {
            "width": 30, 
            "height": 2, 
            "font": ("Arial", 14), 
            "bg": "#87cefa", 
            "fg": "black", 
            "bd": 2, 
            "relief": tk.RAISED
        }
        
        tk.Button(menu_frame, text="Теория", command=self.show_theory, **btn_style).pack(pady=10)
        tk.Button(menu_frame, text="Практика", command=self.show_practice, **btn_style).pack(pady=10)
        tk.Button(menu_frame, text="Тест", command=self.start_test, **btn_style).pack(pady=10)
        tk.Button(menu_frame, text="О программе", command=self.show_about, **btn_style).pack(pady=10)
        tk.Button(menu_frame, text="Справка", command=self.show_help, **btn_style).pack(pady=10)
        tk.Button(menu_frame, text="Выход", command=self.exit_app, **btn_style).pack(pady=10)
        
        # Подпись автора в нижней части экрана
        tk.Label(self.root, text="Автор: Смирнов Илья", font=("Arial", 10, "italic"), bg="#f0f8ff")\
            .pack(side=tk.BOTTOM, pady=5)

    def exit_app(self):
        """Корректное завершение работы приложения."""
        self.root.destroy()

    def show_theory(self):
        """Отображение подробной теории по Microsoft Word."""
        self.clear_window()
        title = tk.Label(self.root, text="Теория по Microsoft Word", font=("Helvetica", 18, "bold"), bg="#f0f8ff")
        title.pack(pady=10)
        
        # Использование виджета Text для отображения большого объёма текста
        theory_box = tk.Text(self.root, wrap=tk.WORD, width=100, height=25, font=("Arial", 12))
        theory_box.pack(padx=20, pady=10)
        for point in theory_points:
            theory_box.insert(tk.END, point + "\n\n")
        theory_box.config(state=tk.DISABLED)
        
        # Панель навигации с кнопками "Назад", "В начало" и "Выход"
        nav_frame = tk.Frame(self.root, bg="#f0f8ff")
        nav_frame.pack(pady=10)
        tk.Button(nav_frame, text="Назад", font=("Arial", 12), width=15, command=self.create_main_menu, bg="#87cefa")\
            .pack(side=tk.LEFT, padx=10)
        tk.Button(nav_frame, text="В начало", font=("Arial", 12), width=15, command=self.create_main_menu, bg="#87cefa")\
            .pack(side=tk.LEFT, padx=10)
        tk.Button(nav_frame, text="Выход", font=("Arial", 12), width=15, command=self.exit_app, bg="#87cefa")\
            .pack(side=tk.LEFT, padx=10)

    def show_practice(self):
        """Отображение практических заданий."""
        self.clear_window()
        title = tk.Label(self.root, text="Практическая часть по Microsoft Word", font=("Helvetica", 18, "bold"), bg="#f0f8ff")
        title.pack(pady=10)
        
        practice_frame = tk.Frame(self.root, bg="#f0f8ff")
        practice_frame.pack(pady=10)
        for task in practice_tasks:
            tk.Label(practice_frame, text=task, anchor="w", justify="left", 
                     wraplength=900, font=("Arial", 12), bg="#f0f8ff")\
                .pack(pady=5, anchor="w", padx=20)
            
        nav_frame = tk.Frame(self.root, bg="#f0f8ff")
        nav_frame.pack(pady=10)
        tk.Button(nav_frame, text="Назад", font=("Arial", 12), width=15, command=self.create_main_menu, bg="#87cefa")\
            .pack(side=tk.LEFT, padx=10)
        tk.Button(nav_frame, text="В начало", font=("Arial", 12), width=15, command=self.create_main_menu, bg="#87cefa")\
            .pack(side=tk.LEFT, padx=10)
        tk.Button(nav_frame, text="Выход", font=("Arial", 12), width=15, command=self.exit_app, bg="#87cefa")\
            .pack(side=tk.LEFT, padx=10)

    def start_test(self):
        """Подготовка к запуску теста: сброс счётчика и отображение первого вопроса."""
        self.score = 0
        self.current_q = 0
        self.user_answers = []
        self.show_question()

    def show_question(self):
        """Отображение текущего вопроса теста."""
        self.clear_window()
        if self.current_q >= len(test_questions):
            self.show_result()
            return

        question, options, _ = test_questions[self.current_q]
        q_frame = tk.Frame(self.root, bg="#f0f8ff")
        q_frame.pack(pady=20)
        
        tk.Label(q_frame, text=f"Вопрос {self.current_q + 1} из {len(test_questions)}", 
                 font=("Helvetica", 16), bg="#f0f8ff")\
            .pack(pady=5)
        tk.Label(q_frame, text=question, font=("Arial", 14), bg="#f0f8ff", wraplength=900)\
            .pack(pady=5)
        
        self.selected_option = tk.StringVar()
        for option in options:
            tk.Radiobutton(q_frame, text=option, variable=self.selected_option, value=option, 
                           font=("Arial", 12), bg="#f0f8ff")\
                .pack(anchor="w", padx=100, pady=2)
        
        # Кнопки для ответа, возврата в меню, справки по тестированию и выхода
        btn_frame = tk.Frame(self.root, bg="#f0f8ff")
        btn_frame.pack(pady=20)
        tk.Button(btn_frame, text="Ответить", font=("Arial", 12), width=15, command=self.check_answer, bg="#87cefa")\
            .pack(side=tk.LEFT, padx=10)
        tk.Button(btn_frame, text="В начало", font=("Arial", 12), width=15, command=self.create_main_menu, bg="#87cefa")\
            .pack(side=tk.LEFT, padx=10)
        tk.Button(btn_frame, text="Справка", font=("Arial", 12), width=15, command=self.show_test_help, bg="#87cefa")\
            .pack(side=tk.LEFT, padx=10)
        tk.Button(btn_frame, text="Выход", font=("Arial", 12), width=15, command=self.exit_app, bg="#87cefa")\
            .pack(side=tk.LEFT, padx=10)

    def check_answer(self):
        """Проверка выбранного ответа и переход к следующему вопросу."""
        answer = self.selected_option.get()
        if not answer:
            messagebox.showwarning("Ошибка", "Пожалуйста, выберите вариант ответа.")
            return
        correct = test_questions[self.current_q][2]
        if answer == correct:
            self.score += 1
        # Сохраняем вопрос, выбранный и правильный ответ для последующего отображения
        self.user_answers.append((test_questions[self.current_q][0], answer, correct))
        self.current_q += 1
        self.show_question()

    def show_result(self):
        """Отображение результатов теста и предоставление возможности повторить тест."""
        self.clear_window()
        tk.Label(self.root, text="Результаты теста", font=("Helvetica", 18, "bold"), bg="#f0f8ff")\
            .pack(pady=10)
        mark = self.grade(self.score)
        tk.Label(self.root, text=f"Правильных ответов: {self.score} из {len(test_questions)}", 
                 font=("Arial", 14), bg="#f0f8ff")\
            .pack(pady=5)
        tk.Label(self.root, text=f"Оценка: {mark}", font=("Arial", 16), bg="#f0f8ff")\
            .pack(pady=5)

        res_frame = tk.Frame(self.root, bg="#f0f8ff")
        res_frame.pack(pady=10)
        # Отображение детализированного отчёта по каждому вопросу
        for q, a, c in self.user_answers:
            text = f"{q}\nВаш ответ: {a} | Правильный ответ: {c}"
            tk.Label(res_frame, text=text, wraplength=900, justify="left", font=("Arial", 12), 
                     bg="#f0f8ff", bd=1, relief=tk.GROOVE)\
                .pack(pady=3, padx=20, fill=tk.X)

        # Панель навигации на экране результатов с дополнительной кнопкой для повтора теста
        nav_frame = tk.Frame(self.root, bg="#f0f8ff")
        nav_frame.pack(pady=10)
        tk.Button(nav_frame, text="Повторить тест", font=("Arial", 12), width=15, command=self.start_test, bg="#87cefa")\
            .pack(side=tk.LEFT, padx=10)
        tk.Button(nav_frame, text="На главную", font=("Arial", 12), width=15, command=self.create_main_menu, bg="#87cefa")\
            .pack(side=tk.LEFT, padx=10)
        tk.Button(nav_frame, text="Выход", font=("Arial", 12), width=15, command=self.exit_app, bg="#87cefa")\
            .pack(side=tk.LEFT, padx=10)

    def grade(self, score):
        """Определение оценивания на основе количества правильных ответов."""
        if score == len(test_questions):
            return "5 (Отлично)"
        elif score >= int(0.75 * len(test_questions)):
            return "4 (Хорошо)"
        elif score >= int(0.5 * len(test_questions)):
            return "3 (Удовлетворительно)"
        else:
            return "2 (Неудовлетворительно)"

    def show_about(self):
        """Отображение информации о программе."""
        self.clear_window()
        about_text = (
            "Данная обучающая программа предназначена для повышения знаний по работе с Microsoft Word.\n\n"
            "В программе представлены следующие разделы:\n"
            "• Теория – подробные описания основных возможностей и функций Microsoft Word.\n"
            "• Практическая часть – задания для самостоятельного выполнения, направленные на закрепление материала.\n"
            "• Тест – контроль знаний с выбором вариантов ответов.\n\n"
            "Дополнительные возможности программы:\n"
            "• Повтор теста для улучшения результата.\n"
            "• Справка с подсказками по прохождению теста и использованию функционала.\n\n"
            "Приятного обучения!\n\n"
            "Автор: Смирнов Илья"
        )
        tk.Label(self.root, text="О программе", font=("Helvetica", 18, "bold"), bg="#f0f8ff")\
            .pack(pady=10)
        text_box = tk.Text(self.root, wrap=tk.WORD, width=90, height=20, font=("Arial", 12))
        text_box.pack(padx=20, pady=10)
        text_box.insert(tk.END, about_text)
        text_box.config(state=tk.DISABLED)
        
        nav_frame = tk.Frame(self.root, bg="#f0f8ff")
        nav_frame.pack(pady=10)
        tk.Button(nav_frame, text="Назад", font=("Arial", 12), width=15, command=self.create_main_menu, bg="#87cefa")\
            .pack(side=tk.LEFT, padx=10)
        tk.Button(nav_frame, text="В начало", font=("Arial", 12), width=15, command=self.create_main_menu, bg="#87cefa")\
            .pack(side=tk.LEFT, padx=10)
        tk.Button(nav_frame, text="Выход", font=("Arial", 12), width=15, command=self.exit_app, bg="#87cefa")\
            .pack(side=tk.LEFT, padx=10)

    def show_help(self):
        """Отображение справочной информации о работе программы."""
        self.clear_window()
        help_text = (
            "Справка по программе:\n\n"
            "1. Теория – здесь вы можете ознакомиться с подробными материалами по функционалу Microsoft Word.\n"
            "2. Практика – раздел содержит задания для самостоятельного выполнения и закрепления материала.\n"
            "3. Тест – выполните тест для проверки полученных знаний. Выбирайте варианты ответов и получайте оценку.\n\n"
            "Дополнительные кнопки:\n"
            "• 'Справка' – подсказки и рекомендации по прохождению теста или работе с приложением.\n"
            "• 'Выход' – завершение работы приложения.\n"
            "• 'Повторить тест' – возможность пройти тест заново для улучшения результата.\n\n"
            "Надеемся, что программа будет полезна для вашего обучения!"
        )
        tk.Label(self.root, text="Справка", font=("Helvetica", 18, "bold"), bg="#f0f8ff")\
            .pack(pady=10)
        text_box = tk.Text(self.root, wrap=tk.WORD, width=90, height=20, font=("Arial", 12))
        text_box.pack(padx=20, pady=10)
        text_box.insert(tk.END, help_text)
        text_box.config(state=tk.DISABLED)
        
        nav_frame = tk.Frame(self.root, bg="#f0f8ff")
        nav_frame.pack(pady=10)
        tk.Button(nav_frame, text="Назад", font=("Arial", 12), width=15, command=self.create_main_menu, bg="#87cefa")\
            .pack(side=tk.LEFT, padx=10)
        tk.Button(nav_frame, text="Выход", font=("Arial", 12), width=15, command=self.exit_app, bg="#87cefa")\
            .pack(side=tk.LEFT, padx=10)

    def show_test_help(self):
        """Отображение подсказок при прохождении теста."""
        messagebox.showinfo("Справка по тесту",
                            "Выберите один из предложенных вариантов ответа и нажмите 'Ответить'.\n"
                            "Если вы не уверены в ответе, можете выбрать любой вариант, а затем просмотреть результаты теста.")

# Запуск приложения
if __name__ == "__main__":
    root = tk.Tk()
    app = WordTrainerApp(root)
    root.mainloop()
