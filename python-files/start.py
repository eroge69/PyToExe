import tkinter as tk
import random
import string
import os


def create_hacking_background():
    canvas = tk.Canvas(root, bg='black', highlightthickness=0)
    canvas.place(relwidth=1, relheight=1)

    streams = []
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()

    class Stream:
        def __init__(self, x):
            self.x = x
            self.chars = []
            self.speed = random.randint(2, 6)
            self.next_spawn = 0

        def add_char(self):
            if self.next_spawn <= 0:
                char = random.choice(string.ascii_letters + string.digits + "!@#$%^&*")
                size = random.randint(8, 14)
                color = '#00ff00' if random.random() < 0.8 else '#00cc00'
                text_id = canvas.create_text(self.x, -20, text=char, fill=color,
                                             font=('Courier', size), anchor='n')
                self.chars.append({'id': text_id, 'y': -20})
                self.next_spawn = random.randint(2, 8)
            else:
                self.next_spawn -= 1

        def update(self):
            self.add_char()
            for char in self.chars[:]:
                char['y'] += self.speed
                canvas.coords(char['id'], self.x, char['y'])
                alpha = max(0, min(1, 1 - (char['y'] / (screen_height * 0.8))))
                green_value = int(alpha * 255)
                color = f'#00{green_value:02x}00'
                try:
                    canvas.itemconfig(char['id'], fill=color)
                except:
                    continue
                if char['y'] > screen_height:
                    canvas.delete(char['id'])
                    self.chars.remove(char)

    for x in range(0, screen_width, 20):
        if random.random() < 0.7:
            streams.append(Stream(x))

    def update_streams():
        for stream in streams:
            stream.update()
        if random.random() < 0.1:
            for stream in streams:
                for char in stream.chars:
                    if random.random() < 0.2:
                        canvas.itemconfig(char['id'], state='hidden')
                    else:
                        canvas.itemconfig(char['id'], state='normal')
        root.after(50, update_streams)

    update_streams()
    return canvas


def start_virus_animation():
    virus_label = tk.Label(root, text="", font=("Impact", 48), fg="green", bg="black")
    virus_label.place(relx=0.5, rely=0.5, anchor="center")

    messages = [
        "ВНИМАНИЕ! ОБНАРУЖЕН ВИРУС!",
        "ЗАРАЖЕНИЕ СИСТЕМЫ: Anchored25%...",
        "ДОСТУП К ФАЙЛАМ ПОЛУЧЕН...",
        "ПЕРЕДАЧА ДАННЫХ НА СЕРВЕР...",
        "ЗАРАЖЕНИЕ СИСТЕМЫ: 68%...",
        "ШИФРОВАНИЕ ФАЙЛОВ...",
        "КРИТИЧЕСКАЯ ОШИБКА СИСТЕМЫ!",
        "ВАШ КОМПЬЮТЕР ВЗЛОМАН!"
    ]

    def update_message(index=0):
        if index < len(messages):
            if index % 2 == 0:
                virus_label.config(fg="green")
            else:
                virus_label.config(fg="#00ff00")
            virus_label.config(text=messages[index])
            root.after(1500, update_message, index + 1)
        else:
            show_blue_screen()

    update_message()


def show_blue_screen():
    for widget in root.winfo_children():
        widget.destroy()

    root.configure(bg='blue')
    error_text = (
        ":( Ваш компьютер был заблокирован из-за подозрительной активности\n\n"
        "Код ошибки: VIRUS_ALERT_0x00007B\n\n"
        "Ваши файлы были зашифрованы. Для разблокировки:\n"
        "1. Переведите $500 в биткоинах\n"
        "2. Отправьте деньги мне на карточку: 0000 0000 0000 0000\n\n"
        "Компьютер будет перезагружен через 10 секунд..."
    )

    bsod_label = tk.Label(root, text=error_text, font=("Arial", 24),
                          fg="white", bg="blue", justify="left")
    bsod_label.place(relx=0.5, rely=0.5, anchor="center")
    root.after(10000, fake_shutdown)


def fake_shutdown():
    root.configure(bg='black')
    for widget in root.winfo_children():
        widget.destroy()

    shutdown_label = tk.Label(root, text="Завершение работы...",
                              font=("Arial", 40), fg="white", bg="black")
    shutdown_label.place(relx=0.5, rely=0.5, anchor="center")
    root.after(3000, shutdown_pc)


def shutdown_pc():
    root.destroy()
    os.system("shutdown /s /t 0")  # Команда немедленного выключения для Windows


# Механизм отключения
sequence = []


def check_key(event):
    global sequence
    key = event.keysym
    sequence.append(key)

    # Ограничиваем длину последовательности до 3
    if len(sequence) > 3:
        sequence.pop(0)

    # Проверяем, совпадает ли последовательность с "3 4 5"
    if sequence == ["3", "4", "5"]:
        root.destroy()  # Просто закрываем окно без выключения ПК


# Создаем окно
root = tk.Tk()
root.attributes('-fullscreen', True)
root.configure(bg='black')

# Отключаем закрытие окна и Escape
root.protocol("WM_DELETE_WINDOW", lambda: None)
root.bind("<Escape>", lambda e: None)

# Привязываем обработчик клавиш
root.bind("<Key>", check_key)

background = create_hacking_background()
root.after(3000, start_virus_animation)

root.mainloop()