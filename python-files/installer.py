import os
import sys
import time
from tkinter import Tk, Listbox, Button, Label, filedialog, messagebox, END, MULTIPLE


class SimpleInstaller:
    def __init__(self, root):
        self.root = root
        self.root.title("Простой установщик")
        self.root.geometry("500x400")
        
        # Определяем папку, из которой запущен установщик
        self.install_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
        
        # Элементы интерфейса
        self.label = Label(root, text=f"Мониторинг папки: {self.install_dir}")
        self.label.pack(pady=10)
        
        self.listbox = Listbox(root, selectmode=MULTIPLE, width=60, height=15)
        self.listbox.pack(pady=10)
        
        self.scan_button = Button(root, text="Сканировать папку", command=self.scan_folder)
        self.scan_button.pack(pady=5)
        
        self.install_button = Button(root, text="Установить выбранное", command=self.install_selected)
        self.install_button.pack(pady=5)
        
        # Первоначальное сканирование
        self.scan_folder()
        
        # Запускаем периодическую проверку папки
        self.periodic_check()
    
    def scan_folder(self):
        """Сканирует папку на наличие файлов"""
        self.listbox.delete(0, END)
        try:
            files = os.listdir(self.install_dir)
            for file in files:
                # Показываем только исполняемые файлы и архивы (можно изменить под свои нужды)
                if file.endswith(('.exe', '.msi', '.zip', '.rar', '.7z')):
                    self.listbox.insert(END, file)
            
            if not self.listbox.size():
                self.listbox.insert(END, "Не найдено файлов для установки")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сканировать папку: {e}")
    
    def install_selected(self):
        """Установка выбранных файлов"""
        selected = self.listbox.curselection()
        if not selected:
            messagebox.showwarning("Внимание", "Выберите файлы для установки")
            return
        
        for index in selected:
            file = self.listbox.get(index)
            if file == "Не найдено файлов для установки":
                continue
                
            file_path = os.path.join(self.install_dir, file)
            try:
                # Здесь должна быть логика установки
                # Для примера просто показываем сообщение
                messagebox.showinfo("Установка", f"Начата установка файла: {file}")
                
                # В реальном приложении здесь можно использовать:
                # os.startfile(file_path) - для запуска exe/msi
                # или subprocess.Popen для более сложных сценариев
                
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось установить {file}: {e}")
    
    def periodic_check(self):
        """Периодическая проверка папки на изменения"""
        self.scan_folder()
        # Проверяем каждые 5 секунд (можно изменить интервал)
        self.root.after(5000, self.periodic_check)


if __name__ == "__main__":
    root = Tk()
    app = SimpleInstaller(root)
    root.mainloop()