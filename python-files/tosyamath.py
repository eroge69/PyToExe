import tkinter as tk
from tkinter import scrolledtext, messagebox
import re

class SimpleLangCompiler:
    def __init__(self, root):
        self.root = root
        self.root.title("Tosya Math")
        self.root.geometry("800x600")
        
        # Переменные для хранения состояния
        self.variables = {}
        
        # Создаем меню
        self.menu_bar = tk.Menu(root)
        self.file_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.file_menu.add_command(label="Открыть", command=self.open_file)
        self.file_menu.add_command(label="Сохранить", command=self.save_file)
        self.file_menu.add_separator()
        self.file_menu.add_command(label="Выход", command=root.quit)
        self.menu_bar.add_cascade(label="Файл", menu=self.file_menu)
        
        self.help_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.help_menu.add_command(label="О программе", command=self.about)
        self.menu_bar.add_cascade(label="Помощь", menu=self.help_menu)
        
        self.root.config(menu=self.menu_bar)
        
        # Панель редактора кода
        self.code_editor = scrolledtext.ScrolledText(
            root, wrap=tk.WORD, width=80, height=20, font=('Courier New', 12)
        )
        self.code_editor.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)
        
        # Панель вывода
        self.output_console = scrolledtext.ScrolledText(
            root, wrap=tk.WORD, width=80, height=10, font=('Courier New', 12),
            bg='black', fg='white'
        )
        self.output_console.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)
        self.output_console.config(state=tk.DISABLED)
        
        # Кнопки управления
        button_frame = tk.Frame(root)
        button_frame.pack(pady=5)
        
        self.run_button = tk.Button(
            button_frame, text="Запуск (F5)", command=self.run_code,
            width=15, bg='green', fg='white'
        )
        self.run_button.pack(side=tk.LEFT, padx=5)
        
        self.clear_button = tk.Button(
            button_frame, text="Очистить", command=self.clear_output,
            width=15
        )
        self.clear_button.pack(side=tk.LEFT, padx=5)
        
        # Горячие клавиши
        self.root.bind('<F5>', lambda event: self.run_code())
        
        # Добавляем пример кода при запуске
        self.code_editor.insert(tk.END, 
            'start:\n'
            'int x = 10\n'
            'str message = "Hello"\n'
            'printCons"message + \\" World\\""\n'
            'printCons\'x + 5\'\n'
            'printCons\'x\'\n'
            'end'
        )
    
    def run_code(self):
        """Выполняет код из редактора"""
        code = self.code_editor.get("1.0", tk.END)
        self.variables = {}  # Очищаем переменные перед каждым запуском
        
        # Проверяем наличие start: и end:
        if not re.search(r'start\s*:', code) or not re.search(r'end\s*', code):
            self.show_error("Ошибка: код должен начинаться с 'start:' и заканчиваться 'end'")
            return
        
        # Извлекаем код между start: и end
        try:
            code_block = re.search(r'start:(.*?)end', code, re.DOTALL).group(1)
        except AttributeError:
            self.show_error("Ошибка: не найден блок кода между 'start:' и 'end'")
            return
        
        # Разбиваем код на строки
        lines = [line.strip() for line in code_block.split('\n') if line.strip()]
        
        # Очищаем консоль перед выполнением
        self.clear_output()
        
        # Выполняем каждую команду
        for line in lines:
            try:
                self.execute_line(line)
            except Exception as e:
                self.show_error(f"Ошибка в строке: '{line}'\n{str(e)}")
                return
    
    def execute_line(self, line):
        """Выполняет одну строку кода"""
        # Обработка объявления переменной
        var_declaration = re.match(r'^(int|str)\s+([a-zA-Z_]\w*)\s*=\s*(.+)$', line)
        if var_declaration:
            var_type, var_name, var_value = var_declaration.groups()
            self.declare_variable(var_type, var_name, var_value)
            return
        
        # Обработка printCons
        print_match = re.match(r'^printCons([\'"])(.*?)\1$', line)
        if print_match:
            quote_type, content = print_match.groups()
            self.handle_print(content, quote_type)
            return
        
        # Если строка не распознана
        raise SyntaxError(f"Неизвестная команда: '{line}'")
    
    def declare_variable(self, var_type, var_name, var_value):
        """Объявляет переменную с указанным типом"""
        # Удаляем кавычки для строк
        if var_type == 'str':
            # Проверяем, что значение в кавычках
            if not (var_value.startswith('"') and var_value.endswith('"')) and \
               not (var_value.startswith("'") and var_value.endswith("'")):
                raise SyntaxError(f"Строковое значение должно быть в кавычках: {var_value}")
            
            # Удаляем кавычки
            var_value = var_value[1:-1]
        elif var_type == 'int':
            try:
                var_value = int(var_value)
            except ValueError:
                raise SyntaxError(f"Недопустимое целое значение: {var_value}")
        
        self.variables[var_name] = {'type': var_type, 'value': var_value}
    
    def handle_print(self, content, quote_type):
        """Обрабатывает команду printCons"""
        # Если это строка в кавычках (просто выводим)
        if quote_type == '"':
            self.print_to_console(content)
            return
        
        # Если это выражение в одинарных кавычках
        try:
            # Проверяем, это просто переменная или выражение
            if content in self.variables:
                # Просто выводим переменную
                value = self.variables[content]['value']
                self.print_to_console(str(value))
            else:
                # Вычисляем выражение
                result = self.evaluate_expression(content)
                self.print_to_console(str(result))
        except Exception as e:
            raise SyntaxError(f"Ошибка при вычислении выражения '{content}': {str(e)}")
    
    def evaluate_expression(self, expr):
        """Вычисляет арифметическое выражение"""
        # Заменяем переменные на их значения
        for var_name in self.variables:
            if self.variables[var_name]['type'] != 'int':
                continue
            expr = expr.replace(var_name, str(self.variables[var_name]['value']))
        
        # Безопасное вычисление выражения
        try:
            return eval(expr, {'__builtins__': None}, {})
        except:
            raise SyntaxError(f"Невозможно вычислить выражение: {expr}")
    
    def print_to_console(self, text):
        """Выводит текст в консоль"""
        self.output_console.config(state=tk.NORMAL)
        self.output_console.insert(tk.END, text + '\n', 'output')
        self.output_console.tag_config('output', foreground='light green')
        self.output_console.config(state=tk.DISABLED)
        self.output_console.see(tk.END)
    
    def show_error(self, message):
        """Показывает ошибку в консоли"""
        self.output_console.config(state=tk.NORMAL)
        self.output_console.insert(tk.END, message + '\n', 'error')
        self.output_console.tag_config('error', foreground='red')
        self.output_console.config(state=tk.DISABLED)
        self.output_console.see(tk.END)
    
    def clear_output(self):
        """Очищает консоль вывода"""
        self.output_console.config(state=tk.NORMAL)
        self.output_console.delete("1.0", tk.END)
        self.output_console.config(state=tk.DISABLED)
    
    def open_file(self):
        """Открывает файл с кодом"""
        try:
            file_path = tk.filedialog.askopenfilename(
                filetypes=[("TosyaMath файлы", "*.sl"), ("Все файлы", "*.*")]
            )
            if file_path:
                with open(file_path, 'r', encoding='utf-8') as file:
                    self.code_editor.delete("1.0", tk.END)
                    self.code_editor.insert(tk.END, file.read())
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось открыть файл: {e}")
    
    def save_file(self):
        """Сохраняет код в файл"""
        try:
            file_path = tk.filedialog.asksaveasfilename(
                defaultextension=".sl",
                filetypes=[("TosyaMath файлы", "*.sl"), ("Все файлы", "*.*")]
            )
            if file_path:
                with open(file_path, 'w', encoding='utf-8') as file:
                    file.write(self.code_editor.get("1.0", tk.END))
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить файл: {e}")
    
    def about(self):
        """Показывает информацию о программе"""
        messagebox.showinfo(
            "О программе",
            "TosyaMath Компилятор\n"
            "Версия 1.0\n\n"
            "Простой язык программирования с поддержкой:\n"
            "- Объявления переменных (int, str)\n"
            "- Арифметических операций\n"
            "- Вывода в консоль\n"
            "- Блоков start: и end:"
        )

if __name__ == "__main__":
    root = tk.Tk()
    compiler = SimpleLangCompiler(root)
    root.mainloop()
