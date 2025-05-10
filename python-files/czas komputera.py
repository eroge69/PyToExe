import time
import os
import datetime
import atexit
import threading

log_file = "czas_pracy.txt"

def log_time(action):
    with open(log_file, "a") as file:
        file.write(f"{datetime.datetime.now()}: {action}\n")

def log_start():
    log_time("Komputer uruchomiony")

def log_stop():
    log_time("Komputer wyłączony")

def update_log():
    while True:
        time.sleep(30)
        log_time("Aktualizacja logu")

if __name__ == "__main__":
    log_start()
    atexit.register(log_stop)
    threading.Thread(target=update_log, daemon=True).start()
    
    while True:
        time.sleep(1)