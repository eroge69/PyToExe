import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import pygame
import os

class TimerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Шалгалтын Таймер")
        self.root.geometry("1920x1080")  # Full HD
        self.root.configure(bg="black")

        self.running = False
        self.paused = False
        self.time_left = 0
        self.bell_before = 60
        self.bell_played = False

        # Фонт
        font_title = ("Arial", 30, "bold")
        font_timer = ("Arial", 150, "bold")
        fg_color = "white"

        # === Top logo + нэр ===
        top_frame = tk.Frame(self.root, bg="black")
        top_frame.pack(pady=20)

        try:
            logo_img = Image.open("Logo.png").resize((100, 100), Image.LANCZOS)
            self.logo = ImageTk.PhotoImage(logo_img)
            tk.Label(top_frame, image=self.logo, bg="black").pack(side="left", padx=20)
        except:
            tk.Label(top_frame, text="[Лого олдсонгүй]", font=("Arial", 12), bg="black", fg="white").pack(side="left", padx=20)

        tk.Label(top_frame, text="ХИЛИЙН ЦЭРГИЙН 0224 ДҮГЭЭР ТУСГАЙ САЛБАР", font=font_title, bg="black", fg=fg_color).pack(side="left")

        # === Timer ===
        self.label_time = tk.Label(self.root, text="00:00:00", font=font_timer, bg="black", fg="lime")
        self.label_time.pack(expand=True)

        # === Товчнууд ===
        button_frame = tk.Frame(self.root, bg="black")
        button_frame.pack(pady=10)

        tk.Button(button_frame, text="ЭХЛЭХ", font=("Arial", 16), width=10, command=self.start_timer).grid(row=0, column=0, padx=10)
        tk.Button(button_frame, text="ЗОГСООХ", font=("Arial", 16), width=10, command=self.pause_timer).grid(row=0, column=1, padx=10)
        tk.Button(button_frame, text="ДУУСГАХ", font=("Arial", 16), width=10, command=self.end_timer).grid(row=0, column=2, padx=10)

        # === Цаг тохируулах ===
        input_frame = tk.Frame(self.root, bg="black")
        input_frame.pack(pady=10)

        self.hour_var = tk.Entry(input_frame, font=("Arial", 16), width=5)
        self.minute_var = tk.Entry(input_frame, font=("Arial", 16), width=5)
        self.second_var = tk.Entry(input_frame, font=("Arial", 16), width=5)
        self.bell_var = tk.Entry(input_frame, font=("Arial", 16), width=5)

        self.hour_var.insert(0, "0")
        self.minute_var.insert(0, "10")
        self.second_var.insert(0, "0")
        self.bell_var.insert(0, "1")

        tk.Label(input_frame, text="Цаг:", font=("Arial", 16), bg="black", fg="white").pack(side="left")
        self.hour_var.pack(side="left")
        tk.Label(input_frame, text="Минут:", font=("Arial", 16), bg="black", fg="white").pack(side="left")
        self.minute_var.pack(side="left")
        tk.Label(input_frame, text="Секунд:", font=("Arial", 16), bg="black", fg="white").pack(side="left")
        self.second_var.pack(side="left")
        tk.Label(input_frame, text="Хонхны өмнө (мин):", font=("Arial", 16), bg="black", fg="white").pack(side="left")
        self.bell_var.pack(side="left")

        self.root.bind("<Escape>", lambda e: self.root.destroy())

        pygame.mixer.init()
        self.update_timer()

    def format_time(self, secs):
        h = secs // 3600
        m = (secs % 3600) // 60
        s = secs % 60
        return f"{h:02}:{m:02}:{s:02}"

    def start_timer(self):
        try:
            hours = int(self.hour_var.get())
            mins = int(self.minute_var.get())
            secs = int(self.second_var.get())
            bell_mins = int(self.bell_var.get())

            self.time_left = hours * 3600 + mins * 60 + secs
            self.bell_before = bell_mins * 60
            self.running = True
            self.paused = False
            self.bell_played = False
        except:
            messagebox.showerror("Алдаа", "Зөв тоо оруулна уу.")

    def pause_timer(self):
        if self.running:
            self.paused = not self.paused

    def end_timer(self):
        self.running = False
        self.time_left = 0
        self.label_time.config(text="00:00:00")
        self.play_sound("end.wav")

    def update_timer(self):
        if self.running and not self.paused and self.time_left > 0:
            self.time_left -= 1
            self.label_time.config(text=self.format_time(self.time_left))

            if self.time_left == self.bell_before and not self.bell_played:
                self.play_sound("bell.wav")
                self.bell_played = True

            if self.time_left <= 0:
                self.end_timer()

        self.root.after(1000, self.update_timer)

    def play_sound(self, sound_file):
        if os.path.exists(sound_file):
            try:
                pygame.mixer.music.load(sound_file)
                pygame.mixer.music.play()
            except Exception as e:
                print("Sound error:", e)

# === App эхлүүлэлт ===
if __name__ == "__main__":
    root = tk.Tk()
    app = TimerApp(root)
    root.mainloop()
