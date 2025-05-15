import os
import re
from colorama import Fore, Style, init
from multiprocessing.dummy import Pool as ThreadPool
from datetime import datetime

init(autoreset=True)

# Global settings
OUTPUT_DIR = "Resultz"
TARGET_FILES = [
    'cpanels.txt', 'whm.txt', 'webmails.txt', 'plesk.txt',
    'WordPress.txt', 'Logins_Joomla.txt', 'Logins_Prestashop.txt',
    'Logins_Laravel.txt', 'Logins_Drupal.txt', 'SMTPs.txt',
    'Office365_SMTPs.txt', 'Zoho_SMTPs.txt', 'Aruba_SMTPs.txt',
    'Logins_Ftp.txt', 'Godaddy_SMTPs.txt', 'Ionos_SMTPs.txt'
]

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def create_dir(path):
    if not os.path.exists(path):
        os.makedirs(path)

def add_http_if_missing(url):
    if not url.startswith(('http://', 'https://')):
        return f'http://{url}'
    return url

def read_file_with_fallback(file_path):
    encodings = ['utf-8', 'latin-1', 'utf-16', 'utf-32']
    for encoding in encodings:
        try:
            with open(file_path, 'r', encoding=encoding, errors='ignore') as f:
                return [line.strip() for line in f if line.strip()]
        except UnicodeDecodeError:
            continue
    print(f"{Fore.RED}[!] Unable to read {file_path}")
    return []

def write_tagged_file(file_name, lines, output_dir):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    tag = f"""
             LOGS SORTER
    [Date & Time]  {now}
    [File Name]  {file_name}
    [Line Count]  {len(lines)}
"""

    output_path = os.path.join(output_dir, file_name)
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(tag + '\n')
            f.writelines('\n'.join(lines) + '\n')
            f.write(tag)
        print(f"{Fore.GREEN}[+] Tag appended to {file_name}")
    except Exception as e:
        print(f"{Fore.RED}[-] Error writing {file_name}: {e}")

def process_email_log_line(line):
    line = add_http_if_missing(line.strip())
    result = None

    if ':2083' in line or ':2082' in line:
        result = handle_cpanel(line)
    elif ':2087' in line or ':2086' in line:
        result = handle_whm(line)
    elif '/wp-login.php' in line:
        result = handle_wordpress(line)
    elif '/administrator/' in line:
        result = handle_joomla(line)
    elif '/admin/' in line:
        result = handle_prestashop(line)
    elif '/login' in line and 'laravel' in line:
        result = handle_laravel(line)
    elif '/user/login' in line:
        result = handle_drupal(line)
    elif ':21' in line:
        result = handle_ftp(line)
    elif 'microsoftonline.' in line:
        result = handle_office365_smtp(line)
    elif 'zoho.' in line:
        result = handle_zoho_smtp(line)
    elif 'aruba.it' in line:
        result = handle_aruba_smtp(line)
    elif 'godaddy.com' in line:
        result = handle_godaddy_smtp(line)
    elif '.ionos.' in line:
        result = handle_ionos_smtp(line)
    elif ':8443' in line:
        result = handle_plesk(line)
    elif ':2096' in line:
        result = handle_webmail(line)

    return result

def handle_cpanel(line):
    host = re.search(r'://(.*?):', line)[0]
    parts = line.replace('http://', '').replace('https://', '').split(':')
    if len(parts) >= 3:
        return f'{host}|{parts[1]}|{parts[2]}', 'cpanels.txt'

def handle_whm(line):
    host = re.search(r'://(.*?):', line)[0]
    parts = line.replace('http://', '').replace('https://', '').split(':')
    if len(parts) >= 3:
        return f'{host}|{parts[1]}|{parts[2]}', 'whm.txt'

def handle_wordpress(line):
    rep_pto = line.replace('http://', '').replace('https://', '')
    spliter = rep_pto.split(':')
    form = f"http://{spliter[0]}#{spliter[1]}@{spliter[2]}"
    if 'https://' in line:
        form = f"https://{spliter[0]}#{spliter[1]}@{spliter[2]}"
    return form, 'WordPress.txt'

def filter_emails(input_file):
    lines = read_file_with_fallback(input_file)
    pool = ThreadPool(500)
    results = pool.map(process_email_log_line, lines)
    pool.close()
    pool.join()

    categorized = {filename: [] for filename in TARGET_FILES}

    for res in results:
        if res:
            content, filename = res
            categorized.setdefault(filename, []).append(content)

    # Write results to files
    for filename, entries in categorized.items():
        path = os.path.join(OUTPUT_DIR, filename)
        with open(path, 'a', encoding='utf-8') as f:
            f.write('\n'.join(entries) + '\n')

    return categorized

def main_menu():
    clear_screen()
    print(f"""{Fore.LIGHTMAGENTA_EX}{Style.DIM}{Style.BRIGHT}
             LOGS SORTER
    """ + Style.RESET_ALL)
    print(Fore.LIGHTWHITE_EX + Style.DIM + Style.BRIGHT + f"        [{Fore.GREEN}!{Fore.LIGHTWHITE_EX}] Choose an option:")
    print(Fore.LIGHTWHITE_EX + Style.DIM + Style.BRIGHT + f"        [{Fore.GREEN}1{Fore.LIGHTWHITE_EX}] TXT_LOGS :")
    print(Fore.LIGHTWHITE_EX + Style.DIM + Style.BRIGHT + f"        [{Fore.GREEN}2{Fore.LIGHTWHITE_EX}] ZIP_LOGS :")

    choice = input(f"        [{Fore.GREEN}?{Fore.LIGHTWHITE_EX}] Select: ").strip()

    if choice == '1':
        input_file = input("[#] Enter input file name: ").strip()
        print(f"[DEBUG] Current working directory: {os.getcwd()}")
        print(f"[DEBUG] Looking for file: {input_file}")

        if not os.path.isfile(input_file):
            print(f"{Fore.RED}[!] File not found: {input_file}")
            print(f"{Fore.YELLOW}[*] Please make sure the file exists in this folder.")
            return

        create_dir(OUTPUT_DIR)
        categorized = filter_emails(input_file)

        for filename, entries in categorized.items():
            print(f"{Fore.CYAN}[+] Found {len(entries)} entries in {filename}")

        # Add tagging
        for filename in TARGET_FILES:
            file_path = os.path.join(OUTPUT_DIR, filename)
            if os.path.exists(file_path):
                lines = read_file_with_fallback(file_path)
                write_tagged_file(filename, lines, OUTPUT_DIR)

    elif choice == '2':
        print("Feature coming soon...")
    else:
        print("Invalid choice.")

if __name__ == "__main__":
    main_menu()