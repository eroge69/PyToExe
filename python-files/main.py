import tkinter as tk
from tkinter import messagebox
import threading
import pyautogui
from PIL import ImageGrab
import keyboard
import sys
import time
import os
import shutil

# Lizenzschlüssel
VALID_KEY = "Ocean-market"
TEMP_DIR = "temp_data"
shooting = False

# Bildschirmmitte berechnen
screen_width, screen_height = pyautogui.size()
center_x, center_y = screen_width // 2, screen_height // 2

# Funktion zum Anzeigen des Lizenzfensters
def show_license_window():
    license_win = tk.Tk()
    license_win.title("🔐 Lizenzüberprüfung")
    license_win.geometry("500x250")
    license_win.configure(bg="#1e1e2f")

    # Titel Label
    tk.Label(license_win, text="🛡 Lizenzschlüssel eingeben", font=("Segoe UI", 18, "bold"),
             fg="#00ffff", bg="#1e1e2f").grid(row=0, column=0, columnspan=2, pady=30)

    # Eintragsfeld für den Lizenzschlüssel
    key_entry = tk.Entry(license_win, font=("Segoe UI", 14), width=30, bg="#2a2a3d", fg="white", insertbackground="white", show="*")
    key_entry.grid(row=1, column=0, padx=10, pady=10)

    # Funktion zum Umschalten der Sichtbarkeit des Lizenzschlüssels
    def toggle_password():
        if key_entry.cget("show") == "*":
            key_entry.config(show="")
            eye_button.update_eye(True)  # Auge zeigt Text an (offenes Auge)
        else:
            key_entry.config(show="*")
            eye_button.update_eye(False)  # Auge verbirgt Text (geschlossenes Auge)

    # EyeButton - Der Button für das Auge
    eye_button = EyeButton(license_win, toggle_password)
    eye_button.grid(row=1, column=1, padx=10)

    # Funktion zur Validierung des Lizenzschlüssels
    def validate_key():
        if key_entry.get() == VALID_KEY:
            license_win.destroy()  # Schließt das Lizenzfenster
            open_main_ui()  # Öffnet das Hauptfenster
        else:
            messagebox.showerror("Fehler", "❌ Ungültiger Lizenzschlüssel.")

    # Weiter-Button
    tk.Button(license_win, text="Weiter", font=("Segoe UI", 12, "bold"), bg="#00bcd4", fg="white",
              width=20, command=validate_key, relief="flat", cursor="hand2").grid(row=2, column=0, columnspan=2, pady=20)

    license_win.mainloop()

# Hauptfenster
def open_main_ui():
    global root, status_label, color_label

    root = tk.Tk()
    root.title("🎯 AutoShooter PRO")
    root.geometry("900x650")
    root.configure(bg="#121212")
    root.protocol("WM_DELETE_WINDOW", panic_exit)

    tk.Label(root, text="AutoShooter PRO", font=("Segoe UI", 28, "bold"), fg="#00ffff", bg="#121212").pack(pady=30)

    status_label = tk.Label(root, text="Status: ❌ Inaktiv", font=("Segoe UI", 16), fg="#ff5252", bg="#121212")
    status_label.pack(pady=10)

    color_label = tk.Label(root, text="Pixel-Farbe: R=0 G=0 B=0", font=("Segoe UI", 14), fg="#aaaaaa", bg="#121212")
    color_label.pack(pady=10)

    button_frame = tk.Frame(root, bg="#121212")
    button_frame.pack(pady=40)

    def make_btn(text, bg, cmd):
        return tk.Button(button_frame, text=text, font=("Segoe UI", 14), width=25, bg=bg, fg="white",
                         relief="flat", cursor="hand2", command=cmd)

    make_btn("▶ Start", "#00c853", start_shooting).grid(row=0, column=0, padx=20, pady=10)
    make_btn("■ Stop", "#d50000", stop_shooting).grid(row=0, column=1, padx=20, pady=10)
    make_btn("🚨 Panikmodus (F12)", "#ff9100", panic_exit).grid(row=1, column=0, columnspan=2, pady=10)
    make_btn("🧹 Alle Spuren löschen", "#546e7a", clear_all_traces_and_exit).grid(row=2, column=0, columnspan=2, pady=10)

    threading.Thread(target=monitor_f12, daemon=True).start()
    root.mainloop()

# EyeButton - Der Button, der das Auge darstellt (Kein Rand um das Auge)
class EyeButton(tk.Canvas):
    def __init__(self, parent, toggle_func, *args, **kwargs):
        super().__init__(parent, width=50, height=50, bg="#1e1e2f", *args, **kwargs)
        self.toggle_func = toggle_func
        self.eye_id = self.create_oval(5, 5, 45, 45, fill="red")  # Nur das Auge ohne Rand
        self.pupil_id = self.create_oval(20, 20, 30, 30, fill="black")  # Pupille innen
        self.update_eye(False)  # Standardmäßig verborgen

        self.bind("<Button-1>", self.toggle_visibility)

    def toggle_visibility(self, event):
        self.toggle_func()

    def update_eye(self, visible):
        """ Update the eye's appearance based on visibility """
        if visible:
            self.itemconfig(self.eye_id, fill="green")  # Offenes Auge
        else:
            self.itemconfig(self.eye_id, fill="red")  # Geschlossenes Auge

# Rot-Erkennungs-Logik
def is_red_shade(r, g, b):
    # Rot muss dominieren, aber gewisse Helligkeit darf sein
    if r > 90 and r > g + 35 and r > b + 35:
        return True
    return False

# Mehrere Pixel rund um die Mitte prüfen (5x5)
def check_center_pixels():
    for dx in range(-2, 3):
        for dy in range(-2, 3):
            x = center_x + dx
            y = center_y + dy
            pixel = ImageGrab.grab().getpixel((x, y))
            r, g, b = pixel
            if is_red_shade(r, g, b):
                return r, g, b, True
    return 0, 0, 0, False

# Shooter-Funktion
def check_pixel():
    global shooting
    while shooting:
        r, g, b, match = check_center_pixels()
        color_label.config(text=f"Pixel-Farbe: R={r} G={g} B={b}")
        if match:
            pyautogui.click()
        time.sleep(0.01)

# Start
def start_shooting():
    global shooting
    shooting = True
    status_label.config(text="Status: ✅ Aktiv", fg="#00e676")
    threading.Thread(target=check_pixel, daemon=True).start()

# Stop
def stop_shooting():
    global shooting
    shooting = False
    status_label.config(text="Status: ❌ Inaktiv", fg="#ff5252")

# Panik-Funktion
def panic_exit():
    try:
        root.destroy()
    except:
        pass
    sys.exit()

# F12 global überwachen
def monitor_f12():
    keyboard.add_hotkey("f12", panic_exit)

# Spuren löschen
def clear_all_traces_and_exit():
    confirm = messagebox.askyesno("Sicher?", "Willst du wirklich alle Spuren löschen und das Programm beenden?")
    if confirm:
        try:
            for path in ["temp_data", "log.txt"]:
                if os.path.isdir(path):
                    shutil.rmtree(path)
                elif os.path.isfile(path):
                    os.remove(path)
            messagebox.showinfo("Fertig", "Alle Daten wurden gelöscht.")
        except Exception as e:
            messagebox.showerror("Fehler", f"Fehler beim Löschen: {e}")
        finally:
            panic_exit()

# Startpunkt
os.makedirs(TEMP_DIR, exist_ok=True)
show_license_window()
