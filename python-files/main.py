
import tkinter as tk
from tkinter import filedialog
import subprocess
import threading

class TubeLiveApp:
    def __init__(self, root):
        self.root = root
        self.root.title("TubeLive Simple")
        self.file_path = ""
        self.proc = None

        tk.Label(root, text="Judul Live").grid(row=0, column=0)
        self.title_entry = tk.Entry(root, width=40)
        self.title_entry.grid(row=0, column=1, columnspan=2)

        tk.Label(root, text="Stream Key").grid(row=1, column=0)
        self.key_entry = tk.Entry(root, width=40)
        self.key_entry.grid(row=1, column=1, columnspan=2)

        tk.Label(root, text="File Video").grid(row=2, column=0)
        self.file_label = tk.Label(root, text="Belum dipilih", width=30, anchor='w')
        self.file_label.grid(row=2, column=1)
        tk.Button(root, text="Pilih File", command=self.pilih_file).grid(row=2, column=2)

        self.start_btn = tk.Button(root, text="Mulai Streaming", command=self.mulai_stream)
        self.start_btn.grid(row=3, column=0, columnspan=2)

        self.stop_btn = tk.Button(root, text="Stop Streaming", command=self.stop_stream)
        self.stop_btn.grid(row=3, column=2)

        self.log_text = tk.Text(root, height=15, width=60)
        self.log_text.grid(row=4, column=0, columnspan=3)

    def pilih_file(self):
        self.file_path = filedialog.askopenfilename()
        self.file_label.config(text=self.file_path.split("/")[-1])

    def mulai_stream(self):
        if not self.file_path or not self.key_entry.get():
            self.log("File dan stream key wajib diisi.")
            return

        cmd = [
            "ffmpeg",
            "-re",
            "-i", self.file_path,
            "-c:v", "libx264",
            "-preset", "veryfast",
            "-maxrate", "2500k",
            "-bufsize", "5000k",
            "-pix_fmt", "yuv420p",
            "-g", "50",
            "-c:a", "aac",
            "-b:a", "128k",
            "-ar", "44100",
            "-f", "flv",
            f"rtmp://a.rtmp.youtube.com/live2/{self.key_entry.get()}"
        ]

        def run():
            self.proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True)
            for line in self.proc.stdout:
                self.log(line)

        threading.Thread(target=run, daemon=True).start()

    def stop_stream(self):
        if self.proc:
            self.proc.terminate()
            self.proc = None
            self.log("Streaming dihentikan.")

    def log(self, msg):
        self.log_text.insert(tk.END, msg + "\n")
        self.log_text.see(tk.END)

if __name__ == "__main__":
    root = tk.Tk()
    app = TubeLiveApp(root)
    root.mainloop()
