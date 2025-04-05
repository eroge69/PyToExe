import tkinter as tk
from tkinter import filedialog

def process_latex_file():
    """
    1. Запрашивает файл, 
    2. Запрашивает 3 числа, 
    3. Изменяет значения `position = `,
    4. Переносит `direction = ` на новую строку,
    5. Сохраняет изменения.
    """

    # 1. Выбор файла
    root = tk.Tk()
    root.withdraw()  # Скрываем основное окно Tkinter
    file_path = filedialog.askopenfilename(filetypes=[("LaTeX files", "*.ltx")])

    if not file_path:
        print("Файл не выбран. Завершение работы.")
        return

    # 2. Запрос 3 чисел
    try:
        offset1 = float(input("Введите первое число (для x-координаты, используйте '.' вместо ','): ").replace(",", "."))
        offset2 = float(input("Введите второе число (для y-координаты, используйте '.' вместо ','): ").replace(",", "."))
        offset3 = float(input("Введите третье число (для z-координаты, используйте '.' вместо ','): ").replace(",", "."))
    except ValueError:
        print("Ошибка: Введены некорректные числа. Завершение работы.")
        return

    # 3. Чтение файла и обработка
    try:
        with open(file_path, 'r') as file:
            lines = file.readlines()
    except FileNotFoundError:
        print(f"Ошибка: Файл '{file_path}' не найден. Завершение работы.")
        return
    except Exception as e:
        print(f"Ошибка при чтении файла: {e}. Завершение работы.")
        return


    modified_lines = []
    for line in lines:
        if "position = " in line:
            try:
                parts = line.split("position = ")
                coordinates_str = parts[1].strip()  # Получаем строку с координатами
                coordinates = coordinates_str.split(",")  # Разделяем на координаты

                # Преобразуем в числа, добавляем смещения и форматируем обратно в строку
                x = float(coordinates[0]) + offset1
                y = float(coordinates[1]) + offset2
                z = float(coordinates[2]) + offset3

                new_coordinates_str = f"{x},{y},{z}"
                modified_line = parts[0] + "position = " + new_coordinates_str + "\n" # Добавляем перенос строки
                modified_lines.append(modified_line)

            except (ValueError, IndexError) as e:
                print(f"Предупреждение: Не удалось обработать строку с 'position = ': {line.strip()}.  Ошибка: {e}")
                modified_lines.append(line)  # В случае ошибки, добавляем строку как есть
        elif "\ndirection =" in line:
            # 5. Перенос "direction =" на новую строку
            modified_line = line.replace("\ndirection =", "\ndirection =\n")
            modified_lines.append(modified_line)
        else:
            modified_lines.append(line)

    # 6. Сохранение изменений
    try:
        with open(file_path, 'w') as file:
            file.writelines(modified_lines)
        print(f"Файл '{file_path}' успешно изменен.")

    except Exception as e:
        print(f"Ошибка при записи в файл: {e}. Изменения не сохранены.")


if __name__ == "__main__":
    process_latex_file()
