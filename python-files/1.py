import tkinter as tk
from tkinter import messagebox, font
import time
import keyboard
import threading
import webbrowser
import pyperclip
import os
import math
import colorsys
import sys

# Настройки
DELAY_AFTER_FIRST_ENTER = 0.05
DELAY_BETWEEN_DOWN = 0.04
DELAY_BETWEEN_ENTERS = 0.001
current_contract = 3
is_active = True
current_theme = "dark"

# Цветовые темы
THEMES = {
    "dark": {"bg": "#1A1A1A", "button": "#353535", "active": "#454545", "text": "white", "highlight": "#5A3A5A"},
    "gray": {"bg": "#2A2A2A", "button": "#4A4A4A", "active": "#5A5A5A", "text": "white", "highlight": "#6A4A6A"},
    "dark_blue": {"bg": "#0A1A2A", "button": "#1A2A4A", "active": "#2A3A5A", "text": "white", "highlight": "#1A3A6A"},
    "dark_red": {"bg": "#2A0A0A", "button": "#4A1A1A", "active": "#5A2A2A", "text": "white", "highlight": "#6A1A1A"},
    "rgb": {"bg": "#1A1A1A", "button": "#353535", "active": "#454545", "text": "white", "highlight": "#5A3A5A"}
}

class ContractCatchApp:
    def __init__(self, root):
        self.root = root
        self.rgb_cycle = False
        self.hue = 0  # Начальное значение цвета (0-1)
        self.setup_icon()
        self.setup_ui()
        self.setup_hotkey()
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

    def setup_icon(self):
        try:
            if os.path.exists("123.ico"):
                self.root.iconbitmap("123.ico")
        except Exception as e:
            print(f"Ошибка загрузки иконки: {e}")

    def setup_ui(self):
        self.root.title("NeeLo3 Controller")
        self.root.geometry("340x650")
        self.root.configure(bg=THEMES[current_theme]["bg"])
        
        # Шрифты
        self.font_title = font.Font(family="Segoe UI", size=14)
        self.font_subtitle = font.Font(family="Segoe UI", size=10)
        self.font_button = font.Font(family="Segoe UI", size=11, weight="bold")
        
        # Заголовок
        self.title_label = tk.Label(self.root, text="🎯 Ловля Контрактов", 
                                  font=self.font_title, fg="white", bg=THEMES[current_theme]["bg"])
        self.title_label.pack(pady=(15,0))
        
        self.subtitle_label = tk.Label(self.root, text="NeeLo3 Scripts | v2.4", 
                                     font=self.font_subtitle, fg="#BBBBBB", bg=THEMES[current_theme]["bg"])
        self.subtitle_label.pack()
        
        # Разделитель
        self.separator = tk.Frame(self.root, height=2, bg="#2A2A2A")
        self.separator.pack(fill="x", pady=15, padx=20)
        
        # Основные кнопки
        buttons = [
            ("🌐 Открыть FunPay", self.open_funpay),
            ("📋 Инструкция", self.show_instructions),
            ("🔄 Вкл/Выкл скрипт", self.toggle_script)
        ]
        
        for text, cmd in buttons:
            btn = tk.Button(self.root, text=text, font=self.font_button, 
                          fg="white", bg=THEMES[current_theme]["button"], 
                          activebackground=THEMES[current_theme]["active"], 
                          relief="flat", command=cmd)
            btn.pack(fill="x", padx=20, pady=5, ipady=8)
        
        # Блок контрактов
        tk.Label(self.root, text="Выбор контракта:", 
                font=("Segoe UI", 12), fg="white", bg=THEMES[current_theme]["bg"]).pack(pady=(15,10))
        
        self.contract_buttons = []
        frame = tk.Frame(self.root, bg=THEMES[current_theme]["bg"])
        frame.pack()
        
        for i in range(1,7):
            btn = tk.Button(frame, text=str(i), width=3, height=1,
                          font=("Segoe UI", 10), fg="white",
                          command=lambda i=i: self.select_contract(i))
            btn.pack(side="left", padx=3)
            self.contract_buttons.append(btn)
        
        # Выбор темы
        theme_frame = tk.Frame(self.root, bg=THEMES[current_theme]["bg"])
        theme_frame.pack(pady=(15, 0))
        
        tk.Label(theme_frame, text="Тема:", font=self.font_subtitle, 
                fg="white", bg=THEMES[current_theme]["bg"]).pack(side="left")
        
        themes = [
            ("dark", "⬛"), 
            ("gray", "⬜"), 
            ("dark_blue", "🟦"), 
            ("dark_red", "🟥"), 
            ("rgb", "RGB")
        ]
        
        for theme, symbol in themes:
            btn = tk.Button(theme_frame, text=symbol, width=3, height=1,
                          font=("Segoe UI", 8), relief="flat",
                          command=lambda t=theme: self.change_theme(t))
            btn.pack(side="left", padx=2)
            btn.config(bg=THEMES[theme]["button"], fg=THEMES[theme]["text"])
        
        # Контакты
        tk.Label(self.root, text="📩 Связь с автором:", 
                font=("Segoe UI", 10), fg="#AAAAAA", bg=THEMES[current_theme]["bg"]).pack(pady=(15,5))
        
        links = [
            ("Telegram: @WhyOverZBC", "https://t.me/WhyOverZBC"),
            ("Discord: .asd0", "copy_discord"),
            ("Телеграм канал: t.me/NeeLoScriptsPrivate", "https://t.me/NeeLoScriptsPrivate")
        ]
        
        for text, url in links:
            lbl = tk.Label(self.root, text=text, font=("Segoe UI", 9), 
                         fg="#4FC3F7", bg=THEMES[current_theme]["bg"], cursor="hand2")
            lbl.pack(pady=1)
            lbl.bind("<Button-1>", lambda e, u=url: self.open_link(u))
        
        # Статус
        self.status_var = tk.StringVar(value="✅ Готов к работе (B)")
        self.status_label = tk.Label(self.root, textvariable=self.status_var, 
                                   font=("Segoe UI", 10), fg="#00FF00", bg=THEMES[current_theme]["bg"])
        self.status_label.pack(pady=(15,5))
        
        self.contract_var = tk.StringVar(value=f"Текущий контракт: {current_contract}")
        tk.Label(self.root, textvariable=self.contract_var,
                font=("Segoe UI", 8), fg="#AAAAAA", bg=THEMES[current_theme]["bg"]).pack()
        
        self.update_contract_buttons()

    def update_contract_buttons(self):
        for i, btn in enumerate(self.contract_buttons, 1):
            btn.config(bg=THEMES[current_theme]["highlight"] if i == current_contract else THEMES[current_theme]["button"])

    def setup_hotkey(self):
        try:
            keyboard.unhook_all()
            keyboard.add_hotkey('b', self.catch_contract)
        except Exception as e:
            self.status_var.set("❌ Ошибка клавиатуры")
            print(f"Keyboard error: {e}")

    def select_contract(self, num):
        global current_contract
        current_contract = num
        self.contract_var.set(f"Текущий контракт: {current_contract}")
        self.status_var.set(f"✅ Контракт {current_contract} выбран")
        self.update_contract_buttons()
        self.root.after(1000, lambda: self.status_var.set("✅ Готов к работе (B)"))

    def change_theme(self, theme):
        global current_theme
        current_theme = theme
        
        if theme == "rgb":
            self.start_rgb_cycle()
        else:
            self.stop_rgb_cycle()
            self.apply_theme()
    
    def apply_theme(self):
        theme = THEMES[current_theme]
        self.root.configure(bg=theme["bg"])
        
        widgets = [
            self.title_label, self.subtitle_label, 
            self.status_label, self.separator, *self.contract_buttons
        ]
        
        for widget in widgets:
            try:
                widget.config(bg=theme["bg"])
                if isinstance(widget, tk.Label):
                    widget.config(fg=theme["text"])
            except:
                pass
        
        self.update_contract_buttons()

    def start_rgb_cycle(self):
        if self.rgb_cycle:
            return
            
        self.rgb_cycle = True
        self.hue = 0
        self.cycle_colors()

    def stop_rgb_cycle(self):
        self.rgb_cycle = False
        if hasattr(self, 'rgb_job'):
            self.root.after_cancel(self.rgb_job)

    def cycle_colors(self):
        if not self.rgb_cycle:
            return
        
        # Плавное изменение цвета через HSV (меняем только Hue)
        r, g, b = colorsys.hsv_to_rgb(self.hue, 0.7, 0.3)
        color = "#{:02x}{:02x}{:02x}".format(int(r*255), int(g*255), int(b*255))
        
        try:
            self.root.configure(bg=color)
            
            # Обновляем только фон основных элементов (для читаемости текста)
            widgets = [
                self.title_label, self.subtitle_label, 
                self.status_label, self.separator
            ]
            
            for widget in widgets:
                try:
                    widget.config(bg=color)
                except:
                    pass
        except:
            self.stop_rgb_cycle()
            return
        
        # Увеличиваем Hue для плавного перехода
        self.hue = (self.hue + 0.005) % 1.0
        
        # Планируем следующее обновление через 50ms для плавности
        self.rgb_job = self.root.after(50, self.cycle_colors)

    def catch_contract(self):
        if not is_active:
            return
            
        self.status_var.set(f"⚡ Ловим контракт {current_contract}...")
        
        def _execute():
            try:
                keyboard.press_and_release('enter')
                time.sleep(DELAY_AFTER_FIRST_ENTER)
                
                for _ in range(current_contract):
                    keyboard.press_and_release('down')
                    time.sleep(DELAY_BETWEEN_DOWN)
                
                for _ in range(30):
                    keyboard.press_and_release('enter')
                    time.sleep(DELAY_BETWEEN_ENTERS)
                
                self.status_var.set(f"✅ Контракт {current_contract} пойман!")
            except Exception as e:
                self.status_var.set(f"❌ Ошибка: {str(e)}")
            
            self.root.after(1000, lambda: self.status_var.set("✅ Готов к работе (B)"))
        
        threading.Thread(target=_execute, daemon=True).start()

    def open_link(self, url):
        if url == "copy_discord":
            pyperclip.copy(".asd0")
            self.status_var.set("Discord скопирован")
            self.root.after(2000, lambda: self.status_var.set("✅ Готов к работе (B)"))
        else:
            webbrowser.open(url)

    def open_funpay(self):
        webbrowser.open("https://funpay.com/users/10529763/")

    def show_instructions(self):
        text = """🎮 Как использовать:
1. Выберите номер контракта (1-6)
2. Откройте окно игры
3. Наведите курсор в игре
4. Нажмите B:
   - Enter (мгновенно)
   - Пауза 50ms
   - N× Вниз (по 40ms)
   - 30× Enter (по 1ms)"""
        messagebox.showinfo("Инструкция", text)

    def toggle_script(self):
        global is_active
        is_active = not is_active
        status = "✅ Скрипт активен (B)" if is_active else "❌ Скрипт отключен"
        self.status_var.set(status)

    def on_close(self):
        try:
            keyboard.unhook_all()
        except:
            pass
        self.root.destroy()

if __name__ == "__main__":
    try:
        root = tk.Tk()
        app = ContractCatchApp(root)
        root.mainloop()
    except Exception as e:
        messagebox.showerror("Ошибка", f"Не удалось запустить приложение:\n{str(e)}")
        sys.exit(1)
