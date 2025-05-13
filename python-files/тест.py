import tkinter as tk
import random
from collections import deque, Counter

# Конфигурация
history_limit = 20
error_memory = deque(maxlen=history_limit)
error_counter = Counter()

# Все возможные ряды
rows = {
    1: "1234567890",
    2: "йцукенгшщзхъ",
    3: "фывапролджэ",
    4: "ячсмитьбю",
}

# Имена для отображения
row_names = {
    1: "1 - Цифровой ряд (1-0)",
    2: "2 - Верхний русский ряд (й-ъ)",
    3: "3 - Средний русский ряд (ф-э)",
    4: "4 - Нижний русский ряд (я-ю)",
}


class DigitTrainer:
    def __init__(self, master, active_chars):
        self.master = master
        self.active_chars = active_chars

        self.master.title("Тренажер")
        self.master.geometry("300x200")
        self.master.configure(bg="black")

        self.current_digit = ""
        self.previous_digit = ""

        self.label = tk.Label(master, text="", font=("Arial", 100), fg="lime", bg="black")
        self.label.pack(expand=True)

        self.master.bind("<Key>", self.on_key_press)
        self.show_new_digit()

    def show_new_digit(self):
        weighted_chars = self.get_weighted_chars()
        new_char = self.current_digit
        while new_char == self.current_digit and len(weighted_chars) > 1:
            new_char = random.choice(weighted_chars)
        self.previous_digit = self.current_digit
        self.current_digit = new_char
        self.label.config(text=self.current_digit)

    def get_weighted_chars(self):
        if len(error_memory) < history_limit:
            return self.active_chars

        weighted = []
        for char in self.active_chars:
            weight = 1 + error_counter[char] * 3
            weighted.extend([char] * weight)
        return weighted

    def on_key_press(self, event):
        user_input = event.char
        if user_input in self.active_chars:
            if user_input == self.current_digit:
                error_memory.append((self.current_digit, True))
                self.error_check_cleanup(self.current_digit)
                self.show_new_digit()
            else:
                error_memory.append((self.current_digit, False))
                error_counter[self.current_digit] += 1


def start_app(active_chars):
    root = tk.Tk()
    app = DigitTrainer(root, active_chars)
    root.mainloop()


def main():
    print("Выберите ряды для тренировки (введите номера через пробел):")
    for key, name in row_names.items():
        print(f"{name}")

    selected_rows = input("Ваш выбор: ").strip().split()
    active_chars = []

    for row_num in selected_rows:
        if row_num.isdigit() and int(row_num) in rows:
            active_chars.extend(list(rows[int(row_num)]))
        else:
            print(f"Неверный номер ряда: {row_num}")

    if not active_chars:
        print("Не выбрано ни одного ряда. Завершение программы.")
        return

    print("\nЗапуск приложения...")
    start_app(active_chars)


if __name__ == '__main__':
    main()