import tkinter as tk
import time
import threading
from tkinter import font

class KronometreApp:
    def __init__(self, master):
        self.master = master
        self.master.title("Kronometre")
        self.running = False
        self.start_time = None
        self.elapsed_time = 0
        self.dark_mode = False

        # Fontlar
        self.montserrat_ultra = font.Font(family="Montserrat", size=40, weight="bold")
        self.montserrat_bold = font.Font(family="Montserrat", size=10, weight="bold")
        self.montserrat_regular = font.Font(family="Montserrat", size=10, weight="normal")

        self.label = tk.Label(master, text="00:00:00.000", font=self.montserrat_ultra)
        self.label.pack(pady=20)

        self.button_frame = tk.Frame(master)
        self.button_frame.pack()

        self.start_button = tk.Button(self.button_frame, text="Başlat", command=self.start, font=self.montserrat_bold)
        self.start_button.pack(side=tk.LEFT, padx=5)

        self.stop_button = tk.Button(self.button_frame, text="Durdur", command=self.stop, font=self.montserrat_bold)
        self.stop_button.pack(side=tk.LEFT, padx=5)

        self.reset_button = tk.Button(self.button_frame, text="Sıfırla", command=self.reset, font=self.montserrat_bold)
        self.reset_button.pack(side=tk.LEFT, padx=5)

        self.mode_button = tk.Button(master, text="Karanlık Moda Geç", command=self.toggle_mode, font=self.montserrat_bold)
        self.mode_button.pack(pady=10)

        # Alt yazı: Mustafa Karabayır
        self.signature_label = tk.Label(master, text="Mustafa Karabayır", font=self.montserrat_regular)
        self.signature_label.pack(pady=(0, 10))  # Butona yakın dursun diye üstten boşluk yok

        self.apply_theme()

    def apply_theme(self):
        if self.dark_mode:
            bg = "#2E2E2E"
            fg = "#FFFFFF"
            button_bg = "#444444"
            button_fg = "#FFFFFF"
            self.master.configure(bg=bg)
            self.label.configure(bg=bg, fg=fg)
            self.button_frame.configure(bg=bg)
            self.mode_button.configure(text="Aydınlık Moda Geç", bg=button_bg, fg=button_fg)
            self.signature_label.configure(bg=bg, fg=fg)
        else:
            bg = "#F0F0F0"
            fg = "#000000"
            button_bg = "#E0E0E0"
            button_fg = "#000000"
            self.master.configure(bg=bg)
            self.label.configure(bg=bg, fg=fg)
            self.button_frame.configure(bg=bg)
            self.mode_button.configure(text="Karanlık Moda Geç", bg=button_bg, fg=button_fg)
            self.signature_label.configure(bg=bg, fg=fg)

        for button in [self.start_button, self.stop_button, self.reset_button]:
            button.configure(bg=button_bg, fg=button_fg)

    def toggle_mode(self):
        self.dark_mode = not self.dark_mode
        self.apply_theme()

    def update(self):
        while self.running:
            current_time = time.time()
            total_time = self.elapsed_time + (current_time - self.start_time)
            hours, rem = divmod(int(total_time), 3600)
            minutes, seconds = divmod(rem, 60)
            milliseconds = int((total_time - int(total_time)) * 1000)
            time_str = f"{hours:02d}:{minutes:02d}:{seconds:02d}.{milliseconds:03d}"
            self.label.config(text=time_str)
            time.sleep(0.05)

    def start(self):
        if not self.running:
            self.start_time = time.time()
            self.running = True
            threading.Thread(target=self.update, daemon=True).start()

    def stop(self):
        if self.running:
            self.elapsed_time += time.time() - self.start_time
            self.running = False

    def reset(self):
        self.running = False
        self.start_time = None
        self.elapsed_time = 0
        self.label.config(text="00:00:00.000")

if __name__ == "__main__":
    root = tk.Tk()
    app = KronometreApp(root)
    root.mainloop()