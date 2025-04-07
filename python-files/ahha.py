import psutil
import os
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class USBEventHandler(FileSystemEventHandler):
    def on_modified(self, event):
        # Check if a USB drive was inserted (usually mounted under /media or /mnt in Linux)
        # For Windows, it might be something like "E:\\", so adjust based on your OS
        if event.src_path.startswith('/media') or event.src_path.startswith('/mnt'):
            print("USB device detected. Shutting down...")
            self.shutdown_system()

    def shutdown_system(self):
        # Shutdown command depending on OS
        if os.name == 'posix':  # For Linux/macOS
            os.system('sudo shutdown -h now')
        elif os.name == 'nt':  # For Windows
            os.system('shutdown /s /t 1')

def monitor_usb():
    # Define the path where USB devices are mounted
    path_to_watch = '/media'  # For Linux
    event_handler = USBEventHandler()
    observer = Observer()
    observer.schedule(event_handler, path_to_watch, recursive=False)
    
    try:
        observer.start()
        print("Monitoring USB devices. The system will shut down when a device is detected.")
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

if __name__ == "__main__":
    monitor_usb()
