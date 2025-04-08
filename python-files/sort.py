import os
import shutil

def group_files_by_prefix():
    current_dir = os.getcwd()

    # Получаем список всех файлов (исключая папки)
    items = os.listdir(current_dir)
    files = [item for item in items if os.path.isfile(os.path.join(current_dir, item))]

    total_files = len(files)
    processed_files = 0
    created_folders = set()

    for item in files:
        full_path = os.path.join(current_dir, item)

        # Проверяем, что в названии файла есть символ "_"
        if "_" in item:
            prefix = item.split("_", 1)[0]
            target_folder = os.path.join(current_dir, prefix)

            # Создаём папку, если её нет
            if not os.path.exists(target_folder):
                os.makedirs(target_folder)
                created_folders.add(prefix)

            # Перемещаем файл
            shutil.move(full_path, os.path.join(target_folder, item))

        processed_files += 1
        # Простейший вывод прогресса (можно удалить "\r", если не нужен перезапись в одной строке)
        print(f"Обработано файлов: {processed_files}/{total_files}", end="\r")

    print("\nГруппировка завершена!")
    print(f"Обработано файлов: {total_files}")
    print(f"Создано папок: {len(created_folders)}")

if __name__ == "__main__":
    group_files_by_prefix()
    input("\nНажмите любую клавишу, чтобы выйти...")
