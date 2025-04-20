import tkinter as tk
from tkinter import font, messagebox
import random

class QuizApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Тест по гидрологии водоёмов")
        self.root.geometry("1366x768")
        
        # Настройка шрифтов 12 11 14 8
        self.question_font = font.Font(family="Arial", size=14, weight="bold")
        self.option_font = font.Font(family="Arial", size=13)
        self.timer_font = font.Font(family="Arial", size=16, weight="bold")
        self.footer_font = font.Font(family="Arial", size=10)
        
        # Таймер (10 минут = 300 секунд)
        self.time_left = 300
        self.timer_running = False
        
        # Подпись разработчика
        self.footer_label = tk.Label(root, text="Тест разработан: TVR12", 
                                   font=self.footer_font, fg="gray")
        self.footer_label.pack(side="bottom", anchor="se", padx=10, pady=10)
        
        # Создаем контейнер для таймера
        self.timer_frame = tk.Frame(root)
        self.timer_frame.pack(pady=10)
        
        self.timer_label = tk.Label(self.timer_frame, text="Осталось времени: 10:00", 
                                  font=self.timer_font, fg="red")
        self.timer_label.pack()
        
        # Основной контейнер для вопроса и вариантов
        self.main_frame = tk.Frame(root)
        self.main_frame.pack(pady=20, fill="both", expand=True)
        
        # Контейнер для номера и текста вопроса
        self.question_container = tk.Frame(self.main_frame)
        self.question_container.pack(fill="x", padx=20)
        
        # Метка для номера вопроса (выравнивание по левому краю)
        self.number_label = tk.Label(self.question_container, text="", 
                                   font=self.question_font, anchor="w", width=4)
        self.number_label.pack(side="left")
        
        # Метка для текста вопроса (выравнивание по левому краю)
        self.question_label = tk.Label(self.question_container, text="", 
                                     wraplength=700, font=self.question_font, 
                                     justify="left", anchor="w")
        self.question_label.pack(side="left", fill="x", expand=True)
        
        # Варианты ответов
        self.radio_var = tk.IntVar()
        self.radio_buttons = []
        for i in range(4):
            rb = tk.Radiobutton(self.main_frame, text="", variable=self.radio_var, 
                               value=i, font=self.option_font, anchor="w", 
                               justify="left", wraplength=700)
            rb.pack(fill="x", padx=50, pady=5)
            self.radio_buttons.append(rb)
        
        # Контейнер для кнопок навигации
        self.button_frame = tk.Frame(root)
        self.button_frame.pack(pady=20)
        
        self.prev_button = tk.Button(self.button_frame, text="← Назад", 
                                   command=self.prev_question, width=10)
        self.prev_button.pack(side="left", padx=20)
        
        self.next_button = tk.Button(self.button_frame, text="Вперед →", 
                                   command=self.next_question, width=10)
        self.next_button.pack(side="left", padx=20)
        
        # Кнопка завершения теста
        self.submit_button = tk.Button(root, text="Завершить тест", 
                                     command=self.submit_quiz, state="disabled",
                                     font=self.option_font)
        self.submit_button.pack(pady=10)
        
        # Кнопка перезапуска теста (изначально скрыта)
        self.restart_button = tk.Button(root, text="Пройти тест снова", 
                                      command=self.restart_quiz,
                                      font=self.option_font)
        self.restart_button.pack_forget()

        # Полный список вопросов (без номеров)
        self.all_questions = [
            {
                "question": "Естественный водоем замедленного водообмена, не имеющий обратной связи с океаном, это...",
                "options": ["Пруд", "Водохранилище", "Озеро", "Река"],
                "correct": 2
            },            
			{
                "question": "Для образования водоемов требуются...",
                "options": ["Постоянные дожди и уклон поверхности", "Отсутствие подземного стока и испарения", 
                           "Солнечная активность и равнинная местность", "Котловина и вода"],
                "correct": 3
            },
            {
                "question": "Эндогенные факторы, действующие при формировании котловин водоемов, это факторы...",
                "options": ["Происходящие на поверхности Земли", "Происходящие на дне водоема", 
                           "Происходящие внутри земной коры", "Происходящие при строительстве хозяйственных объектов"],
                "correct": 2
            },
            {
                "question": "Какие котловины водоемов образуются в районах, где подземные воды вымывают из почвы соли?",
                "options": ["Суффозионные", "Аккумулятивные", "Вулканические", "Эрозионные"],
                "correct": 0
            },
            {
                "question": "Переформирование берегов водоемов происходит под действием ветровых волн. Этот процесс носит название...",
                "options": ["Абляция", "Обструкция", "Коррозия", "Абразия"],
                "correct": 3
            },
            {
                "question": "К основным приходным составляющим водного баланса водоемов не относится...",
                "options": ["Поверхностный приток", "Осадки", "Испарение", "Конденсация водных паров"],
                "correct": 2
            },
            {
                "question": "Уравнение водного баланса сточных и бессточных водоемов различается на величину...",
                "options": ["Испарения", "Стока", "Притока", "Осадков"],
                "correct": 1
            },
            {
                "question": "Наиболее распространенный способ расчета испарения с водной поверхности...",
                "options": ["Формула ГГИ", "Метод Константинова", "Формула Владимирова", "Метод отношения площадей"],
                "correct": 0
            },
            {
                "question": "Показатель условного водообмена - это…",
                "options": ["Отношение суммы объема притока и объема осадков к объему озера", 
                           "Отношение разности объема притока и объема осадков к объему озера", 
                           "Отношение разности общего объема озера и объема притока к объему осадков", 
                           "Отношение суммы объема притока и объема стока к объему озера"],
                "correct": 0
            },
            {
                "question": "По интенсивности водообмена...",
                "options": ["Реки занимают промежуточное положение между озерами и океаном", 
                           "Океан занимает промежуточное положение между реками и озерами", 
                           "Реки занимают промежуточное положение между океаном и озерами", 
                           "Озера занимают промежуточное положение между реками и океаном"],
                "correct": 2
            },
            {
                "question": "Главной причиной колебаний уровней водоемов является...",
                "options": ["Солнечная активность", "Ветровая деятельность", 
                           "Изменчивость составляющих водного баланса", "Речной сток"],
                "correct": 2
            },
            {
                "question": "Доля тепла, получаемого водоемом от того или иного источника...",
                "options": ["Не изменяется в течение года", "Не меняется от сезона к сезону", 
                           "Меняется от года к году, оставаясь в течение года неизменным", 
                           "Меняется от сезона к сезону"],
                "correct": 3
            },
            {
                "question": "Распределение температуры по глубине, при котором по всей толще воды температура составляет примерно 4 градуса Цельсия, называется...",
                "options": ["Гомотермия", "Прямая стратификация", "Обратная стратификация", "Эпитермия"],
                "correct": 0
            },
            {
                "question": "Верхняя зона водоема, которая характеризуется малыми градиентами температуры или их отсутствием, называется...",
                "options": ["Металимнион", "Гиполимнион", "Эпилимнион", "Гомолимнион"],
                "correct": 2
            },
            {
                "question": "Тепловой барьер, который разделяет водоем на теплоактивную и теплоинертную зоны, называется...",
                "options": ["Гомотермия", "Гиполимнион", "Стратификация", "Термобар"],
                "correct": 3
            },
            {
                "question": "Какие виды волн образуются под действием ветра?",
                "options": ["Ветровые", "Нагонные", "Стоячие", "Свободные"],
                "correct": 0
            },
            {
                "question": "Горизонтальная линия, пересекающая профиль волны таким образом, что площади выше и ниже неё одинаковы - это...",
                "options": ["Длина волны", "Средняя волновая линия", "Результирующая волна", "Подошва волны"],
                "correct": 1
            },
            {
                "question": "Расстояние между вершиной волны и её подошвой - это...",
                "options": ["Высота волны", "Длина волны", "Крутизна волны", "Период волны"],
                "correct": 0
            },
            {
                "question": "Расстояние между двумя вершинами или между двумя подошвами волны - это...",
                "options": ["Длина волны", "Период волны", "Крутизна волны", "Высота волны"],
                "correct": 0
            },
            {
                "question": "Волнение, продолжающееся некоторое время на крупных водоемах при полном прекращении ветра, это…",
                "options": ["Рябь", "Затухающее волнение", "Мертвая зыбь", "Установившееся волнение"],
                "correct": 2
            },
            {
                "question": "Какие виды течений возникают, когда в силу тех или иных причин возникает наклон водной поверхности?",
                "options": ["Нагонные", "Градиентные", "Стоковые", "Ветровые"],
                "correct": 1
            },
            {
                "question": "Какие виды течений существуют после прекращения силы, вызвавшей тот или иной вид движения воды?",
                "options": ["Вдольбереговые", "Бароградиентные", "Инерционные", "Волновые"],
                "correct": 2
            },
            {
                "question": "При длительном действии ветра в одном направлении формируется устойчивое дрейфовое течение, при этом происходит перемещение масс воды из одной части водоема в другую. Повышение уровня в наветренной части водоема при этом называется…",
                "options": ["Сгон", "Дрейф", "Нагон", "Градиент"],
                "correct": 2
            },
            {
                "question": "Максимальная минерализация соляных озер наблюдается...",
                "options": ["В конце теплой части года", "В середине холодной части года", "В конце холодной части года", "В начале теплой части года"],
                "correct": 0
            },
            {
                "question": "Газы, которые поступают в воду из атмосферы, называют...",
                "options": ["Автохтонные", "Аллохтонные", "Эпилимнионные", "Активные"],
                "correct": 1
            },
            {
                "question": "Согласно классификации озер по трофности, глубокие, холодноводные водоёмы с чистой и прозрачной водой, относятся к группе...",
                "options": ["Эвтрофные", "Мезотрофные", "Олиготрофные", "Дистрофные"],
                "correct": 2
            },
            {
                "question": "Уравнение (dV/dT) = Vпр + Vос - Vисп, где пр - приток, ос - осадки, исп - испарение, V - объем, T - время, описывает...",
                "options": ["Изменение запасов воды для вогнутых болотных массивов котловинного залегания", 
                           "Изменение запасов воды для выпуклых болотных массивов котловинного залегания", 
                           "Изменение запасов воды для переходных болотных массивов террасного залегания"],
                "correct": 1
            },
            {
                "question": "Толщу торфа в болотах можно разделить на две зоны: деятельный и инертный горизонты. Что является границей?",
                "options": ["Глубина, до которой проникает солнечный свет", "Уровень торфяной залежи", "Уровень болотных грунтовых вод", "Глубина инфильтрации"],
                "correct": 2
            },
            {
                "question": "Основным источником влаги, образующей ледник, являются…",
                "options": ["Жидкие атмосферные осадки", "Разницы температур на склоне и вершине", "Твердые атмосферные осадки", "Изменения режима испарения"],
                "correct": 2
            },
            {
                "question": "Ледники именно этого типа принимают непосредственное участие в формировании стока рек.",
                "options": ["Горные", "Покровные", "Сетчатые"],
                "correct": 0
            }
        ]

        # Инициализация теста
        self.initialize_quiz()
    
    def initialize_quiz(self):
        """Инициализация теста с перемешанными вопросами"""
        # Перемешиваем вопросы
        self.questions = random.sample(self.all_questions, len(self.all_questions))
        
        # Инициализация параметров теста
        self.current_question = 0
        self.score = 0
        self.user_answers = [None] * len(self.questions)
        self.test_completed = False
        
        # Обновление интерфейса
        self.update_question()
        self.start_timer()
    
    def start_timer(self):
        """Запуск таймера"""
        self.timer_running = True
        self.update_timer()
    
    def update_timer(self):
        """Обновление отображения таймера"""
        if not self.timer_running:
            return
            
        minutes = self.time_left // 60
        seconds = self.time_left % 60
        self.timer_label.config(text=f"Осталось времени: {minutes:02d}:{seconds:02d}")
        
        if self.time_left <= 0:
            self.timer_running = False
            messagebox.showwarning("Время вышло!", "Время на прохождение теста истекло!")
            self.submit_quiz()
            return
        
        self.time_left -= 1
        self.root.after(1000, self.update_timer)
    
    def update_question(self):
        """Обновление отображения текущего вопроса"""
        if self.current_question < len(self.questions):
            q = self.questions[self.current_question]
            
            # Устанавливаем номер вопроса (выравнивание по левому краю)
            self.number_label.config(text=f"{self.current_question + 1}.")
            
            # Устанавливаем текст вопроса (выравнивание по левому краю)
            self.question_label.config(text=q["question"])
            
            # Обновляем варианты ответов
            for i, option in enumerate(q["options"]):
                self.radio_buttons[i].config(text=option)
            
            # Устанавливаем сохраненный ответ или сбрасываем
            if self.user_answers[self.current_question] is not None:
                self.radio_var.set(self.user_answers[self.current_question])
            else:
                self.radio_var.set(-1)
            
            # Обновляем состояние кнопок навигации
            self.prev_button.config(state="normal" if self.current_question > 0 else "disabled")
            self.next_button.config(state="normal" if self.current_question < len(self.questions) - 1 else "disabled")
            self.submit_button.config(state="normal" if self.current_question == len(self.questions) - 1 else "disabled")
    
    def next_question(self):
        """Переход к следующему вопросу"""
        self.user_answers[self.current_question] = self.radio_var.get()
        self.current_question += 1
        self.update_question()
    
    def prev_question(self):
        """Переход к предыдущему вопросу"""
        self.user_answers[self.current_question] = self.radio_var.get()
        self.current_question -= 1
        self.update_question()
    
    def submit_quiz(self):
        """Завершение теста и вывод результатов"""
        self.timer_running = False
        self.test_completed = True
        self.user_answers[self.current_question] = self.radio_var.get()
        self.calculate_score()
        
        # Показываем кнопку перезапуска теста
        self.restart_button.pack(pady=10)
        
        # Создаем окно результатов
        result_window = tk.Toplevel(self.root)
        result_window.title("Результаты теста")
        result_window.geometry("800x600")
        
        # Настройка прокрутки
        canvas = tk.Canvas(result_window)
        scrollbar = tk.Scrollbar(result_window, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas)
        
        scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Вывод результатов
        result_text = f"Ваш результат: {self.score} из {len(self.questions)}\n"
        percentage = (self.score / len(self.questions)) * 100
        
        # Определение оценки
        if percentage >= 85:
            grade = "«Вот теперь тебя люблю я, Вот теперь тебя хвалю я! Наконец-то ты, лапуля, Винокуру угодил!» (5)"
        elif percentage >= 70:
            grade = "Подтянись! Ещё! Е-ш-ш-о! Молодец! Герой! Отлично! Так! Оценка хорошо. (4)"
        elif percentage >= 50:
            grade = "Я не стыжусь, что ярый скептик и на душе не свет, а тьма; сомненье — лучший антисептик от загнивания ума. (3)"
        else:
            grade = "За дебоши, лень и тупость, за отчаянную глупость мы не сдавшего балбеса попросили выйти вон… (2)"
        
        # Отображение оценки
        result_label = tk.Label(scrollable_frame, text=result_text + f"Оценка: {grade}\n\n",
                              font=self.question_font)
        result_label.pack(anchor="w")
        
        # Отображение подробных результатов
        for i, q in enumerate(self.questions):
            user_answer = self.user_answers[i]
            correct_answer = q["correct"]
            
            # Текст вопроса
            question_label = tk.Label(scrollable_frame, text=f"{q['question']}", 
                                    font=self.question_font, wraplength=700, justify="left")
            question_label.pack(anchor="w", pady=(10, 0))
            
            # Варианты ответов с подсветкой
            for opt_idx, option in enumerate(q["options"]):
                option_text = option
                if opt_idx == correct_answer:
                    option_text = f"{option} (Правильный ответ)"
                
                if user_answer == opt_idx:
                    if user_answer == correct_answer:
                        color = "green"
                    else:
                        color = "red"
                    option_label = tk.Label(scrollable_frame, text=f"  {option_text}", 
                                          font=self.option_font, fg=color, wraplength=650, 
                                          justify="left")
                else:
                    if opt_idx == correct_answer:
                        option_label = tk.Label(scrollable_frame, text=f"  {option_text}", 
                                              font=self.option_font, fg="blue", wraplength=650, 
                                              justify="left")
                    else:
                        option_label = tk.Label(scrollable_frame, text=f"  {option}", 
                                              font=self.option_font, wraplength=650, 
                                              justify="left")
                
                option_label.pack(anchor="w")
        
        # Кнопка закрытия окна результатов
        close_button = tk.Button(result_window, text="Закрыть", command=result_window.destroy)
        close_button.pack(pady=10)
    
    def restart_quiz(self):
        """Перезапуск теста с новым порядком вопросов"""
        self.initialize_quiz()
        self.restart_button.pack_forget()
    
    def calculate_score(self):
        """Подсчет правильных ответов"""
        self.score = 0
        for i, q in enumerate(self.questions):
            if self.user_answers[i] == q["correct"]:
                self.score += 1

if __name__ == "__main__":
    root = tk.Tk()
    app = QuizApp(root)
    root.mainloop()
