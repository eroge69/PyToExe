import tkinter as tk
from tkinter import messagebox
from datetime import datetime
import time
import threading
import os
import json
from pygame import mixer

# Initialize audio mixer
mixer.init()

# File to store your custom times
SAVE_FILE = "period_times.json"

# Default times for each slot
default_times = [
    "7:50 AM", "8:25 AM", "8:30 AM", "9:10 AM", "9:50 AM",
    "10:30 AM", "10:50 AM", "11:30 AM", "12:10 PM", "12:50 PM", "1:30 PM"
]

# Custom labels
period_labels = [
    "Period 1", "Register marking", "Period 2", "Period 3", "Period 4",
    "Interval", "Period 5", "Period 6", "Period 7", "Period 8", "End"
]

def load_times():
    if os.path.exists(SAVE_FILE):
        with open(SAVE_FILE, "r") as f:
            return json.load(f)
    return default_times.copy()

def save_times():
    times = [e.get() for e in entries]
    with open(SAVE_FILE, "w") as f:
        json.dump(times, f)
    messagebox.showinfo("Saved", "Schedule saved successfully!")

def play_sound(idx):
    fn = f"{idx+1}.mp3"
    if os.path.exists(fn):
        mixer.music.load(fn)
        mixer.music.play()
    else:
        print(f"Audio file not found: {fn}")

def check_time():
    played = [False] * len(entries)
    while True:
        now = datetime.now().strftime("%I:%M %p").lstrip("0")
        for i, entry in enumerate(entries):
            val = entry.get().strip().lower()
            if val == "no":
                continue
            try:
                sched = datetime.strptime(val, "%I:%M %p").strftime("%I:%M %p").lstrip("0")
            except ValueError:
                continue
            if now == sched:
                if not played[i]:
                    play_sound(i)
                    played[i] = True
            else:
                played[i] = False
        time.sleep(1)

def update_clock():
    while True:
        now = datetime.now().strftime("%I:%M:%S %p").lstrip("0")
        clock_label.config(text=now)
        time.sleep(1)

# Function to play the 12th audio with confirmation prompt
def play_announcement():
    if messagebox.askyesno("Confirmation", "Are you sure?"):
        fn = "12.mp3"
        if os.path.exists(fn):
            mixer.music.load(fn)
            mixer.music.play()
        else:
            print("Audio file not found: 12.mp3")

# Function to stop the announcement audio
def stop_announcement():
    mixer.music.stop()

# ——— GUI SETUP ———
root = tk.Tk()
root.title("School Bell Scheduler - Mo/Dutugemunu Central College")
root.geometry("500x700")
root.resizable(False, False)
root.configure(bg="#22e7e1")  # Set background color

tk.Label(root, text="School Bell Scheduler", font=("Arial", 20, "bold"), bg="#22e7e1").pack(pady=20)

frame_container = tk.Frame(root, bg="#22e7e1")
frame_container.pack(pady=10)

entries = []
loaded = load_times()

for i, label_text in enumerate(period_labels):
    row = tk.Frame(frame_container, bg="#22e7e1")
    row.pack(fill="x", pady=5)

    tk.Label(row, text=label_text, font=("Arial", 14), width=18, anchor="w", bg="#22e7e1").pack(side=tk.LEFT, padx=5)

    e = tk.Entry(row, font=("Arial", 14), width=15)
    e.insert(0, loaded[i])
    e.pack(side=tk.LEFT, padx=5)
    entries.append(e)

    tk.Button(row, text="▶ Play", font=("Arial", 12), command=lambda i=i: play_sound(i)).pack(side=tk.LEFT, padx=5)

footer = tk.Frame(root, bg="#22e7e1")
footer.pack(side=tk.BOTTOM, fill=tk.X, pady=15, padx=10)

clock_label = tk.Label(
    footer,
    text="",
    font=("Arial", 20, "bold"),
    bg="#2196F3",
    fg="white",
    padx=10,
    pady=10,
    anchor="w",
    relief="groove"
)
clock_label.pack(side=tk.LEFT, padx=(10, 0))

tk.Label(
    footer,
    text="Pahantharuka Media Unit DCC",
    font=("Arial", 14, "bold"),
    bg="#22e7e1",
    fg="gray"
).pack(side=tk.RIGHT, padx=(0, 10))

# Announcement Buttons (Start & Stop)
announcement_frame = tk.Frame(root, bg="#22e7e1")
announcement_frame.pack(pady=15)

tk.Button(announcement_frame, 
          text="📢 Announcement Start", 
          font=("Arial", 14), 
          bg="#f39c12", 
          fg="white", 
          command=play_announcement).pack(side=tk.LEFT, padx=5)

tk.Button(announcement_frame, 
          text="⏹ Announcement Stop", 
          font=("Arial", 14), 
          bg="red", 
          fg="white", 
          command=stop_announcement).pack(side=tk.LEFT, padx=5)

# Launch background threads
threading.Thread(target=check_time, daemon=True).start()
threading.Thread(target=update_clock, daemon=True).start()

root.mainloop()