import csv
import os

def load_databases(file_paths):
    databases = []
    for path in file_paths:
        if os.path.isfile(path):
            try:
                with open(path, newline='', encoding='utf-8') as f:
                    reader = csv.DictReader(f, delimiter=';')
                    data = list(reader)
                    if data:
                        databases.append((path, data))
                    else:
                        print(f"Файл {path} пустой.")
            except Exception as e:
                print(f"[!] Ошибка при чтении файла {path}: {e}")
        else:
            print(f"[!] Файл {path} не найден.")
    return databases

def search_in_databases(databases, search_field, search_value):
    search_value = search_value.strip().lower()
    found = False

    for filename, data in databases:
        print(f"[^] Данные из базы: {filename}")
        matches = [row for row in data if row.get(search_field, '').strip().lower() == search_value]

        if matches:
            found = True
            for row in matches:
                print("—" * 50)
                for key, value in row.items():
                    print(f"[*] {key}: {value}")
                    what = input("[^] Чтобы вернуться в меню, нажмите Enter: ")
                    main()
        else:
            print("[!] Совпадений не найдено.")
            what = input("[^] Чтобы вернуться в меню, нажмите Enter: ")
            main()

    if not found:
        print("[!] Поиск завершен. Совпадений не найдено.")
        what = input("[^] Чтобы вернуться в меню, нажмите Enter: ")
        main()

def main():
    os.system("clear")
    print("""
    
__        _______ ____    _____ 
\ \      / / ____| __ )  |___ / 
 \ \ /\ / /|  _| |  _ \    |_ \ 
  \ V  V / | |___| |_) |  ___) |
   \_/\_/  |_____|____/  |____/ 
    """)
    files_input = input("[^] Введите имена csv файлов через пробел: ").strip()
    what = input(f"[~] Вы указали: {files_input}, Верно? (+/-): ")
    if what == "-":
        main()
    elif what == "+":
        file_list = [f.strip() for f in files_input.split(' ')]
        print("[*] Проверка файлов, пожалуйста подождите...")
        databases = load_databases(file_list)
        if not databases:
            print("[!] Не удалось загрузить базы данных.")
            return

        headers_sample = databases[0][1][0].keys()
        print("Доступные поля для поиска:")
        print("—" * 50)
        for field in headers_sample:
            print(f"[*] {field}")

        search_field = input("[~] Введите название поля для поиска: ").strip()
        search_value = input("[~] Введите значение для поиска: ").strip()

        search_in_databases(databases, search_field, search_value)
    else:
        print("[!] Некорректный ввод")
        main()


main()
