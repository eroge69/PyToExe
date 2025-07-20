import tkinter as tk
from tkinter import messagebox, ttk
import threading
import time
import webbrowser
import os
import sys
from playsound import playsound
import random

# === CONFIG ===
LOADING_TIME = 10  # seconds for loading bar
SOUNDS = {
    'start': 'https://actions.google.com/sounds/v1/alarms/beep_short.ogg',
    'glitch': 'glitch.wav',   # You can download or replace this with a local sound file
    'popup': 'popup.wav',
    'creepy': 'creepy.wav'
}

# For this demo, I'll use some built-in Windows beep sounds via winsound instead of playsound 
# to avoid file dependencies. But playsound can play mp3/wav if you provide files.

try:
    import winsound
    SOUND_LIB = 'winsound'
except ImportError:
    SOUND_LIB = 'playsound'

# Helper to play sounds
def play_sound(file=None, freq=800, dur=200):
    if SOUND_LIB == 'winsound':
        if file:
            try:
                winsound.PlaySound(file, winsound.SND_FILENAME | winsound.SND_ASYNC)
            except:
                pass
        else:
            winsound.Beep(freq, dur)
    else:
        if file and os.path.exists(file):
            playsound(file, block=False)

# --- Main app class ---
class PrankLoader:
    def __init__(self, root):
        self.root = root
        self.root.title("CS2 Cheat Loader")
        self.root.geometry("500x300")
        self.root.configure(bg='black')
        self.root.attributes('-topmost', True)
        self.root.resizable(False, False)

        self.label = tk.Label(self.root, text="CS2 Cheat Loader", font=("Consolas", 24, "bold"), fg="red", bg="black")
        self.label.pack(pady=30)

        self.status_label = tk.Label(self.root, text="Initializing...", font=("Consolas", 14), fg="white", bg="black")
        self.status_label.pack(pady=10)

        self.progress = ttk.Progressbar(self.root, orient='horizontal', length=400, mode='determinate')
        self.progress.pack(pady=20)
        self.progress['value'] = 0

        self.glitch_effect_active = False

        # Start the initial delay then confirmation popup
        self.root.after(3000, self.ask_confirmation)

        # Start flicker effect
        self.flicker()

    def flicker(self):
        # Randomly flicker the label color between red and dark red to simulate glitch
        if self.glitch_effect_active:
            color = random.choice(['#FF0000', '#8B0000', '#FF4500'])
            self.label.config(fg=color)
        else:
            self.label.config(fg="red")
        self.root.after(200, self.flicker)

    def ask_confirmation(self):
        self.glitch_effect_active = True
        play_sound(freq=1000, dur=300)
        answer = messagebox.askyesno("Warning", "Are you sure you want to run it?")
        if answer:
            self.status_label.config(text="Loading cheat... Do not close.")
            play_sound(freq=700, dur=500)
            threading.Thread(target=self.loading_sequence).start()
        else:
            self.status_label.config(text="Operation cancelled.")
            play_sound(freq=300, dur=700)
            self.glitch_effect_active = False
            self.root.after(2000, self.root.destroy)

    def loading_sequence(self):
        self.progress['maximum'] = 100
        for i in range(101):
            time.sleep(LOADING_TIME / 100)
            self.progress['value'] = i
            if i % 15 == 0:
                # Play glitch beep randomly during loading
                play_sound(freq=random.randint(400,1200), dur=100)
            self.root.update_idletasks()

        self.status_label.config(text="Loading complete!")
        self.glitch_effect_active = False
        play_sound(freq=1200, dur=400)
        time.sleep(0.5)

        # Open browser prank
        self.status_label.config(text="Launching cheat UI...")
        prank_url = "www.gmail.com"  # classic rickroll hacker prank
        webbrowser.open(prank_url)
        play_sound(freq=1500, dur=600)
        time.sleep(8)

        # Attempt to close browser (only works on Windows with taskkill, optional)
        self.status_label.config(text="Closing cheat UI...")
        if sys.platform.startswith('win'):
            os.system('taskkill /im chrome.exe /f >nul 2>&1')
            os.system('taskkill /im opera.exe /f >nul 2>&1')
            os.system('taskkill /im msedge.exe /f >nul 2>&1')
        time.sleep(2)

        # Final scary popup
        play_sound(freq=500, dur=800)
        messagebox.showerror("Security Alert", "Next time turn on antivirus buddy.\nEnjoy getting your passwords stolen.")
        self.root.destroy()

def main():
    root = tk.Tk()
    style = ttk.Style(root)
    style.theme_use('clam')
    style.configure("TProgressbar", troughcolor='black', background='red')

    app = PrankLoader(root)
    root.mainloop()

if __name__ == "__main__":
    main()
