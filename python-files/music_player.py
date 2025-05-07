import tkinter as tk
from tkinter import filedialog
import pygame
from mutagen.mp3 import MP3
from PIL import Image, ImageTk
import os

class MusicPlayer:
    def __init__(self, root):
        self.root = root
        self.root.title("Simple Music Player")
        self.root.geometry("400x500")
        self.root.resizable(False, False)

        pygame.mixer.init()

        self.track_path = None
        self.paused = False

        self.label = tk.Label(self.root, text="No track selected", wraplength=380)
        self.label.pack(pady=10)

        self.cover_canvas = tk.Canvas(self.root, width=300, height=300)
        self.cover_canvas.pack()

        self.select_btn = tk.Button(self.root, text="Select Track", command=self.load_track)
        self.select_btn.pack(pady=5)

        self.play_btn = tk.Button(self.root, text="Play", command=self.play)
        self.play_btn.pack(pady=5)

        self.pause_btn = tk.Button(self.root, text="Pause / Resume", command=self.toggle_pause)
        self.pause_btn.pack(pady=5)

        self.stop_btn = tk.Button(self.root, text="Stop", command=self.stop)
        self.stop_btn.pack(pady=5)

    def load_track(self):
        filetypes = [("Audio files", "*.mp3 *.wav")]
        path = filedialog.askopenfilename(filetypes=filetypes)
        if path:
            self.track_path = path
            audio = MP3(path)
            self.label.config(text=f"Loaded: {os.path.basename(path)}\nLength: {int(audio.info.length)} sec")
            self.load_cover(path)

    def play(self):
        if self.track_path:
            pygame.mixer.music.load(self.track_path)
            pygame.mixer.music.play()
            self.paused = False

    def stop(self):
        pygame.mixer.music.stop()

    def toggle_pause(self):
        if self.paused:
            pygame.mixer.music.unpause()
        else:
            pygame.mixer.music.pause()
        self.paused = not self.paused

    def load_cover(self, path):
        default_img = "cassette.png"
        if os.path.exists(default_img):
            img = Image.open(default_img)
            img = img.resize((300, 300))
            self.album_img = ImageTk.PhotoImage(img)
            self.cover_canvas.create_image(0, 0, anchor=tk.NW, image=self.album_img)

if __name__ == "__main__":
    root = tk.Tk()
    app = MusicPlayer(root)
    root.mainloop()
