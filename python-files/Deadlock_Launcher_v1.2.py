launcher_code = """
import os
import json
import shutil
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
from PIL import ImageTk, Image
import subprocess

CONFIG_FILE = "config.json"
BACKGROUND_IMAGE = "header_darkened.jpg"
ICON_PATH = "deadlock_icon.ico"

MODDED_SEARCH_PATHS = \"\"\"\
SearchPaths 
{
    Game                citadel/addons
    Mod                 citadel
    Write               citadel
    Game                citadel
    Write               core
    Mod                 core
    Game                core
}
\"\"\"

class DeadlockModLauncher:
    def __init__(self, root):
        self.root = root
        self.root.title("Deadlock Mod Launcher")
        self.root.geometry("600x440")
        self.root.resizable(False, False)

        if os.path.exists(ICON_PATH):
            try:
                self.root.iconbitmap(ICON_PATH)
            except Exception as e:
                print(f"Could not set icon: {e}")

        self.game_dir = tk.StringVar()
        self.load_last_directory()

        self.setup_background()
        self.create_widgets()

    def setup_background(self):
        if os.path.exists(BACKGROUND_IMAGE):
            bg_image = Image.open(BACKGROUND_IMAGE)
            self.bg_photo = ImageTk.PhotoImage(bg_image)
            self.bg_label = tk.Label(self.root, image=self.bg_photo)
            self.bg_label.place(x=0, y=0, relwidth=1, relheight=1)

        self.overlay = tk.Frame(self.root, bg="#000000", bd=0)
        self.overlay.place(relx=0.05, rely=0.05, relwidth=0.9, relheight=0.9)

    def create_widgets(self):
        frame = tk.Frame(self.overlay, bg="#1e1e1e")
        frame.pack(pady=10)

        tk.Label(frame, text="Deadlock Install Folder", fg="white", bg="#1e1e1e", font=("Segoe UI", 10, "bold")).pack()
        path_frame = tk.Frame(frame, bg="#1e1e1e")
        path_frame.pack(pady=5)

        path_entry = tk.Entry(path_frame, textvariable=self.game_dir, width=50)
        path_entry.pack(side=tk.LEFT, padx=5)
        tk.Button(path_frame, text="Browse", command=self.browse_directory).pack(side=tk.LEFT)

        button_frame = tk.Frame(frame, bg="#1e1e1e")
        button_frame.pack(pady=10)

        tk.Button(button_frame, text="Check & Patch gameinfo.gi", command=self.patch_gameinfo).pack(pady=5)
        tk.Button(button_frame, text="Open Addons Folder", command=self.open_addons_folder).pack(pady=5)
        tk.Button(button_frame, text="Launch Deadlock", command=self.launch_game).pack(pady=5)

        self.log = scrolledtext.ScrolledText(self.overlay, wrap=tk.WORD, height=10, width=70)
        self.log.pack(padx=10, pady=10)
        self.log.config(state=tk.DISABLED)

    def browse_directory(self):
        folder = filedialog.askdirectory()
        if folder:
            self.game_dir.set(folder)
            self.save_last_directory(folder)

    def log_message(self, msg):
        self.log.config(state=tk.NORMAL)
        self.log.insert(tk.END, msg + "\\n")
        self.log.yview(tk.END)
        self.log.config(state=tk.DISABLED)

    def save_last_directory(self, path):
        with open(CONFIG_FILE, "w") as f:
            json.dump({"deadlock_dir": path}, f)

    def load_last_directory(self):
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, "r") as f:
                try:
                    data = json.load(f)
                    self.game_dir.set(data.get("deadlock_dir", ""))
                except json.JSONDecodeError:
                    pass

    def patch_gameinfo(self):
        game_path = self.game_dir.get()
        if not game_path:
            messagebox.showerror("Error", "Please select the Deadlock install directory.")
            return

        citadel_path = os.path.join(game_path, "game", "citadel")
        addons_path = os.path.join(citadel_path, "addons")
        gameinfo_path = os.path.join(citadel_path, "gameinfo.gi")
        backup_path = gameinfo_path + ".backup"

        # Ensure addons folder exists
        if not os.path.isdir(addons_path):
            os.makedirs(addons_path)
            self.log_message(f"Created missing folder: {addons_path}")
        else:
            self.log_message(f"Addons folder exists: {addons_path}")

        if not os.path.isfile(gameinfo_path):
            self.log_message("Error: gameinfo.gi not found.")
            return

        with open(gameinfo_path, "r") as f:
            content = f.read()

        if "citadel/addons" in content:
            self.log_message("gameinfo.gi already patched.")
            return

        if not os.path.exists(backup_path):
            shutil.copyfile(gameinfo_path, backup_path)
            self.log_message("Backup of original gameinfo.gi created.")

        patched_content = self.replace_search_paths(content, MODDED_SEARCH_PATHS)
        with open(gameinfo_path, "w") as f:
            f.write(patched_content)
        self.log_message("gameinfo.gi successfully patched!")

    def replace_search_paths(self, content, replacement_block):
        import re
        pattern = re.compile(r"SearchPaths\\s*\\{[^}]+\\}", re.DOTALL)
        return pattern.sub(replacement_block, content)

    def is_gameinfo_patched(self):
        game_path = self.game_dir.get()
        gameinfo_path = os.path.join(game_path, "game", "citadel", "gameinfo.gi")
        if not os.path.isfile(gameinfo_path):
            return False
        with open(gameinfo_path, "r") as f:
            return "citadel/addons" in f.read()

    def launch_game(self):
        if not self.is_gameinfo_patched():
            self.log_message("Error: gameinfo.gi is not patched. Please patch before launching.")
            messagebox.showerror("Not Patched", "Patch gameinfo.gi before launching the game.")
            return
        try:
            subprocess.run(["start", "steam://rungameid/1422450"], shell=True)
            self.log_message("Launching Deadlock via Steam...")
        except Exception as e:
            self.log_message(f"Failed to launch Deadlock: {e}")

    def open_addons_folder(self):
        game_path = self.game_dir.get()
        addons_path = os.path.join(game_path, "game", "citadel", "addons")
        if not os.path.isdir(addons_path):
            os.makedirs(addons_path)
            self.log_message("Addons folder created.")
        try:
            os.startfile(addons_path)
            self.log_message("Opened addons folder.")
        except Exception as e:
            self.log_message(f"Failed to open addons folder: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = DeadlockModLauncher(root)
    root.mainloop()
"""

# Save the file for download
output_file = "\Users\<Username>\Desktop\Deadlock_Launcher_v1.2.py"
with open(output_file, "w") as f:
    f.write(launcher_code)

output_file
