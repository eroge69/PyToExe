# py2exe: no console

import tkinter as tk
import random
from collections import deque, Counter

# Настройки адаптации
history_limit = 20
error_memory = deque(maxlen=history_limit)
error_counter = Counter()

class DigitTrainer:
    def __init__(self, master):
        self.master = master
        self.master.title("Тренажер цифр")
        self.master.geometry("300x200")
        self.master.configure(bg="black")
        self.current_digit = ""
        self.previous_digit = ""

        self.label = tk.Label(master, text="", font=("Arial", 100), fg="lime", bg="black")
        self.label.pack(expand=True)

        master.bind("<Key>", self.on_key_press)
        self.show_new_digit()

    def show_new_digit(self):
        weighted_digits = self.get_weighted_digits()
        new_digit = self.current_digit
        while new_digit == self.current_digit:
            new_digit = random.choice(weighted_digits)
        self.previous_digit = self.current_digit
        self.current_digit = new_digit
        self.label.config(text=self.current_digit)

    def get_weighted_digits(self):
        if len(error_memory) < history_limit:
            return [str(i) for i in range(10)]

        weighted = []
        for i in range(10):
            digit = str(i)
            weight = 1 + error_counter[digit] * 3
            weighted.extend([digit] * weight)
        return weighted

    def on_key_press(self, event):
        if event.char.isdigit():
            if event.char == self.current_digit:
                error_memory.append((self.current_digit, True))
                self.error_check_cleanup(self.current_digit)
                self.show_new_digit()
            else:
                error_memory.append((self.current_digit, False))
                error_counter[self.current_digit] += 1

    def error_check_cleanup(self, digit):
        recent_errors = [d for d, correct in error_memory if not correct and d == digit]
        if not recent_errors:
            error_counter[digit] = 0

if __name__ == '__main__':
    root = tk.Tk()
    app = DigitTrainer(root)
    root.mainloop()
