import os

# Устанавливаем текущую директорию в путь к исполнению скрипта
directory = os.getcwd()  # Получаем текущую директорию
# Указываем часть пути, которую нужно удалить
path_to_remove = "C:/User/Владимир/Documents/Paradox Interactive/Stellaris/"

# Проходим по всем файлам в директории
for filename in os.listdir(directory):
    if filename.endswith('.mod'):
        file_path = os.path.join(directory, filename)
        
        # Читаем содержимое файла
        with open(file_path, 'r', encoding='utf-8') as file:
            lines = file.readlines()
        
        # Открываем файл для записи
        with open(file_path, 'w', encoding='utf-8') as file:
            for line in lines:
                # Заменяем часть пути на пустую строку
                new_line = line.replace(path_to_remove, "")
                file.write(new_line)  # Записываем строку обратно в файл

print("Замены завершены.")