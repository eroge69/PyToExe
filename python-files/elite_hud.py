import os
import json
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# Path to your Journal folder (make sure to update if needed)
JOURNAL_FOLDER = os.path.expanduser('~/Saved Games/Frontier Developments/Elite Dangerous')

class JournalHandler(FileSystemEventHandler):
    def __init__(self):
        pass

    def on_modified(self, event):
        if event.is_directory:
            return
        
        if "Journal" in event.src_path:
            with open(event.src_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                if lines:
                    try:
                        last_event = json.loads(lines[-1])
                        self.handle_event(last_event)
                    except json.JSONDecodeError:
                        pass  # sometimes partial lines, skip

    def handle_event(self, event):
        event_type = event.get('event')

        if event_type == "UnderAttack":
            self.show_message("WARNING: You are under attack!")
        
        if event_type == "FuelLow":
            self.show_message("ALERT: Fuel is low!")

    def show_message(self, message):
        print(f"HUD Alert: {message}")  # This will print to the Replit console

def main():
    print("Monitoring Elite Dangerous Journal for events...")
    observer = Observer()
    event_handler = JournalHandler()
    observer.schedule(event_handler, JOURNAL_FOLDER, recursive=False)
    observer.start()
    
    try:
        while True:
            time.sleep(1)  # Keeps the script running
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

if __name__ == "__main__":
    main()
