import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
import io

# Создание окна
root = tk.Tk()
root.title("Тренажёр по языкам программирования")

root.config(bg="#2e2e2e")
root.attributes('-fullscreen', True)

# Темы и теория для каждого языка
languages = {
    "Python": {
        "topics": ["Основы синтаксиса", "Переменные и типы данных", "Условия и циклы", "Функции", "Списки и строки"],
        "theory": {
            "Основы синтаксиса": """Python — это высокоуровневый язык программирования, который используется в различных областях, включая веб-разработку, анализ данных, искусственный интеллект, автоматизацию задач и многое другое.\n\n
            Синтаксис Python минималистичен и прост, что делает его отличным выбором для начинающих. Основные элементы программы — это отступы, ключевые слова и операторы.\n\n
            Пример базовой программы Python:\n
            python\n
            print("Hello, World!")\n
            В Python нет необходимости в точках с запятой в конце строк, а блоки кода определяются с помощью отступов, а не фигурных скобок.\n
            Таким образом, в Python код всегда будет выглядеть аккуратно и легко читаемым.""",
            
            "Переменные и типы данных": """В Python переменные не требуют явного указания типа данных. Это динамически типизированный язык.\n\n
            Основные типы данных в Python:\n
            - int (целые числа): Пример: x = 5\n
            - float (вещественные числа): Пример: y = 3.14\n
            - str (строки): Пример: name = "Alice"\n
            - bool (логические значения): Пример: is_active = True\n
            - list (списки): Пример: my_list = [1, 2, 3, 4]\n
            - tuple (кортежи): Пример: my_tuple = (1, 2, 3)\n
            - dict (словарь): Пример: my_dict = {'key': 'value'}\n
            Пример использования переменной:\n
            python\n
            x = 10\n
            y = 3.14\n
            name = "Alice"\n
            print(x, y, name)\n
            Python автоматически присваивает тип в зависимости от значения, которое вы назначаете переменной. Также, вы можете изменять тип переменной в любой момент, например, можно присвоить строку переменной, а затем преобразовать её в число.""",
            
            "Условия и циклы": """Условия в Python выполняются с помощью операторов if, elif и else. Это позволяет программе принимать решения на основе значений переменных. Циклы позволяют повторять действия.\n\n
            Пример условия:\n
            python\n
            x = 10\n
            if x > 5:\n
                print("x больше 5")\n
            else:\n
                print("x меньше или равно 5")\n
            В Python условные операторы могут быть записаны в несколько строк, но часто они могут быть записаны и в одну строку для упрощения кода:\n
            python\n
            x = 10\n
            print("x больше 5") if x > 5 else print("x меньше или равно 5")\n
            Пример цикла for (перебор элементов):\n
            python\n
            for i in range(5):\n
                print(i)\n
            Цикл while выполняет код, пока условие истинно:\n
            python\n
            i = 0\n
            while i < 5:\n
                print(i)\n
                i += 1\n
            Важно помнить, что цикл может быть бесконечным, если условие не изменяется (например, если забыть увеличить переменную i в примере выше).""",
            
            "Функции": """Функции — это блоки кода, которые выполняют определённую задачу. Функции позволяют организовывать код в более удобные и логичные части. Вызывая одну и ту же функцию, можно многократно использовать одну и ту же логику.\n\n
            Определение функции выглядит так:\n
            python\n
            def greet(name):\n
                print(f"Hello, {name}")\n
            В этом примере функция greet принимает параметр name и выводит сообщение.\n\n
            Чтобы использовать функцию, нужно вызвать её с нужными аргументами:\n
            python\n
            greet("Alice")\n
            Функции могут возвращать значения с помощью ключевого слова return.\n
            Пример функции, которая возвращает результат:\n
            python\n
            def add(a, b):\n
                return a + b\n
            result = add(2, 3)\n
            print(result)  # Выведет 5\n
            Функции позволяют не только уменьшить количество повторяющегося кода, но и улучшить его читаемость и поддержку.""",
            
            "Списки и строки": """Списки (list) и строки (string) — это типы данных, которые позволяют хранить несколько элементов. Оба типа поддерживают индексацию, срезы и различные операции.\n\n
            Пример списка:\n
            python\n
            my_list = [1, 2, 3, 4]\n
            my_list.append(5)  # Добавить элемент в конец списка\n
            my_list[0] = 10  # Изменить первый элемент списка\n
            Пример строки:\n
            python\n
            my_string = "Hello, Python!"\n
            print(my_string[0])  # Доступ к первому символу строки\n
            print(my_string[0:5])  # Вывод среза: "Hello"\n
            В Python индексация начинается с 0, то есть первый элемент списка или строки имеет индекс 0. Также строки и списки поддерживают отрицательную индексацию, где -1 — это последний элемент.\n\n
            Пример отрицательной индексации:\n
            python\n
            print(my_list[-1])  # Выведет последний элемент списка\n
            print(my_string[-1])  # Выведет последний символ строки\n
            Важно помнить, что строки в Python являются неизменяемыми объектами, то есть вы не можете изменить символ строки напрямую. Для изменения строки нужно создать новую строку.""",
        },
        "tasks": {
            "Основы синтаксиса": "Напишите программу, которая выводит 'Привет, Python!' в консоль.",
            "Переменные и типы данных": "Создайте переменную x и присвойте ей число 10, затем выведите её на экран.",
            "Условия и циклы": "Напишите программу, которая выводит все чётные числа (num) от 1 до 20.",
            "Функции": "Напишите функцию, которая принимает имя и выводит 'Привет, <имя>!'",
            "Списки и строки": "Напишите программу, которая создаёт список user_list в котором будут числа от 1 до 5 и выводит его элементы (item) в цикле.",
        }
    },
    
    # Добавление языка JavaScript
    "JavaScript": {
        "topics": [
            "Основы синтаксиса",
            "Переменные и типы данных",
            "Условия и циклы",
            "Функции",
            "Массивы",
            "Объекты"
        ],
        "theory": {
            "Основы синтаксиса": """JavaScript — это язык программирования, который используется для создания динамических веб-страниц. Это язык сценариев, который выполняется в браузере пользователя.\n\n
            Основные элементы синтаксиса: переменные, операторы, функции, условия и циклы.\n\n
            Пример базовой программы на JavaScript:\n
            javascript\n
            console.log('Hello, World!');\n
            В JavaScript строки заканчиваются точками с запятой. Код внутри функций или условий часто ограничивается фигурными скобками.\n
            Также JavaScript чувствителен к регистру — например, переменные с именами `Variable` и `variable` будут разными.""",
            
            "Переменные и типы данных": """JavaScript имеет несколько типов данных: примитивные и ссылочные.\n\n
            Примитивные типы данных: string, number, boolean, null, undefined, symbol.\n
            Ссылочные типы данных: object, array.\n\n
            Пример объявления переменной:\n
            javascript\n
            let age = 25;\n
            let name = 'Alice';\n
            let isActive = true;\n
            Переменные можно объявлять с помощью ключевых слов `let`, `const` или `var`.""",
            
            "Условия и циклы": """Условия в JavaScript можно реализовать с помощью операторов if, else, и switch. Циклы — это конструкции для повторения действий.\n\n
            Пример условия:\n
            javascript\n
            let age = 18;\n
            if (age >= 18) {\n
                console.log('Взрослый');\n
            } else {\n
                console.log('Несовершеннолетний');\n
            }\n
            Пример цикла for:\n
            javascript\n
            for (let i = 0; i < 5; i++) {\n
                console.log(i);\n
            }\n
            Пример цикла while:\n
            javascript\n
            let i = 0;\n
            while (i < 5) {\n
                console.log(i);\n
                i++;\n
            }""",
            
            "Функции": """Функции в JavaScript — это блоки кода, которые выполняют действия. Функции могут принимать параметры и возвращать значения.\n\n
            Пример функции:\n
            javascript\n
            function greet(name) {\n
                console.log('Hello, ' + name);\n
            }\n
            greet('Alice');\n
            Функции могут быть как обычными, так и стрелочными:\n
            javascript\n
            const add = (a, b) => a + b;\n
            console.log(add(2, 3));  // Выведет 5""",
            
            "Массивы": """Массивы — это списки элементов в JavaScript. Массивы могут хранить данные любого типа.\n\n
            Пример массива:\n
            javascript\n
            let numbers = [1, 2, 3, 4];\n
            console.log(numbers[0]);  // Выведет 1\n
            Чтобы вывести последнее число:\n
            console.log(numbers[numbers.length - 1]) // Выведет 4\n
            Массивы поддерживают различные методы для работы с элементами, например: `.push()`, `.pop()`, `.shift()`, `.unshift()`, `.map()`, `.filter()`.""",
            
            "Объекты": """Объекты в JavaScript позволяют хранить данные в виде пар "ключ-значение".\n\n
            Пример объекта:\n
            javascript\n
            let person = {\n
                name: 'Alice',\n
                age: 25,\n
                greet: function() { console.log('Hello, ' + this.name); }\n
            };\n
            console.log(person.name);  // Выведет Alice\n
            person.greet();  // Выведет Hello, Alice""",
        },
        "tasks": {
            "Основы синтаксиса": "Напишите программу, которая выводит в консоль фразу 'Привет, JavaScript!'",
            "Переменные и типы данных": "Объявите переменную name, присвойте ей имя Алексей и выведите в консоль строку:'Его зовут [name]', где [name] — значение переменной",
            "Условия и циклы": "Напишите программу, которая выводит в консоль все четные числа от 1 до 10, используя цикл for.",
            "Функции": "Напишите функцию greet(name), которая принимает имя как аргумент и выводит в консоль фразу:'Привет, (name)'",
            "Массивы": "Создайте массив numbers из пяти чисел. Выведите в консоль первое и последнее число из массива.",
            "Объекты": "Создайте объект student с полями name Олег (имя) и age 21 (возраст). Выведите в консоль фразу:'Студент [name] имеет возраст [age]'",
        },
    },

    # Добавление языка Паскаль
    "Pascal": {
        "topics": [
            "Введение в Паскаль",
            "Переменные и типы данных",
            "Операторы ввода и вывода",
            "Арифметические и логические операции",
            "Условные операторы (if, case)",
            "Циклы (for, while, repeat)"
        ],
        "theory": {
            "Введение в Паскаль": """Паскаль — это структурированный язык программирования, разработанный в 1970\n
            году швейцарским ученым Никлаусом Виртом. Язык был создан для преподавания программирования\n
            и демонстрации принципов структурного программирования, таких как разделение программы\n
            на модули и использование контрольных структур (циклы, условия).\n
            Программа на Паскале состоит из:\n
                Заголовка программы с указанием имени программы, например program HelloWorld;.\n
                Секции объявления переменных (если таковые используются), которая начинается с ключевого слова var.\n
                Основной части программы, которая заключается в блоке begin и end..\n
            Пример базовой программы:\n
                program HelloWorld;\n
                begin\n
                    writeln('Hello, Pascal!');\n
                end.\n
            Программа выводит текст на экран и завершает выполнение. Паскаль является языком с сильной\n
            типизацией, что означает, что типы данных переменных должны быть объявлены заранее.""",
            
            "Переменные и типы данных": """Переменные в Паскале — это области памяти, которым присваиваются имена для хранения\n
            данных. Переменные должны быть объявлены в начале программы в разделе var. Паскаль\n
            поддерживает множество типов данных, среди которых:\n
                integer — целые числа, например: 3, -45, 1024.\n
                real — числа с плавающей запятой, например: 3.14, -0.001, 2.718.\n
                char — одиночный символ, например: 'a', '1', '#'.\n
                string — строка символов, например: 'Hello', 'Pascal', '1234'.\n
                boolean — логическое значение, принимающее два состояния: true или false.\n
            Пример объявления переменных:\n
                var\n
                    age: integer;\n
                    name: string;\n
                    height: real;\n
                    isStudent: boolean;\n
                begin\n
                    age := 20;\n
                    name := 'Alex';\n
                    height := 1.75;\n
                    isStudent := true;\n
                    writeln('Name: ', name, ', Age: ', age);\n
                end.\n
            При объявлении переменных важно выбирать правильный тип данных для каждой\n
            переменной, чтобы избежать ошибок при выполнении программы.""",
            
            "Операторы ввода и вывода": """В Паскале для ввода данных с клавиатуры используется оператор readln, а для вывода данных на экран — оператор writeln.\n
            readln позволяет считывать данные с клавиатуры и сохранять их в\n
            переменных, а writeln выводит текст или значения переменных на экран.\n
                writeln — вывод данных с переходом на новую строку.\n
                write — вывод данных без перехода на новую строку.\n
                readln — ввод данных с клавиатуры.\n
                read — ввод данных без перехода на новую строку.\n
            Пример:\n
                var\n
                    name: string;\n
                    age: integer;\n
                begin\n
                    writeln('Enter your name:');\n
                    readln(name);\n
                    writeln('Enter your age:');\n
                    readln(age);\n
                    writeln('Hello, ', name, '. You are ', age, ' years old.');\n
                end.\n
            Ввод данных с помощью readln прекращается, как только пользователь нажимает клавишу Enter. Этот оператор\n
            может быть использован для ввода различных типов данных, если\n
            соответствующие переменные объявлены.""",
            
            "Арифметические и логические операции": """Паскаль поддерживает стандартные арифметические и логические операции.\n

            Арифметические операции:\n
+ — сложение\n
- — вычитание\n
* — умножение\n
/ — деление (для целых чисел деление возвращает результат с остатком)\n
div — целочисленное деление\n
mod — операция остатка от деления\n
Логические операции:\n
and — логическое "и"\n
or — логическое "или"\n
not — логическое "не"\n
=, <>, <, >, <=, >= — операции сравнения.\n
Пример использования арифметических операций:\n
var\n
  a, b, sum: integer;\n
begin\n
  a := 10;\n
  b := 5;\n
  sum := a + b;\n
  writeln('Sum: ', sum);\n
end.\n
Пример использования логических операций:\n
var\n
  isEven, isPositive: boolean;\n
begin\n
  isEven := 10 mod 2 = 0;\n
  isPositive := 10 > 0;\n
  writeln('Is number even? ', isEven);\n
  writeln('Is number positive? ', isPositive);\n
end.""",
            
            "Условные операторы (if, case)": """Условные операторы позволяют выполнить различные действия в зависимости от значения выражений.\n

if — проверяет условие и выполняет действия, если оно истинно.\n
\n
\n
if condition then\n
  statement;\n
else — выполняет альтернативное действие, если условие ложно.\n
\n
\n
if condition then\n
  statement\n
else\n
  alternative_statement;\n
 \n 
case — используется для множественного выбора, когда необходимо проверить несколько возможных значений переменной.\n
\n
\n
case variable of\n
  value1: statement1;\n
  value2: statement2;\n
  ...\n
else\n
  default_statement;\n
end;\n
\n
Пример с if:\n
\n
\n
var\n
  num: integer;\n
begin\n
  readln(num);\n
  if num > 0 then\n
    writeln('Positive number')\n
  else\n
    writeln('Non-positive number');\n
end.\n
\n
Пример с case:\n
var\n
  day: integer;\n
begin\n
  readln(day);\n
  case day of\n
    1: writeln('Monday');\n
    2: writeln('Tuesday');\n
    3: writeln('Wednesday');\n
    4: writeln('Thursday');\n
    5: writeln('Friday');\n
    6: writeln('Saturday');\n
    7: writeln('Sunday');\n
  else\n
    writeln('Invalid day');\n
  end;\n
end.""",
            "Циклы (for, while, repeat)":"""Циклы используются для многократного выполнения блока кода, пока условие выполняется.\n
\n
for — цикл с заданным числовым диапазоном, выполняется фиксированное количество раз.\n
\n
\n
for variable := start_value to end_value do\n
  statement;\n
while — цикл, который выполняется, пока условие истинно.\n
\n
\n
while condition do\n
  statement;\n
repeat — цикл, который выполняется хотя бы один раз, а затем проверяет условие.\n
\n
\n
repeat\n
  statement;\n
until condition;\n
Пример с for:\n
var\n
  i: integer;\n
begin\n
  for i := 1 to 5 do\n
    writeln(i);\n
end.\n
Пример с while:\n
var\n
  i: integer;\n
begin\n
  i := 1;\n
  while i <= 5 do\n
  begin\n
    writeln(i);\n
    i := i + 1;\n
  end;\n
end.\n
\n
Пример с repeat:\n
var\n
  i: integer;\n
begin\n
  i := 1;\n
  repeat\n
    writeln(i);\n
    i := i + 1;\n
  until i > 5;\n
end.
"""
        },
        "tasks": {
            "Введение в Паскаль": "Напишите программу, которая выводит на экран текст 'Привет, Паскаль!''.",
            "Переменные и типы данных": "Объявите переменные для хранения имени name (строка) и возраста age (целое число), присвойте им значения Джон, 25 и выведите на экран.",
            "Операторы ввода и вывода": "Напишите программу, которая запрашивает имя пользователя name и выводит его на экран.",
            "Арифметические и логические операции": "Напишите программу, которая выполняет сложение двух чисел num1=10 и num2=5 и выводит результат sum.",
            "Условные операторы (if, case)": "Напишите программу, которая проверяет, является ли число четным или нечетным.",
            "Циклы (for, while, repeat)": "Напишите программу, которая выводит числа от 1 до 5 с помощью цикла for."
        },
    },
}

