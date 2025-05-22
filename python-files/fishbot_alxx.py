import tkinter as tk
import threading
import time
import pytesseract
import pyscreenshot as ImageGrab
import winsound
import keyboard
import pyautogui

# Configurează calea către tesseract dacă e nevoie
# pytesseract.pytesseract.tesseract_cmd = r"D:\Tesserect OCR Local\tesseract.exe"

running = False
start_time = None
fish_count = 0
fish_log = []

WINDOW_NAME = "[GTA5.exe]: RAGE Multiplayer"
CAPTCHA_KEYWORDS = ["Tasteaza codul", "identificat ca fiind AFK"]


def beep_alert():
    winsound.Beep(1000, 800)  # 1000Hz pentru 800ms


def detect_captcha():
    img = ImageGrab.grab()
    text = pytesseract.image_to_string(img, lang='ron')
    for word in CAPTCHA_KEYWORDS:
        if word in text:
            beep_alert()
            return True
    return False


def monitor():
    global running, fish_count, start_time
    while running:
        if detect_captcha():
            app.update_status("CAPTCHA detectat! Script oprit.")
            running = False
            return

        fish_count += 1  # Simulăm că a prins un pește
        now = time.time()
        elapsed = now - start_time
        rate = fish_count / (elapsed / 60) if elapsed > 0 else 0

        log = f"Pește #{fish_count} | Timp: {int(elapsed)}s | Rată: {rate:.2f}/min"
        fish_log.append(log)
        app.update_stats(log)
        time.sleep(3)  # Simulare delay între pești


class App:
    def __init__(self, root):
        self.root = root
        root.title("FishBot - The Alxx Creation")

        self.status = tk.Label(root, text="Status: Inactiv", fg="red")
        self.status.pack()

        self.stats = tk.Text(root, height=15, width=50)
        self.stats.pack()

        self.footer = tk.Label(root, text="The Alxx Creation", fg="gray")
        self.footer.pack(side="bottom")

        self.check_key()

    def check_key(self):
        if keyboard.is_pressed('9'):
            self.toggle()
            time.sleep(0.5)  # Anti-rebound
        self.root.after(100, self.check_key)

    def toggle(self):
        global running, start_time, fish_count
        running = not running
        if running:
            self.update_status("Rulează")
            fish_count = 0
            start_time = time.time()
            threading.Thread(target=monitor, daemon=True).start()
        else:
            self.update_status("Inactiv")

    def update_status(self, text):
        self.status.config(text=f"Status: {text}", fg="green" if running else "red")

    def update_stats(self, log):
        self.stats.insert(tk.END, log + "\n")
        self.stats.see(tk.END)


root = tk.Tk()
app = App(root)
root.mainloop()
