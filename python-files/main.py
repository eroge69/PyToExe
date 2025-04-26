import os
import xml.etree.ElementTree as ET
from openpyxl import load_workbook

# coding=cp1251

# Чтение данных из Excel
def read_serials_from_excel(excel_filename, sheet_name=None, column='A'):
    workbook = load_workbook(filename=excel_filename)
    worksheet = workbook.active if sheet_name is None else workbook[sheet_name]
    rows = list(worksheet.rows)[1:]  # Пропускаем первую строку заголовков
    return [row[ord(column.upper()) - ord('A')].value for row in rows if row[ord(column.upper()) - ord('A')].value]

# Обновление XML файла
def update_xml(xml_filename, new_data):
    tree = ET.parse(xml_filename)
    root = tree.getroot()

    # Найдем нужный элемент СвМайнинг
    майнинг_element = root.find('.//СвМайнинг')

    # Для каждого нового серийного номера создаем элемент СвОборуд
    for serial in new_data:
        своборуд = ET.SubElement(майнинг_element, 'СвОборуд')
        своборудсправоч = ET.SubElement(своборуд, 'СвОборудСправоч')
        своборудсправоч.attrib['КодОборуд'] = '00144'
        своборудсправоч.attrib['ЗаводНом'] = serial
        своборудсправоч.attrib['КоличЧасЭкспл'] = '100'

    # Сохраняем изменения
    tree.write(xml_filename, encoding='windows-1251', xml_declaration=True)

# Основной блок программы
if __name__ == '__main__':
    excel_file = 'input.xlsx'  # имя вашего Excel файла
    xml_file = 'output.xml'  # имя вашего XML шаблона

    # Читаем серийные номера из Excel
    serial_numbers = read_serials_from_excel(excel_file)

    # Обновляем XML файл новыми серийными номерами
    update_xml(xml_file, serial_numbers)

    print(f"Серийные номера успешно добавлены в {xml_file}.")
