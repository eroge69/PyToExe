import os
import sys
import csv
import subprocess
import argparse

# Проверка запуска из EXE и открытие CMD
if getattr(sys, 'frozen', False):
    subprocess.Popen(f'cmd /k "{sys.executable}"', shell=True)
    sys.exit()

# Основной код базы данных
DB_FILE = 'phone_database.csv'

def init_db():
    if not os.path.exists(DB_FILE):
        with open(DB_FILE, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['Телефон', 'Почта', 'Пароль', 'Username'])

def show_db():
    init_db()
    try:
        with open(DB_FILE, 'r', encoding='utf-8') as f:
            data = list(csv.reader(f))
    except:
        data = []
    
    print("\n{:<3} {:<15} {:<20} {:<15} {:<15}".format('№', 'Телефон', 'Почта', 'Пароль', 'Username'))
    print('-'*70)
    for i, row in enumerate(data[1:] if len(data) > 1 else [], 1):
        print("{:<3} {:<15} {:<20} {:<15} {:<15}".format(i, *row))

def add_entry(phone, email='', password='', username=''):
    if not (phone.startswith('+') and phone[1:].isdigit() and len(phone) >= 10):
        print("Ошибка: неверный формат телефона. Пример: +79123456789")
        return False
    
    init_db()
    with open(DB_FILE, 'a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow([
            phone,
            email,
            password,
            f"@{username.lstrip('@')}" if username else ''
        ])
    print("✓ Запись добавлена")
    return True

def delete_entry(index):
    init_db()
    with open(DB_FILE, 'r', encoding='utf-8') as f:
        data = list(csv.reader(f))
    
    if index < 1 or index >= len(data):
        print("Ошибка: неверный индекс записи")
        return False
    
    del data[index]
    with open(DB_FILE, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerows(data)
    print("✓ Запись удалена")
    return True

def edit_entry(index, field, value):
    fields_map = {
        '1': 0, 'номер': 0, 'phone': 0,
        '2': 1, 'почта': 1, 'email': 1,
        '3': 2, 'пароль': 2, 'password': 2,
        '4': 3, 'username': 3
    }
    
    field_index = fields_map.get(field.lower(), -1)
    if field_index == -1:
        print("Ошибка: неверное поле")
        return False
    
    init_db()
    with open(DB_FILE, 'r', encoding='utf-8') as f:
        data = list(csv.reader(f))
    
    if index < 1 or index >= len(data):
        print("Ошибка: неверный индекс записи")
        return False
    
    if field_index == 0 and not (value.startswith('+') and value[1:].isdigit() and len(value) >= 10):
        print("Ошибка: неверный формат телефона")
        return False
    
    if field_index == 3 and value:
        value = f"@{value.lstrip('@')}"
    
    # Расширяем список, если нужно
    while len(data[index]) <= field_index:
        data[index].append('')
    
    data[index][field_index] = value
    with open(DB_FILE, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerows(data)
    print("✓ Запись обновлена")
    return True

def main():
    parser = argparse.ArgumentParser(description="База данных телефонов")
    subparsers = parser.add_subparsers(dest='command', required=True)
    
    # Show command
    show_parser = subparsers.add_parser('show', help='Показать все записи')
    
    # Add command
    add_parser = subparsers.add_parser('add', help='Добавить запись')
    add_parser.add_argument('phone', help='Номер телефона (+XXXXXXXXXX)')
    add_parser.add_argument('--email', help='Электронная почта', default='')
    add_parser.add_argument('--password', help='Пароль', default='')
    add_parser.add_argument('--username', help='Имя пользователя (без @)', default='')
    
    # Delete command
    del_parser = subparsers.add_parser('delete', help='Удалить запись')
    del_parser.add_argument('index', type=int, help='Номер записи')
    
    # Edit command
    edit_parser = subparsers.add_parser('edit', help='Изменить запись')
    edit_parser.add_argument('index', type=int, help='Номер записи')
    edit_parser.add_argument('field', help='Поле (1-номер, 2-почта, 3-пароль, 4-username)')
    edit_parser.add_argument('value', help='Новое значение')
    
    args = parser.parse_args()
    
    if args.command == 'show':
        show_db()
    elif args.command == 'add':
        add_entry(args.phone, args.email, args.password, args.username)
    elif args.command == 'delete':
        delete_entry(args.index)
    elif args.command == 'edit':
        edit_entry(args.index, args.field, args.value)

if __name__ == '__main__':
    # Если запущено как EXE - команда уже выполнена в начале файла
    if not getattr(sys, 'frozen', False):
        main()
