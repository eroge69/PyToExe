import os
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import time

FOLDER_TO_WATCH = "./watched_folder"  # Change this to your desired folder
OUTPUT_FILE = "file_list.txt"

def update_file_list(folder, output_file):
    with open(output_file, 'w') as f:
        for filename in os.listdir(folder):
            file_path = os.path.join(folder, filename)
            if os.path.isfile(file_path):
                f.write(filename + '\n')
    print(f"Updated file list with contents of {folder}")

class FolderMonitorHandler(FileSystemEventHandler):
    def on_created(self, event):
        if not event.is_directory:
            print(f"New file detected: {event.src_path}")
            update_file_list(FOLDER_TO_WATCH, OUTPUT_FILE)

if __name__ == "__main__":
    if not os.path.exists(FOLDER_TO_WATCH):
        os.makedirs(FOLDER_TO_WATCH)

    update_file_list(FOLDER_TO_WATCH, OUTPUT_FILE)

    event_handler = FolderMonitorHandler()
    observer = Observer()
    observer.schedule(event_handler, path=FOLDER_TO_WATCH, recursive=False)
    observer.start()
    print(f"Monitoring folder: {FOLDER_TO_WATCH}")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