# Функция для смены страниц
def show_page(page):
    for frame in [frame_home, frame_topics, frame_theory, frame_practice]:
        frame.pack_forget()
    page.pack()



# Стартовая страница (выбор языка)
def choose_language():
    global current_language
    current_language = language_listbox.get(tk.ACTIVE)
    
    # Обновляем список тем для выбранного языка
    topic_listbox.delete(0, tk.END)
    for topic in languages[current_language]["topics"]:
        topic_listbox.insert(tk.END, topic)
    
    # Переключаемся на страницу с темами
    show_page(frame_topics)

# Страница с темами
def choose_topic():
    selected_topic = topic_listbox.get(tk.ACTIVE)
    
    if selected_topic:
        # Переключаемся на страницу теории
        show_theory(selected_topic)
    else:
        messagebox.showwarning("Предупреждение", "Выберите тему для отображения теории.")

# Теория
def show_theory(selected_topic):
    theory_text.delete(1.0, tk.END)  # Очищаем текст перед вставкой
    theory_text.insert(tk.END, languages[current_language]["theory"][selected_topic])  # Вставляем текст теории
    
    # Добавляем кнопку для перехода к практике
    next_button.pack_forget()  # Скрываем кнопку с прошлого перехода
    next_button.pack(pady=10)
    
    # Добавляем кнопку возврата к темам
    back_to_topics_button.pack(pady=10)  # Показываем кнопку "Назад к темам"
    
    # Показываем кнопку возврата к выбору языка
    back_to_language_button.pack(pady=10)  # Показываем кнопку "Назад к выбору языка"
    
    show_page(frame_theory)

