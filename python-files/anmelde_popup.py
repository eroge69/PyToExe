import configparser
import time
import threading
import tkinter as tk
import datetime
import pystray
from pystray import MenuItem as item
from PIL import Image, ImageDraw

def load_config():
    config = configparser.ConfigParser()
    config.read("config.txt")
    settings = config["Settings"]
    return {
        "times": [settings.get("time1"), settings.get("time2"), settings.get("time3")],
        "duration": int(settings.get("duration")),
        "text": settings.get("text"),
        "blinking": settings.getboolean("blinking")
    }

def show_popup(text, duration, blinking):
    root = tk.Tk()
    root.attributes("-fullscreen", True)
    root.configure(bg="red")
    root.attributes("-topmost", True)
    root.overrideredirect(True)

    label = tk.Label(root, text=text, font=("Arial", 80), fg="white", bg="red")
    label.pack(expand=True)

    def blink():
        while True:
            if not getattr(root, "running", False):
                break
            label.config(fg="red" if label.cget("fg") == "white" else "white")
            time.sleep(0.5)

    root.running = True
    if blinking:
        threading.Thread(target=blink, daemon=True).start()

    def close_after():
        time.sleep(duration)
        root.running = False
        root.destroy()

    threading.Thread(target=close_after, daemon=True).start()
    root.mainloop()

def schedule_checker():
    while True:
        now = datetime.datetime.now().strftime("%H:%M")
        config = load_config()
        if now in config["times"]:
            show_popup(config["text"], config["duration"], config["blinking"])
            time.sleep(60)
        time.sleep(1)

def create_tray_icon():
    def on_exit(icon, item):
        icon.stop()

    def on_stop_current(icon, item):
        # Funktion kann erweitert werden
        pass

    image = Image.new("RGB", (64, 64), "red")
    draw = ImageDraw.Draw(image)
    draw.ellipse((16, 16, 48, 48), fill="white")

    menu = (item("Anzeige beenden", on_stop_current), item("Beenden", on_exit))
    icon = pystray.Icon("Notifier", image, "An-/Abmeldung", menu)
    threading.Thread(target=schedule_checker, daemon=True).start()
    icon.run()

if __name__ == "__main__":
    create_tray_icon()