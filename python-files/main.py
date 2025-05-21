import time
import threading
import os
import pygame

log_path = os.path.expandvars("C:/Users/hayka/AppData/Roaming/.minecraft/logs/latest.log")  # Update if needed

def follow_log(file_path, callback):
    """ Continuously watch a log file and call 'callback(line)' for each new line. """
    with open(file_path, "r", encoding="utf-8") as f:
        f.seek(0, os.SEEK_END)
        while True:
            line = f.readline()
            if line:
                callback(line.strip())
            else:
                time.sleep(0.1)

def handle_log_line(line):
    """ Custom action when a new line is read from the log. """
    if "Welcome to Hypixel SkyBlock!" in line:
        print("🟢 Detected Skyblock join!")
        pygame.init()
        pygame.mixer.init()
        pygame.mixer.music.load("intro.mp3")
        pygame.mixer.music.play()

        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(10)

def start_log_watcher():
    print(f"👀 Watching {log_path}")
    watcher_thread = threading.Thread(target=follow_log, args=(log_path, handle_log_line), daemon=True)
    watcher_thread.start()

if __name__ == "__main__":
    start_log_watcher()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n🛑 Exiting log watcher.")