# Переход к практике
def go_to_practice():
    selected_topic = topic_listbox.get(tk.ACTIVE)
    task_label.config(text=languages[current_language]["tasks"][selected_topic])
    
    # Скрываем кнопку "Перейти к практике" на странице практики
    practice_button.pack_forget()
    
    
    show_page(frame_practice)

# Функция для отображения теории
def show_theory(selected_topic):
    theory_text.delete(1.0, tk.END)  # Очищаем текст перед вставкой
    theory_text.insert(tk.END, languages[current_language]["theory"][selected_topic])  # Вставляем текст теории
    
    # Показываем кнопку перехода к практике
    next_button.pack(pady=10)
    
    # Добавляем кнопку возврата к темам
    back_to_topics_button.pack(pady=10)  # Показываем кнопку "Назад к темам"
    
    # Показываем кнопку возврата к выбору языка
    back_to_language_button.pack(pady=10)  # Показываем кнопку "Назад к выбору языка"
    
    show_page(frame_theory)    

# Задание
def show_task():
    selected_topic = topic_listbox.get(tk.ACTIVE)
    task_label.config(text=languages[current_language]["tasks"][selected_topic])




# Функция для проверки выполнения задания (проверка введённого текста)
def check_task():
    task = task_label.cget("text")
    user_input = console_input.get("1.0", tk.END).strip()
    
    if task == languages["JavaScript"]["tasks"]["Основы синтаксиса"]:
        expected_text = "console.log('Привет, JavaScript!');"
        if user_input == expected_text:
            messagebox.showinfo("Успех", "Задание выполнено правильно!")
        else:
            messagebox.showerror("Ошибка", f"ОЖИДАЛОСЬ:\n{expected_text} \n ПОЛУЧЕНО: \n{user_input}")
    
    elif task == languages["JavaScript"]["tasks"]["Переменные и типы данных"]:
        expected_text = 'let name = "Алексей";\nconsole.log("Меня зовут " + name);'
        expected_text2 = 'let name = "Алексей";\nconsole.log(`Меня зовут ${name}`);'
                        
        if user_input == expected_text or expected_text2:
            messagebox.showinfo("Успех", "Задание выполнено правильно!")
        else:
            messagebox.showerror("Ошибка", f"ОЖИДАЛОСЬ:\n{expected_text} \n ПОЛУЧЕНО: \n{user_input}")

    elif task == languages["JavaScript"]["tasks"]["Условия и циклы"]:
        expected_text = "for (let i = 1; i <= 10; i++){\nif (i % 2 === 0){\nconsole.log(i);\n}\n}"
        if user_input == expected_text:
            messagebox.showinfo("Успех", "Задание выполнено правильно!")
        else:
            messagebox.showerror("Ошибка", f"ОЖИДАЛОСЬ:\n{expected_text} \n ПОЛУЧЕНО: \n{user_input}")

    elif task == languages["JavaScript"]["tasks"]["Функции"]:
        expected_text = "function greet(name) {\nconsole.log('Привет' + name);\n}"
        if user_input == expected_text:
            messagebox.showinfo("Успех", "Задание выполнено правильно!")
        else:
            messagebox.showerror("Ошибка", f"ОЖИДАЛОСЬ:\n{expected_text} \n ПОЛУЧЕНО: \n{user_input}")
    
    elif task == languages["JavaScript"]["tasks"]["Массивы"]:
        expected_text = "let numbers = [10, 20, 30, 40, 50];\nconsole.log(numbers[0]);\nconsole.log(numbers[numbers.length - 1]);"
        if user_input == expected_text:
            messagebox.showinfo("Успех", "Задание выполнено правильно!")
        else:
            messagebox.showerror("Ошибка", f"ОЖИДАЛОСЬ:\n{expected_text} \n ПОЛУЧЕНО: \n{user_input}")
    
    elif task == languages["JavaScript"]["tasks"]["Объекты"]:
        expected_text = "let student = {\nname: 'Олег',\nage: 21\n};\nconsole.log(`Студент ${student.name} имеет возраст ${student.age}`);"
        if user_input == expected_text:
            messagebox.showinfo("Успех", "Задание выполнено правильно!")
        else:
            messagebox.showerror("Ошибка", f"ОЖИДАЛОСЬ:\n{expected_text} \n ПОЛУЧЕНО: \n{user_input}")
    
    elif task == languages["Python"]["tasks"]["Основы синтаксиса"]:
        expected_text = "print('Привет, Python!')"
        if user_input == expected_text:
            messagebox.showinfo("Успех", "Задание выполнено правильно!")
        else:
            messagebox.showerror("Ошибка", f"ОЖИДАЛОСЬ:\n{expected_text} \n ПОЛУЧЕНО: \n{user_input}")
    
    elif task == languages["Python"]["tasks"]["Переменные и типы данных"]:
        expected_text = "x = 10\nprint(x)"
        if user_input == expected_text:
            messagebox.showinfo("Успех", "Задание выполнено правильно!")
        else:
            messagebox.showerror("Ошибка", f"ОЖИДАЛОСЬ:\n{expected_text} \n ПОЛУЧЕНО: \n{user_input}")

    elif task == languages["Python"]["tasks"]["Условия и циклы"]:
        expected_text = "for num in range(1, 21):\n if num % 2 == 0:\n  print(num)"
        if user_input == expected_text:
            messagebox.showinfo("Успех", "Задание выполнено правильно!")
        else:
            messagebox.showerror("Ошибка", f"ОЖИДАЛОСЬ:\n{expected_text} \n ПОЛУЧЕНО: \n{user_input}")
    
    elif task == languages["Python"]["tasks"]["Функции"]:
        expected_text = "def greet(name):\n print(f'Привет, {name}!')"
        if user_input == expected_text:
            messagebox.showinfo("Успех", "Задание выполнено правильно!")
        else:
            messagebox.showerror("Ошибка", f"ОЖИДАЛОСЬ:\n{expected_text} \n ПОЛУЧЕНО: \n{user_input}")

    elif task == languages["Python"]["tasks"]["Списки и строки"]:
        expected_text = "user_list = [1, 2, 3, 4, 5]\nfor item in user_list:\n print(item)"
        if user_input == expected_text:
            messagebox.showinfo("Успех", "Задание выполнено правильно!")
        else:
            messagebox.showerror("Ошибка", f"ОЖИДАЛОСЬ:\n{expected_text} \n ПОЛУЧЕНО: \n{user_input}")
    
    elif task == languages["Pascal"]["tasks"]["Введение в Паскаль"]:
        expected_text = "begin\n writeln('Привет, Паскаль!');\nend"
        if user_input == expected_text:
            messagebox.showinfo("Успех", "Задание выполнено правильно!")
        else:
            messagebox.showerror("Ошибка", f"ОЖИДАЛОСЬ:\n{expected_text} \n ПОЛУЧЕНО: \n{user_input}")

    elif task == languages["Pascal"]["tasks"]["Переменные и типы данных"]:
        expected_text = "var\n name: string;\n age: integer;\nbegin\n name := 'Джон';\n age := 25;\n writeln(name);\n writeln(age);\nend."
        if user_input == expected_text:
            messagebox.showinfo("Успех", "Задание выполнено правильно!")
        else:
            messagebox.showerror("Ошибка", f"ОЖИДАЛОСЬ:\n{expected_text} \n ПОЛУЧЕНО: \n{user_input}")

    elif task == languages["Pascal"]["tasks"]["Операторы ввода и вывода"]:
        expected_text = "var\n name: string;\nbegin\n readln(name);\n writeln(name);\nend."
        if user_input == expected_text:
            messagebox.showinfo("Успех", "Задание выполнено правильно!")
        else:
            messagebox.showerror("Ошибка", f"ОЖИДАЛОСЬ:\n{expected_text} \n ПОЛУЧЕНО: \n{user_input}")

    elif task == languages["Pascal"]["tasks"]["Арифметические и логические операции"]:
        expected_text = "var\n num1, num2, sum: integer;\nbegin\n num1 := 10;\n num2 := 5;\n sum := num1 + num2;\n writeln('The sum is: ', sum);\nend."
        if user_input == expected_text:
            messagebox.showinfo("Успех", "Задание выполнено правильно!")
        else:
            messagebox.showerror("Ошибка", f"ОЖИДАЛОСЬ:\n{expected_text} \n ПОЛУЧЕНО: \n{user_input}")

    elif task == languages["Pascal"]["tasks"]["Условные операторы (if, case)"]:
        expected_text = "var\n number: integer;\nbegin\n writeln('Enter a number:');\n readln(number);\n if number mod 2 = 0 then\n  writeln('The number is even.')\n else\n  writeln('The number is odd.');\nend."
        if user_input == expected_text:
            messagebox.showinfo("Успех", "Задание выполнено правильно!")
        else:
            messagebox.showerror("Ошибка", f"ОЖИДАЛОСЬ:\n{expected_text} \n ПОЛУЧЕНО: \n{user_input}")

    elif task == languages["Pascal"]["tasks"]["Циклы (for, while, repeat)"]:
        expected_text = "var\n i: integer;\nbegin\n for i := 1 to 5 do\n  writeln(i);\nend."
        if user_input == expected_text:
            messagebox.showinfo("Успех", "Задание выполнено правильно!")
        else:
            messagebox.showerror("Ошибка", f"ОЖИДАЛОСЬ:\n{expected_text} \n ПОЛУЧЕНО: \n{user_input}")



    else:
        messagebox.showwarning("Предупреждение", "Проверка для этого задания ещё не реализована.")

