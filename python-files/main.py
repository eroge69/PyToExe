import os
import zipfile
import tarfile
import threading
import tkinter as tk
from tkinter import filedialog, messagebox

FONT = ("Segoe UI", 12)
BG_COLOR = "#f5f5dc"  # jasnopiaskowy

class UnpackerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Rozpakowywacz backupów (.zip / .tar.gz)")
        self.root.geometry("420x200")
        self.root.configure(bg=BG_COLOR)
        self.root.resizable(False, False)

        self.path_var = tk.StringVar()
        self.create_widgets()

    def create_widgets(self):
        tk.Label(self.root, text="Ścieżka do folderu z backupami:", font=FONT, bg=BG_COLOR).pack(pady=10)

        self.path_entry = tk.Entry(self.root, textvariable=self.path_var, width=35, font=FONT)
        self.path_entry.pack(pady=(0, 20))

        btn_frame = tk.Frame(self.root, bg=BG_COLOR)
        btn_frame.pack()

        browse_btn = tk.Button(btn_frame, text="Wybierz folder...", command=self.browse_folder, font=FONT, width=15)
        browse_btn.pack(side=tk.LEFT, padx=(0, 40))  

        self.ok_button = tk.Button(btn_frame, text="OK", command=self.on_ok, font=FONT, width=10)
        self.ok_button.pack(side=tk.LEFT)

        self.status_label = tk.Label(self.root, text="", font=FONT, bg=BG_COLOR)
        self.status_label.pack(pady=20)

        self.loading_label = tk.Label(self.root, text="", font=FONT, bg=BG_COLOR)
        self.loading_label.pack(pady=10)

    def browse_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.path_var.set(folder)

    def on_ok(self):
        path = self.path_var.get().strip().replace('"', '')
        if not os.path.isdir(path):
            messagebox.showerror("Błąd", "Podana ścieżka jest nieprawidłowa.")
            return

        self.ok_button.config(state=tk.DISABLED)
        self.status_label.config(text="Rozpoczynam rozpakowywanie...")
        self.loading_label.config(text="⏳ Proszę czekać, trwa rozpakowywanie...")

        threading.Thread(target=self.unpack_files, args=(path,), daemon=True).start()

    def unpack_files(self, folder_path):
        unpacked_count = 0

        for file_name in os.listdir(folder_path):
            file_path = os.path.join(folder_path, file_name)
            if not os.path.isfile(file_path):
                continue

            try:
                if file_name.lower().endswith(".zip"):
                    with zipfile.ZipFile(file_path, 'r') as archive:
                        archive.extractall(folder_path)
                    os.remove(file_path)
                    unpacked_count += 1

                elif file_name.lower().endswith((".tar.gz", ".tar")):
                    with tarfile.open(file_path, 'r:*') as archive:
                        archive.extractall(folder_path)
                    os.remove(file_path)
                    unpacked_count += 1

            except Exception as e:
                print(f"Nie udało się rozpakować {file_name}: {e}")

        self.loading_label.config(text="")
        self.status_label.config(text=f"✅ Rozpakowano {unpacked_count} plików.")
        self.ok_button.config(state=tk.NORMAL)

def main():
    root = tk.Tk()
    app = UnpackerApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
