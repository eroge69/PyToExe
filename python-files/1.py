import sqlite3
from datetime import datetime, timedelta
import tkinter as tk
from tkinter import messagebox

class HabitTracker:
    def __init__(self, root):
        self.root = root
        self.root.title("Дерево привычек")
        self.root.geometry("1000x600")
        self.root.configure(bg='#f5f5f5')
        
        # База данных
        self.conn = sqlite3.connect('habits.db', isolation_level=None)
        self.cursor = self.conn.cursor()
        self.create_tables()
        
        # Интерфейс
        self.create_widgets()
        self.load_habits()
        
        # Текущий выбор
        self.current_habit = None
        self.streak_days = 0
        
        # Стадии дерева
        self.tree_stages = {
            0: {"symbol": "🌳", "name": "Земля"},
            5: {"symbol": "🌱", "name": "Росток"}, 
            15: {"symbol": "🌿", "name": "Маленькое дерево"},
            25: {"symbol": "🌸", "name": "Цветущее дерево"},
            30: {"symbol": "🌳", "name": "Дерево с яблоками"}
        }

    def create_tables(self):
        """Создаем таблицы в БД с проверкой существования"""
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS habits (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS completions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                habit_id INTEGER,
                date TEXT,
                UNIQUE(habit_id, date),
                FOREIGN KEY (habit_id) REFERENCES habits(id)
            )
        ''')

    def create_widgets(self):
        """Создаем элементы интерфейса"""
        self.menu_frame = tk.Frame(self.root, width=200, bg='#2c3e50')
        self.menu_frame.pack(side=tk.LEFT, fill=tk.Y)
        
        tk.Button(
            self.menu_frame, text="☰", font=('Arial', 20),
            command=self.toggle_habits, bg='#2c3e50', fg='white'
        ).pack(pady=10)
        
        self.habits_listbox = tk.Listbox(
            self.menu_frame, bg='#34495e', fg='white',
            selectbackground='#3498db', font=('Arial', 12)
        )
        self.habits_listbox.pack(fill=tk.BOTH, expand=True)
        self.habits_listbox.bind("<<ListboxSelect>>", self.select_habit)
        
        center_frame = tk.Frame(self.root, bg='#f5f5f5')
        center_frame.pack(fill=tk.BOTH, expand=True)
        
        self.tree_label = tk.Label(
            center_frame, text="🟫", font=('Arial', 100),
            bg='white', bd=2, relief=tk.GROOVE
        )
        self.tree_label.pack(pady=20)
        
        self.days_label = tk.Label(
            center_frame, text="0", font=('Arial', 24, 'bold'), bg='#f5f5f5'
        )
        self.days_label.pack()
        
        self.days_unit_label = tk.Label(
            center_frame, text="дней", font=('Arial', 16), bg='#f5f5f5'
        )
        self.days_unit_label.pack()
        
        tk.Button(
            center_frame, text="✓ Отметить день", font=('Arial', 14),
            bg='#2ecc71', fg='white', command=self.mark_day
        ).pack(pady=20)
        
        history_frame = tk.Frame(self.root, width=250, bg='#ecf0f1')
        history_frame.pack(side=tk.RIGHT, fill=tk.Y)
        
        tk.Label(
            history_frame, text="История", font=('Arial', 14, 'bold'), bg='#ecf0f1'
        ).pack(pady=10)
        
        self.history_listbox = tk.Listbox(
            history_frame, font=('Arial', 11), bg='white'
        )
        self.history_listbox.pack(fill=tk.BOTH, expand=True)
        
        self.add_habit_frame = tk.Frame(self.root, bg='#f5f5f5')
        self.add_habit_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.new_habit_entry = tk.Entry(self.add_habit_frame, font=('Arial', 12))
        self.new_habit_entry.pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            self.add_habit_frame, text="Добавить привычку",
            command=self.add_habit, bg='#3498db', fg='white'
        ).pack(side=tk.LEFT)

    def toggle_habits(self):
        if self.habits_listbox.winfo_ismapped():
            self.habits_listbox.pack_forget()
        else:
            self.habits_listbox.pack(fill=tk.BOTH, expand=True)

    def add_habit(self):
        name = self.new_habit_entry.get().strip()
        if not name:
            return

        # Проверка на повтор по нижнему регистру
        self.cursor.execute("SELECT name FROM habits")
        existing_names = [row[0].strip().lower() for row in self.cursor.fetchall()]
        if name.lower() in existing_names:
            messagebox.showinfo("Повтор", "Такая привычка уже добавлена.")
            return

        self.cursor.execute("INSERT INTO habits (name) VALUES (?)", (name,))
        self.new_habit_entry.delete(0, tk.END)
        self.load_habits()

    def load_habits(self):
        self.habits_listbox.delete(0, tk.END)
        self.cursor.execute("SELECT name FROM habits")
        seen = set()
        for row in self.cursor.fetchall():
            name_clean = row[0].strip().lower()
            if name_clean not in seen:
                seen.add(name_clean)
                self.habits_listbox.insert(tk.END, row[0])

    def select_habit(self, event):
        selection = self.habits_listbox.curselection()
        if selection:
            self.current_habit = self.habits_listbox.get(selection[0])
            self.update_display()

    def mark_day(self):
        if not self.current_habit:
            messagebox.showwarning("Выбор", "Выберите привычку.")
            return
        self.cursor.execute("SELECT id FROM habits WHERE name = ?", (self.current_habit,))
        habit_id = self.cursor.fetchone()[0]
        today = datetime.now().date().isoformat()
        try:
            self.cursor.execute("INSERT INTO completions (habit_id, date) VALUES (?, ?)", (habit_id, today))
            self.update_display()
        except sqlite3.IntegrityError:
            messagebox.showinfo("Уже отмечено", "Сегодня уже отмечено.")

    def calculate_streak(self, dates):
        if not dates:
            return 0
        streak = 0
        today = datetime.now().date()
        for i, date_str in enumerate(dates):
            date_obj = datetime.strptime(date_str, "%Y-%m-%d").date()
            expected_date = today - timedelta(days=streak)
            if date_obj == expected_date:
                streak += 1
            else:
                break
        return streak

    def update_tree(self):
        stage_symbol = "🟫"
        for threshold in sorted(self.tree_stages.keys(), reverse=True):
            if self.streak_days >= threshold:
                stage_symbol = self.tree_stages[threshold]["symbol"]
                break
        self.tree_label.config(text=stage_symbol)

    def update_display(self):
        if not self.current_habit:
            return
        self.cursor.execute("SELECT id FROM habits WHERE name = ?", (self.current_habit,))
        habit_id = self.cursor.fetchone()[0]
        self.cursor.execute("SELECT date FROM completions WHERE habit_id = ? ORDER BY date DESC", (habit_id,))
        dates = [row[0] for row in self.cursor.fetchall()]
        self.history_listbox.delete(0, tk.END)
        for date in dates[:10]:
            self.history_listbox.insert(tk.END, date)
        self.streak_days = self.calculate_streak(dates)
        self.days_label.config(text=f"{self.streak_days}")
        self.update_tree()

if __name__ == "__main__":
    root = tk.Tk()
    app = HabitTracker(root)
    root.mainloop()
