import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
import requests
import time
import os
from urllib.parse import urlparse

class DownloadApp:
    def __init__(self, root):
        self.root = root
        self.root.title("PY Dani's DownloadR")
        self.root.geometry("500x300")
        self.root.resizable(False, False)

        # UI Elements
        self.url_label = tk.Label(root, text="Download URL:")
        self.url_label.pack(pady=5)

        self.url_entry = tk.Entry(root, width=60)
        self.url_entry.pack(pady=5)

        self.choose_button = tk.Button(root, text="Choose Folder to Save In", command=self.choose_folder)
        self.choose_button.pack(pady=5)

        self.location_label = tk.Label(root, text="No folder selected")
        self.location_label.pack(pady=5)

        self.download_button = tk.Button(root, text="Start Download", command=self.start_download_thread)
        self.download_button.pack(pady=10)

        self.progress = ttk.Progressbar(root, orient='horizontal', length=400, mode='determinate')
        self.progress.pack(pady=5)

        self.status_label = tk.Label(root, text="")
        self.status_label.pack()

        self.speed_label = tk.Label(root, text="")
        self.speed_label.pack()

        self.save_folder = None
        self.full_file_path = None

    def choose_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.save_folder = folder
            self.location_label.config(text=self.save_folder)

    def start_download_thread(self):
        thread = threading.Thread(target=self.download_file)
        thread.start()

    def download_file(self):
        url = self.url_entry.get().strip()
        if not url:
            messagebox.showerror("Error", "Please enter a URL.")
            return
        if not self.save_folder:
            messagebox.showerror("Error", "Please choose a folder.")
            return

        filename = os.path.basename(urlparse(url).path)
        if not filename:
            messagebox.showerror("Error", "Could not extract filename from URL.")
            return

        self.full_file_path = os.path.join(self.save_folder, filename)

        try:
            response = requests.get(url, stream=True)
            total_length = int(response.headers.get('content-length', 0))
            self.status_label.config(text=f"Downloading: {filename} ({self.size_fmt(total_length)})")
            self.progress["maximum"] = total_length

            with open(self.full_file_path, "wb") as f:
                dl = 0
                start_time = time.time()
                for data in response.iter_content(chunk_size=4096):
                    f.write(data)
                    dl += len(data)
                    elapsed = time.time() - start_time
                    speed = dl / elapsed if elapsed > 0 else 0
                    percent = (dl / total_length) * 100 if total_length else 0

                    # Update UI
                    self.progress["value"] = dl
                    self.speed_label.config(text=f"Speed: {self.size_fmt(speed)}/s | {percent:.2f}%")
                    self.root.update_idletasks()

            self.status_label.config(text="Download complete!")
            self.speed_label.config(text="Saved to: " + self.full_file_path)
        except Exception as e:
            messagebox.showerror("Error", f"Download failed: {str(e)}")

    def size_fmt(self, num, suffix="B"):
        for unit in ["", "K", "M", "G", "T"]:
            if abs(num) < 1024.0:
                return f"{num:.2f} {unit}{suffix}"
            num /= 1024.0
        return f"{num:.2f} P{suffix}"

if __name__ == "__main__":
    root = tk.Tk()
    app = DownloadApp(root)
    root.mainloop()
