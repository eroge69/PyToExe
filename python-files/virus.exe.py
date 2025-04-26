import tkinter as tk
from PIL import Image, ImageSequence
import ctypes
import os
import time
import requests
from io import BytesIO
import threading

class Virus:
    def __init__(self, master):
        self.master = master
        master.title("Albanian Virus")
        master.geometry("600x600")

        self.count = 0
        self.label = tk.Label(master, text=str(self.count), font=("GothamBold", 24))
        self.label.grid(row=0, column=0, pady=(20, 10))

        self.notsigma = tk.Label(master, text="Reach 1000 or virus comes", font=("GothamBold", 24))
        self.notsigma.grid(row=1, column=0, pady=(20, 10))

        self.decrement_btn = tk.Button(master, text="Decrement", font=("GothamBold", 24), command=self.decrement)
        self.decrement_btn.grid(row=2, column=0, padx=(20, 10))

        self.increment_btn = tk.Button(master, text="Increment", font=("GothamBold", 24), command=self.increment)
        self.increment_btn.grid(row=3, column=0, padx=(20, 10))

        # Start updating the desktop background with the GIF from the URL
        self.update_desktop_background("https://media.tenor.com/AN2p1JhF0akAAAAM/mewing.gif")

    def increment(self):
        self.count += 1
        self.label.config(text=str(self.count))

    def decrement(self):
        self.count -= 1
        self.label.config(text=str(self.count))

    def update_desktop_background(self, gif_url):
        # Download the GIF from the URL
        response = requests.get(gif_url)
        gif = Image.open(BytesIO(response.content))

        # Extract frames and save them temporarily
        frames = []
        for i, frame in enumerate(ImageSequence.Iterator(gif)):
            frame_path = f"frame_{i}.bmp"  # Save as BMP (Windows wallpaper format)
            frame.convert("RGB").save(frame_path)
            frames.append(frame_path)

        # Function to set the desktop wallpaper
        def set_wallpaper(image_path):
            ctypes.windll.user32.SystemParametersInfoW(20, 0, image_path, 0)

        # Cycle through frames and set them as wallpaper
        def cycle_frames():
            while True:
                for frame_path in frames:
                    set_wallpaper(os.path.abspath(frame_path))
                    time.sleep(0.1)  # Adjust delay for frame rate

        # Start cycling frames in a separate thread
        threading.Thread(target=cycle_frames, daemon=True).start()


root = tk.Tk()
app = Virus(root)
root.mainloop()