# Функция для выполнения кода
def run_code():
    check_task()



# Функция возврата к теории
def back_to_theory():
    selected_topic = topic_listbox.get(tk.ACTIVE)
    show_theory(selected_topic)

# Функция возврата к темам
def back_to_topics():
    show_page(frame_topics)

# Функция возврата к выбору языка
def back_to_language():
    show_page(frame_home)

# Структура страницы выбора языка
frame_home = tk.Frame(root, bg="#2e2e2e")

welcome_label = tk.Label(frame_home, text="Выберите язык программирования", font=("Arial", 24), bg="#2e2e2e", fg="white")
welcome_label.pack(pady=20)

language_listbox = tk.Listbox(frame_home, font=("Arial", 25), bg="#3e3e3e", fg="white", width=35, height=20 )
for language in languages.keys():
    language_listbox.insert(tk.END, language)
language_listbox.pack(pady=10)

choose_button = tk.Button(frame_home, text="Выбрать язык", command=choose_language, font=("Arial", 16), bg="#4CAF50", fg="white", relief="flat", width=55, height= 1)
choose_button.pack(pady=10)

frame_home.pack()

# Структура страницы с темами
frame_topics = tk.Frame(root, bg="#2e2e2e")

topic_listbox = tk.Listbox(frame_topics, font=("Arial", 25), bg="#3e3e3e", fg="white", width=35, height=20)
topic_listbox.pack(pady=10)

