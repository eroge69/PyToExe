import pandas as pd
import os
import sys

script_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
excel_files = [f for f in os.listdir(script_dir) 
              if f.endswith('.xlsx') and f != 'combined.xlsx']

if not excel_files:
    print("Нет файлов для объединения.")
    input("Нажмите Enter...")
    sys.exit()

combined_data = pd.DataFrame()
total_files = len(excel_files)

print(f"Найдено файлов для обработки: {total_files}\n{'-'*40}")

for file in excel_files:
    file_path = os.path.join(script_dir, file)
    try:
        df = pd.read_excel(file_path, sheet_name=0, header=None)
        combined_data = pd.concat([combined_data, df], ignore_index=True)
        
        # Статистика по текущему файлу
        rows, cols = df.shape
        print(
            f"[{excel_files.index(file)+1}/{total_files}] {file}\n"
            f"Добавлено: {rows} строк | {cols} колонок\n"
            f"{'-'*40}"
        )
    except Exception as e:
        print(f"Ошибка в {file}: {str(e)}\n{'-'*40}")

output_path = os.path.join(script_dir, 'combined.xlsx')

try:
    combined_data.to_excel(output_path, index=False, header=False)
    
    # Статистика итогового файла
    total_rows, total_cols = combined_data.shape
    print(
        f"\n{'='*40}\n"
        f"ИТОГОВЫЙ ФАЙЛ: {output_path}\n"
        f"Общее количество строк: {total_rows}\n"
        f"Общее количество колонок: {total_cols}\n"
        f"{'='*40}"
    )
except Exception as e:
    print(f"\n{'!'*40}\nОшибка сохранения: {str(e)}\n{'!'*40}")

input("\nНажмите Enter для выхода...")