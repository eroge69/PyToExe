import json
import os

# Автоматическое создание файла если его нет
if not os.path.exists("abonents.json"):
    with open("abonents.json", "w", encoding="utf-8") as f:
        json.dump([], f)

# Загрузка данных
with open("abonents.json", "r+", encoding="utf-8") as file:
    try:
        abonents = json.load(file)
    except json.decoder.JSONDecodeError:
        abonents = []

def show_all(allkeys):
    i = 0
    for contact in abonents:
        i += 1
        print(f'{i}. {contact["name"]} {contact["surname"]}, Адрес: {contact["address"]}, Номер: {contact["number"]}')

def search(searchable):
    searchable = input("Введите имя, фамилию, адрес или номер телефона интересующего абонента:\n")
    founded = []
    
    for abonent in abonents:
        if searchable.lower() in [str(v).lower() for v in abonent.values()]:
            founded.append(abonent)
    
    if founded:
        for contact in founded:
            print(f"Имя: {contact['name']}, Фамилия: {contact['surname']}, Адрес: {contact['address']}, Телефон: {contact['number']}")
    else:
        print("Абонент не найден.")

def add(newabonent):
    new_name = input("Введите имя нового абонента: ")
    new_surname = input("Введите фамилию нового абонента: ")
    new_address = input("Введите адрес нового абонента: ")
    new_phone = input("Введите номер телефона нового абонента: ")
    new_abonent_info = {
        "name": new_name, 
        "surname": new_surname, 
        "address": new_address, 
        "number": new_phone
    }
    abonents.append(new_abonent_info)
    print(f"Абонент - {new_name} {new_surname} добавлен!")
    with open("abonents.json", "w", encoding="utf-8") as file:
        json.dump(abonents, file, indent=4, ensure_ascii=False)

def redact(redact_abonent):
    search_term = input("Введите любую информацию абонента для поиска: ")
    results = []
    
    for abonent in abonents:
        if any(search_term.lower() in str(v).lower() for v in abonent.values()):
            results.append(abonent)
    
    if not results:
        print("Совпадений не найдено.")
        return
    
    print("Найдены контакты:")
    for i, contact in enumerate(results, 1):
        print(f"{i}. {contact['name']} {contact['surname']} ({contact['number']})")
    
    choice = int(input("Введите номер контакта для редактирования: ")) - 1
    if choice < 0 or choice >= len(results):
        print("Неверный выбор")
        return
    
    field = input("Введите поле для изменения (name, surname, address, number): ")
    if field not in ["name", "surname", "address", "number"]:
        print("Неверное поле")
        return
    
    new_value = input(f"Введите новое значение для {field}: ")
    results[choice][field] = new_value
    
    with open("abonents.json", "w", encoding="utf-8") as file:
        json.dump(abonents, file, indent=4, ensure_ascii=False)
    print("Изменения сохранены!")

print("------------------------------------\nДобро пожаловать в телефонную книжку.\n------------------------------------")
while True:
    operation = input("------------------------------------\nВыберите операцию:\n1.Show\n2.Search\n3.Add\n4.Redact\n5.Exit\n------------------------------------\n").strip().lower()

    if operation == "show" or operation == "1":
        show_all(abonents)
    elif operation == "search" or operation == "2":
        search(abonents)
    elif operation == "add" or operation == "3":
        add(abonents)
    elif operation == "redact" or operation == "4":
        redact(abonents)
    elif operation == "exit" or operation == "5":
        exit()