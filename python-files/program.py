import time
import os
import shutil
import fnmatch # For pattern matching
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import logging

# --- !!! --- CONFIGURATION --- !!! ---
# --- !!! ---   PLEASE EDIT   --- !!! ---
config = {
    "DOWNLOADS_FOLDER": os.path.join(os.path.expanduser("~"), "Downloads"),
    # Example Google Drive paths:
    # "GOOGLE_DRIVE_TARGET_FOLDER": "G:\\My Drive\\FromDownloads", # If using virtual drive G:
    # "GOOGLE_DRIVE_TARGET_FOLDER": os.path.join(os.path.expanduser("~"), "Google Drive", "FromDownloads"), # Common location
    "GOOGLE_DRIVE_TARGET_FOLDER": "C:\\Path\\To\\Your\\Google Drive Sync Folder\\TargetSubfolder", # <--- !!! EDIT THIS !!!
    "FILE_PATTERNS_TO_MOVE": [
        "*.pdf",
        "Inventory_*.csv",
        "invoice_*.xlsx",
        "specific_file_name.zip"
        # Add more patterns or specific filenames here
    ],
    "CHECK_DELAY_SECONDS": 5, # Wait a few seconds to ensure file is fully written
    "LOG_FILE": os.path.join(os.path.expanduser("~"), "download_mover.log") # Log file in user's home directory
}
# --- !!! --- END CONFIGURATION --- !!! ---

# Setup logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    handlers=[
                        logging.FileHandler(config["LOG_FILE"]),
                        logging.StreamHandler() # Also print to console
                    ])

class DownloadHandler(FileSystemEventHandler):
    def on_created(self, event):
        if event.is_directory:
            return

        filepath = event.src_path
        filename = os.path.basename(filepath)

        logging.info(f"Detected new file: {filepath}")

        # Check if the filename matches any of the patterns
        should_move = False
        for pattern in config["FILE_PATTERNS_TO_MOVE"]:
            if fnmatch.fnmatch(filename, pattern):
                should_move = True
                break

        if should_move:
            logging.info(f"'{filename}' matches a pattern. Waiting {config['CHECK_DELAY_SECONDS']}s for file to finalize...")
            time.sleep(config["CHECK_DELAY_SECONDS"]) # Wait for file to be fully written

            # Ensure the target Google Drive folder exists
            target_folder = config["GOOGLE_DRIVE_TARGET_FOLDER"]
            if not os.path.exists(target_folder):
                try:
                    os.makedirs(target_folder)
                    logging.info(f"Created target Google Drive folder: {target_folder}")
                except Exception as e:
                    logging.error(f"Could not create target folder {target_folder}: {e}")
                    return # Stop if we can't create the folder

            destination_path = os.path.join(target_folder, filename)

            # Handle potential filename conflicts in destination
            counter = 1
            base, ext = os.path.splitext(filename)
            while os.path.exists(destination_path):
                destination_path = os.path.join(target_folder, f"{base}_{counter}{ext}")
                counter += 1
                logging.info(f"File already exists, trying new name: {os.path.basename(destination_path)}")


            try:
                logging.info(f"Attempting to move '{filepath}' to '{destination_path}'")
                shutil.move(filepath, destination_path)
                logging.info(f"Successfully moved '{filename}' to '{os.path.basename(destination_path)}' in Google Drive folder.")
            except Exception as e:
                logging.error(f"Error moving file '{filename}': {e}")
        else:
            logging.info(f"'{filename}' does not match any specified patterns. Ignoring.")


if __name__ == "__main__":
    # Validate paths
    if not os.path.isdir(config["DOWNLOADS_FOLDER"]):
        logging.error(f"Downloads folder not found: {config['DOWNLOADS_FOLDER']}")
        print(f"Error: Downloads folder not found: {config['DOWNLOADS_FOLDER']}. Please check the script configuration.")
        exit()

    # It's okay if GOOGLE_DRIVE_TARGET_FOLDER doesn't exist yet, we try to create it.
    # But the base of Google Drive should exist if it's already set up.
    # Let's check the parent of the target folder if it's specified.
    gdrive_parent_check = os.path.dirname(config["GOOGLE_DRIVE_TARGET_FOLDER"])
    if gdrive_parent_check and not os.path.isdir(gdrive_parent_check) and gdrive_parent_check != config["GOOGLE_DRIVE_TARGET_FOLDER"]:
         # This check is a bit naive if the target folder is directly in the root of a drive, e.g. "G:\MyFiles"
         # In that case, dirname("G:\MyFiles") is "G:\", which should exist.
         # If target is "G:\", dirname is "G:\"
        if not (len(gdrive_parent_check) == 3 and gdrive_parent_check.endswith(":\\")): # Check for root like "G:\"
             logging.warning(f"Parent of Google Drive target folder might not exist: {gdrive_parent_check}. The script will attempt to create the full path.")


    logging.info("Starting Download Mover script...")
    logging.info(f"Monitoring folder: {config['DOWNLOADS_FOLDER']}")
    logging.info(f"Target Google Drive folder: {config['GOOGLE_DRIVE_TARGET_FOLDER']}")
    logging.info(f"File patterns to move: {', '.join(config['FILE_PATTERNS_TO_MOVE'])}")
    logging.info(f"Log file: {config['LOG_FILE']}")


    event_handler = DownloadHandler()
    observer = Observer()
    observer.schedule(event_handler, config["DOWNLOADS_FOLDER"], recursive=False) # recursive=False for Downloads folder
    observer.start()
    logging.info("Observer started. Press Ctrl+C to stop.")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logging.info("Stopping observer...")
        observer.stop()
    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")
        observer.stop()
    observer.join()
    logging.info("Download Mover script stopped.")