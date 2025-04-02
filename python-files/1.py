import os
from PIL import Image

def get_image_widths(folder_path):
    for filename in os.listdir(folder_path):
        try:
            img = Image.open(os.path.join(folder_path, filename))
            width, height = img.size
            print(f'{filename}: Ширина = {width} пикселей')
        except IOError:
            print(f'Невозможно прочитать размер файла {filename}')

folder_path = input("Введите путь к папке с изображениями: ")
get_image_widths(folder_path)
input("Нажмите Enter для выхода...") # Добавляем паузу