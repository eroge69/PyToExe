# -*- coding: utf-8 -*-
import os
import re
import codecs
from multiprocessing.dummy import Pool
from datetime import datetime

try:
    from colorama import Fore, Style, init
    init(autoreset=True)
except ImportError:
    class Fore:
        GREEN = ''
        RED = ''
        CYAN = ''
        WHITE = ''
        LIGHTWHITE_EX = ''
        LIGHTMAGENTA_EX = ''
    class Style:
        DIM = ''
        BRIGHT = ''
        RESET_ALL = ''

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def add_http_if_missing(url):
    if not url.startswith(('http://', 'https://')):
        return 'http://' + url
    return url

def code1():
    print(Fore.LIGHTMAGENTA_EX + Style.BRIGHT + Style.DIM + "         JUST A LOG SORTER" + Style.RESET_ALL)
    input_file = raw_input("[#] - LOGS  :").strip()

    try:
        with open(input_file, 'r') as f:
            target = [line.strip() for line in f if line.strip()]
    except IOError:
        print(Fore.RED + "[!] The file \"%s\" was not found." % input_file)
        return

    def filer(liness):
        try:
            liness = add_http_if_missing(liness)
            if ':2083' in liness or ':2082' in liness:
                try:
                    host = re.findall(r'://(.*?):', liness)[0]
                    parts = liness.replace('http://', '').replace('https://', '').split(':')
                    user, password = parts[1], parts[2]
                    result = 'http://%s:2083|%s|%s' % (host, user, password)
                    with open('cpanels.txt', 'a') as f:
                        f.write(result + '\n')
                    print(result)
                except IndexError:
                    pass
            # Add more elif conditions here for other ports/patterns
        except Exception as e:
            print("Error:", str(e))

    pool = Pool(500)
    pool.map(filer, target)
    pool.close()
    pool.join()

def main():
    clear_screen()
    print(Fore.LIGHTMAGENTA_EX + Style.DIM + Style.BRIGHT + "             LOGS SORTER")
    print(Fore.LIGHTWHITE_EX + Style.DIM + Style.BRIGHT + "        [%s1%s] TXT_LOGS :" % (Fore.GREEN, Fore.LIGHTWHITE_EX))
    print(Fore.LIGHTWHITE_EX + Style.DIM + Style.BRIGHT + "        [%s2%s] ZIP_LOGS :" % (Fore.GREEN, Fore.LIGHTWHITE_EX))
    choice = raw_input("        [%s!%s]  --select  :" % (Fore.GREEN, Fore.LIGHTWHITE_EX)).strip()

    if choice == '1':
        code1()
    else:
        print("Invalid choice.")

if __name__ == "__main__":
    main()