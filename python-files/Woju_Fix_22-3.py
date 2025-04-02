# author: Woju
# Fix22

import os
import shutil
import time
from dataclasses import dataclass
from typing import Dict, List

@dataclass
class HashMap:
    old_vs_new: Dict[str, Dict[str, str]]

# Define hash replacements for Phoebe
old_vs_new = {
    "Phoebe21": {
        "3a4bf877": "8ee2fb7c",
        "a284a970": "00b2a919",
        "baea13f2": "ecac2cc5"
    },
    "Phoebe22": {
        "8ee2fb7c": "026f7616",
        "00b2a919": "8ba3d365",
        "ecac2cc5": "2c8f9580",
	"4a30f1df": "83bc4e8a",
        "83bc4e8a.dds": "4a30f1df.dds"
    },
    "RoverM21": {
        "d53c2cc7": "c9db8418",
        "f8375eb4": "3ab7c4d1",
        "6e2f48ba": "a4be44e5"
    },
    "RoverM22": {
        "c9db8418": "e18ca2cc",
        "3ab7c4d1": "f8375eb4",
        "a4be44e5": "6e2f48ba",
        "a1c0d97c": "f16d5dae",
        "f16d5dae.dds": "a1c0d97c.dds",
        "7931ea8a": "fedfec0e",
        "fedfec0e.dds": "7931ea8a.dds"
    },
    "RoverF": {
        "e8b5a730": "3533a957"
    },
    "Zhezhi": {
        "c8b08afd": "b4525ff8",
        "4cdc5987": "a7ff2cab",
        "7ebe61e9": "2208a16a"
    },
    "Lingyang": {
        "8b3c13f9": "9925d10e",
        "b239a59d": "d02c1cb1",
	"497106c3": "2e3de562"
    },
    "Chixia21": {
        "489b5f2a": "94afca13",
    },
    "Chixia22": {
        "94afca13": "489b5f2a",
        "7988637b": "45e0cedb",
        "873ca04e": "ba246036",
        "ba246036.dds": "873ca04e.dds",
        "489b5f2a.dds": "94afca13.dds"
    },
}

hash_maps = HashMap(old_vs_new)

def log_message(log, message):
    log.append(message)
    print(message)

def create_backup(file_path):
    backup_path = file_path + ".bak"
    shutil.copy2(file_path, backup_path)
    return backup_path

def collect_ini_files(folder_path: str) -> List[str]:
    """ Collect .ini files only from the script's location and subfolders (ignore upper folders) """
    ini_files = []
    script_folder = os.path.abspath(folder_path)  # Get script's absolute path

    for root, _, files in os.walk(script_folder):  # Scan current folder and subfolders
        for file in files:
            if file.lower().endswith('.ini'):
                ini_files.append(os.path.join(root, file))

    return ini_files

def apply_hash_fix(folder_path):
    log = []
    ini_files = collect_ini_files(folder_path)

    if not ini_files:
        log_message(log, "No .ini files found.")
        return log, 0, 0

    modified_files = 0

    for file_path in ini_files:
        try:
            log_message(log, f"Processing: {file_path}")

            # Force UTF-8 with error handling
            with open(file_path, "r", encoding="utf-8", errors="ignore") as file:
                content = file.read()

            modified = False

            for character, mappings in hash_maps.old_vs_new.items():
                for old_hash, new_hash in mappings.items():
                    if old_hash in content:
                        content = content.replace(old_hash, new_hash)
                        modified = True
                        log_message(log, f"[{character}] Replaced Hash {old_hash} → {new_hash}")

            if modified:
                create_backup(file_path)
                with open(file_path, "w", encoding="utf-8") as file:
                    file.write(content)
                modified_files += 1
                log_message(log, f"Updated: {file_path}")
            else:
                log_message(log, "No changes needed.")

        except Exception as e:
            log_message(log, f"Error processing {file_path}: {str(e)}")

    return log, modified_files, len(ini_files)

if __name__ == '__main__':
    folder_path = os.path.abspath(os.getcwd())  # Get current folder (script location)
    start_time = time.time()

    log, modified_files, total_files = apply_hash_fix(folder_path)

    end_time = time.time()
    elapsed_time = end_time - start_time

    print(f"\nProcessing took {elapsed_time:.2f} seconds")
    print(f"Total files found: {total_files}")
    print(f"Processed {modified_files} files")

    input("Subscribe Woju Mods YouTube, Press Enter to exit...")
