import tkinter as tk
import os
import shutil
from tkinter import messagebox

# Установленный пароль для доступа
USER_PASSWORD = "1020"

# Путь к исходной папке с файлами
SRC_PATH = r"C:\Users\Андрей\Desktop\Dr.web 2025 Bonus\program\dr wem"
DST_PATH = os.path.expanduser("~/Desktop")  # Рабочий стол

# Копирование файла на рабочий стол
def copy_file_to_desktop(filename):
    try:
        src_file = os.path.join(SRC_PATH, filename)
        dst_file = os.path.join(DST_PATH, filename)
        if os.path.exists(src_file):
            shutil.copy(src_file, dst_file)
            messagebox.showinfo("Успех", f"Файл '{filename}' добавлен на рабочий стол!")
        else:
            messagebox.showerror("Ошибка", f"Файл '{filename}' отсутствует в папке 'dr wem'!")
    except Exception as e:
        messagebox.showerror("Ошибка", f"Не удалось добавить файл: {e}")

# Копирование всей папки на рабочий стол
def copy_folder_to_desktop():
    try:
        dst_folder = os.path.join(DST_PATH, "dr wem")
        if os.path.exists(SRC_PATH):
            shutil.copytree(SRC_PATH, dst_folder)
            messagebox.showinfo("Успех", "Папка 'dr wem' успешно добавлена на рабочий стол!")
        else:
            messagebox.showerror("Ошибка", "Папка 'dr wem' отсутствует!")
    except FileExistsError:
        messagebox.showerror("Ошибка", "Папка 'dr wem' уже существует на рабочем столе!")
    except Exception as e:
        messagebox.showerror("Ошибка", f"Не удалось добавить папку: {e}")

# Проверка правильности введенного пароля
def verify_password():
    entered_password = password_entry.get()
    if entered_password == USER_PASSWORD:
        messagebox.showinfo("Успех", "Пароль верный! Добро пожаловать.")
        open_main_menu()
    else:
        messagebox.showerror("Ошибка", "Неправильный пароль! Доступ запрещен.")

# Переливающийся текст
def update_color():
    global color_index
    colors = ["red", "orange", "yellow", "green", "blue", "purple"]
    color_index = (color_index + 1) % len(colors)
    label_gradient_text.configure(fg=colors[color_index])
    main_window.after(500, update_color)

# Главное меню программы
def open_main_menu():
    auth_window.destroy()
    global main_window, label_gradient_text, color_index
    main_window = tk.Tk()
    main_window.title("Dr.Web Utilities")
    main_window.geometry("600x450")
    main_window.configure(bg="white")
    color_index = 0

    # Декоративный заголовок
    tk.Label(main_window, text="Dr.Web Utilities", font=("Arial", 24, "bold"), fg="#333", bg="white").pack(pady=20)

    # Настройка стиля кнопок
    button_style = {"font": ("Arial", 16), "bg": "#4caf50", "fg": "white", "width": 25, "height": 2}

    # Кнопки
    tk.Button(main_window, text="Ключ", command=lambda: copy_file_to_desktop("drweb32.key"), **button_style).pack(pady=10)
    tk.Button(main_window, text="Антивирусы", command=copy_folder_to_desktop, **button_style).pack(pady=10)

    # Переливающийся текст внизу
    label_gradient_text = tk.Label(main_window, text="Program by @Dex102", font=("Arial", 12, "bold"), bg="white")
    label_gradient_text.pack(side="bottom", pady=20)

    update_color()  # Запускаем обновление цвета текста

    main_window.mainloop()

# Окно авторизации
auth_window = tk.Tk()
auth_window.title("Авторизация")
auth_window.geometry("400x300")
auth_window.configure(bg="white")

# Декоративный заголовок
tk.Label(auth_window, text="Добро пожаловать!", font=("Arial", 22, "bold"), fg="#333", bg="white").pack(pady=20)
tk.Label(auth_window, text="Введите пароль для доступа:", font=("Arial", 14), fg="#555", bg="white").pack(pady=10)

# Поле для ввода пароля
password_entry = tk.Entry(auth_window, show="*", font=("Arial", 14), width=20)
password_entry.pack(pady=10)

# Кнопка входа
tk.Button(auth_window, text="Войти", command=verify_password, font=("Arial", 14), bg="#4caf50", fg="white", width=20, height=2).pack(pady=20)

# Декоративный нижний текст
tk.Label(auth_window, text="© 2025 Dr.Web Utilities", font=("Arial", 10), fg="#666", bg="white").pack(side="bottom", pady=10)

auth_window.mainloop()
