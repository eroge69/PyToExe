import customtkinter as ctk
from tkinter import filedialog
import os

import moviepy.editor as mp

# Set theme and color scheme
ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

class VideoToAudioConverter(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Configure window
        self.title("Cute Video to Audio Converter 🎵")
        self.geometry("600x400")
        self.configure(fg_color="#FFE5E5")  # Light pink background

        # Create main frame
        self.main_frame = ctk.CTkFrame(self, fg_color="#FFF0F5", corner_radius=20)
        self.main_frame.pack(pady=20, padx=20, fill="both", expand=True)

        # Title label
        self.title_label = ctk.CTkLabel(
            self.main_frame,
            text="Video to Audio Converter 🎥 ➜ 🎵",
            font=("Arial", 24, "bold"),
            text_color="#FF69B4"
        )
        self.title_label.pack(pady=20)

        # Select video button
        self.select_button = ctk.CTkButton(
            self.main_frame,
            text="Select Video File 📁",
            command=self.select_video,
            font=("Arial", 16),
            fg_color="#FF69B4",
            hover_color="#FF1493",
            corner_radius=10
        )
        self.select_button.pack(pady=15)

        # Selected file label
        self.file_label = ctk.CTkLabel(
            self.main_frame,
            text="No file selected",
            font=("Arial", 14),
            text_color="#666666"
        )
        self.file_label.pack(pady=10)

        # Convert button
        self.convert_button = ctk.CTkButton(
            self.main_frame,
            text="Convert to Audio 🎵",
            command=self.convert_video,
            font=("Arial", 16),
            fg_color="#87CEEB",
            hover_color="#4169E1",
            corner_radius=10
        )
        self.convert_button.pack(pady=15)

        # Status label
        self.status_label = ctk.CTkLabel(
            self.main_frame,
            text="",
            font=("Arial", 14),
            text_color="#666666"
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
            self.status_label.configure(text="Please select a video file first!", text_color="#FF0000")
            return

        # Ask for save location
        save_path = filedialog.asksaveasfilename(
            defaultextension=".mp3",
            filetypes=[("MP3 files", "*.mp3")]
        )

        if save_path:
            try:
                self.status_label.configure(text="Converting... Please wait", text_color="#FFA500")
                self.update()

                # Convert video to audio
                video = mp.VideoFileClip(self.video_path)
                video.audio.write_audiofile(save_path)
                video.close()

                self.status_label.configure(text="Conversion completed successfully! 🎉", text_color="#008000")
            except Exception as e:
                self.status_label.configure(text=f"Error: {str(e)}", text_color="#FF0000")

if __name__ == "__main__":
    app = VideoToAudioConverter()
    app.mainloop()