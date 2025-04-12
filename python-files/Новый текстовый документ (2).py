import pandas as pd
import os

def merge_excel_files(directory, output_file):
    all_data = []
    first_file = True
    header = None

    for filename in os.listdir(directory):
        if filename.endswith('.xlsx') or filename.endswith('.xls'):
            file_path = os.path.join(directory, filename)
            df = pd.read_excel(file_path)

            # Если это первый файл, сохраняем заголовок
            if first_file:
                header = df.columns.tolist()
                first_file = False
            else:
                df.columns = header  # Устанавливаем заголовки на основе первого файла

            all_data.append(df)

    # Объединяем все данные в один DataFrame
    combined_df = pd.concat(all_data, ignore_index=True)
    
    # Сохраняем в итоговый файл
    combined_df.to_excel(output_file, index=False)

# Использование функции
if __name__ == "__main__":
    merge_excel_files("путь_к_вашей_папке", "объединенный_файл.xlsx")