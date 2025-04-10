import ctypes
import os
import sys
import tkinter as tk
from tkinter import messagebox

def change_cursor(cursor_path):
    try:
        # Загружаем курсор (работает для .cur и .ani)
        cursor = ctypes.windll.user32.LoadCursorFromFileW(cursor_path)
        
        if cursor:
            # Устанавливаем курсор глобально (требует админских прав)
            ctypes.windll.user32.SetSystemCursor(cursor, 32512)  # 32512 = стандартный курсор
            messagebox.showinfo("Успех!", "Курсор изменён!")
        else:
            messagebox.showerror("Ошибка", "Не удалось загрузить курсор!")
    except Exception as e:
        messagebox.showerror("Ошибка", f"Ошибка: {e}")

if __name__ == "__main__":
    # Путь к курсору (D:\Курсор писюн.ani или .cur)
    cursor_path = "rD:\"  # Замените на свой путь
    
    if not os.path.exists(cursor_path):
        messagebox.showerror("Ошибка", f"Файл не найден: {cursor_path}")
        sys.exit(1)
    
    change_cursor(cursor_path) 