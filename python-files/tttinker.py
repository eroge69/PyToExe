import time
import threading
import psutil
import tkinter as tk
from tkinter import ttk, scrolledtext
from pynput import keyboard, mouse
import win32gui

# --- CONFIG ---
IDLE_THRESHOLD = 1260  # 21 minutes
UPDATE_INTERVAL = 1000  # ms
LOG_WINDOW_SIZE = 6     # Fewer log lines for a tiny window

# --- GLOBALS ---
last_activity_time = time.time()
running = False
keyboard_listener = None
mouse_listener = None

def truncate_text(text, max_length=15):
    return text if len(text) <= max_length else text[:max_length-3] + "..."

# --- TKINTER GUI ---
root = tk.Tk()
root.title("RBLX Idle Monitor")
root.geometry("230x120")
root.resizable(False, False)

# Set window transparency (0.1=very transparent, 1.0=opaque)
root.attributes("-alpha", 0.4)  # You can adjust 0.7 to your liking[2][7]

main_frame = ttk.Frame(root)
main_frame.pack(expand=True, fill='both', padx=2, pady=2)

# Four Columns (as a grid for compactness)
labels = []
for i, lbl in enumerate(["Active", "Status", "Focus", "Timer"]):
    l = ttk.Label(main_frame, text=lbl, font=('Arial', 8, 'bold'))
    l.grid(row=0, column=i, sticky="nsew", padx=1, pady=1)
    labels.append(l)

process_label = ttk.Label(main_frame, font=('Arial', 8), width=11, anchor="w", wraplength=120)
process_label.grid(row=1, column=0, sticky="nsew", padx=1, pady=1)

status_label = ttk.Label(main_frame, font=('Arial', 8), width=7, anchor="center")
status_label.grid(row=1, column=1, sticky="nsew", padx=1, pady=1)

focus_label = ttk.Label(main_frame, font=('Arial', 8), width=6, anchor="center")
focus_label.grid(row=1, column=2, sticky="nsew", padx=1, pady=1)

timer_label = ttk.Label(main_frame, font=('Arial', 8), width=8, anchor="center")
timer_label.grid(row=1, column=3, sticky="nsew", padx=1, pady=1)

# Log output (very small)
log_frame = ttk.Frame(root)
log_frame.pack(fill='both', expand=True, padx=2, pady=1)
output_box = scrolledtext.ScrolledText(log_frame, wrap=tk.WORD, height=3, font=('Arial', 7))
output_box.pack(expand=True, fill='both')

def log(msg):
    output_box.insert(tk.END, f"[{time.strftime('%H:%M:%S')}] {msg}\n")
    lines = output_box.get('1.0', tk.END).splitlines()
    if len(lines) > LOG_WINDOW_SIZE:
        output_box.delete('1.0', f"{len(lines) - LOG_WINDOW_SIZE + 1}.0")
    output_box.see(tk.END)

def format_time(seconds):
    hours, rem = divmod(seconds, 3600)
    minutes, seconds = divmod(rem, 60)
    return f"{int(hours):02}:{int(minutes):02}:{int(seconds):02}"

def get_foreground_window_title():
    try:
        return win32gui.GetWindowText(win32gui.GetForegroundWindow())
    except Exception:
        return "(Unknown)"

def is_roblox_running():
    for proc in psutil.process_iter(['name']):
        if proc.info['name'] and proc.info['name'].lower() == "robloxplayerbeta.exe":
            return proc
    return None

def is_roblox_focused():
    roblox_proc = is_roblox_running()
    if not roblox_proc:
        return False
    return get_foreground_window_title().strip() == "Roblox"

def get_readable_key(key):
    if hasattr(key, 'char') and key.char is not None:
        return key.char
    return str(key).split('.')[-1].capitalize()

def get_readable_button(button):
    mapping = {
        mouse.Button.left: "Left Mouse Button",
        mouse.Button.right: "Right Mouse Button",
        mouse.Button.middle: "Middle Mouse Button"
    }
    return mapping.get(button, str(button))

def on_key_press(key):
    global last_activity_time
    if is_roblox_running():
        if is_roblox_focused():
            readable = get_readable_key(key)
            log(f"Key: {readable}")
            last_activity_time = time.time()

def on_click(button, pressed):
    global last_activity_time
    if pressed:
        if is_roblox_running():
            if is_roblox_focused():
                readable = get_readable_button(button)
                log(f"Click: {readable}")
                last_activity_time = time.time()

def monitor_loop():
    global running, last_activity_time
    while running:
        time.sleep(1)
        roblox_proc = is_roblox_running()
        now = time.time()

        if roblox_proc:
            idle_duration = now - last_activity_time
            if idle_duration >= IDLE_THRESHOLD:
                log("Idle limit! Killing.")
                try:
                    roblox_proc.kill()
                except Exception as e:
                    log(f"Kill fail: {e}")
                stop_monitoring()
                break
        else:
            last_activity_time = now

def start_monitoring():
    global running, keyboard_listener, mouse_listener
    if not running:
        running = True
        threading.Thread(target=monitor_loop, daemon=True).start()
        keyboard_listener = keyboard.Listener(on_press=on_key_press)
        mouse_listener = mouse.Listener(on_click=on_click)
        keyboard_listener.start()
        mouse_listener.start()
        log("Started.")

def stop_monitoring():
    global running, keyboard_listener, mouse_listener
    running = False
    if keyboard_listener:
        keyboard_listener.stop()
        keyboard_listener = None
    if mouse_listener:
        mouse_listener.stop()
        mouse_listener = None
    log("Stopped.")

def update_gui():
    roblox_proc = is_roblox_running()
    roblox_focused = is_roblox_focused()
    title = get_foreground_window_title()
    process_label.config(text=truncate_text(title))
    status_label.config(text="Run" if roblox_proc else "Stop")
    focus_label.config(text="Yes" if roblox_focused else "No")
    if roblox_proc:
        idle_time = time.time() - last_activity_time
    else:
        idle_time = 0
    timer_label.config(text=format_time(idle_time))
    root.after(UPDATE_INTERVAL, update_gui)

# --- Control Buttons (tiny) ---
button_frame = ttk.Frame(root)
button_frame.pack(pady=1)
ttk.Button(button_frame, text="Start", command=start_monitoring, width=5).pack(side='left', padx=2)
ttk.Button(button_frame, text="Stop", command=stop_monitoring, width=5).pack(side='left', padx=2)

# Start monitoring by default
start_monitoring()
update_gui()
root.mainloop()

