import os
import re
import string

# Регулярное выражение для поиска IP:PORT или домен:порт
IP_PORT_REGEX = re.compile(
    r'((?:\d{1,3}\.){3}\d{1,3}|\[[0-9a-fA-F:.]+\]|[a-zA-Z0-9.-]+)'
    r':(?:[1-9][0-9]{0,3}|[1-5][0-9]{4}|6[0-5]{2}[0-3][0-5])'
)

# Расширения файлов, которые стоит проверить
TEXT_EXTENSIONS = {'.txt', '.json', '.conf', '.ini', '.log', '.yaml', '.yml', '.xml'}

def get_all_drives():
    """Возвращает список доступных дисков в системе (только Windows)"""
    return ['%s:\\' % d for d in string.ascii_uppercase if os.path.exists('%s:' % d)]

def find_vpnly_directories(drives):
    """Ищет все директории, содержащие 'vpnly' в имени"""
    result_dirs = []
    for drive in drives:
        print(f"[+] Поиск в {drive}")
        try:
            for root, dirs, files in os.walk(drive, topdown=True):
                # Убираем нежелательные папки
                dirs[:] = [d for d in dirs if d not in {'$Recycle.Bin', 'System Volume Information'}]
                if 'vpnly' in root.lower():
                    print(f"  Найдена папка: {root}")
                    result_dirs.append(root)
        except Exception as e:
            print(f"[-] Ошибка при сканировании {root}: {e}")
    return result_dirs

def search_ip_port_in_file(file_path):
    """Проверяет файл на наличие IP:PORT"""
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
            matches = IP_PORT_REGEX.findall(content)
            if matches:
                print(f"\n[!] Найдены совпадения в: {file_path}")
                for match in set(matches):
                    print(f"    → {match}")
    except Exception as e:
        pass

def scan_files_in_directory(directory):
    """Сканирует все файлы в указанной директории"""
    for root, _, files in os.walk(directory):
        for file in files:
            file_path = os.path.join(root, file)
            ext = os.path.splitext(file)[1].lower()
            if ext in TEXT_EXTENSIONS:
                search_ip_port_in_file(file_path)

if __name__ == '__main__':
    print("[+] Начало поиска...\n")
    drives = get_all_drives()
    vpnly_dirs = find_vpnly_directories(drives)

    if not vpnly_dirs:
        print("[-] Папки с 'vpnly' не найдены.")
    else:
        print("\n[+] Начинаю анализ файлов...")
        for directory in vpnly_dirs:
            scan_files_in_directory(directory)
        print("\n[+] Сканирование завершено.")