choose_topic_button = tk.Button(frame_topics, text="Выбрать тему", command=choose_topic, font=("Arial", 16), bg="#2196F3", fg="white", relief="flat", width=50, height= 1)
choose_topic_button.pack(pady=10)

# Кнопка возврата к выбору языка
back_to_language_button = tk.Button(frame_topics, text="Назад к выбору языка", command=back_to_language, font=("Arial", 16), bg="#FF9800", fg="white", relief="flat", width=50, height= 1)
back_to_language_button.pack_forget()

frame_topics.pack_forget()



# Структура страницы теории
frame_theory = tk.Frame(root, bg="#2e2e2e")

theory_text = tk.Text(frame_theory, height=40, width=80, bg="#1e1e1e", fg="white", font=("Courier", 15))
theory_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)

# Скроллбар для теории
theory_scrollbar = tk.Scrollbar(frame_theory, command=theory_text.yview)
theory_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
theory_text.config(yscrollcommand=theory_scrollbar.set)

# Кнопка перехода к практике
next_button = tk.Button(frame_theory, text="Перейти к практике", command=go_to_practice, font=("Arial", 14), bg="#FF9800", fg="white", relief="flat", width=25)
next_button.pack_forget()

# Кнопка возврата к темам
back_to_topics_button = tk.Button(frame_theory, text="Назад к темам", command=back_to_topics, font=("Arial", 14), bg="#FF9800", fg="white", relief="flat", width=25)
back_to_topics_button.pack_forget()

