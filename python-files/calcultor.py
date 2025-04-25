import tkinter as tk
from tkinter import ttk
import threading
import keyboard
import mouse
import time
from tkinter import messagebox

class AutoClickerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Супер Автокликер")
        self.root.geometry("400x500")
        self.root.resizable(False, False)
        
        # Стили
        self.style = ttk.Style()
        self.style.configure("Custom.TButton",
                           padding=10,
                           font=('Helvetica', 10, 'bold'))
        
        self.style.configure("Custom.TLabel",
                           font=('Helvetica', 10),
                           padding=5)
        
        # Переменные
        self.clicking = False
        self.selected_button = tk.StringVar(value="left")
        self.cps = tk.DoubleVar(value=1.0)
        self.is_active = False
        
        self.create_widgets()
        self.start_listener()
        
        # Анимация при запуске
        self.root.attributes('-alpha', 0.0)
        self.fade_in()

    def fade_in(self):
        alpha = self.root.attributes('-alpha')
        if alpha < 1.0:
            alpha += 0.1
            self.root.attributes('-alpha', alpha)
            self.root.after(20, self.fade_in)

    def create_widgets(self):
        # Главный фрейм
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Заголовок
        title_label = ttk.Label(main_frame,
                              text="СУПЕР АВТОКЛИКЕР",
                              font=('Helvetica', 16, 'bold'),
                              style="Custom.TLabel")
        title_label.pack(pady=20)

        # Фрейм для настроек
        settings_frame = ttk.LabelFrame(main_frame, text="Настройки", padding="10")
        settings_frame.pack(fill=tk.X, pady=10)

        # Выбор кнопки мыши
        button_label = ttk.Label(settings_frame,
                               text="Выберите кнопку мыши:",
                               style="Custom.TLabel")
        button_label.pack(anchor=tk.W)

        button_frame = ttk.Frame(settings_frame)
        button_frame.pack(fill=tk.X, pady=5)

        ttk.Radiobutton(button_frame,
                       text="Левая кнопка мыши",
                       variable=self.selected_button,
                       value="left").pack(side=tk.LEFT, padx=5)
        
        ttk.Radiobutton(button_frame,
                       text="Правая кнопка мыши",
                       variable=self.selected_button,
                       value="right").pack(side=tk.LEFT, padx=5)

        # Настройка CPS (кликов в секунду)
        cps_label = ttk.Label(settings_frame,
                            text="Кликов в секунду:",
                            style="Custom.TLabel")
        cps_label.pack(anchor=tk.W, pady=(10, 0))

        cps_scale = ttk.Scale(settings_frame,
                            from_=1,
                            to=20,
                            variable=self.cps,
                            orient=tk.HORIZONTAL)
        cps_scale.pack(fill=tk.X, pady=5)

        # Статус
        self.status_label = ttk.Label(main_frame,
                                    text="Статус: Неактивен",
                                    style="Custom.TLabel")
        self.status_label.pack(pady=20)

        # Информация
        info_text = ("Инструкция:\n"
                    "1. Выберите кнопку мыши\n"
                    "2. Установите желаемую скорость\n"
                    "3. Зажмите выбранную кнопку мыши для активации\n"
                    "4. Отпустите кнопку для остановки")
        
        info_label = ttk.Label(main_frame,
                             text=info_text,
                             justify=tk.LEFT,
                             style="Custom.TLabel")
        info_label.pack(pady=20)

    def start_listener(self):
        def listen():
            while True:
                if mouse.is_pressed("left") and self.selected_button.get() == "left":
                    self.activate_clicker()
                elif mouse.is_pressed("right") and self.selected_button.get() == "right":
                    self.activate_clicker()
                elif not mouse.is_pressed("left") and not mouse.is_pressed("right"):
                    self.deactivate_clicker()
                time.sleep(0.1)

        listener_thread = threading.Thread(target=listen, daemon=True)
        listener_thread.start()

    def activate_clicker(self):
        if not self.is_active:
            self.is_active = True
            self.status_label.config(text="Статус: Активен")
            self.start_clicking()

    def deactivate_clicker(self):
        if self.is_active:
            self.is_active = False
            self.status_label.config(text="Статус: Неактивен")
            self.clicking = False

    def start_clicking(self):
        def click_loop():
            self.clicking = True
            while self.clicking and self.is_active:
                button = self.selected_button.get()
                if button == "left":
                    mouse.click(button="left")
                else:
                    mouse.click(button="right")
                time.sleep(1 / self.cps.get())

        click_thread = threading.Thread(target=click_loop, daemon=True)
        click_thread.start()

if __name__ == "__main__":
    root = tk.Tk()
    app = AutoClickerApp(root)
    root.mainloop()