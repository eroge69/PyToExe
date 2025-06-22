import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog, ttk
import threading
import os

from ytptennis import generate_ytp_tennis

class TennisGUI:
    def __init__(self, root):
        self.root = root
        root.title("YTP Tennis Generator")
        root.geometry("500x400")
        root.resizable(False, False)

        # Variables
        self.youtube_url = tk.StringVar()
        self.audio_file = tk.StringVar()
        self.image_files = []
        self.output_file = tk.StringVar(value="final_output.mp4")
        self.chaos = tk.BooleanVar(value=False)
        self.long = tk.BooleanVar(value=False)

        # Widgets
        ttk.Label(root, text="YouTube URL:").pack(pady=4, anchor='w', padx=10)
        ttk.Entry(root, textvariable=self.youtube_url, width=60).pack(padx=10, fill='x')

        ttk.Label(root, text="Audio File (MP3/WAV):").pack(pady=4, anchor='w', padx=10)
        frame_audio = ttk.Frame(root)
        frame_audio.pack(padx=10, fill='x')
        ttk.Entry(frame_audio, textvariable=self.audio_file, width=45).pack(side='left', fill='x', expand=True)
        ttk.Button(frame_audio, text="Browse", command=self.browse_audio).pack(side='left', padx=5)

        ttk.Label(root, text="Images/GIFs:").pack(pady=4, anchor='w', padx=10)
        frame_images = ttk.Frame(root)
        frame_images.pack(padx=10, fill='x')
        self.images_label = ttk.Label(frame_images, text="No files selected.")
        self.images_label.pack(side='left', fill='x', expand=True)
        ttk.Button(frame_images, text="Add Files", command=self.browse_images).pack(side='left', padx=5)

        ttk.Label(root, text="Output File:").pack(pady=4, anchor='w', padx=10)
        frame_output = ttk.Frame(root)
        frame_output.pack(padx=10, fill='x')
        ttk.Entry(frame_output, textvariable=self.output_file, width=45).pack(side='left', fill='x', expand=True)
        ttk.Button(frame_output, text="Browse", command=self.browse_output).pack(side='left', padx=5)

        ttk.Checkbutton(root, text="Enable Chaos Mode", variable=self.chaos).pack(pady=4, anchor='w', padx=10)
        ttk.Checkbutton(root, text="Enable Long Mode", variable=self.long).pack(pady=4, anchor='w', padx=10)

        ttk.Button(root, text="Generate YTP Tennis", command=self.start_generation).pack(pady=16)
        self.progress = ttk.Label(root, text="")
        self.progress.pack(pady=4)

    def browse_audio(self):
        file = filedialog.askopenfilename(filetypes=[("Audio Files", "*.mp3 *.wav")])
        if file:
            self.audio_file.set(file)

    def browse_images(self):
        files = filedialog.askopenfilenames(filetypes=[("Images and GIFs", "*.jpg *.jpeg *.png *.gif")])
        if files:
            self.image_files = list(files)
            self.images_label.config(text=f"{len(self.image_files)} file(s) selected.")

    def browse_output(self):
        file = filedialog.asksaveasfilename(defaultextension=".mp4", filetypes=[("MP4 Video", "*.mp4")])
        if file:
            self.output_file.set(file)

    def start_generation(self):
        # Validation
        if not self.youtube_url.get().strip():
            messagebox.showerror("Error", "Please enter a YouTube URL.")
            return
        if not self.audio_file.get().strip():
            messagebox.showerror("Error", "Please select an audio file.")
            return
        if not self.image_files:
            messagebox.showerror("Error", "Please select at least one image/gif file.")
            return
        if not self.output_file.get().strip():
            messagebox.showerror("Error", "Please specify an output file.")
            return

        self.progress.config(text="Generating... Please wait.")
        self.root.update()

        # Run in background thread to avoid freezing the GUI
        thread = threading.Thread(target=self.run_generator)
        thread.start()

    def run_generator(self):
        try:
            generate_ytp_tennis(
                source_video=self.youtube_url.get(),
                audio_file=self.audio_file.get(),
                image_files=self.image_files,
                output_file=self.output_file.get(),
                chaos=self.chaos.get(),
                long=self.long.get()
            )
            self.progress.config(text="Done! Output saved.")
            messagebox.showinfo("Success", "YTP Tennis Video generated successfully!")
        except Exception as e:
            self.progress.config(text="Failed.")
            messagebox.showerror("Error", f"Generation failed:\n{e}")

def main():
    root = tk.Tk()
    app = TennisGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()