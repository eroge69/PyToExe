import tkinter as tk
from tkinter import filedialog, ttk
import os
import moviepy.editor as mp

class VideoToAudioConverter(tk.Tk):
    def __init__(self):
        super().__init__()

        # Configure window
        self.title("Video to Audio Converter 🎵")
        self.geometry("600x400")
        self.configure(bg="#FFE5E5")

        # Create main frame
        self.main_frame = tk.Frame(self, bg="#FFF0F5")
        self.main_frame.pack(pady=20, padx=20, fill="both", expand=True)

        # Title label
        self.title_label = tk.Label(
            self.main_frame,
            text="Video to Audio Converter 🎥 ➜ 🎵",
            font=("Arial", 24, "bold"),
            fg="#FF69B4",
            bg="#FFF0F5"
        )
        self.title_label.pack(pady=20)

        # Select video button
        self.select_button = tk.Button(
            self.main_frame,
            text="Select Video File 📁",
            command=self.select_video,
            font=("Arial", 16),
            bg="#FF69B4",
            fg="white",
            relief="raised"
        )
        self.select_button.pack(pady=15)

        # Selected file label
        self.file_label = tk.Label(
            self.main_frame,
            text="No file selected",
            font=("Arial", 14),
            fg="#666666",
            bg="#FFF0F5"
        )
        self.file_label.pack(pady=10)

        # Convert button
        self.convert_button = tk.Button(
            self.main_frame,
            text="Convert to Audio 🎵",
            command=self.convert_video,
            font=("Arial", 16),
            bg="#87CEEB",
            fg="white",
            relief="raised"
        )
        self.convert_button.pack(pady=15)

        # Status label
        self.status_label = tk.Label(
            self.main_frame,
            text="",
            font=("Arial", 14),
            fg="#666666",
            bg="#FFF0F5"
        )
        self.status_label.pack(pady=10)

        self.video_path = None

    def select_video(self):
        self.video_path = filedialog.askopenfilename(
            filetypes=[("Video files", "*.mp4 *.avi *.mkv *.mov")]
        )
        if self.video_path:
            self.file_label.configure(text=os.path.basename(self.video_path))

    def convert_video(self):
        if not self.video_path:
            self.status_label.configure(text="Please select a video file first!", fg="#FF0000")
            return

        save_path = filedialog.asksaveasfilename(
            defaultextension=".mp3",
            filetypes=[("MP3 files", "*.mp3")]
        )

        if save_path:
            try:
                self.status_label.configure(text="Converting... Please wait", fg="#FFA500")
                self.update()

                video = mp.VideoFileClip(self.video_path)
                video.audio.write_audiofile(save_path)
                video.close()

                self.status_label.configure(text="Conversion completed successfully! 🎉", fg="#008000")
            except Exception as e:
                self.status_label.configure(text=f"Error: {str(e)}", fg="#FF0000")

if __name__ == "__main__":
    app = VideoToAudioConverter()
    app.mainloop()
