import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import os

class Exercise:
    def __init__(self, name, level, functions):
        self.name = name
        self.level = level
        self.functions = [func.strip().lower() for func in functions]

class ExerciseApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Exercise Manager")
        self.root.geometry("800x600")  # Увеличенный размер окна
        self.filename = "exercises.txt"
        self.exercises = self.load_exercises()
        
        self.create_widgets()
        self.update_exercise_list()

    def create_widgets(self):
        # Main Frame
        main_frame = ttk.Frame(self.root, padding=15)
        main_frame.pack(fill="both", expand=True)
        
        # Exercise List
        ttk.Label(main_frame, text="Список упражнений:", font=('Arial', 12, 'bold')).pack(anchor="w")
        
        self.exercise_tree = ttk.Treeview(main_frame, 
                                       columns=("Name", "Level", "Functions"), 
                                       show="headings",
                                       height=15)
        
        # Настройка колонок
        self.exercise_tree.heading("Name", text="Название", anchor="w")
        self.exercise_tree.heading("Level", text="Уровень", anchor="w")
        self.exercise_tree.heading("Functions", text="Функции", anchor="w")
        
        self.exercise_tree.column("Name", width=200, minwidth=150)
        self.exercise_tree.column("Level", width=80, minwidth=60)
        self.exercise_tree.column("Functions", width=400, minwidth=300)
        
        self.exercise_tree.pack(fill="both", expand=True, pady=10)
        
        # Button Frame
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill="x", pady=10)
        
        ttk.Button(button_frame, text="Добавить", command=self.add_exercise).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Рекомендации", command=self.show_recommendations).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Сохранить и выйти", command=self.save_and_exit).pack(side="right", padx=5)

    def load_exercises(self):
        exercises = []
        if os.path.exists(self.filename):
            try:
                with open(self.filename, 'r', encoding='utf-8') as file:
                    content = file.read().strip().split('\n\n')
                    for entry in content:
                        lines = entry.split('\n')
                        ex_data = {'name': None, 'level': None, 'functions': []}
                        for line in lines:
                            if line.startswith('Название: '):
                                ex_data['name'] = line.split(': ')[1].strip()
                            elif line.startswith('Уровень: '):
                                ex_data['level'] = int(line.split(': ')[1].strip())
                            elif line.startswith('Функции: '):
                                funcs = line.split(': ')[1].strip().split(', ')
                                ex_data['functions'] = [f.lower() for f in funcs]
                        if all(ex_data.values()):
                            exercises.append(Exercise(**ex_data))
            except Exception as e:
                messagebox.showerror("Ошибка", f"Ошибка загрузки файла: {str(e)}")
        return exercises

    def save_exercises(self):
        try:
            with open(self.filename, 'w', encoding='utf-8') as file:
                for ex in self.exercises:
                    file.write(f"Название: {ex.name}\n")
                    file.write(f"Уровень: {ex.level}\n")
                    file.write(f"Функции: {', '.join(ex.functions)}\n\n")
            return True
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка сохранения: {str(e)}")
            return False

    def update_exercise_list(self):
        for item in self.exercise_tree.get_children():
            self.exercise_tree.delete(item)
        for ex in self.exercises:
            self.exercise_tree.insert("", "end", values=(
                ex.name,
                ex.level,
                ", ".join(ex.functions)
            ))

    def add_exercise(self):
        dialog = ExerciseDialog(self.root)
        self.root.wait_window(dialog.top)
        if dialog.result:
            self.exercises.append(dialog.result)
            self.update_exercise_list()

    def show_recommendations(self):
        target_part = simpledialog.askstring("Рекомендации", "Введите часть названия упражнения 3-го уровня:")
        if not target_part:
            return
        
        # Ищем все упражнения 3-го уровня, содержащие введённую подстроку
        target_part = target_part.lower()
        found_exercises = [
            ex for ex in self.exercises 
            if ex.level == 3 and target_part in ex.name.lower()
        ]
        
        if not found_exercises:
            messagebox.showinfo("Информация", "Упражнения 3-го уровня не найдены!")
            return
        
        # Если найдено несколько - предлагаем выбрать
        if len(found_exercises) > 1:
            choice = self.ask_exercise_choice(found_exercises)
            if choice is None:
                return
            found_ex = found_exercises[choice]
        else:
            found_ex = found_exercises[0]
        
        recs = self.get_recommendations(found_ex)
        self.show_recommendation_window(recs, found_ex.name)

    def ask_exercise_choice(self, exercises):
        window = tk.Toplevel(self.root)
        window.title("Выбор упражнения")
        window.geometry("400x300")
        
        ttk.Label(window, text="Выберите упражнение:", font=('Arial', 11)).pack(pady=10)
        
        listbox = tk.Listbox(window, width=50)
        listbox.pack(fill="both", expand=True, padx=10, pady=5)
        
        for idx, ex in enumerate(exercises, 1):
            listbox.insert("end", f"{idx}. {ex.name} (функции: {', '.join(ex.functions)})")
        
        selected_idx = [None]  # Используем список для mutable хранилища
        
        def on_select():
            selected_idx[0] = listbox.curselection()[0]
            window.destroy()
        
        ttk.Button(window, text="Выбрать", command=on_select).pack(pady=10)
        
        window.wait_window()
        return selected_idx[0] if selected_idx[0] is not None else None

    def show_recommendation_window(self, recommendations, ex_name):
        window = tk.Toplevel(self.root)
        window.title(f"Рекомендации для: {ex_name}")
        window.geometry("600x400")
        
        notebook = ttk.Notebook(window)
        notebook.pack(fill="both", expand=True)
        
        for func, ex_list in recommendations.items():
            frame = ttk.Frame(notebook)
            notebook.add(frame, text=func.capitalize())
            
            if ex_list:
                columns = ("#1", "#2")
                tree = ttk.Treeview(frame, columns=columns, show="headings")
                tree.heading("#1", text="Название")
                tree.heading("#2", text="Уровень")
                tree.column("#1", width=300)
                tree.column("#2", width=100)
                
                for ex in ex_list:
                    tree.insert("", "end", values=(ex.name, ex.level))
                
                tree.pack(fill="both", expand=True, padx=10, pady=10)
            else:
                ttk.Label(frame, text="Нет рекомендаций для этой функции").pack(pady=20)

    def save_and_exit(self):
        if self.save_exercises():
            self.root.destroy()
            
    def get_recommendations(self, target_ex):
        func_to_ex = {}
        for ex in self.exercises:
            if ex.level in (1, 2):
                for func in ex.functions:
                    if func not in func_to_ex:
                        func_to_ex[func] = []
                    func_to_ex[func].append(ex)
        
        recommendations = {}
        for func in set(target_ex.functions):
            candidates = func_to_ex.get(func, [])
            seen = set()
            unique_candidates = []
            for ex in candidates:
                if ex.name not in seen:
                    seen.add(ex.name)
                    unique_candidates.append(ex)
            recommendations[func] = unique_candidates
        return recommendations        

