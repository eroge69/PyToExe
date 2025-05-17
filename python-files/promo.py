import tkinter as tk
from tkinter import ttk, messagebox
import pyperclip  # Для работы с буфером обмена
import sys

# Конфигурация
APP_TITLE = "Проверка промокода"
WINDOW_SIZE = "500x300"
BG_COLOR = "#f5f5f5"
FONT = ("Arial", 12)
CORRECT_PROMO = "MST44KzNPgiGDp53S3LrnMJAcZd42YfasFRXej"


class PromoCodeApp:
    def __init__(self, root):
        self.root = root
        self.setup_ui()

    def setup_ui(self):
        # Настройка главного окна
        self.root.title(APP_TITLE)
        self.root.geometry(WINDOW_SIZE)
        self.root.resizable(False, False)
        self.root.configure(bg=BG_COLOR)

        # Стиль для виджетов
        style = ttk.Style()
        style.configure("TFrame", background=BG_COLOR)
        style.configure("TLabel", background=BG_COLOR, font=FONT)
        style.configure("TButton", font=FONT)

        # Основной контейнер
        main_frame = ttk.Frame(self.root)
        main_frame.pack(pady=20, padx=20, fill=tk.BOTH, expand=True)

        # Поле ввода промокода
        ttk.Label(main_frame, text="Введите промокод:").pack(pady=(0, 5))

        self.entry = ttk.Entry(main_frame, font=FONT, width=40)
        self.entry.pack(pady=5)

        # Кнопки
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(pady=10)

        ttk.Button(
            btn_frame,
            text="Проверить",
            command=self.check_promo,
            style="TButton"
        ).pack(side=tk.LEFT, padx=5)

        ttk.Button(
            btn_frame,
            text="Вставить",
            command=self.paste_from_clipboard,
            style="TButton"
        ).pack(side=tk.LEFT, padx=5)

        # Поле вывода информации
        self.info_label = ttk.Label(
            main_frame,
            text="",
            wraplength=400,
            justify=tk.CENTER
        )
        self.info_label.pack(pady=10, fill=tk.X)

    def check_promo(self):
        promo = self.entry.get().strip()

        if not promo:
            self.show_info("Введите промокод!", "red")
            return

        if promo == CORRECT_PROMO:
            success_info = """
            Промокод верный!

            Напиши в Telegram: @MST_tg
            И напиши ему промокод и код 
            (промокод который был. Код: 114931737)
            """
            self.show_info(success_info, "green")
        else:
            self.show_info("❌ Ошибка: Неверный промокод!", "red")

    def paste_from_clipboard(self):
        try:
            clipboard_text = pyperclip.paste()
            self.entry.delete(0, tk.END)
            self.entry.insert(0, clipboard_text)
        except Exception as e:
            self.show_info(f"Ошибка вставки: {str(e)}", "red")

    def show_info(self, message, color):
        self.info_label.config(text=message, foreground=color)


def main():
    root = tk.Tk()
    try:
        pyperclip.paste()  # Проверка доступности буфера обмена
    except:
        messagebox.showwarning("Ошибка", "Не удалось получить доступ к буферу обмена")
    app = PromoCodeApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()