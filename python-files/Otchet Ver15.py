import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime
import os
import random
from itertools import cycle

def load_list_from_file(filename, default_items):
    try:
        if not os.path.exists(filename):
            with open(filename, "w", encoding="utf-8") as f:
                f.write("\n".join(default_items))
            return default_items
        with open(filename, "r", encoding="utf-8") as file:
            return [line.strip() for line in file if line.strip()]
    except Exception as e:
        messagebox.showerror("Ошибка", f"Не удалось загрузить {filename}:\n{e}")
        return default_items

class ReportApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Формирование отчета")
        self.root.geometry("1400x800")  # Увеличил высоту для комментариев
        
        self.devices = load_list_from_file("device.txt", ["Принтер HP LaserJet Pro M404n", "Сканер Epson Perfection V39", "Ноутбук Dell XPS 15"])
        self.actions = load_list_from_file("work.txt", [
            "Почистили от пыли", "Заменили термопасту", 
            "Заменили картридж", "Выполнили калибровку", 
            "Обновили ПО", "Обновили драйверы",
            "Проверили на вирусы", "Заменили батарею"
        ])
        self.report_entries = []
        self.comments = {}  # Словарь для хранения комментариев
        self.current_file = None
        self.action_combos = []
        
        self.colors = cycle([
            '#FF0000', '#FF7F00', '#FFFF00', '#00FF00',
            '#0000FF', '#4B0082', '#9400D3', '#FF1493',
            '#00FFFF', '#7CFC00', '#FFD700', '#FF4500'
        ])
        
        self.create_widgets()
        self.animate_title()
    
    def animate_title(self):
        next_color = next(self.colors)
        self.title_label.config(fg=next_color)
        self.root.after(500, self.animate_title)
    
    def terminate_all(self):
        """Очистка всех выпадающих списков"""
        for combo in self.action_combos:
            combo.set('')
        self.device_combo.set('')
        self.quantity_entry.delete(0, tk.END)
        self.comment_entry.delete(0, tk.END)
    
    def add_entry(self):
        device = self.device_combo.get()
        quantity = self.quantity_entry.get()
        comment = self.comment_entry.get().strip()
        
        if not device:
            messagebox.showerror("Ошибка", "Выберите устройство!")
            return
        
        if not quantity.isdigit():
            messagebox.showerror("Ошибка", "Введите число в поле 'Количество'!")
            return
        
        selected_actions = []
        for combo in self.action_combos:
            action = combo.get()
            if action and action not in selected_actions:
                selected_actions.append(action)
        
        if not selected_actions:
            messagebox.showerror("Ошибка", "Выберите хотя бы одно действие!")
            return
        
        actions_str = ", ".join(selected_actions)
        entry = f"{device} | {actions_str} | {quantity}.шт"
        
        if comment:
            entry += f" [{comment}]"
            self.comments[len(self.report_entries)] = comment
        
        self.report_entries.append(entry)
        self.report_list.insert(tk.END, entry)
        self.quantity_entry.delete(0, tk.END)
        self.comment_entry.delete(0, tk.END)
    
    def on_entry_select(self, event):
        """Обработчик выбора записи в списке"""
        selection = self.report_list.curselection()
        if selection:
            index = selection[0]
            if index in self.comments:
                self.comment_entry.delete(0, tk.END)
                self.comment_entry.insert(0, self.comments[index])
            else:
                self.comment_entry.delete(0, tk.END)
    
    def clear_comment(self):
        """Очистка поля комментария"""
        self.comment_entry.delete(0, tk.END)
    
    def create_widgets(self):
        # Главный контейнер
        main_container = tk.Frame(self.root)
        main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Анимированный заголовок
        self.title_label = tk.Label(
            main_container,
            text="Ультимативная и могучая утилита отчетности работы, имени Ананьева Вадима Александровича!!!",
            font=('Arial', 16, 'bold'),
            fg='red',
            pady=10
        )
        self.title_label.pack(fill=tk.X)
        
        # Контейнер для основного содержимого
        content_paned = tk.PanedWindow(main_container, orient=tk.HORIZONTAL)
        content_paned.pack(fill=tk.BOTH, expand=True)
        
        # ===== ЛЕВАЯ КОЛОНКА (компактная форма) =====
        left_frame = tk.Frame(content_paned)
        content_paned.add(left_frame, width=700)
        
        # Секция выбора устройства с кнопкой ТЕРМИНИРОВАТЬ
        device_frame = tk.Frame(left_frame)
        device_frame.pack(fill=tk.X, pady=3)
        
        tk.Label(device_frame, text="1. Устройство:", font=('Arial', 9, 'bold')).pack(side=tk.LEFT)
        
        self.device_combo = ttk.Combobox(
            device_frame, 
            values=self.devices, 
            state="readonly", 
            width=40,
            font=('Arial', 9)
        )
        self.device_combo.pack(side=tk.LEFT, padx=5)
        
        # Кнопка ТЕРМИНИРОВАТЬ (с фиксированной шириной)
        tk.Button(
            device_frame, 
            text="ТЕРМИНИРОВАТЬ!", 
            command=self.terminate_all,
            font=('Arial', 9, 'bold'),
            bg='#ff0000',
            fg='white',
            height=1,
            width=15  # Фиксированная ширина
        ).pack(side=tk.LEFT)
        
        # Секция выбора действий (компактная)
        actions_frame = tk.LabelFrame(left_frame, text="2. Действия (до 8)", font=('Arial', 9, 'bold'), padx=5, pady=5)
        actions_frame.pack(fill=tk.X, pady=5)
        
        for i in range(8):
            action_frame = tk.Frame(actions_frame)
            action_frame.pack(fill=tk.X, pady=1)
            
            tk.Label(action_frame, text=f"{i+1}:", width=3, anchor='w', font=('Arial', 9)).pack(side=tk.LEFT)
            
            combo = ttk.Combobox(
                action_frame, 
                values=self.actions, 
                state="readonly", 
                width=35,
                font=('Arial', 9)
            )
            combo.pack(side=tk.LEFT, padx=2, fill=tk.X, expand=True)
            self.action_combos.append(combo)
            
            tk.Button(
                action_frame, 
                text="×", 
                command=lambda c=combo: c.set(''),
                width=2,
                font=('Arial', 9),
                fg='red'
            ).pack(side=tk.LEFT, padx=2)
        
        # Секция количества (компактная)
        quantity_frame = tk.LabelFrame(left_frame, text="3. Количество", font=('Arial', 9, 'bold'), padx=5, pady=5)
        quantity_frame.pack(fill=tk.X, pady=3)
        
        self.quantity_entry = tk.Entry(quantity_frame, width=8, font=('Arial', 10))
        self.quantity_entry.pack(pady=2)
        
        # Кнопка добавления (с фиксированной шириной)
        tk.Button(
            left_frame, 
            text="Добавить запись", 
            command=self.add_entry,
            width=18,  # Фиксированная ширина
            height=1,
            font=('Arial', 9, 'bold'),
            bg='#4CAF50',
            fg='white'
        ).pack(pady=8)
        
        # Секция управления (компактная)
        manage_frame = tk.LabelFrame(left_frame, text="Управление", font=('Arial', 9, 'bold'), padx=5, pady=5)
        manage_frame.pack(fill=tk.X, pady=5)
        
        # Первая строка кнопок (с фиксированной шириной)
        btn_frame1 = tk.Frame(manage_frame)
        btn_frame1.pack(fill=tk.X, pady=2)
        
        buttons1 = [
            ("Открыть", self.open_report, '#2196F3', 12),
            ("Новый", self.new_report, '#FF9800', 12),
            ("Сохранить", self.save_report, '#4CAF50', 12)
        ]
        
        for text, command, color, width in buttons1:
            tk.Button(
                btn_frame1, 
                text=text, 
                command=command,
                width=width,
                height=1,
                font=('Arial', 9),
                bg=color,
                fg='white'
            ).pack(side=tk.LEFT, padx=2)
        
        # Вторая строка кнопок (с фиксированной шириной)
        btn_frame2 = tk.Frame(manage_frame)
        btn_frame2.pack(fill=tk.X, pady=2)
        
        buttons2 = [
            ("Удалить послед.", self.delete_last_entry, '#f44336', 12),
            ("Удалить выбр.", self.delete_selected, '#f44336', 12),
            ("Вверх", self.move_up, '#9C27B0', 8),
            ("Вниз", self.move_down, '#9C27B0', 8),
            ("Очистить", self.clear_entries, '#607D8B', 10)
        ]
        
        for text, command, color, width in buttons2:
            tk.Button(
                btn_frame2, 
                text=text, 
                command=command,
                width=width,
                height=1,
                font=('Arial', 9),
                bg=color,
                fg='white'
            ).pack(side=tk.LEFT, padx=2)
        
        # ===== ПРАВАЯ КОЛОНКА (список записей + комментарии) =====
        right_frame = tk.Frame(content_paned)
        content_paned.add(right_frame, minsize=500)
        
        # Список записей
        list_frame = tk.LabelFrame(right_frame, text="Текущие записи", font=('Arial', 10, 'bold'), padx=10, pady=10)
        list_frame.pack(fill=tk.BOTH, expand=True)
        
        list_scrollbar = tk.Scrollbar(list_frame)
        list_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.report_list = tk.Listbox(
            list_frame, 
            width=80, 
            height=25,  # Уменьшил высоту для комментариев
            yscrollcommand=list_scrollbar.set,
            font=('Arial', 10),
            selectbackground="#a6a6a6",
            selectmode=tk.SINGLE
        )
        self.report_list.pack(fill=tk.BOTH, expand=True)
        self.report_list.bind('<<ListboxSelect>>', self.on_entry_select)
        
        list_scrollbar.config(command=self.report_list.yview)
        
        # Секция комментариев
        comment_frame = tk.LabelFrame(right_frame, text="Комментарий к записи", font=('Arial', 10, 'bold'), padx=10, pady=10)
        comment_frame.pack(fill=tk.X, pady=5)
        
        comment_control_frame = tk.Frame(comment_frame)
        comment_control_frame.pack(fill=tk.X)
        
        self.comment_entry = tk.Entry(
            comment_control_frame,
            font=('Arial', 10),
            width=50
        )
        self.comment_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        tk.Button(
            comment_control_frame,
            text="X",
            command=self.clear_comment,
            font=('Arial', 10, 'bold'),
            fg='red',
            width=3
        ).pack(side=tk.LEFT)

    # Остальные методы без изменений
    def move_up(self):
        selection = self.report_list.curselection()
        if not selection:
            messagebox.showwarning("Предупреждение", "Выберите строку для перемещения!")
            return
        
        index = selection[0]
        if index == 0:
            return
        
        # Обновляем индексы комментариев при перемещении
        comment = self.comments.pop(index, None)
        if comment is not None:
            self.comments[index-1] = comment
        
        self.report_entries[index], self.report_entries[index-1] = self.report_entries[index-1], self.report_entries[index]
        self.refresh_list()
        self.report_list.select_set(index-1)
    
    def move_down(self):
        selection = self.report_list.curselection()
        if not selection:
            messagebox.showwarning("Предупреждение", "Выберите строку для перемещения!")
            return
        
        index = selection[0]
        if index == len(self.report_entries)-1:
            return
        
        # Обновляем индексы комментариев при перемещении
        comment = self.comments.pop(index, None)
        if comment is not None:
            self.comments[index+1] = comment
        
        self.report_entries[index], self.report_entries[index+1] = self.report_entries[index+1], self.report_entries[index]
        self.refresh_list()
        self.report_list.select_set(index+1)
    
    def refresh_list(self):
        self.report_list.delete(0, tk.END)
        for entry in self.report_entries:
            self.report_list.insert(tk.END, entry)
    
    def delete_selected(self):
        selection = self.report_list.curselection()
        if selection:
            index = selection[0]
            # Удаляем комментарий для удаляемой записи
            if index in self.comments:
                del self.comments[index]
            # Обновляем индексы оставшихся комментариев
            new_comments = {}
            for i, comment in self.comments.items():
                if i > index:
                    new_comments[i-1] = comment
                elif i < index:
                    new_comments[i] = comment
            self.comments = new_comments
            
            self.report_list.delete(index)
            self.report_entries.pop(index)
        else:
            messagebox.showwarning("Предупреждение", "Выберите строку для удаления!")
    
    def open_report(self):
        filename = filedialog.askopenfilename(
            title="Выберите файл отчета",
            filetypes=(("Текстовые файлы", "*.txt"), ("Все файлы", "*.*"))
        )
        if not filename:
            return
        
        try:
            with open(filename, "r", encoding="utf-8") as file:
                self.report_entries = []
                self.comments = {}
                for line in file:
                    line = line.strip()
                    if line:
                        # Извлекаем комментарий из квадратных скобок
                        if '[' in line and ']' in line:
                            parts = line.split('[')
                            main_part = parts[0].strip()
                            comment = parts[1].replace(']', '').strip()
                            self.report_entries.append(main_part)
                            self.comments[len(self.report_entries)-1] = comment
                        else:
                            self.report_entries.append(line)
            
            self.refresh_list()
            self.current_file = filename
            messagebox.showinfo("Успех", f"Отчет {os.path.basename(filename)} успешно загружен")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить файл:\n{e}")
    
    def new_report(self):
        if self.report_entries:
            if not messagebox.askyesno("Подтверждение", "Создать новый отчет? Текущие данные будут потеряны."):
                return
        
        self.report_entries = []
        self.comments = {}
        self.refresh_list()
        self.current_file = None
        self.device_combo.set('')
        self.quantity_entry.delete(0, tk.END)
        self.comment_entry.delete(0, tk.END)
        for combo in self.action_combos:
            combo.set('')
    
    def delete_last_entry(self):
        if self.report_entries:
            # Удаляем комментарий для последней записи
            if len(self.report_entries)-1 in self.comments:
                del self.comments[len(self.report_entries)-1]
            self.report_entries.pop()
            self.report_list.delete(tk.END)
        else:
            messagebox.showwarning("Предупреждение", "Список уже пуст!")
    
    def clear_entries(self):
        if self.report_entries:
            if messagebox.askyesno("Подтверждение", "Очистить весь список?"):
                self.report_entries.clear()
                self.comments.clear()
                self.refresh_list()
        else:
            messagebox.showwarning("Предупреждение", "Список уже пуст!")
    
    def save_report(self):
        if not self.report_entries:
            messagebox.showerror("Ошибка", "Нет данных для сохранения!")
            return
        
        if self.current_file:
            filename = self.current_file
        else:
            filename = filedialog.asksaveasfilename(
                defaultextension=".txt",
                filetypes=(("Текстовые файлы", "*.txt"), ("Все файлы", "*.*")),
                initialfile=datetime.now().strftime("%d %B %Y.txt")
            )
            if not filename:
                return
            self.current_file = filename
        
        try:
            with open(filename, "w", encoding="utf-8") as file:
                for i, entry in enumerate(self.report_entries):
                    if i in self.comments:
                        file.write(f"{entry} [{self.comments[i]}]\n")
                    else:
                        file.write(f"{entry}\n")
            messagebox.showinfo("Успех", f"Отчёт сохранён в файл:\n{filename}")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка при сохранении:\n{e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = ReportApp(root)
    root.mainloop()