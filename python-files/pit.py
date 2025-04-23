import os
import sys

def rename_files(root_dir):
    for root, _, files in os.walk(root_dir):
        for filename in files:
            if filename.endswith("-(OK).jpg"):
                old_path = os.path.join(root, filename)
                new_filename = filename.replace("-(OK)", "")
                new_path = os.path.join(root, new_filename)
                
                try:
                    os.rename(old_path, new_path)
                    print(f'[OK] Переименовано: "{filename}" → "{new_filename}"')
                except Exception as e:
                    print(f'[ERROR] Ошибка с файлом "{filename}": {e}')

if __name__ == "__main__":
    print("=== Mass Renamer (Python) ===")
    folder = input("Введите путь к папке (или оставьте пустым для текущей): ").strip()
    
    if not folder:
        folder = os.getcwd()
    
    if not os.path.exists(folder):
        print(f"Ошибка: папка '{folder}' не существует!")
        sys.exit(1)
    
    rename_files(folder)
    print("\nГотово! Нажмите Enter чтобы выйти...")
    input()