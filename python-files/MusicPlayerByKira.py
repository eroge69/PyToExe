from distutils.core import setup
import pygame # Импорт всякого кала // Import some shit
import os
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk
from pygame import mixer
from mutagen.mp3 import MP3
import py2exe

class MusicPlayer(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Advanced Music Player By Kira!") 
        self.geometry("1920x1080")
        self.is_paused = False
        self.current_track_index = 0
        self.track_list = []
        self.is_dark_theme = False  # Проверка Темы // Theme Check

        # Интерфейс // UI
        self.track_label = tk.Label(self, text="No track loaded", wraplength=250)
        self.track_label.pack(pady=10)

        self.play_button = ttk.Button(self, text=">", command=self.play_music)
        self.play_button.pack(pady=5)

        self.pause_button = ttk.Button(self, text="||", command=self.pause_music)
        self.pause_button.pack(pady=5)

        self.stop_button = ttk.Button(self, text="||", command=self.stop_music)
        self.stop_button.pack(pady=5)

        self.previous_button = ttk.Button(self, text="<--", command=self.previous_track)
        self.previous_button.pack(pady=5)

        self.next_button = ttk.Button(self, text="-->", command=self.next_track)
        self.next_button.pack(pady=5)

        self.track_listbox = tk.Listbox(self, selectmode=tk.SINGLE, width=40)
        self.track_listbox.pack(pady=20)

        self.load_track_button = ttk.Button(self, text="Add to Playlist", command=self.add_to_playlist)
        self.load_track_button.pack(pady=5)

        self.clear_playlist_button = ttk.Button(self, text="Clear Playlist", command=self.clear_playlist)
        self.clear_playlist_button.pack(pady=5)

        self.clear_playlist_button = ttk.Button(self, text="Repeat Song", command=self.repeat_song)
        self.clear_playlist_button.pack(pady=5)

        self.clear_playlist_button = ttk.Button(self, text="Repeat Playlist", command=self.repeat_playlist)
        self.clear_playlist_button.pack(pady=5)
        
        self.volume_scale = tk.Scale(self, from_=0, to=1, resolution=0.1, orient=tk.HORIZONTAL, label="Volume", command=self.set_volume)
        self.volume_scale.set(1.0)  
        self.volume_scale.pack(pady=10)

        # Кнопка для переключения тем / Button To Change Theme 
        self.toggle_theme_button = ttk.Button(self, text="Change Theme", command=self.toggle_theme)
        self.toggle_theme_button.pack(pady=5)

        self.update_theme()  # Я хз как это работает но оно работает , не трогайте это // Idk how it works but it works , dont touch it
    
    def repeat_song(self):
        pygame.mixer.music.play(-1)

    def repeat_playlist(self):
        pygame.mixer.music.play(-1)

    def add_to_playlist(self):
        music_file = filedialog.askopenfilename(
            title="Load Music",
            filetypes=(("MP3 files", "*.mp3"), ("All files", "*.*"))
        )
        if music_file:
            self.track_list.append(music_file)
            self.track_listbox.insert(tk.END, os.path.basename(music_file))

    def clear_playlist(self):
        self.track_list.clear()
        self.track_listbox.delete(0, tk.END)
        self.track_label.config(text="No track loaded")

    def play_music(self):
        if not self.track_list:
            messagebox.showwarning("Warning", "No track loaded!")
            return

        if self.current_track_index < len(self.track_list):
            mixer.music.load(self.track_list[self.current_track_index])
            mixer.music.play()
            self.update_track_info()

    def pause_music(self):
        if not self.track_list:
            messagebox.showwarning("Warning", "No track loaded!")
            return
        if self.is_paused:
            mixer.music.unpause()
            self.is_paused = False
        else:
            mixer.music.pause()
            self.is_paused = True

    def stop_music(self):
        mixer.music.stop()

    def previous_track(self):
        if self.track_list:
            self.current_track_index = (self.current_track_index - 1) % len(self.track_list)
            self.play_music()

    def next_track(self):
        if self.track_list:
            self.current_track_index = (self.current_track_index + 1) % len(self.track_list)
            self.play_music()

    def set_volume(self, volume):
        mixer.music.set_volume(float(volume))

    def update_track_info(self):
        if self.track_list:
            audio = MP3(self.track_list[self.current_track_index])
            self.track_label.config(text=f"{audio['TIT2']}: {audio['TPE1']}")

    def toggle_theme(self):
        self.is_dark_theme = not self.is_dark_theme
        self.update_theme()

    def update_theme(self):
        if self.is_dark_theme:
            self.configure(bg='black')
            self.track_label.config(bg='black', fg='white')
            self.play_button.config(style='Dark.TButton')
            self.pause_button.config(style='Dark.TButton')
            self.stop_button.config(style='Dark.TButton')
            self.load_button.config(style='Dark.TButton')
            self.previous_button.config(style='Dark.TButton')
            self.next_button.config(style='Dark.TButton')
            self.toggle_theme_button.config(style='Dark.TButton')
            self.clear_playlist_button.config(style='Dark.TButton')
            self.load_track_button.config(style='Dark.TButton')
            self.track_listbox.config(bg='black', fg='white')
            self.volume_scale.config(bg='black', fg='white')
        else:
            self.configure(bg='white')
            self.track_label.config(bg='white', fg='black')
            self.play_button.config(style='Light.TButton')
            self.pause_button.config(style='Light.TButton')
            self.stop_button.config(style='Light.TButton')
            self.previous_button.config(style='Light.TButton')
            self.next_button.config(style='Light.TButton')
            self.toggle_theme_button.config(style='Light.TButton')
            self.clear_playlist_button.config(style='Light.TButton')
            self.load_track_button.config(style='Light.TButton')
            self.track_listbox.config(bg='white', fg='black')
            self.volume_scale.config(bg='white', fg='black')

if __name__ == "__main__":
    pygame.init()
    mixer.init()
    app = MusicPlayer()
    app.mainloop()
    pygame.quit()
setup(console=['MusicPlayerByKira.py'])