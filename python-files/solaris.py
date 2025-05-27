import tkinter as tk
from tkinter import ttk, messagebox
import threading
import time
import subprocess
import sys
import os
import tkinter.font as font

class SplashScreen(tk.Toplevel):
    def __init__(self, parent, text="Solaris Engine"):
        super().__init__(parent)  # Toujours appeler super().__init__ d'abord
        self.overrideredirect(True)

        width = 400
        height = 200
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f"{width}x{height}+{x}+{y}")

        label = tk.Label(self, text=text, font=("Arial", 36, "bold"))
        label.pack(expand=True)

        # Ajout du label de version en bas à droite
        ver_font = font.Font(family="Comic Sans MS", size=9, slant="italic")
        splashver_label = tk.Label(self, text="v0.1 2008 Release", font=ver_font, fg="gray50", bg=self["bg"])
        splashver_label.place(relx=1.0, rely=1.0, anchor="se", x=-10, y=-10)

class MenuApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Solaris Engine - Menu")
        self.wm_iconbitmap("logo.ico")
        self.window_width = 1280
        self.window_height = 720
        x = (self.winfo_screenwidth() // 2) - (self.window_width // 2)
        y = (self.winfo_screenheight() // 2) - (self.window_height // 2)
        self.geometry(f"{self.window_width}x{self.window_height}+{x}+{y}")
        self.resizable(False, False)

        self.splash = SplashScreen(self, "Solaris Engine")
        self.withdraw()
        threading.Thread(target=self.delayed_load).start()

    def delayed_load(self):
        time.sleep(3)
        self.after(0, self.show_menu)

    def show_menu(self):
        self.splash.destroy()
        self.deiconify()

        # Taskbar
        taskbar = tk.Frame(self, bg="gray20", height=40)
        taskbar.pack(fill="x", side="top")

        label = tk.Label(taskbar, text="Solaris Engine", fg="white", bg="gray20", font=("Arial", 14, "bold"))
        label.pack(side="left", padx=10)

        btn_editer = ttk.Button(taskbar, text="Éditer", command=self.open_editor)
        btn_editer.pack(side="left", padx=10)

        # Contenu principal
        content = tk.Frame(self, bg="white")
        content.pack(expand=True, fill="both")

        title_frame = tk.Frame(content, bg="white")
        title_frame.pack(pady=20)

        label_title = tk.Label(title_frame, text="Solaris Engine", font=("Arial", 24, "bold"), bg="white")
        label_title.pack(side="left")

        label_version = tk.Label(title_frame, text="v0.1 2008 Release", font=("Arial", 12), fg="gray50", bg="white")
        label_version.pack(side="left", padx=(5, 0))

        bottom_frame = tk.Frame(content, bg="white")
        bottom_frame.pack(side="bottom", fill="x", padx=10, pady=10)

        patch_title = tk.Label(bottom_frame, text="Mises à Jours 2008 Release:", font=("Arial", 14, "bold"), bg="white")
        patch_title.pack(anchor="w")

        patch_text = tk.Text(bottom_frame, height=5, bg="white", relief="flat", wrap="word")
        patch_text.pack(fill="x")
        patch_text.insert("1.0", "Taskbar de côntrolle créé\nDernier bouton crée : Sauvegarder\nEn cours de développement sur la 2d")
        patch_text.config(state="disabled")

        desc = tk.Label(bottom_frame, text="Solaris Engine 2008-2025",
                        font=("Arial", 12), bg="white", wraplength=1200, justify="left")
        desc.pack(anchor="w", pady=(5, 0))

    def open_editor(self):
        # Lancer le splash + l'éditeur dans un thread pour garder le flow propre
        def start_editor():
            splash = SplashScreen(self, "Solaris Editor")
            splash.update()
            time.sleep(2)  # Simule le chargement
            splash.destroy()
            subprocess.Popen([sys.executable, "editor.py"])
            self.destroy()  # Ferme la fenêtre menu uniquement après splash

        threading.Thread(target=start_editor).start()

if __name__ == "__main__":
    app = MenuApp()
    app.mainloop()
