import tkinter as tk
from tkinter import filedialog, messagebox
import time
import random
import pyautogui
import pyperclip
import threading

class TyperThread(threading.Thread):
    def __init__(self, messages, min_delay, max_delay, greeting, running_flag):
        super().__init__()
        self.messages = messages
        self.min_delay = min_delay
        self.max_delay = max_delay
        self.greeting = greeting
        self.running_flag = running_flag

    def run(self):
        print("Запуск через 3 секунды... Убедитесь, что курсор установлен в нужном поле ввода!")
        time.sleep(3)

        try:
            while self.running_flag.is_set():
                if self.messages:
                    message = random.choice(self.messages)
                    full_message = f"{self.greeting} {message}" if self.greeting else message
                    print(f"Отправляется: '{full_message}'")

                    pyperclip.copy(full_message)
                    pyautogui.hotkey("ctrl", "v")
                    pyautogui.press("enter")

                    delay = random.randint(self.min_delay, self.max_delay)
                    time.sleep(delay / 1000.0)
                else:
                    time.sleep(1)
        except Exception as e:
            print(f"Ошибка в потоке печати: {e}")

class AutoTyperApp:
    def __init__(self, master):
        self.master = master
        master.title("Бот Лила")
        master.geometry("600x350")
        master.config(bg="#333333")
        master.resizable(False, False) # Запрещаем изменение размеров окна

        self.running = threading.Event()
        self.typer_thread = None

        self.greeting_label = tk.Label(master, text="Обращение (необязательно):", bg="#333333", fg="#dddddd")
        self.greeting_label.pack(pady=5, padx=10, anchor='w') # anchor='w' - выравнивание по западу

        self.greeting_entry = tk.Entry(master, bg="#555555", fg="#dddddd")
        self.greeting_entry.pack(pady=5, padx=10, fill=tk.X) # Разрешаем растягивание по горизонтали

        self.messages_label = tk.Label(master, text="Сообщения (каждое с новой строки):", bg="#333333", fg="#dddddd")
        self.messages_label.pack(pady=5, padx=10, anchor='w')

        self.messages_text = tk.Text(master, height=10, width=50, bg="#555555", fg="#dddddd") # Указываем фиксированную ширину
        self.messages_text.pack(pady=5, padx=10, fill=tk.BOTH, expand=False) # Разрешаем растягивание, но не расширение

        self.delay_frame = tk.Frame(master, bg="#333333")
        self.delay_frame.pack(pady=5, padx=10, fill=tk.X)

        self.min_delay_label = tk.Label(self.delay_frame, text="Мин. задержка (мс):", bg="#333333", fg="#dddddd")
        self.min_delay_label.pack(side=tk.LEFT)
        self.min_delay_entry = tk.Entry(self.delay_frame, width=10, bg="#555555", fg="#dddddd")
        self.min_delay_entry.insert(0, "1000")
        self.min_delay_entry.pack(side=tk.LEFT, padx=5)

        self.max_delay_label = tk.Label(self.delay_frame, text="Макс. задержка (мс):", bg="#333333", fg="#dddddd")
        self.max_delay_label.pack(side=tk.LEFT, padx=10)
        self.max_delay_entry = tk.Entry(self.delay_frame, width=10, bg="#555555", fg="#dddddd")
        self.max_delay_entry.insert(0, "2000")
        self.max_delay_entry.pack(side=tk.LEFT, padx=5)

        self.button_frame = tk.Frame(master, bg="#333333")
        self.button_frame.pack(pady=10, padx=10, fill=tk.X)

        self.start_button = tk.Button(self.button_frame, text="Старт", command=self.start_typing, bg="#555555", fg="#dddddd")
        self.start_button.pack(side=tk.LEFT, padx=5, expand=False) # Не расширять

        self.stop_button = tk.Button(self.button_frame, text="Стоп", command=self.stop_typing, state=tk.DISABLED, bg="#555555", fg="#dddddd")
        self.stop_button.pack(side=tk.LEFT, padx=5, expand=False) # Не расширять

        self.load_button = tk.Button(self.button_frame, text="Выбрать файл", command=self.load_file, bg="#555555", fg="#dddddd")
        self.load_button.pack(side=tk.RIGHT, padx=5, expand=False) # Не расширять

    def start_typing(self):
        messages_text = self.messages_text.get("1.0", tk.END).strip()
        messages = [line.strip() for line in messages_text.splitlines() if line.strip()]
        greeting = self.greeting_entry.get().strip()

        if not messages:
            messagebox.showwarning("Внимание", "Пожалуйста, введите сообщения.")
            return

        try:
            min_delay = int(self.min_delay_entry.get())
            max_delay = int(self.max_delay_entry.get())
            if max_delay < min_delay:
                max_delay = min_delay
        except ValueError:
            messagebox.showerror("Ошибка", "Пожалуйста, введите корректные значения задержки.")
            return

        self.running.set()
        self.typer_thread = TyperThread(messages, min_delay, max_delay, greeting, self.running)
        self.typer_thread.start()

        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)

    def stop_typing(self):
        if self.typer_thread and self.running.is_set():
            self.running.clear()
            self.typer_thread.join()
            self.typer_thread = None
            self.start_button.config(state=tk.NORMAL)
            self.stop_button.config(state=tk.DISABLED)

    def load_file(self):
        file_path = filedialog.askopenfilename(
            defaultextension=".txt",
            filetypes=[("Текстовые файлы", "*.txt"), ("Все файлы", "*.*")],
            title="Выберите файл с сообщениями"
        )
        if file_path:
            try:
                with open(file_path, "r", encoding="utf-8") as file:
                    self.messages_text.delete("1.0", tk.END)
                    self.messages_text.insert(tk.END, file.read())
            except IOError:
                messagebox.showerror("Ошибка", f"Не удалось открыть файл: {file_path}")

if __name__ == "__main__":
    root = tk.Tk()
    app = AutoTyperApp(root)
    root.mainloop()
