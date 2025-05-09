import os
import tkinter as tk
from tkinter import filedialog, messagebox
from datetime import datetime

def get_file_metadata_time(file_path):
    """Получает время создания файла и возвращает в формате YYYYMMDDHHMMSS"""
    try:
        # Получаем время создания файла (в секундах с эпохи)
        creation_time = os.path.getctime(file_path)
        # Преобразуем в читаемый формат
        dt = datetime.fromtimestamp(creation_time)
        return dt.strftime("%Y%m%d%H%M%S")
    except Exception as e:
        messagebox.showerror("Ошибка", f"Не удалось получить метаданные: {e}")
        return None

def select_and_rename_file():
    """Выбирает файл и переименовывает его"""
    file_path = filedialog.askopenfilename(title="Выберите файл")
    if not file_path:
        return
    
    new_name = get_file_metadata_time(file_path)
    if not new_name:
        return
    
    # Получаем расширение файла
    file_ext = os.path.splitext(file_path)[1]
    new_file_path = os.path.join(
        os.path.dirname(file_path),
        f"{new_name}{file_ext}"
    )
    
    try:
        os.rename(file_path, new_file_path)
        messagebox.showinfo("Успех", f"Файл переименован в:\n{new_file_path}")
    except Exception as e:
        messagebox.showerror("Ошибка", f"Не удалось переименовать файл: {e}")

# Создаем графический интерфейс
root = tk.Tk()
root.title("Переименовыватель файлов")

label = tk.Label(root, text="Выберите файл для переименования по дате создания")
label.pack(pady=10)

button = tk.Button(root, text="Выбрать файл", command=select_and_rename_file)
button.pack(pady=10)

root.mainloop()