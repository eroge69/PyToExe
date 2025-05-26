import os
import psutil
import threading
import random
import string
import time
import numpy as np

# Stress test CPU
def stress_cpu():
    while True:
        pass

# Stress test RAM
def stress_ram():
    data = []
    try:
        while True:
            data.append([random.random() for _ in range(10**7)])  # Adjust the size if needed
    except MemoryError:
        print("Out of RAM!")

# Stress test GPU (simpler with numpy for now, you can extend with PyCUDA)
def stress_gpu():
    while True:
        np.random.rand(10000, 10000)  # Creates large random arrays continuously

# Fill up Storage (careful with this, it will fill up the drive!)
def fill_storage():
    try:
        file_count = 0
        while True:
            filename = f"junkfile_{file_count}.txt"
            with open(filename, "w") as f:
                f.write(''.join(random.choices(string.ascii_letters + string.digits, k=10**6)))  # 1MB file
            file_count += 1
    except Exception as e:
        print(f"Error filling storage: {e}")

# Start stress tests in different threads
if __name__ == "__main__":
    print("Starting stress tests...")

    # Start CPU stress
    cpu_thread = threading.Thread(target=stress_cpu, daemon=True)
    cpu_thread.start()

    # Start RAM stress
    ram_thread = threading.Thread(target=stress_ram, daemon=True)
    ram_thread.start()

    # Start GPU stress (simulated)
    gpu_thread = threading.Thread(target=stress_gpu, daemon=True)
    gpu_thread.start()

    # Start storage filling
    storage_thread = threading.Thread(target=fill_storage, daemon=True)
    storage_thread.start()