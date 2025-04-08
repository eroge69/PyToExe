import os
import shutil
from tqdm import tqdm

def group_files_by_prefix():
    current_dir = os.getcwd()
    
    # Составляем список всех файлов (исключая папки)
    items = os.listdir(current_dir)
    files = [item for item in items if os.path.isfile(os.path.join(current_dir, item))]
    
    total_files = len(files)
    created_folders = set()
    
    # Используем tqdm для отображения прогресса
    for item in tqdm(files, desc="Группировка файлов", ncols=80):
        full_path = os.path.join(current_dir, item)
        
        # Проверяем, что в названии файла есть символ "_"
        if "_" in item:
            # Префикс (часть имени файла до "_")
            prefix = item.split("_", 1)[0]
            
            # Целевая папка
            target_folder = os.path.join(current_dir, prefix)
            
            # Создаём папку, если её нет
            if not os.path.exists(target_folder):
                os.makedirs(target_folder)
                created_folders.add(prefix)
            
            # Перемещаем файл
            shutil.move(full_path, os.path.join(target_folder, item))
    
    print(f"\nОбработано файлов: {total_files}")
    print(f"Создано папок: {len(created_folders)}")

if __name__ == "__main__":
    group_files_by_prefix()
    input("\nНажмите любую клавишу, чтобы выйти...")
