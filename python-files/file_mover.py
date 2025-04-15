import os
import shutil
from tkinter import Tk, Listbox, Button, Frame, Label, filedialog, messagebox, MULTIPLE
from send2trash import send2trash
from dotenv import load_dotenv

class FileMoverApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Garbage Collector 2")
        self.root.geometry("600x500")  # Ширина 600, высота 500
        
        # Загрузка .env и получение пути
        load_dotenv()
        self.current_dir = os.path.expanduser(os.getenv('WORK_DIR'))
        
        # Проверка существования директории
        if not self.current_dir or not os.path.isdir(self.current_dir):
            print(f"Неверный путь в .env: {self.current_dir}")
            self.current_dir = filedialog.askdirectory(title="Выберите начальную директорию")
            if not self.current_dir or not os.path.isdir(self.current_dir):
                messagebox.showerror("Ошибка", "Неверная директория")
                self.root.destroy()
                return
            
        # Основной фрейм
        main_frame = Frame(self.root)
        main_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Список файлов и папок с возможностью множественного выбора
        self.file_list = Listbox(main_frame, selectmode='extended')
        self.file_list.pack(side='left', fill='both', expand=True, padx=(0, 10))
        
        # Фрейм для кнопок
        self.button_frame = Frame(main_frame)
        self.button_frame.pack(side='right', fill='y')
        
        # Автоматическая обработка файлов при запуске
        self.process_files_on_start()
        
    def process_files_on_start(self):
        """Автоматическая обработка файлов при запуске программы"""
        try:
            items = os.listdir(self.current_dir)
            
            # Ищем папку для изображений
            img_dir = os.path.join(self.current_dir, '!img')
            if not os.path.exists(img_dir):
                img_dir = None
                
            for item in items:
                full_path = os.path.join(self.current_dir, item)
                
                # Удаляем .torrent файлы
                if item.endswith('.torrent') and os.path.isfile(full_path):
                    try:
                        send2trash(full_path)
                        continue
                    except Exception as e:
                        print(f"Не удалось удалить файл {item}: {str(e)}")
                        
                # Перемещаем изображения
                if img_dir and os.path.isfile(full_path):
                    ext = os.path.splitext(item)[1].lower()
                    if ext in ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp']:
                        try:
                            shutil.move(full_path, os.path.join(img_dir, item))
                        except Exception as e:
                            print(f"Не удалось переместить изображение {item}: {str(e)}")
        
        except Exception as e:
            print(f"Ошибка при автоматической обработке файлов: {str(e)}")

        # Обновление интерфейса
        self.update_interface()
        
    def update_interface(self):
        # Очистка списка и кнопок
        self.file_list.delete(0, 'end')
        for widget in self.button_frame.winfo_children():
            widget.destroy()
            
        # Получение списка файлов и папок
        try:
            items = os.listdir(self.current_dir)
        except PermissionError:
            messagebox.showerror("Ошибка", "Нет доступа к директории")
            return
            
        # Добавление файлов и папок в список
        for item in items:
            full_path = os.path.join(self.current_dir, item)
            if not item.startswith('!') and (os.path.isfile(full_path) or os.path.isdir(full_path)) and item.lower() != 'desktop.ini':
                self.file_list.insert('end', item)
                
        # Кнопка удаления
        delete_btn = Button(self.button_frame, text="Удалить", 
                           command=self.delete_files, bg='red', fg='white')
        delete_btn.pack(fill='x', pady=10)
        
        # Создание кнопок только для папок с "!"
        for item in items:
            full_path = os.path.join(self.current_dir, item)
            if item.startswith('!') and os.path.isdir(full_path):
                btn = Button(self.button_frame, text=item, 
                           command=lambda path=full_path: self.move_files(path),
                           bg='lightblue')
                btn.pack(fill='x', pady=2)
                
    def move_files(self, target_dir):
        # Получение выбранных файлов
        selected_indices = self.file_list.curselection()
        if not selected_indices:
            messagebox.showwarning("Предупреждение", "Не выбраны файлы для перемещения")
            return
            
        # Перемещение файлов
        for i in selected_indices:
            filename = self.file_list.get(i)
            src = os.path.join(self.current_dir, filename)
            try:
                shutil.move(src, target_dir)
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось переместить файл {filename}: {str(e)}")
                return
                
        # Обновление интерфейса
        self.update_interface()
        
    def delete_files(self):
        # Получение выбранных файлов
        selected_indices = self.file_list.curselection()
        if not selected_indices:
            messagebox.showwarning("Предупреждение", "Не выбраны файлы для удаления")
            return
            
        # Перемещение файлов в корзину
        for i in selected_indices:
            filename = self.file_list.get(i)
            src = os.path.join(self.current_dir, filename)
            try:
                send2trash(src)
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось удалить файл {filename}: {str(e)}")
                return
                
        # Обновление интерфейса
        self.update_interface()

if __name__ == "__main__":
    root = Tk()
    app = FileMoverApp(root)
    root.mainloop()
