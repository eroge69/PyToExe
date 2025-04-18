
import time
import os
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from PyPDF2 import PdfReader
import win32api
import win32print

# Ordner, der überwacht wird
WATCH_FOLDER = r"C:\Messprotokolle"

class PDFHandler(FileSystemEventHandler):
    def on_created(self, event):
        if event.src_path.endswith(".pdf"):
            time.sleep(1)  # Warte auf vollständiges Schreiben
            print(f"Neue Datei erkannt: {event.src_path}")
            try:
                reader = PdfReader(event.src_path)
                text = "".join(page.extract_text() or "" for page in reader.pages)
                if "PASS" in text.upper() or "PASS" in os.path.basename(event.src_path).upper():
                    print("PASS erkannt – Drucke Datei...")
                    win32api.ShellExecute(
                        0, "print", event.src_path, None, ".", 0
                    )
                else:
                    print("Kein PASS – Datei wird ignoriert.")
            except Exception as e:
                print(f"Fehler beim Verarbeiten: {e}")

if __name__ == "__main__":
    print(f"Überwache Ordner: {WATCH_FOLDER}")
    observer = Observer()
    observer.schedule(PDFHandler(), path=WATCH_FOLDER, recursive=False)
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
