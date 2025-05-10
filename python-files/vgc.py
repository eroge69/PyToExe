import os
import sys
import time
import ctypes
import subprocess
import threading
import itertools
import logging
from typing import Optional

# Constants
PROCESS_NAME = "vgc.exe"
SERVICE_NAME = "vgc"
VALORANT_PROCESS = "VALORANT-Win64-Shipping.exe"

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def is_admin() -> bool:
    """Check if the script is running with admin privileges."""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except Exception:
        return False

def run_as_admin():
    """Relaunch the script with admin privileges."""
    params = ' '.join([f'"{arg}"' for arg in sys.argv])
    try:
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, params, None, 1)
    except Exception as e:
        logging.error(f"Failed to elevate privileges: {e}")
    sys.exit()

def is_process_running(process_name: str) -> bool:
    """Check if a process is running."""
    try:
        output = subprocess.check_output(['tasklist'], shell=True, universal_newlines=True, stderr=subprocess.DEVNULL)
        return process_name.lower() in output.lower()
    except subprocess.CalledProcessError:
        return False

def run_service_command(command: str, service_name: str) -> bool:
    """Run a service command (start/stop)."""
    try:
        completed = subprocess.run(['sc', command, service_name], shell=True, capture_output=True, text=True)
        if completed.returncode == 0:
            logging.info(f"Service '{service_name}' {command} command succeeded.")
            return True
        else:
            logging.error(f"Service '{service_name}' {command} command failed:\n{completed.stdout}{completed.stderr}")
            return False
    except Exception as e:
        logging.error(f"Error executing service command '{command}': {e}")
        return False

def spinner(text: str, wait_event: threading.Event):
    """Display a spinner animation while waiting."""
    for c in itertools.cycle(['|', '/', '-', '\\']):
        if wait_event.is_set():
            break
        print(f'\r{text} {c}', end='', flush=True)
        time.sleep(0.1)
    print('\r' + ' ' * (len(text) + 2) + '\r', end='', flush=True)

def wait_for_valorant(process_name: str):
    """Wait for the Valorant process to start."""
    logging.info("Waiting for Valorant to start... (This may take some time)")
    wait_event = threading.Event()
    spinner_thread = threading.Thread(target=spinner, args=("Checking Valorant process", wait_event))
    spinner_thread.start()
    try:
        while not is_process_running(process_name):
            time.sleep(5)
    except KeyboardInterrupt:
        wait_event.set()
        spinner_thread.join()
        logging.info("Exit requested by user during waiting. Exiting...")
        sys.exit()
    wait_event.set()
    spinner_thread.join()
    logging.info("Valorant is running!")
    logging.info("The script will now wait indefinitely. Press Ctrl+C to exit.")
    idle_forever()

def simulate_action(text: str, seconds: int = 3):
    """Simulate an action with a spinner."""
    wait_event = threading.Event()
    spinner_thread = threading.Thread(target=spinner, args=(text, wait_event))
    spinner_thread.start()
    try:
        time.sleep(seconds)
    except KeyboardInterrupt:
        wait_event.set()
        spinner_thread.join()
        logging.info("Exit requested by user. Exiting...")
        sys.exit()
    wait_event.set()
    spinner_thread.join()
    logging.info(f"{text} completed.")

def handle_service(service_name: str, process_name: str):
    """Handle the service by stopping and restarting it if necessary."""
    if is_process_running(process_name):
        logging.info(f"Service '{service_name}' is already running.")
        logging.info("Stopping service...")
        run_service_command('stop', service_name)
        time.sleep(5)
        logging.info("Starting service again...")
        run_service_command('start', service_name)
        time.sleep(5)
    else:
        logging.info(f"Service '{service_name}' is not running. Starting service...")
        run_service_command('start', service_name)
        time.sleep(5)

def idle_forever():
    """Keep the script idle indefinitely with minimal CPU usage."""
    try:
        wait_event = threading.Event()
        wait_event.wait()  # Wait indefinitely until interrupted
    except KeyboardInterrupt:
        logging.info("Exit requested by user. Exiting...")

def menu():
    """Display the main menu."""
    while True:
        print("\nChoose an option:")
        print("1. Run First (simulate popup bypass)")
        print("2. Run Second (simulate vgc bypass)")
        print("3. Exit")
        choice = input("Enter your choice (1/2/3): ").strip()
        if choice == '1':
            simulate_action("Running popup bypass simulation...")
            logging.info("(Thread cycle checking and suspending threads is not possible in this script.)")
        elif choice == '2':
            simulate_action("Starting vgc bypass simulation...")
            logging.info("(Suspending specific threads is not possible in this script.)")
        elif choice == '3':
            logging.info("Exiting...")
            time.sleep(1)
            break
        else:
            logging.warning("Invalid choice. Please enter 1, 2, or 3.")

def main():
    """Main entry point of the script."""
    if not is_admin():
        logging.warning("Admin privileges required. Relaunching as administrator...")
        run_as_admin()

    logging.info("Starting vgc bypass script...")
    time.sleep(2)

    handle_service(SERVICE_NAME, PROCESS_NAME)
    wait_for_valorant(VALORANT_PROCESS)
    menu()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logging.info("Script interrupted by user, exiting...")
        sys.exit()