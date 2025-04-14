import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import serial
import serial.tools.list_ports
import threading
import time

# Serial communication
ser = None
reading = False
armed = False

# Theme colors
theme = {
    "bg": "#2e2e2e",
    "fg": "#ffffff",
    "btn": "#444444",
    "entry": "#3a3a3a",
    "log_bg": "#1e1e1e",
    "log_fg": "#e0e0e0",
    "highlight": "lightgreen",
    "armed": "#aa0000"
}

def list_serial_ports():
    ports = serial.tools.list_ports.comports()
    return [port.device for port in ports]

def connect_serial():
    global ser, reading
    try:
        selected_port = port_dropdown.get()
        ser = serial.Serial(selected_port, 115200, timeout=1)
        log_output(f"[Connected to {selected_port}]")
        if not reading:
            reading = True
            threading.Thread(target=read_serial, daemon=True).start()
    except Exception as e:
        messagebox.showerror("Connection Error", str(e))

def log_output(message):
    output_log.config(state='normal')
    output_log.insert(tk.END, message + '\n')
    output_log.yview(tk.END)
    output_log.config(state='disabled')

    global armed
    if "ltd state machine state=ARMING" in message:
        armed = True
        update_arm_button()
    elif "ltd state machine state=STOP_ARM" in message:
        armed = False
        update_arm_button()
    elif "ltd state machine state=POWERED" in message:
        toggle_arm_button.config(state='normal')
    elif "password:" in message.lower():
        login_button.config(text="Password")

def read_serial():
    global ser, reading
    while reading:
        try:
            if ser and ser.in_waiting:
                line = ser.readline().decode(errors='ignore').strip()
                if line:
                    log_output(line)
        except Exception as e:
            log_output(f"[ERROR reading serial: {e}]")
            break

def send_command(cmd):
    global ser
    if ser and ser.is_open:
        ser.write((cmd + '\n').encode())
        log_output(f"> {cmd}")

def login_sequence():
    send_command("arete")

def start_client():
    send_command("cd drs_client")
    time.sleep(1)
    send_command("sudo ./client /dev/ttyUSB0 115200")

def send_manual_command():
    cmd = manual_entry.get().strip()
    if cmd:
        send_command(cmd)
        manual_entry.delete(0, tk.END)

def toggle_arm_disarm():
    if armed:
        send_command("d")
    else:
        send_command("a")

def update_arm_button():
    if armed:
        toggle_arm_button.config(text="Armed", bg=theme["armed"])
        fire_button.config(state='normal')
        stop_button.config(state='normal')
    else:
        toggle_arm_button.config(text="Disarmed", bg=theme["btn"])
        fire_button.config(state='disabled')
        stop_button.config(state='disabled')

def on_close():
    global ser, reading
    reading = False
    if ser and ser.is_open:
        ser.close()
    root.destroy()

# --- GUI Setup ---
root = tk.Tk()
root.title("DRS Pi Utility")
root.configure(bg=theme["bg"])
root.protocol("WM_DELETE_WINDOW", on_close)

# Fonts
font_label = ("Segoe UI", 10)

# COM Port Frame
top_frame = tk.Frame(root, bg=theme["bg"])
top_frame.grid(row=0, column=0, columnspan=4, padx=10, pady=10, sticky='w')

tk.Label(top_frame, text="Select COM Port:", bg=theme["bg"], fg=theme["fg"], font=font_label).pack(side=tk.LEFT)
port_dropdown = ttk.Combobox(top_frame, values=list_serial_ports(), width=20)
port_dropdown.pack(side=tk.LEFT, padx=5)
refresh_button = tk.Button(top_frame, text="Refresh", bg=theme["btn"], fg=theme["fg"], command=lambda: port_dropdown.config(values=list_serial_ports()))
refresh_button.pack(side=tk.LEFT, padx=5)
connect_button = tk.Button(top_frame, text="Connect", bg=theme["btn"], fg=theme["fg"], command=connect_serial)
connect_button.pack(side=tk.LEFT, padx=5)

# Login & Start Buttons
control_frame = tk.Frame(root, bg=theme["bg"])
control_frame.grid(row=1, column=0, columnspan=4, padx=10, pady=5, sticky='w')

login_button = tk.Button(control_frame, text="Login", width=12, bg=theme["btn"], fg=theme["fg"], command=login_sequence)
login_button.pack(side=tk.LEFT, padx=5)
start_button = tk.Button(control_frame, text="Start Client", width=12, bg=theme["btn"], fg=theme["fg"], command=start_client)
start_button.pack(side=tk.LEFT, padx=5)

# Command Buttons
button_frame = tk.Frame(root, bg=theme["bg"])
button_frame.grid(row=2, column=0, columnspan=4, padx=10, pady=5)

toggle_arm_button = tk.Button(button_frame, text="Disarmed", width=12, bg=theme["btn"], fg=theme["fg"], state='disabled', command=toggle_arm_disarm)
toggle_arm_button.pack(side=tk.LEFT, padx=5)
fire_button = tk.Button(button_frame, text="Fire", width=10, bg=theme["btn"], fg=theme["fg"], state='disabled', command=lambda: send_command("f"))
stop_button = tk.Button(button_frame, text="Stop", width=10, bg=theme["btn"], fg=theme["fg"], state='disabled', command=lambda: send_command("s"))

fire_button.pack(side=tk.LEFT, padx=5)
stop_button.pack(side=tk.LEFT, padx=5)

# Output Log
output_log = scrolledtext.ScrolledText(root, state='disabled', width=80, height=20, wrap=tk.WORD, bg=theme["log_bg"], fg=theme["log_fg"], insertbackground=theme["fg"])
output_log.grid(row=3, column=0, columnspan=4, padx=10, pady=10)

# Manual Command Input
manual_frame = tk.Frame(root, bg=theme["bg"])
manual_frame.grid(row=4, column=0, columnspan=4, padx=10, pady=5, sticky='we')

manual_entry = tk.Entry(manual_frame, width=60, bg=theme["entry"], fg=theme["fg"], insertbackground=theme["fg"])
manual_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
manual_entry.bind("<Return>", lambda event: send_manual_command())

send_button = tk.Button(manual_frame, text="Send", bg=theme["btn"], fg=theme["fg"], command=send_manual_command)
send_button.pack(side=tk.LEFT, padx=5)

root.mainloop()