frame_theory.pack_forget()

# Структура страницы практики
frame_practice = tk.Frame(root, bg="#2e2e2e")

task_label = tk.Label(frame_practice, text="", font=("Arial", 18), bg="#2e2e2e", fg="white", justify=tk.LEFT)
task_label.pack(pady=10)

# Поле для ввода текста (консольный ввод)
console_input = tk.Text(frame_practice, height=40, width=80, bg="#f5f5f5", fg="black", font=("Courier", 12))
console_input.pack(pady=10)

# Кнопка для выполнения кода
run_button = tk.Button(frame_practice, text="Проверить ввод", command=run_code, font=("Arial", 16), bg="#4CAF50", fg="white", relief="flat", width=30)
run_button.pack(pady=10)

frame_practice.pack_forget()

# Кнопка для возврата к теории
back_to_theory_button = tk.Button(frame_practice, text="Назад к теории", command=back_to_theory, font=("Arial", 16), bg="#FF9800", fg="white", relief="flat", width=30)
back_to_theory_button.pack(pady=10)

# Кнопка для начала практики
practice_button = tk.Button(frame_practice, text="Перейти к практике", command=show_task, font=("Arial", 12), bg="#FF9800", fg="white", relief="flat", width=20)
practice_button.pack(pady=10)

frame_practice.pack_forget()




# Запуск приложения
root.mainloop()
