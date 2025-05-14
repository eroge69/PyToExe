import os
import re
import sys

def process_line(line, search_string):
    """
    Process a line to check if it contains the search string and extract URL, email/username, password.
    Returns None if the line doesn't match the search string or is invalid.
    """
    if search_string.lower() not in line.lower():
        return None
    
    email_pattern = r'([\w\.-]+@[\w\.-]+\.\w+)'
    match = re.search(email_pattern, line)
    if match:
        email_or_username = match.group(1)
        email_start, email_end = match.span()
        url = line[:email_start].strip(" :")
        password = line[email_end:].strip(" :")
        if url and password:
            return url, email_or_username, password
    
    # Fallback: split by spaces if no email is found
    parts = line.split()
    if len(parts) >= 3:
        url = parts[0]
        email_or_username = parts[1]
        password = " ".join(parts[2:])
        return url, email_or_username, password
    
    return None

def process_file(input_file, search_strings, output_format, seen_dict):
    """
    Process a single file for all search strings, writing results to separate output files.
    seen_dict maps search strings to sets of seen lines for deduplication.
    """
    try:
        with open(input_file, 'r', encoding='utf-8') as infile:
            for line in infile:
                line = line.strip()
                if not line:
                    continue
                
                for search_string in search_strings:
                    if line in seen_dict[search_string]:
                        continue
                    seen_dict[search_string].add(line)
                    
                    result = process_line(line, search_string)
                    if result:
                        url, email_or_username, password = result
                        output_file = f"{search_string}.txt"
                        with open(output_file, 'a', encoding='utf-8') as outfile:
                            if output_format == "post":
                                formatted = (
                                    f"Ссылка: {url}\n"
                                    f"Почта/никнейм: {email_or_username}\n"
                                    f"Пароль: {password}\n\n"
                                )
                                outfile.write(formatted)
                            else:  # combo
                                outfile.write(f"{email_or_username}:{password}\n")
    except FileNotFoundError:
        print(f"Файл {input_file} не найден.")
    except UnicodeDecodeError:
        print(f"Ошибка декодирования файла {input_file}.")
    except Exception as e:
        print(f"Ошибка при обработке файла {input_file}: {e}")

def main():
    # Get mode
    print("Режимы: 1 - один файл, 2 - папка с файлами")
    mode = input("Выберите режим (1/2): ").strip()
    if mode not in ("1", "2"):
        print("Неверный режим. Выберите 1 или 2.")
        sys.exit(1)
    
    # Get output format
    output_format = input("Выберите формат вывода (пост/комбо): ").strip().lower()
    if output_format not in ("пост", "комбо"):
        print("Неверный формат. Выберите 'пост' или 'комбо'.")
        sys.exit(1)
    
    # Get search strings
    search_input = input("Введите строки для поиска (через запятую или пробел): ").strip()
    search_strings = [s.strip() for s in re.split(r'[,\s]+', search_input) if s.strip()]
    if not search_strings:
        print("Не указаны строки для поиска.")
        sys.exit(1)
    
    # Initialize deduplication sets for each search string
    seen_dict = {s: set() for s in search_strings}
    
    if mode == "1":
        input_file = input("Введите путь к входному файлу: ").strip()
        if not os.path.isfile(input_file):
            print(f"Файл {input_file} не существует.")
            sys.exit(1)
        process_file(input_file, search_strings, output_format, seen_dict)
    else:
        folder_path = input("Введите путь к папке с txt файлами: ").strip()
        if not os.path.isdir(folder_path):
            print(f"Папка {folder_path} не существует.")
            sys.exit(1)
        
        txt_files = [f for f in os.listdir(folder_path) if f.endswith('.txt')]
        if not txt_files:
            print(f"В папке {folder_path} нет txt файлов.")
            sys.exit(1)
        
        for txt_file in txt_files:
            input_file = os.path.join(folder_path, txt_file)
            process_file(input_file, search_strings, output_format, seen_dict)
    
    print("Обработка завершена. Результаты сохранены в файлах:")
    for search_string in search_strings:
        print(f"- {search_string}.txt")

if __name__ == "__main__":
    main()