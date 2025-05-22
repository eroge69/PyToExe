from openpyxl import Workbook
from openpyxl.styles import Font
import os
import fitz
from datetime import datetime

# Меняем текущую директорию на ту, где находится скрипт
script_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(script_dir)

# Создание файла описи, добавление в него заголовков таблицы
inventory_name = "Опись_" + datetime.now().strftime("%Y_%m_%d_%H_%M_%S") + ".xlsx"
wb = Workbook()
ws = wb.active
ws.append(('Наименование папки', 'Количество страниц'))

# Функция для подсчёта страниц в файле
def pages_count(file_name):
    try:
        with fitz.open(file_name) as doc:
            return doc.page_count
    except Exception as e:
        print(f"Ошибка при чтении {file_name}: {e}")
        return 0
    
# Создание словаря и списка папок
result = dict()
folders = [item for item in os.listdir(script_dir) if os.path.isdir(os.path.join(script_dir, item))]

# Проход по списку папок, создание списка файлов в каждой папке, проход по списку файлов, добавление в словарь количества страниц для конкретной папки 
for folder_name in folders:
    curent_folder = folder_name
    file_list = [os.path.join(script_dir,curent_folder,file) for file in os.listdir(curent_folder) if file.endswith('.pdf')]
    result[folder_name] = 0
    for file in file_list:
        result[folder_name] +=  pages_count(file)
        print(f'{file} обработан')
    ws.append((folder_name, result[folder_name]))    

ws.column_dimensions["A"].width = 70
ws.column_dimensions["B"].width = 20

bold_font = Font(bold=True)

for cell in ws[1]:  # Строка 1
    cell.font = bold_font

wb.save(inventory_name)