class ExerciseDialog(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.result = None
        self.title("Добавить упражнение")
        self.geometry("400x250")
        self.create_widgets()
        
    def create_widgets(self):
        ttk.Label(self, text="Добавление нового упражнения", font=('Arial', 11, 'bold')).pack(pady=10)
        
        # Name
        ttk.Label(self, text="Название:").pack(anchor="w", padx=20)
        self.name_entry = ttk.Entry(self, width=30)
        self.name_entry.pack(padx=20, pady=5, fill="x")
        
        # Level
        ttk.Label(self, text="Уровень сложности:").pack(anchor="w", padx=20)
        self.level_var = tk.StringVar()
        ttk.Combobox(self, 
                    textvariable=self.level_var, 
                    values=["1", "2", "3"],
                    width=5).pack(anchor="w", padx=20, pady=5)
        
        # Functions
        ttk.Label(self, text="Функции (через запятую):").pack(anchor="w", padx=20)
        self.func_entry = ttk.Entry(self, width=30)
        self.func_entry.pack(padx=20, pady=5, fill="x")
        
        # Buttons
        button_frame = ttk.Frame(self)
        button_frame.pack(pady=15)
        
        ttk.Button(button_frame, text="Добавить", command=self.validate).pack(side="left", padx=10)
        ttk.Button(button_frame, text="Отмена", command=self.destroy).pack(side="right", padx=10)

    def validate(self):
        name = self.name_entry.get().strip()
        level = self.level_var.get()
        funcs = [f.strip().lower() for f in self.func_entry.get().split(",") if f.strip()]
        
        errors = []
        if not name:
            errors.append("Введите название упражнения")
        if not level.isdigit() or int(level) not in {1, 2, 3}:
            errors.append("Уровень должен быть числом от 1 до 3")
        if not funcs:
            errors.append("Укажите хотя бы одну функцию")
        
        if errors:
            messagebox.showerror("Ошибка", "\n".join(errors))
            return
        
        self.result = Exercise(name, int(level), funcs)
        self.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = ExerciseApp(root)
    root.mainloop()