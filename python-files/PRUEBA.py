import tkinter as tk
from tkinter import filedialog, messagebox
import os
import json
import subprocess

CONFIG_FILE = "obs_config.json"

# Posibles rutas por defecto
DEFAULT_PATHS = [
    r"C:\Program Files\obs-studio\bin\64bit\obs64.exe",
    r"C:\Program Files (x86)\obs-studio\bin\64bit\obs64.exe"
]

class OBSLauncherApp:
    def __init__(self, root):
        self.root = root
        self.root.title("OBS Launcher")
        self.root.geometry("420x300")
        self.root.resizable(False, False)

        self.obs_path = ""

        # Cargar configuración si existe, o intentar detectar automáticamente
        self.load_config_or_detect()

        # Título
        tk.Label(root, text="OBS Launcher", font=("Arial", 16, "bold")).pack(pady=10)

        # Texto de ruta
        tk.Label(root, text="Ruta actual de OBS:", font=("Arial", 10)).pack()
        self.label_ruta = tk.Label(root, text=self.obs_path or "No seleccionada", wraplength=380, fg="blue")
        self.label_ruta.pack(pady=5)

        # Botón para seleccionar carpeta
        self.btn_seleccionar = tk.Button(
            root, text="Seleccionar carpeta de OBS", command=self.seleccionar_obs,
            font=("Arial", 11), padx=10, pady=5
        )
        self.btn_seleccionar.pack(pady=10)

        # BOTÓN START para iniciar OBS
        self.btn_start = tk.Button(
            root, text="START", command=self.iniciar_obs,
            font=("Arial", 14, "bold"), bg="green", fg="white", width=20, height=2
        )
        self.btn_start.pack(pady=20)

    def seleccionar_obs(self):
        carpeta = filedialog.askdirectory(title="Selecciona la carpeta donde está OBS")
        if carpeta:
            ruta_obs = os.path.join(carpeta, "obs64.exe")
            if os.path.isfile(ruta_obs):
                self.obs_path = ruta_obs
                self.label_ruta.config(text=self.obs_path)
                self.save_config()
            else:
                messagebox.showerror("Error", "No se encontró 'obs64.exe' en la carpeta seleccionada.")

    def iniciar_obs(self):
        if not self.obs_path or not os.path.isfile(self.obs_path):
            messagebox.showerror("Error", "No se ha seleccionado una ruta válida de OBS.")
            return
        try:
            cwd = os.path.dirname(self.obs_path)
            subprocess.Popen(self.obs_path, cwd=cwd)
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo iniciar OBS:\n{e}")

    def save_config(self):
        with open(CONFIG_FILE, "w") as f:
            json.dump({"obs_path": self.obs_path}, f)

    def load_config_or_detect(self):
        # Intenta cargar config guardada
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, "r") as f:
                data = json.load(f)
                self.obs_path = data.get("obs_path", "")
                if os.path.isfile(self.obs_path):
                    return

        # Si no hay config válida, intenta buscar automáticamente
        for path in DEFAULT_PATHS:
            if os.path.isfile(path):
                self.obs_path = path
                self.save_config()
                break

if __name__ == "__main__":
    root = tk.Tk()
    app = OBSLauncherApp(root)
    root.mainloop()