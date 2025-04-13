import tkinter as tk
import pygame
import random

# Инициализация pygame для воспроизведения музыки
pygame.mixer.init()
pygame.mixer.music.load('Pesn.mp3')
pygame.mixer.music.play(-1)  # Бесконечное воспроизведение

# Функция для создания окна
def create_window():
    window = tk.Toplevel(root)  # Используем Toplevel для создания нового окна
    window.title("I'm Invincible")
    
    img = tk.PhotoImage(file='scale.png')  # Создание нового объекта изображения для каждого окна
    label = tk.Label(window, image=img)
    label.image = img  # Сохранение ссылки на изображение
    label.pack()

    # Запрет на закрытие окна
    window.protocol("WM_DELETE_WINDOW", lambda: None)

    # Разброс окон по экрану
    x = random.randint(0, root.winfo_screenwidth() - 200)  # 200 - ширина окна
    y = random.randint(0, root.winfo_screenheight() - 200)  # 200 - высота окна
    window.geometry(f"+{x}+{y}")

# Функция для добавления чисел в текстовое поле
def add_numbers():
    number = random.randint(1, 100)  # Генерация случайного числа
    color = "#{:06x}".format(random.randint(0, 0xFFFFFF))  # Генерация случайного цвета
    text_widget.insert(tk.END, f"{number} ", 'color')  # Добавление числа в текстовое поле
    text_widget.tag_config('color', foreground=color)  # Установка цвета текста
    text_widget.see(tk.END)  # Прокрутка вниз

    # Запланировать следующий вызов через 1000 мс (1 секунда)
    root.after(1000, add_numbers)

# Основное окно
root = tk.Tk()
root.withdraw()  # Скрываем основное окно

# Создание текстового поля для отображения чисел
text_widget = tk.Text(root, height=10, width=50)
text_widget.pack()

# Создание окон
for _ in range(30):
    create_window()

# Запуск функции для добавления чисел
add_numbers()

root.mainloop()
