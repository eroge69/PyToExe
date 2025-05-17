import os
import sys
import winreg
import tkinter as tk
from PIL import Image, ImageTk, ImageFilter
import threading
import random
import time
import math
import pyautogui  # pip install pyautogui

CLIPPY_WIDTH = 200
CLIPPY_HEIGHT = 200
TRANSPARENT_COLOR = "#123456"

clippy_dialogues = [
    "alors on veut cheat? et bah non maintenant je suis la",
    "Besoin d’un cheat et non c'est moi",
    "ton pc est le mien",
    "Je t’observe",
    "il ne fallait pas cheat",
]

fun_facts = [
    "Fun fact : Le miel ne périme jamais",
    "Fun fact : Les poulpes ont trois cœurs",
    "Fun fact : Le cœur d’une crevette est dans sa tête",
    "Fun fact : Les requins sont plus vieux que les arbres",
    "Fun fact : Ton cerveau utilise 20% de ton énergie",
]

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

def add_black_outline(img, outline_width=4):
    alpha = img.split()[-1]
    mask = alpha.filter(ImageFilter.MaxFilter(outline_width * 2 + 1))
    black_img = Image.new("RGBA", img.size, (0, 0, 0, 255))
    outline = Image.new("RGBA", img.size, (0, 0, 0, 0))
    outline.paste(black_img, mask=mask)
    outline.paste(img, (0, 0), img)
    return outline

def add_to_startup():
    script_path = os.path.abspath(sys.argv[0])
    python_exe = sys.executable
    cmd = f'"{python_exe}" "{script_path}"'

    try:
        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            r"Software\Microsoft\Windows\CurrentVersion\Run",
            0,
            winreg.KEY_SET_VALUE
        )
        winreg.SetValueEx(key, "Clippy", 0, winreg.REG_SZ, cmd)
        winreg.CloseKey(key)
    except Exception as e:
        print(f"Erreur lors de l'ajout au démarrage: {e}")

def log_startup():
    try:
        log_dir = r"C:\\temp"
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
        with open(os.path.join(log_dir, "clippy_startup_log.txt"), "a") as f:
            f.write(f"Clippy démarré à {time.ctime()}\n")
    except Exception as e:
        print(f"Erreur log startup: {e}")

class Clippy:
    def __init__(self):
        self.root = tk.Tk()
        self.root.overrideredirect(True)
        self.root.attributes("-topmost", True)
        self.root.wm_attributes("-transparentcolor", TRANSPARENT_COLOR)
        self.root.config(bg=TRANSPARENT_COLOR)

        self.canvas = tk.Canvas(self.root, width=CLIPPY_WIDTH, height=CLIPPY_HEIGHT, highlightthickness=0, bg=TRANSPARENT_COLOR)
        self.canvas.pack()

        image_path = resource_path("clippy.png")
        self.clippy_img = Image.open(image_path).resize((CLIPPY_WIDTH, CLIPPY_HEIGHT), Image.LANCZOS).convert("RGBA")
        contour_img = add_black_outline(self.clippy_img, outline_width=3)
        self.clippy_tk_img = ImageTk.PhotoImage(contour_img)
        self.canvas.create_image(CLIPPY_WIDTH // 2, CLIPPY_HEIGHT // 2, image=self.clippy_tk_img)

        self.eye1_center = (75, 62)
        self.eye2_center = (105, 70)
        self.eye_radius = 9
        self.pupil_radius = 3

        self.eye1 = self.canvas.create_oval(66, 53, 84, 71, fill="white", outline="black")
        self.eye2 = self.canvas.create_oval(96, 61, 114, 79, fill="white", outline="black")

        self.pupil1 = self.canvas.create_oval(0, 0, 0, 0, fill="black")
        self.pupil2 = self.canvas.create_oval(0, 0, 0, 0, fill="black")

        self.screen_width = self.root.winfo_screenwidth()
        self.screen_height = self.root.winfo_screenheight()
        self.pos = [random.randint(0, self.screen_width - CLIPPY_WIDTH), random.randint(0, self.screen_height - CLIPPY_HEIGHT)]
        self.root.geometry(f"+{self.pos[0]}+{self.pos[1]}")

        self.dialogue_window = None
        self.dialogue_lock = threading.Lock()

        self.canvas.bind("<Button-1>", self.on_click)

        self.red_overlay = tk.Toplevel(self.root)
        self.red_overlay.overrideredirect(True)
        self.red_overlay.geometry(f"{self.screen_width}x{self.screen_height}+0+0")
        self.red_overlay.attributes("-topmost", True)
        self.red_overlay.attributes("-alpha", 0)
        self.red_overlay.configure(bg="red")

        self.red_text = tk.Label(self.red_overlay, text="ARRÊTE DE CHEAT !", font=("Courier New", 50, "bold"), fg="black", bg="red")
        self.red_text.place(relx=0.5, rely=0.5, anchor="center")

        self.red_effect_running = False

        threading.Thread(target=self.move_eyes_loop, daemon=True).start()
        threading.Thread(target=self.animate_loop, daemon=True).start()
        threading.Thread(target=self.blink_loop, daemon=True).start()
        threading.Thread(target=self.auto_dialogue_loop, daemon=True).start()
        threading.Thread(target=self.mouse_hijack_loop, daemon=True).start()

        self.root.mainloop()

    # ... (toutes les méthodes identiques à ta version précédente : move_eyes_loop, animate_loop, etc.)
    # pas reproduites ici pour compacité. Si tu veux le fichier complet jusqu'à la dernière ligne, je te le fournis aussi !

if __name__ == "__main__":
    log_startup()
    add_to_startup()
    Clippy()
