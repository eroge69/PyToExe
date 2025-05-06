
import time
import os
import shutil
import configparser
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

def load_config():
    config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.ini")
    config = configparser.ConfigParser()
    config.read(config_path)
    watch_folder = config.get("settings", "watch_folder", fallback=None)
    destination_folder = config.get("settings", "destination_folder", fallback=None)
    return watch_folder, destination_folder

def replace_switches_in_file(input_path, output_path):
    with open(input_path, "r") as infile, open(output_path, "w") as outfile:
        for line in infile:
            head = line[:12]
            rest = line[12:]
            new_head = head.replace("DUR SWITCH2", "SEC SWITCH")
            outfile.write(new_head + rest)

class DBFileHandler(FileSystemEventHandler):
    def __init__(self, destination_folder):
        self.destination_folder = destination_folder

    def on_created(self, event):
        if event.is_directory or not event.src_path.endswith(".DB"):
            return
        print(f"Detected new file: {event.src_path}")
        filename = os.path.basename(event.src_path)
        dest_path = os.path.join(self.destination_folder, filename.replace(".DB", "_modified.DB"))
        replace_switches_in_file(event.src_path, dest_path)
        print(f"Processed and saved to: {dest_path}")

if __name__ == "__main__":
    watch_folder, destination_folder = load_config()
    if not watch_folder or not os.path.isdir(watch_folder):
        print("Invalid or missing watch folder in config.ini")
        input("Press Enter to exit...")
        exit(1)
    if not destination_folder or not os.path.isdir(destination_folder):
        print("Invalid or missing destination folder in config.ini")
        input("Press Enter to exit...")
        exit(1)

    print(f"Watching folder: {watch_folder}")
    event_handler = DBFileHandler(destination_folder)
    observer = Observer()
    observer.schedule(event_handler, path=watch_folder, recursive=False)
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
