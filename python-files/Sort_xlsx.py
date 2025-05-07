import os
import pandas as pd
from tkinter import Tk, Button, Label, filedialog, messagebox

def sort_folders():
    # Выбор Excel файла через диалоговое окно
    file_path = filedialog.askopenfilename(
        title="Выберите Excel файл",
        filetypes=[("Excel files", "*.xlsx *.xls")]
    )
    
    if not file_path:
        messagebox.showinfo("Информация", "Файл не выбран. Операция отменена.")
        return

    try:
        # Чтение Excel файла
        df = pd.read_excel(file_path, header=None)  # Без заголовков
        folder_names = df.iloc[:, 0].dropna().astype(str).tolist()  # Первый столбец
  # Считываем названия папок из столбца loan_id
    except Exception as e:
        messagebox.showerror("Ошибка", f"Не удалось прочитать Excel файл: {e}")
        return

    # Выбор директории с папками
    source_directory = filedialog.askdirectory(title="Выберите папку с папками")
    if not source_directory:
        messagebox.showinfo("Информация", "Папка не выбрана. Операция отменена.")
        return

    # Создание папки "Есть в реестре", если она не существует
    target_folder = os.path.join(source_directory, "Есть в реестре")
    if not os.path.exists(target_folder):
        os.makedirs(target_folder)

    # Получение списка папок в выбранной директории
    all_folders = [name for name in os.listdir(source_directory) if os.path.isdir(os.path.join(source_directory, name))]

    # Фильтрация папок, которые есть в реестре
    folders_to_move = [folder for folder in all_folders if folder in folder_names]

    # Перемещение папок
    moved_count = 0
    for folder in folders_to_move:
        source_path = os.path.join(source_directory, folder)
        target_path = os.path.join(target_folder, folder)
        try:
            os.rename(source_path, target_path)
            moved_count += 1
        except Exception as e:
            messagebox.showwarning("Предупреждение", f"Не удалось переместить папку {folder}: {e}")

    # Вывод статистики
    total_in_registry = len(folder_names)
    messagebox.showinfo(
        "Статистика",
        f"Всего названий папок в реестре: {total_in_registry}\n"
        f"Найдено и перемещено папок: {moved_count}"
    )

# Создание GUI
root = Tk()
root.title("Сортировка папок")

label = Label(root, text="Выберите Excel файл с реестром папок")
label.pack(pady=10)

button = Button(root, text="Выбрать реестр", command=sort_folders)
button.pack(pady=20)

root.mainloop()