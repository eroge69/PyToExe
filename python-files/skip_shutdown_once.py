import subprocess
import time

# Replace with your actual task name (including folder if any), e.g., r"\MyFolder\MyTask"
task_name = r"\Shutdown @22u00"

def disable_task(name):
    subprocess.run(["schtasks", "/Change", "/TN", name, "/Disable"], check=True)
    print(f"Task {name} disabled.")

def enable_task(name):
    subprocess.run(["schtasks", "/Change", "/TN", name, "/Enable"], check=True)
    print(f"Task {Shutdown} re-enabled.")

def skip_once(name, wait_seconds=86400):
    try:
        disable_task(name)
        print(f"Waiting {wait_seconds} seconds before re-enabling...")
        time.sleep(wait_seconds)
        enable_task(name)
    except subprocess.CalledProcessError as e:
        print(f"An error occurred: {e}")

# Skip once, wait 1 dag (86400 seconds) before re-enabling
skip_once(task_name, wait_seconds=86400)
