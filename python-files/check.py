def check_duplicate_lines(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            lines = file.readlines()
        
        # Убираем лишние пробелы и символы перевода строки
        lines = [line.strip() for line in lines]
        
        # Проверяем на дубликаты
        if len(lines) != len(set(lines)):
            print("В файле найдены дубликаты строк.")
        else:
            print("Дубликаты строк не найдены.")
    
    except FileNotFoundError:
        print(f"Файл '{file_path}' не найден.")
    except Exception as e:
        print(f"Произошла ошибка: {e}")

if __name__ == "__main__":
    file_path = input("Введите путь к файлу .txt: ")
    check_duplicate_lines(file_path)