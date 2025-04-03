import tkinter as tk
from tkinter import filedialog, messagebox, ttk, simpledialog
from PIL import Image, ImageTk, ImageOps, ImageFilter
import os
import json
import subprocess
import platform
import time
from datetime import datetime
import hashlib

class GameBoostCenter:
    def __init__(self, root):
        self.root = root
        self.current_theme = "dark"
        self.animation_speed = 15
        self.animation_running = False
        self.games = []
        self.current_game_index = 0
        self.users = {}
        self.current_user = None
        self.game_sessions = {}
        self.settings_window = None
        self.cover_images = []  # Для хранения всех загруженных изображений
        self.data_file = "games.json"
        self.users_file = "users.json"
        
        # Инициализация цветов
        self.bg_color = "#1a1a1a"
        self.fg_color = "white"
        self.btn_bg = "#2d2d2d"
        self.highlight_color = "#4CAF50"
        
        # Переменные для анимации
        self.animation_direction = 0  # 0 - нет анимации, -1 - влево, 1 - вправо
        self.animation_progress = 0
        self.current_cover_pos = 0
        self.next_cover_pos = 0
        self.current_cover_img = None
        self.next_cover_img = None
        
        self.create_widgets()
        self.load_data()
        self.check_authentication()
        self.update_display()

    def create_widgets(self):
        """Создание всех элементов интерфейса"""
        self.root.title("Game Boost Center")
        self.root.geometry("1100x650")
        self.root.configure(bg=self.bg_color)
        icon = PhotoImage(file='logo.png')
        window.iconphoto(True,icon)
        
        # Верхняя панель
        self.top_frame = tk.Frame(self.root, bg=self.bg_color, height=50)
        self.top_frame.pack(fill=tk.X)
        
        self.settings_btn = tk.Button(self.top_frame, text="⚙️", font=("Arial", 16), 
                                    command=self.open_settings, bd=0, bg=self.btn_bg, fg=self.fg_color)
        self.settings_btn.pack(side=tk.RIGHT, padx=10)
        
        self.theme_btn = tk.Button(self.top_frame, text="🌓", font=("Arial", 16), 
                                 command=self.toggle_theme, bd=0, bg=self.btn_bg, fg=self.fg_color)
        self.theme_btn.pack(side=tk.RIGHT, padx=10)
        
        self.login_btn = tk.Button(self.top_frame, text="👤", font=("Arial", 16), 
                                 command=self.login, bd=0, bg=self.btn_bg, fg=self.fg_color)
        self.login_btn.pack(side=tk.RIGHT, padx=10)
        
        # Основной контент
        self.main_frame = tk.Frame(self.root, bg=self.bg_color)
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Левая панель с описанием
        self.desc_frame = tk.Frame(self.main_frame, bg=self.bg_color, width=300)
        self.desc_frame.pack(side=tk.LEFT, fill=tk.Y, padx=20)
        
        self.game_title = tk.Label(self.desc_frame, text="", font=("Arial", 20), 
                                 fg=self.fg_color, bg=self.bg_color, wraplength=250)
        self.game_title.pack(pady=20)
        
        self.game_desc = tk.Label(self.desc_frame, text="", font=("Arial", 12), 
                                fg=self.fg_color, bg=self.bg_color, wraplength=250, justify=tk.LEFT)
        self.game_desc.pack()
        
        self.game_stats = tk.Label(self.desc_frame, text="", font=("Arial", 10), 
                                 fg=self.fg_color, bg=self.bg_color, wraplength=250, justify=tk.LEFT)
        self.game_stats.pack(pady=20)
        
        # Центральная часть с обложкой
        self.center_frame = tk.Frame(self.main_frame, bg=self.bg_color)
        self.center_frame.pack(fill=tk.BOTH, expand=True)
        
        # Canvas для анимации обложек
        self.cover_canvas = tk.Canvas(self.center_frame, bg=self.bg_color, highlightthickness=0, width=1024, height=600)
        self.cover_canvas.pack(expand=True)
        self.cover_canvas.bind("<Button-1>", lambda e: self.play_game())
        
        # Кнопки листания
        self.prev_btn = tk.Button(self.center_frame, text="◀", font=("Arial", 20), 
                                command=self.prev_game, bd=0, bg=self.btn_bg, fg=self.fg_color)
        self.prev_btn.place(relx=0.05, rely=0.5, anchor="center")
        
        self.next_btn = tk.Button(self.center_frame, text="▶", font=("Arial", 20), 
                                command=self.next_game, bd=0, bg=self.btn_bg, fg=self.fg_color)
        self.next_btn.place(relx=0.95, rely=0.5, anchor="center")
        
        # Панель управления
        self.control_frame = tk.Frame(self.main_frame, bg=self.bg_color)
        self.control_frame.pack(fill=tk.X, pady=5)
        
        self.play_btn = tk.Button(self.control_frame, text="ИГРАТЬ", font=("Arial", 16), 
                                command=self.play_game, bg=self.highlight_color, fg="white", bd=0, padx=15, pady=5)
        self.play_btn.pack(side=tk.LEFT, padx=50)
        
        self.delete_btn = tk.Button(self.control_frame, text="УДАЛИТЬ", font=("Arial", 16), 
                                  command=self.delete_game, bg="#F44336", fg="white", bd=0, padx=15, pady=5)
        self.delete_btn.pack(side=tk.RIGHT, padx=50)

    def open_settings(self):
        """Открывает окно настроек"""
        if not self.current_user:
            messagebox.showwarning("Ошибка", "Войдите в систему")
            return
            
        if self.settings_window and self.settings_window.winfo_exists():
            self.settings_window.lift()
            return
            
        self.settings_window = tk.Toplevel(self.root)
        self.settings_window.title("Настройки")
        self.settings_window.geometry("500x600")
        
        # Создаем вкладки
        tab_control = ttk.Notebook(self.settings_window)
        
        # Вкладка добавления игры
        add_tab = ttk.Frame(tab_control)
        self.create_add_game_tab(add_tab)
        tab_control.add(add_tab, text="Добавить игру")
        
        # Вкладка пользователей (для админа)
        if self.users.get(self.current_user, {}).get("role") == "admin":
            user_tab = ttk.Frame(tab_control)
            self.create_user_tab(user_tab)
            tab_control.add(user_tab, text="Пользователи")
        
        tab_control.pack(expand=1, fill="both")
        self.settings_window.protocol("WM_DELETE_WINDOW", self.on_settings_close)

    def create_add_game_tab(self, parent):
        """Создает вкладку для добавления игры"""
        tk.Label(parent, text="Название игры:").pack(pady=(10, 0))
        name_entry = tk.Entry(parent, width=40)
        name_entry.pack()
        
        tk.Label(parent, text="Описание:").pack(pady=(10, 0))
        desc_entry = tk.Text(parent, height=5, width=40)
        desc_entry.pack()
        
        tk.Label(parent, text="Путь к игре:").pack(pady=(10, 0))
        path_entry = tk.Entry(parent, width=40)
        path_entry.pack()
        tk.Button(parent, text="Обзор...", command=lambda: self.browse_file(path_entry)).pack()
        
        tk.Label(parent, text="Обложка:").pack(pady=(10, 0))
        cover_entry = tk.Entry(parent, width=40)
        cover_entry.pack()
        tk.Button(parent, text="Обзор...", command=lambda: self.browse_image(cover_entry)).pack()
        
        tk.Button(parent, text="Добавить игру", command=lambda: self.add_game(
            name_entry.get(),
            desc_entry.get("1.0", tk.END).strip(),
            path_entry.get(),
            cover_entry.get()
        )).pack(pady=20)

    def create_user_tab(self, parent):
        """Создает вкладку управления пользователями"""
        tk.Label(parent, text="Новый пользователь:").pack(pady=(10, 0))
        
        tk.Label(parent, text="Логин:").pack()
        login_entry = tk.Entry(parent)
        login_entry.pack()
        
        tk.Label(parent, text="Пароль:").pack()
        pass_entry = tk.Entry(parent, show="*")
        pass_entry.pack()
        
        tk.Button(parent, text="Добавить", command=lambda: self.add_user(
            login_entry.get(),
            pass_entry.get()
        )).pack(pady=10)
        
        # Список пользователей
        user_list = tk.Listbox(parent)
        for user in self.users:
            if user != "admin":
                user_list.insert(tk.END, user)
        user_list.pack(fill=tk.BOTH, expand=True, pady=10)
        
        tk.Button(parent, text="Удалить", command=lambda: self.remove_user(
            user_list.get(tk.ACTIVE)
        )).pack()

    def load_cover_image(self, path, size=(450, 550)):
        """Загрузка и масштабирование обложки игры"""
        if path and os.path.exists(path):
            try:
                img = Image.open(path)
                img = img.resize(size, Image.LANCZOS)
                
                # Добавляем эффект тени как в PS5
                shadow = Image.new('RGBA', (size[0]+20, size[1]+20), (0, 0, 0, 0))
                shadow.paste(ImageOps.expand(img.convert('RGBA'), border=10, fill=0), (0, 0))
                
                # Применяем размытие для тени
                shadow = shadow.filter(ImageFilter.GaussianBlur(10))
                
                # Накладываем оригинальное изображение поверх тени
                shadow.paste(img, (10, 10), img.convert('RGBA') if img.mode == 'RGBA' else None)
                
                return ImageTk.PhotoImage(shadow)
            except Exception as e:
                print(f"Ошибка загрузки изображения: {e}")
        
        # Возвращаем прозрачное изображение, если обложка не загружена
        img = Image.new('RGBA', size, (0, 0, 0, 0))
        return ImageTk.PhotoImage(img)

    def start_animation(self, direction):
        """Начало анимации перелистывания"""
        if self.animation_running or len(self.games) < 2:
            return
            
        self.animation_direction = direction
        self.animation_progress = 0
        
        # Определяем следующую игру
        next_index = (self.current_game_index + direction) % len(self.games)
        
        # Загружаем текущую и следующую обложки
        self.current_cover_img = self.load_cover_image(
            self.games[self.current_game_index].get("cover"))
        self.next_cover_img = self.load_cover_image(
            self.games[next_index].get("cover"))
        
        # Начальные позиции для анимации
        self.current_cover_pos = 0
        self.next_cover_pos = direction * 1100  # Начальная позиция следующей обложки
        
        self.animation_running = True
        self.animate_covers()

    def animate_covers(self):
        """Анимация перелистывания обложек"""
        if not self.animation_running:
            return
            
        self.animation_progress += self.animation_speed
        
        # Плавное движение с замедлением в конце
        progress = min(self.animation_progress, 100) / 100
        ease_progress = self.ease_out_quad(progress)
        
        # Обновляем позиции
        self.current_cover_pos = -self.animation_direction * 1100 * ease_progress
        self.next_cover_pos = self.animation_direction * 1100 * (1 - ease_progress)
        
        # Отрисовываем обложки
        self.draw_covers()
        
        if self.animation_progress < 100:
            self.root.after(16, self.animate_covers)  # ~60 FPS
        else:
            self.finish_animation()

    def ease_out_quad(self, t):
        """Функция плавности для анимации"""
        return 1 - (1 - t) * (1 - t)

    def draw_covers(self):
        """Отрисовка обложек на canvas"""
        self.cover_canvas.delete("all")
        canvas_width = self.cover_canvas.winfo_width()
        canvas_height = self.cover_canvas.winfo_height()
        
        # Центрируем обложки по вертикали
        y_pos = (canvas_height - 550) // 2
        
        # Текущая обложка
        if self.current_cover_img:
            self.cover_canvas.create_image(
                canvas_width // 2 + self.current_cover_pos,
                y_pos,
                image=self.current_cover_img,
                anchor=tk.NW
            )
        
        # Следующая обложка
        if self.next_cover_img:
            self.cover_canvas.create_image(
                canvas_width // 2 + self.next_cover_pos,
                y_pos,
                image=self.next_cover_img,
                anchor=tk.NW
            )

    def finish_animation(self):
        """Завершение анимации и обновление индекса"""
        self.animation_running = False
        self.current_game_index = (self.current_game_index + self.animation_direction) % len(self.games)
        self.animation_direction = 0
        self.update_display()

    def prev_game(self):
        """Переключение на предыдущую игру с анимацией"""
        if len(self.games) > 1:
            self.start_animation(-1)

    def next_game(self):
        """Переключение на следующую игру с анимацией"""
        if len(self.games) > 1:
            self.start_animation(1)

    def update_display(self):
        """Обновление отображения текущей игры"""
        if not self.games:
            self.game_title.config(text="Нет игр")
            self.game_desc.config(text="Добавьте игры через настройки")
            self.game_stats.config(text="")
            self.cover_canvas.delete("all")
            return
        
        game = self.games[self.current_game_index]
        self.game_title.config(text=game["name"])
        self.game_desc.config(text=game["description"])
        
        # Статистика игры
        stats_text = ""
        if "last_played" in game:
            stats_text += f"Последний запуск: {game['last_played']}\n"
        if game["name"] in self.game_sessions:
            total_time = sum(s['duration'] for s in self.game_sessions[game['name']])
            stats_text += f"Всего времени: {total_time//60} мин {total_time%60} сек\n"
        if self.current_user:
            stats_text += f"Пользователь: {self.current_user}"
        
        self.game_stats.config(text=stats_text)
        
        # Загрузка и отображение текущей обложки
        self.current_cover_img = self.load_cover_image(game.get("cover"))
        self.draw_covers()

    def toggle_theme(self):
        """Переключение между светлой и темной темой"""
        if self.current_theme == "dark":
            self.current_theme = "light"
            self.bg_color = "#f0f0f0"
            self.fg_color = "black"
            self.btn_bg = "#e0e0e0"
        else:
            self.current_theme = "dark"
            self.bg_color = "#1a1a1a"
            self.fg_color = "white"
            self.btn_bg = "#2d2d2d"
        
        self.update_theme_colors()

    def update_theme_colors(self):
        """Обновление цветов всех элементов интерфейса"""
        self.root.configure(bg=self.bg_color)
        self.top_frame.configure(bg=self.bg_color)
        self.main_frame.configure(bg=self.bg_color)
        self.desc_frame.configure(bg=self.bg_color)
        self.center_frame.configure(bg=self.bg_color)
        self.control_frame.configure(bg=self.bg_color)
        self.cover_canvas.configure(bg=self.bg_color)
        
        self.game_title.configure(bg=self.bg_color, fg=self.fg_color)
        self.game_desc.configure(bg=self.bg_color, fg=self.fg_color)
        self.game_stats.configure(bg=self.bg_color, fg=self.fg_color)
        
        for btn in [self.settings_btn, self.theme_btn, self.login_btn, 
                   self.prev_btn, self.next_btn]:
            btn.configure(bg=self.btn_bg, fg=self.fg_color)
        
        # Кнопка "Играть" всегда зеленая
        self.play_btn.configure(bg="#4CAF50")
        self.delete_btn.configure(bg="#F44336")

    def load_data(self):
        """Загрузка сохраненных данных"""
        try:
            if os.path.exists(self.data_file):
                with open(self.data_file, "r", encoding='utf-8') as f:
                    self.games = json.load(f)
            
            if os.path.exists(self.users_file):
                with open(self.users_file, "r", encoding='utf-8') as f:
                    self.users = json.load(f)
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить данные:\n{str(e)}")

    def save_data(self):
        """Сохранение данных в файлы"""
        try:
            with open(self.data_file, "w", encoding='utf-8') as f:
                json.dump(self.games, f, ensure_ascii=False, indent=4)
            
            with open(self.users_file, "w", encoding='utf-8') as f:
                json.dump(self.users, f, ensure_ascii=False, indent=4)
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить данные:\n{str(e)}")

    def play_game(self):
        """Запуск выбранной игры"""
        if not self.games or not self.current_user:
            messagebox.showwarning("Ошибка", "Войдите в систему для запуска игр")
            return
            
        game = self.games[self.current_game_index]
        game_path = os.path.abspath(os.path.expanduser(game["path"]))
        start_time = time.time()
        
        try:
            if not os.path.exists(game_path):
                messagebox.showerror("Ошибка", f"Файл игры не найден:\n{game_path}")
                return
            
            game_dir = os.path.dirname(game_path)
            
            if platform.system() == "Windows":
                try:
                    os.startfile(game_path)
                except:
                    subprocess.Popen([game_path], cwd=game_dir, shell=True)
            elif platform.system() == "Darwin":
                subprocess.Popen(["open", game_path], cwd=game_dir)
            else:
                subprocess.Popen([game_path], cwd=game_dir)
            
            # Сохраняем статистику
            game["last_played"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            if game["name"] not in self.game_sessions:
                self.game_sessions[game["name"]] = []
            self.game_sessions[game["name"]].append({
                "user": self.current_user,
                "date": game["last_played"],
                "duration": int(time.time() - start_time)
            })
            self.save_data()
            self.update_display()
            
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось запустить игру:\n{str(e)}")

    def delete_game(self):
        """Удаление текущей игры"""
        if not self.games or not self.current_user:
            messagebox.showwarning("Ошибка", "Войдите в систему")
            return
            
        if messagebox.askyesno("Подтверждение", "Удалить эту игру из коллекции?"):
            del self.games[self.current_game_index]
            self.current_game_index = max(0, min(self.current_game_index, len(self.games) - 1))
            self.save_data()
            self.update_display()

    def check_authentication(self):
        """Проверка аутентификации пользователя"""
        if not os.path.exists(self.users_file):
            self.register_admin()
        elif not self.current_user:
            self.login()

    def register_admin(self):
        """Регистрация администратора"""
        password = simpledialog.askstring("Регистрация", "Создайте пароль администратора:", show='*')
        if password:
            self.users["admin"] = {
                "password": hashlib.sha256(password.encode()).hexdigest(),
                "role": "admin"
            }
            self.save_data()
            self.current_user = "admin"
            messagebox.showinfo("Успех", "Администратор зарегистрирован")

    def login(self):
        """Вход пользователя"""
        login = simpledialog.askstring("Вход", "Введите Игрок")
        if login in self.users:
            password = simpledialog.askstring("Вход", "Введите 123", show='*')
            if password and hashlib.sha256(password.encode()).hexdigest() == self.users[login]["password"]:
                self.current_user = login
                messagebox.showinfo("Успех", f"Добро пожаловать, {login}!")
                return
        
        messagebox.showerror("Ошибка", "Неверный логин или пароль")

    def browse_file(self, entry):
        """Открытие диалога выбора файла"""
        filepath = filedialog.askopenfilename(
            title="Выберите файл игры",
            filetypes=[("Исполняемые файлы", "*.exe *.bat *.lnk"), ("Все файлы", "*.*")]
        )
        if filepath:
            entry.delete(0, tk.END)
            entry.insert(0, os.path.normpath(filepath))

    def browse_image(self, entry):
        """Открытие диалога выбора изображения"""
        filepath = filedialog.askopenfilename(
            title="Выберите обложку",
            filetypes=[("Изображения", "*.png *.jpg *.jpeg"), ("Все файлы", "*.*")]
        )
        if filepath:
            entry.delete(0, tk.END)
            entry.insert(0, os.path.normpath(filepath))

    def add_game(self, name, description, path, cover):
        """Добавление новой игры"""
        if not name or not path:
            messagebox.showerror("Ошибка", "Название и путь обязательны")
            return
            
        if not os.path.exists(path):
            messagebox.showerror("Ошибка", "Указанный файл не найден")
            return
            
        self.games.append({
            "name": name,
            "description": description,
            "path": os.path.normpath(path),
            "cover": os.path.normpath(cover) if cover and os.path.exists(cover) else ""
        })
        self.save_data()
        self.update_display()
        messagebox.showinfo("Успех", "Игра добавлена")

    def add_user(self, login, password):
        """Добавление нового пользователя"""
        if not login or not password:
            messagebox.showerror("Ошибка", "Введите логин и пароль")
            return
            
        if login in self.users:
            messagebox.showerror("Ошибка", "Пользователь уже существует")
            return
            
        self.users[login] = {
            "password": hashlib.sha256(password.encode()).hexdigest(),
            "role": "user"
        }
        self.save_data()
        messagebox.showinfo("Успех", "Пользователь добавлен")

    def remove_user(self, login):
        """Удаление пользователя"""
        if login in self.users and login != "admin":
            del self.users[login]
            self.save_data()
            messagebox.showinfo("Успех", "Пользователь удален")

    def on_settings_close(self):
        """Закрытие окна настроек"""
        if self.settings_window:
            self.settings_window.destroy()
            self.settings_window = None

if __name__ == "__main__":
    root = tk.Tk()
    app = GameBoostCenter(root)
    root.mainloop()