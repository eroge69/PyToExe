import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from datetime import datetime
import json
import os

class SoloLevelingGoalsApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Solo Leveling Goals")
        self.root.geometry("700x800")
        self.root.configure(bg="#121212")
        
        # Настройка стиля Solo Leveling (тёмный + синие акценты)
        self.setup_solo_leveling_theme()
        
        # Данные
        self.data_file = "solo_goals.json"
        self.goals = self.load_data()
        
        # Интерфейс
        self.create_widgets()
        self.update_goals_list()
        
        # Автосохранение при закрытии
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def setup_solo_leveling_theme(self):
        style = ttk.Style()
        style.theme_use('alt')
        
        # Цвета
        self.bg_color = "#121212"
        self.fg_color = "#e0e0e0"
        self.accent_color = "#3a7ebf"
        self.card_bg = "#1e1e1e"
        
        # Настройка стилей
        style.configure(".", background=self.bg_color, foreground=self.fg_color)
        style.configure("TFrame", background=self.bg_color)
        style.configure("TLabel", background=self.bg_color, foreground=self.fg_color, font=("Arial", 12))
        style.configure("TButton", background=self.accent_color, foreground="#ffffff", 
                       font=("Arial", 10, "bold"), padding=8)
        style.configure("Treeview", background=self.card_bg, fieldbackground=self.card_bg, 
                       foreground=self.fg_color, font=("Arial", 10))
        style.map("Treeview", background=[("selected", self.accent_color)])
        style.configure("Treeview.Heading", background="#2a2a2a", foreground=self.fg_color,
                       font=("Arial", 11, "bold"))
        style.configure("TNotebook", background=self.bg_color)
        style.configure("TNotebook.Tab", background="#2a2a2a", foreground=self.fg_color,
                       padding=[10, 5], font=("Arial", 10, "bold"))
    
    def create_widgets(self):
        # Основной контейнер
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Верхняя панель добавления цели
        add_frame = ttk.Frame(main_frame)
        add_frame.pack(fill=tk.X, pady=(0, 15))
        
        ttk.Label(add_frame, text="Новая цель:").pack(side=tk.LEFT, padx=(0, 10))
        self.goal_entry = ttk.Entry(add_frame, width=30)
        self.goal_entry.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=5)
        
        ttk.Button(add_frame, text="+", width=3, command=self.add_goal).pack(side=tk.LEFT)
        
        # Описание цели
        desc_frame = ttk.Frame(main_frame)
        desc_frame.pack(fill=tk.X, pady=(0, 15))
        
        ttk.Label(desc_frame, text="Описание:").pack(side=tk.LEFT, padx=(0, 10))
        self.desc_entry = scrolledtext.ScrolledText(desc_frame, height=4, wrap=tk.WORD, 
                                                  bg=self.card_bg, fg=self.fg_color,
                                                  insertbackground=self.fg_color)
        self.desc_entry.pack(fill=tk.X, expand=True)
        
        # Таблица целей
        self.tree = ttk.Treeview(main_frame, columns=("Status", "Goal", "Description", "Date"), 
                                show="headings", height=15)
        self.tree.heading("Status", text="✓", anchor="center")
        self.tree.heading("Goal", text="Цель")
        self.tree.heading("Description", text="Описание")
        self.tree.heading("Date", text="Дата")
        self.tree.column("Status", width=40, anchor="center")
        self.tree.column("Goal", width=180)
        self.tree.column("Description", width=250)
        self.tree.column("Date", width=120)
        self.tree.pack(fill=tk.BOTH, expand=True, pady=(0, 15))
        
        # Кнопки управления
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill=tk.X)
        
        ttk.Button(btn_frame, text="Выполнено", command=self.mark_complete).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Редактировать", command=self.edit_goal).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Удалить", command=self.delete_goal).pack(side=tk.LEFT, padx=5)
        
        # Статистика
        stats_frame = ttk.LabelFrame(main_frame, text="Статистика")
        stats_frame.pack(fill=tk.X, pady=10)
        
        self.total_label = ttk.Label(stats_frame, text="Всего целей: 0")
        self.total_label.pack(side=tk.LEFT, padx=10)
        
        self.completed_label = ttk.Label(stats_frame, text="Выполнено: 0")
        self.completed_label.pack(side=tk.LEFT, padx=10)
    
    def add_goal(self):
        goal_text = self.goal_entry.get()
        description = self.desc_entry.get("1.0", tk.END).strip()
        
        if goal_text:
            self.goals.append({
                "text": goal_text,
                "description": description,
                "completed": False,
                "date": datetime.now().strftime("%d.%m.%Y %H:%M")
            })
            self.save_data()
            self.update_goals_list()
            self.goal_entry.delete(0, tk.END)
            self.desc_entry.delete("1.0", tk.END)
        else:
            messagebox.showwarning("Ошибка", "Введите текст цели!")
    
    def mark_complete(self):
        selected = self.tree.selection()
        if selected:
            item = self.tree.item(selected)
            goal_text = item['values'][1]
            
            for goal in self.goals:
                if goal['text'] == goal_text:
                    goal['completed'] = not goal['completed']
                    break
            
            self.save_data()
            self.update_goals_list()
    
    def edit_goal(self):
        selected = self.tree.selection()
        if selected:
            item = self.tree.item(selected)
            goal_text = item['values'][1]
            
            for goal in self.goals:
                if goal['text'] == goal_text:
                    edit_window = tk.Toplevel(self.root)
                    edit_window.title("Редактирование цели")
                    edit_window.geometry("500x400")
                    edit_window.configure(bg=self.bg_color)
                    
                    ttk.Label(edit_window, text="Цель:").pack(pady=(10, 0))
                    goal_entry = ttk.Entry(edit_window, width=50)
                    goal_entry.insert(0, goal['text'])
                    goal_entry.pack(pady=5)
                    
                    ttk.Label(edit_window, text="Описание:").pack(pady=(10, 0))
                    desc_entry = scrolledtext.ScrolledText(edit_window, height=10, wrap=tk.WORD,
                                                          bg=self.card_bg, fg=self.fg_color)
                    desc_entry.insert("1.0", goal['description'])
                    desc_entry.pack(pady=5, padx=10, fill=tk.BOTH)
                    
                    def save_changes():
                        goal['text'] = goal_entry.get()
                        goal['description'] = desc_entry.get("1.0", tk.END).strip()
                        self.save_data()
                        self.update_goals_list()
                        edit_window.destroy()
                    
                    ttk.Button(edit_window, text="Сохранить", command=save_changes).pack(pady=10)
                    break
    
    def delete_goal(self):
        selected = self.tree.selection()
        if selected:
            if messagebox.askyesno("Удаление", "Удалить выбранную цель?"):
                item = self.tree.item(selected)
                goal_text = item['values'][1]
                
                self.goals = [goal for goal in self.goals if goal['text'] != goal_text]
                self.save_data()
                self.update_goals_list()
    
    def update_goals_list(self):
        self.tree.delete(*self.tree.get_children())
        
        completed_count = 0
        for goal in self.goals:
            status = "✓" if goal['completed'] else "✗"
            short_desc = (goal['description'][:50] + '...') if len(goal['description']) > 50 else goal['description']
            self.tree.insert("", tk.END, values=(status, goal['text'], short_desc, goal['date']))
            if goal['completed']:
                completed_count += 1
        
        self.total_label.config(text=f"Всего целей: {len(self.goals)}")
        self.completed_label.config(text=f"Выполнено: {completed_count}")
    
    def load_data(self):
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except:
                return []
        return []
    
    def save_data(self):
        with open(self.data_file, "w", encoding="utf-8") as f:
            json.dump(self.goals, f, ensure_ascii=False, indent=2)
    
    def on_closing(self):
        self.save_data()
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = SoloLevelingGoalsApp(root)
    root.mainloop()